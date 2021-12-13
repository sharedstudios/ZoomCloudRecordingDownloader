import mysql.connector
import main as lda

mydb = mysql.connector.connect(
  host="recordings1.cu9plsuquxf7.us-east-1.rds.amazonaws.com",
  user="admin",
  password="sharedstudios",
  database="zoomRecordingsDB"
)

mycursor = mydb.cursor()

def extract_topic(meetingID):
  command = f"SELECT filtered_transcript FROM recordings WHERE meetingId = '{meetingID}'"
  mycursor.execute(command)
  transcript = ""
  row_count = 1
  for trans in mycursor:
    if trans[0] == "":
      continue
    row_count = mycursor.rowcount
    transcript += trans[0]
  if transcript.replace(" ", '') == "":
    return (meetingID, "No transcript", "")
  transcript = [transcript[i: i+(int(len(transcript)/row_count))] for i in range(0, len(transcript), int(len(transcript)/row_count))][0] # chop repeated rows
  return (meetingID, transcript, lda.myLda(transcript))

def update_RDS(meetingId, topic):
  command = f"""UPDATE recordings SET topic = '{topic}' where meetingID = '{meetingId}'"""
  print(command)
  mycursor.execute(command)
  mydb.commit()

if __name__ == "__main__":
  command = "SELECT meetingId from recordings;"
  mycursor.execute(command)

  meetingIds = []

  for meetingId in mycursor:
    meetingIds.append((meetingId[0]))

  meetingIds = meetingIds[6670: ]

  for meetingId in meetingIds:
    print(str(meetingIds.index(meetingId)) + " / " + str(len(meetingIds)))
    lda_result = extract_topic(meetingId)
    topics = ", ".join(lda_result[2])
    update_RDS(meetingId, topics)
