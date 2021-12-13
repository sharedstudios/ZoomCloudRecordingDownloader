import requests
import webbrowser
import json
import os
from time import sleep
import sys
import datetime

# keeping our api key and api secret off the program file so it's secure
fl = open('api.txt', 'r')
apis = fl.readlines()

# print apis

apiKey = apis[0].replace("\n", "")
apiSec = apis[1].replace("\n", "")
em = apis[2].replace("\n", "")
pas = apis[3].replace("\n", "")
JWTtoken= apis[4].replace("\n", "")

# call /meetings/{meetingId}/recordings api
# get all data of recordings
# get registransts info /meetings/{meetingId}/recordings/registrants
# get number of registranst
# get registrants questions
# get Meeting participants infos
# get meeting participant count

# this is defined to make sure no illegal character appear in potential filenames
def correctFileName(filename):
    ret = filename.lower()
    illegalFirstChars = [' ', '.', '_', '-']
    illegalChars = ['#', '%', '&', '{', '}', '\\', '<', '>', '*', '?', ' ', '$', '!', "'", '"', ':', '@', '.', "'"]
    for index in range(len(filename)):
        if not filename[index] in illegalFirstChars:
            ret = filename[index:]
            break

    if '/' in filename:
        ret = ret.replace('/', '%2F')

    for char in illegalChars:
        ret = ret.replace(char, "")
    return ret


def getAllMeetingId():
    meetingIds = []
    infile = open('summary.txt')
    for line in infile:
        if '/' in line:
            line = line.replace('/', '%2F')
        line = line.strip()
        if not line[0] == '*' and not line[0:2] == '--':
            meetingIds.append(line.split(' ')[0])
    return meetingIds


session_requests = requests.session()
signin = "https://zoom.us/signin"
values = {'email': em,
          'password': pas}
result = session_requests.post(signin, data=values)

# first set of parameters passed to api call
userlistparam = {'api_key': apiKey, 'api_secret': apiSec, "type":"past", 'data_type': "JSON", 'page_size': 300, "from":"2019-10-10", "to":"2019-12-30"}

headers = {
    "authorization": "Bearer " + JWTtoken,
}

meetingIds = getAllMeetingId()

def queryMeetingInfo(meetingId):
    detail = requests.get(f'https://api.zoom.us/v2/meetings/{meetingId}/recordings', headers=headers, params=userlistparam).json()
    registrantsInfo = requests.get(f'https://api.zoom.us/v2/meetings/{meetingId}/recordings/registrants', headers=headers, params=userlistparam).json()
    if(len(registrantsInfo) <=2):
        registrantsCount = 0
    else:
        registrantsCount = len(registrantsInfo['registrants'])
    regisQuestion = requests.get(f'https://api.zoom.us/v2/meetings/{meetingId}/recordings/registrants/questions', headers=headers, params=userlistparam).json()
    if(len(regisQuestion) <=2):
        regisQuestion = {"error 3001": "no regis question"}
    participantsInfo = requests.get(f'https://api.zoom.us/v2/metrics/meetings/{meetingId}/participants', headers=headers, params=userlistparam).json()
    if(len(participantsInfo) <=2):
        participantsInfo = {"error 3001": "no participant"}
    if(len(participantsInfo) <=2):
        participantsCount = 0
    else:
        participantsCount = len(participantsInfo['participants'])

    return [detail, registrantsInfo, registrantsCount, regisQuestion, participantsInfo, participantsCount]


