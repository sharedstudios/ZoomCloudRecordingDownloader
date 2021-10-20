import database
import os

def correctIllegalChar(filename):
    ret = filename.lower()
    illegalFirstChars = [' ', '.', '_', '-']
    illegalChars = [ '?', '"', "'"]
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
files1 = [file for file in files1 if (".CHAT" in file)]
# print(files1)

def insertTrChat():
    for filename in files:
        meetingId = filename[0:filename.find('.')].split('-')[6][:filename.find('.')]
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
        # if len(transcriptContent) == 0:
        #     transcript = "None"
        #
        # if len(chatContent) == 0:
        #     chat = "None"
        transcript = correctIllegalChar(transcript)
        chat = correctIllegalChar(chat)
        filteredTranscript = "".join(database.filterTranscript(transcriptContent))
        filteredChat = "".join(database.filterChat(chatContent))
        filteredTranscript = correctIllegalChar(filteredTranscript)
        filteredChat = correctIllegalChar(filteredChat)
        database.insertRow('recordings', ['meetingId', 'transcript', 'filtered_transcript', 'chat', 'filtered_chat'], [meetingId, transcript, filteredTranscript, chat, filteredChat])



database.deleteAllRow('recordings')

# database.dropRow('recordings', 'meetingId', 'a')
insertTrChat()
database.printContent('recordings')


