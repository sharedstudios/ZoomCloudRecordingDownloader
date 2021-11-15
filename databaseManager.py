import json

import database
import os
import zoomRecordingMetadata

def correctIllegalChar(filename):
    ret = filename.lower()
    illegalFirstChars = [' ', '.', '_', '-']
    illegalChars = [ '?', '"', "'"]
    # illegalChars = ['#', '%', '&', '{', '}', '\\', '<', '>', '*', '?', '/',  '$', '!', "'", '"', ':', '@', '.', "'"]
    for index in range(len(filename)):
        if not filename[index] in illegalFirstChars:
            ret = filename[index:]
            break

    for char in illegalChars:
        ret = ret.replace(char, "")
    return ret

# get all filename
files = os.listdir('./transcript')
files1 = os.listdir('./chat')
files = [file for file in files if ("TRANSCRIPT" in file)]
files1 = [file for file in files1 if ("CHAT" in file)]
print(files1)

def insertTrChat():
    # ids that does not transcript
    remainingIDs = zoomRecordingMetadata.getAllMeetingId()
    for i in range(len(remainingIDs)):
        if '/' in remainingIDs[i]:
            remainingIDs[i].replace('/', '%2F')
            continue
        remainingIDs[i] = correctIllegalChar(remainingIDs[i])

    # insert to row to database that has transcript

    for filename in files:
        # print(filename)
        meetingId = filename[0:filename.find('.')].split('-')[-1][:filename.find('.')]

        try:
            for id in remainingIDs:
                if '%2F' in id and id.replace('%2F', "") == meetingId:
                    meetingId = id
                    remainingIDs.remove(id)

        except ValueError:
            continue


        transcriptContent = []
        chatContent = []

        try:
            transcriptFile = open(f'./transcript/{filename}')
            transcriptContent = transcriptFile.readlines()
        except FileNotFoundError:
            print(f"transcript of {filename} not exist")

        try:
            filename = filename.replace("audio_transcript", "chat_file")
            filename = filename.split('.')[0] + '.CHAT'
            chatFile = open(f'./chat/{filename}')
            chatContent = chatFile.readlines()
        except FileNotFoundError:
            print(f"chat of {filename} not exist")

        transcript = " ".join(transcriptContent)
        chat = " ".join(chatContent)


        transcript = correctIllegalChar(transcript)
        chat = correctIllegalChar(chat)
        filteredTranscript = "".join(database.filterTranscript(transcriptContent))
        filteredChat = "".join(database.filterChat(chatContent))
        filteredTranscript = correctIllegalChar(filteredTranscript)
        filteredChat = correctIllegalChar(filteredChat)
        metadata = zoomRecordingMetadata.queryMeetingInfo(meetingId)
        for i in range(len(metadata)):
           metadata[i] = correctIllegalChar(str(metadata[i]))
        keys = ['meetingId', 'transcript', 'filtered_transcript', 'chat', 'filtered_chat', 'meetingDetail', 'registrantsInfo', 'registrantsCount', 'regisQuestion', 'participantsInfo', 'participantsCount']
        vals = [meetingId, transcript, filteredTranscript, chat, filteredChat] + metadata
        database.insertRow('recordings', keys, vals)


        chatFilename = filename.replace("audio_transcript", "chat_file").split('.')[0] + '.CHAT'

        try:
            files1.remove(chatFilename)
        except ValueError:
            continue

    # insert file that has only chat but no transcript

    print("Has only chat but no transcript " + str(len(files1)))
    print(files1)

    for chatfile in files1:
        meetingId = chatfile[0:chatfile.find('.')].split('-')[-1][:chatfile.find('.')]

        try:
            remainingIDs.remove(meetingId)
        except ValueError:
            continue

        chatContent = []
        try:
            chatFile = open(f'./chat/{chatfile}')
            chatContent = chatFile.readlines()
        except FileNotFoundError:
            print("chat file DNE")
        chat = " ".join(chatContent)
        chat = correctIllegalChar(chat)
        filteredChat = correctIllegalChar(filteredChat)
        metadata = zoomRecordingMetadata.queryMeetingInfo(meetingId)
        for i in range(len(metadata)):
            metadata[i] = correctIllegalChar(str(metadata[i]))
        keys = ['meetingId', 'transcript', 'filtered_transcript', 'chat', 'filtered_chat', 'meetingDetail',
                'registrantsInfo', 'registrantsCount', 'regisQuestion', 'participantsInfo', 'participantsCount']
        vals = [meetingId, "", "", chat, filteredChat] + metadata
        database.insertRow('recordings', keys, vals)

    print("No transcript nor chat " + str(len(remainingIDs)))
    print(remainingIDs)

    # insert row to database that doesnt have transcript nor chat recordings
    for remainingID in remainingIDs:
        metadata = zoomRecordingMetadata.queryMeetingInfo(remainingID)
        for i in range(len(metadata)):
            metadata[i] = correctIllegalChar(str(metadata[i]))
        keys = ['meetingId', 'transcript', 'filtered_transcript', 'chat', 'filtered_chat', 'meetingDetail',
                'registrantsInfo', 'registrantsCount', 'regisQuestion', 'participantsInfo', 'participantsCount']
        vals = [remainingID, "", "", "", ""] + metadata
        database.insertRow('recordings', keys, vals)

def insertAWSTranscript():
    files = os.listdir('./AWS_Transcript_Results')
    files = [file for file in files if ("audio_only" in file)]
    print(files)
    with open('summary.txt','r') as summary:
        for line in summary:
            if '**' in line or '----' in line:
                continue
            id = line.strip().split()[0]
            for i in range(len(files)):
                if '/' not in id:
                    continue
                if id.replace('/', "") in files[i]:
                    print(id)
                    dbId = id.replace('/', '%2F')
                    print(dbId)
                    with open('./AWS_Transcript_Results/'+files[i]) as t:
                        aws_trans = json.load(t)
                        aws_trans = aws_trans['results']['transcripts'][0]['transcript']
                        database.updateTable('recordings', 'aws_transcript', aws_trans, dbId)




if __name__ == "__main__":
  database.deleteAllRow('recordings')
  # database.dropRow('recordings', 'meetingId', 'a')
  insertTrChat()
  # database.printContent('recordings')

  insertAWSTranscript()



