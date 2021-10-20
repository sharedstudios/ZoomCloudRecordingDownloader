import requests
import webbrowser
import json
import os
from time import sleep
import sys
import datetime
import googleDriveUploader

# CHAT OR TRANSCRIPT

format = "CHAT"

# keeping our api key and api secret off the program file so it's secure
fl = open('api.txt', 'r')
apis = fl.readlines()

# print apis

apiKey = apis[0].replace("\n", "")
apiSec = apis[1].replace("\n", "")
em = apis[2].replace("\n", "")
pas = apis[3].replace("\n", "")
JWTtoken= apis[4].replace("\n", "")


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

# first set of parameters passed to api call
userlistparam = {'api_key': apiKey, 'api_secret': apiSec, 'data_type': "JSON", 'page_size': 300}

headers = {
    "authorization": "Bearer " + JWTtoken,
}
# call to retrieve json object containing list of zoom users
userlistjson = requests.get('https://api.zoom.us/v2/users', headers=headers, params=userlistparam).json()
users = userlistjson['users']
summary = []
durationTotal = 0
userMeetingCount = 0

# partial upload by user index
# users = users[:]
for user in users:
    print(user)

# for loop to go through each user in the list
for i in range(len(users)):

    # this retireves user that is currently being looked at and relevant info
    currUser = users[i]
    # if user has any recordings, this string will be the name of created directory
    username = f"{currUser['first_name']}-{currUser['last_name']}"
    if username == "-":
        username = currUser['email'][:currUser['email'].find('@')]
    # user id needed to pass to api call
    currID = currUser['id']
    # earliest event date
    firstDate = datetime.date(2014, 1, 1)
    # current range of to date
    currentTo = datetime.date.today()
    # current range of from date
    # currentTo = datetime.date(2018, 2, 1)
    currentFrom = currentTo - datetime.timedelta(weeks=4)

    # download the monthly recording until the first date of the events
    while currentFrom >= firstDate:

        # convert date obj to string format
        currentFromStr = currentFrom.strftime("%Y-%m-%d")
        currentToStr = currentTo.strftime("%Y-%m-%d")

        print('Checking User "%s" for recordings' % username + ' from ' + currentFromStr + ' to ' + currentToStr + "---" + str(i+1) + '/' + str(len(users)))
        # Waits 1 Second to Prevent Too Many API Calls at once
        sleep(1)


        # second set of parameters passed to second api call
        videolistparams = {'api_key': apiKey, 'api_secret': apiSec, 'data_type': "JSON", 'userId': currID, 'page_size': 300,
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
                else:
                    sys.exit(
                        "Unknown Error. Please run program again. If problem persists, contact justinp@sharedstudios.com")

            break
        currUserMeetings = videolistjson['meetings']

        print(f"{username} has {len(currUserMeetings)} awaiting to be downloaded and uploaded")
        userMeetingCount += len(currUserMeetings)
        # if this user has any recordings, this block of code will download them
        if (len(currUserMeetings) > 0):
            print('%d Recordings found for User "%s"; Downloading the new recording MP4 Files' % (
            len(currUserMeetings), username))
            # if folder for videos does not exist yet, creates a folder named after username
            if not os.path.exists("./transcript"):
                os.makedirs("./transcript")



            # print " "

            # for loop iterates through a meeting object, and we specfically want to contruct the meeting name
            # as well as iterate through recordings of a meeting
            for j in range(len(currUserMeetings)):
                currMeeting = currUserMeetings[j]
                # print(currMeeting['start_time'])
                meetingName = currMeeting['topic'] + "-" + currMeeting['start_time']
                meetingName = correctFileName(meetingName)

                # get all meeting ids and their duration
                summary.append(currMeeting['uuid'] + " " + str(currMeeting['duration']) + '\n')
                durationTotal += currMeeting['duration']

                # a meeting might have multiple recordings, so this code block will iterate through those meetings
                for k in range(len(currMeeting['recording_files'])):

                    currRecording = currMeeting['recording_files'][k]
                    # print(currRecording)
                    # some recording files are just audio, so we want to ensure we're only downloading the videos
                    # print currRecording

                    # if currRecording['file_type'] != 'TRANSCRIPT':
                    #     continue

                    if currRecording['file_type'] != format:
                        continue


                    # oldFilename = meetingName + '-' + str(k + 1) + '.' + currRecording['file_type']
                    oldFilename = username + '-' + currRecording['recording_start'][:10] + '-' + currRecording['id'] + '.' + currRecording['file_type']
                    # we finally  get to the code where we start donwloading
                    username = correctFileName(username)
                    filename = username + '-' + currRecording['recording_start'][:10] + '-' + currRecording['recording_type']+ '-' + currMeeting['uuid']


                    # if recording file is already downloaded, this script won't download it again
                    # this allows us to call this script to download new files after downloading an inital batch
                    filename = correctFileName(filename)
                    filename +=  '.' + currRecording['file_type']
                    local_dir = f"./{format.lower()}/"+filename
                    if not os.path.exists(local_dir):  # to store locally, use ["./" + username + "/" + filename]
                        link = currRecording['download_url']
                        link += "?access_token="+JWTtoken
                        with open(local_dir, "wb") as f:
                            print("Downloading %s" % filename)
                            response = session_requests.get(link, stream=True)
                            # total_length = response.headers.get('file_size')
                            total_length = currRecording['file_size']
                            if total_length == 0:
                                # f.write(response.content)
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
                                # print(f.name)

                                # comment the following 2 lines if you only want to download them locally
                                # googleDriveUploader.uploadFile(f.name, correctFileName(username))
                                # delete local file
                                # os.remove(f.name)
                    else:
                        print("Already Downloaded %d.%d out of %d" % (j + 1, k + 1, len(currUserMeetings)))

                        # f.close()

                        # print filename
                if j == (len(currUserMeetings) - 1):
                    print("Done Downloading User %s Recordings" % username + ' from ' + currentFromStr + ' to ' + currentToStr)
                    print

        currentTo = currentFrom
        currentFrom -= datetime.timedelta(weeks=4)

    summary.append('*' * 5 + " " + str(i+1) + " "+ username + ' * ' * 5 + str(userMeetingCount) + " meetings"  + '\n')
    userMeetingCount = 0

        # print username

print('*' * 15)
print(len(summary)-1)
print('*' * 15)
print(durationTotal)

sumFile = open("summary.txt", 'w')
sumFile.writelines(summary)
sumFile.writelines(['---------', "Total meeting count " + str(len(summary)-1), " / Total duration " + str(durationTotal)])
