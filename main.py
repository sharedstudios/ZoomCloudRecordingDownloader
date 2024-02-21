import requests
import webbrowser
import json
import os
from time import sleep
import sys
import datetime
import base64
import googleDriveUploader

# keeping our api key and api secret off the program file so it's secure
fl = open('api.txt', 'r')
apis = fl.readlines()

# access api key information from file
accountId = apis[0].replace("\n", "")
clientId = apis[1].replace("\n", "")
clientSec = apis[2].replace("\n", "")
em = apis[3].replace("\n", "")
pas = apis[4].replace("\n", "")

clientDataString = '%s:%s' % (clientId,clientSec)
encodedClientData = base64.b64encode(clientDataString.encode()).decode()
zoomAccessToken = ''

# get zoom access with server to server app info
def getZoomAccessToken():
    authUrl = 'https://zoom.us/oauth/token?grant_type=account_credentials&account_id=%s' % accountId
    headers = {
        'authorization': 'Basic %s' % encodedClientData
        }
    payload = ""
    res = requests.request("POST", authUrl, headers=headers, data=payload)
    if(res.status_code == 200):
        global zoomAccessToken
        zoomAccessToken = res.json()['access_token']
    else:
        print("Unable to retrieve access_token for zoom. Please check client id, client secret and account id provided in api.txt file")
        sys.exit()

getZoomAccessToken()

headers = {
    "authorization": "Bearer " + zoomAccessToken,
}

# this is defined to make sure no illegal character appear in potential filenames
def correctFileName(filename):
    ret = filename.lower()
    illegalFirstChars = [' ', '.', '_', '-']
    illegalChars = ['#', '%', '&', '{', '}', '\\', '<', '>', '*', '?', '/', ' ', '$', '!', "'", '"', ':', '@', '.', "'"]
    for index in range(len(filename)):
        if not filename[index] in illegalFirstChars:
            ret = filename[index:]
            break

    for char in illegalChars:
        ret = ret.replace(char, "")
    return ret

# had to implement sessions since zoom is annoying and forcing me to login to download their recordings
session_requests = requests.session()
signin = "https://zoom.us/signin"
values = {'email': em,
          'password': pas}
result = session_requests.post(signin, data=values)


# call to retrieve list of zoom users
def getUsers():
    userlistparam = {'api_key': clientId, 'api_secret': clientSec, 'data_type': "JSON", 'page_size': 300}
    res = requests.get('https://api.zoom.us/v2/users', headers=headers, params=userlistparam)
    if (res.status_code == 401):
        getZoomAccessToken()
        sleep(10)
        getUsers()
    if (res.status_code == 200):
        return res.json()['users']

users = getUsers()
summary = []
durationTotal = 0
userMeetingCount = 0

# for i in range(len(users)):
#     print(users[i])

# partial upload by user index
# users = users[0:3]
# for user in users:
#     print(user)
# users = users[30:] # upload from 30 to end

# for loop to go through each user in the list
for i in range(len(users)):

    # this retireves user that is currently being looked at and relevant info
    currUser = users[i]
    # temp change to only download if general or events
    currUserEmail = currUser['email']
    # if user has any recordings, this string will be the name of created directory
    username = f"{currUser['first_name']}-{currUser['last_name']}"
    if username == "-":
        username = currUser['email'][:currUser['email'].find('@')]
    # user id needed to pass to api call
    currID = currUser['id']
    # current range of firstDate (date from which you want to start looking for video)
    firstDate = datetime.date(2024, 1, 1)
    # current range of to date (date from which you want to end looking for video)
    currentTo = datetime.date.today()
    # current range of from date
    currentFrom = currentTo - datetime.timedelta(weeks=4)

    # download the monthly recording until the first date of the events
    while currentFrom >= firstDate:

        # convert date obj to string format
        currentFromStr = currentFrom.strftime("%Y-%m-%d")
        currentToStr = currentTo.strftime("%Y-%m-%d")

        print('Checking User "%s[%s]" for recordings' % (username,currUserEmail) + ' from ' + currentFromStr + ' to ' + currentToStr + "---" + str(i+1) + '/' + str(len(users)))
        # Waits 1 Second to Prevent Too Many API Calls at once
        sleep(1)


        # second set of parameters passed to second api call
        videolistparams = {'api_key': clientId, 'api_secret': clientSec, 'data_type': "JSON", 'userId': currID, 'page_size': 300,
                        'from': currentFromStr, 'to': currentToStr}

        # call to retrieve json object cotaining list of user recordings
        while True:
            videolistjson = requests.get(f"https://api.zoom.us/v2/users/{currID}/recordings", headers=headers,
                                        params=videolistparams).json()

            if "error" in videolistjson:
                if videolistjson["error"]["code"] == 403:
                    print("Too Many API Calls at Once. Will Retry API Call in One Minute")
                    sleep(60)
                    continue
                if videolistjson["error"]["code"] == 401:
                    print("Access token expired error. Refreshing and Retrying")
                    getZoomAccessToken()
                    sleep(10)
                    continue
                else:
                    sys.exit(
                        "Unknown Error. Please run program again. If problem persists, contact danara@sharedstudios.com")

            break
        currUserMeetings = videolistjson['meetings']

        print(f"{username} has {len(currUserMeetings)} awaiting to be downloaded and uploaded")
        userMeetingCount += len(currUserMeetings)
        # if this user has any recordings, this block of code will download them
        if (len(currUserMeetings) > 0):
            print('%d Recordings found for User "%s"; Downloading the new recording MP4 Files' % (
            len(currUserMeetings), username))
            # if folder for videos does not exist yet, creates a folder named after username
            #if not os.path.exists("./" + username):
                # os.makedirs("./" + username)

            # print username
            # print " "

            # for loop iterates through a meeting object, and we specfically want to contruct the meeting name
            # as well as iterate through recordings of a meeting
            for j in range(len(currUserMeetings)):
                currMeeting = currUserMeetings[j]
                print(currMeeting['start_time'])
                meetingName = currMeeting['topic'] + "-" + currMeeting['start_time']
                meetingName = correctFileName(meetingName)
                # get all meeting ids and their duration
                summary.append(currMeeting['uuid'] + " " + str(currMeeting['duration']) + '\n')
                durationTotal += currMeeting['duration']


                # a meeting might have multiple recordings, so this code block will iterate through those meetings
                for k in range(len(currMeeting['recording_files'])):

                    currRecording = currMeeting['recording_files'][k]
                    oldFilename = username + '-' + currRecording['recording_start'][:10] + '-' + currRecording['id'] + '.' + currRecording['file_type']
                    
                    # we finally  get to the code where we start donwloading
                    filename = username + '-' + currRecording['recording_start'][:10] + '-' + currRecording['recording_type']+ '-' + currMeeting['uuid'] + '.' + currRecording['file_type']
                    filename = correctFileName(filename)

                    # check if the file exist in google drive or not
                    if googleDriveUploader.containsFile(oldFilename) or googleDriveUploader.containsFile(filename):
                        print(f"Current file already exists in google drive -- {k+1}/{len(currMeeting['recording_files'])}")
                        fileid = googleDriveUploader.lookupFileId(filename) or googleDriveUploader.lookupFileId(oldFilename)
                        # print(fileid)
                        googleDriveUploader.updateFileName(fileid, filename)
                        continue

                    # if recording file is already downloaded, this script won't download it again
                    # this allows us to call this script to download new files after downloading an inital batch
                    if not os.path.exists(filename):  # to store locally, use ["./" + username + "/" + filename]
                        link = currRecording['download_url']
                        link += "?access_token="+zoomAccessToken
                        with open(filename, "wb") as f:
                            print("Downloading %s" % filename)
                            response = session_requests.get(link, stream=True)
                            if (response.status_code == 401):
                                getZoomAccessToken()
                                sleep(10)
                                response = session_requests.get(link, stream=True)
                            total_length = currRecording['file_size']
                            if total_length == 0:
                                continue
                            else:
                                print(currRecording)
                                total_length = int(total_length)
                                dl = 0
                                for data in response.iter_content(chunk_size=4096):
                                    dl += len(data)
                                    f.write(data)
                                    per = (100.0 * dl) / total_length
                                    done = int(50 * dl / total_length)
                                    sys.stdout.write("\r[%s%s]%f%%" % ('=' * done, ' ' * (50-done),per))
                                    sys.stdout.flush()
                                print(" Finished Downloading %s" % filename + f" {k+1} / {len(currMeeting['recording_files'])}")
                                # upload file to google drive
                                print(f.name)
                                googleDriveUploader.uploadFile(f.name, correctFileName(username)) # comment out this line if you only want to download them locally
                                # delete local file
                                f.close()
                                os.remove(f.name) # comment out this line if you only want to download them locally
                    else:
                        print("Already Downloaded %d.%d out of %d" % (j + 1, k + 1, len(currUserMeetings)))

                        # print filename
                if j == (len(currUserMeetings) - 1):
                    print("Done Downloading User %s Recordings" % username + ' from ' + currentFromStr + ' to ' + currentToStr)
                    print

        currentTo = currentFrom
        currentFrom -= datetime.timedelta(weeks=4)
    summary.append('*' * 5 + " " + str(i + 1) + " " + username + ' *' * 5 + str(userMeetingCount) + " meetings" + '\n')
    userMeetingCount = 0

    # print username

print('*' * 15)
print(len(summary))
print('*' * 15)
print(durationTotal)
sumFile = open("summary1.txt", 'w')
sumFile.writelines(summary)
sumFile.writelines(['---------', "Total meeting count " + str(len(summary)-1), " / Total duration " + str(durationTotal)])