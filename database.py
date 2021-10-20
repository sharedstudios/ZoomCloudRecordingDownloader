import mysql.connector
import re

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="sharedstudios",
  database="zoomRecordingsDB"
)

mycursor = mydb.cursor()


def filterTranscript(transcriptContent):
  transcriptContent = transcriptContent[1:]  # delete the first line
  filtered = []
  i = 1
  for line in transcriptContent:
    if i == 4:
      filtered.append(line)
      i = 0
    i += 1

  for i in range(len(filtered)):
    if len(filtered[i].split(': ')) > 1:
      filtered[i] = filtered[i].split(': ')[1]

  return filtered


def filterChat(chatContent):
  filtered = []
  for line in chatContent:
    # change the format if the line starts with time
    if re.match('[0-2][0-9]:[0-9][0-9]:[0-9][0-9]', line):
      line = line[9:]
      filtered.append(line[line.find(':')+2:]) # get the clear line and delete the first tab
      continue
    filtered.append(line)
  return filtered


def insertRow(table, column, data):
  col = '('+ ",".join(column) + ')'
  # val = '( SELECT"'+ '","'.join(data) + '")'
  val = f"('{data[0]}', '{data[1]}', '{data[2]}', '{data[3]}', '{data[4]}' )"

  # command = f'''INSERT INTO {table} {col}
  #               SELECT * FROM {val} AS tmp
  #               WHERE NOT EXISTS (
  #                 SELECT {column[0]} FROM {table} WHERE {column[0]} = "{data[0]}"
  #               ) LIMIT 1;'''

  # print(command)

  command = f"INSERT INTO {table} {col} values {val}; "
  print(command)
  mycursor.execute(command)
  mydb.commit()

def dropRow(table, col, val):
  command = f"DELETE FROM {table} WHERE {col} = "
  if isinstance(val, int):
    command += val
  else:
    command += "'"+val+"'"

  mycursor.execute(command)
  mydb.commit()


def deleteAllRow(table):
  command = f"DELETE FROM {table};"
  mycursor.execute(command)
  mydb.commit()


def printContent(table):
  print('-' * 10)
  mycursor.execute(f"SELECT * FROM {table};")
  for line in mycursor:
    print(line)
  print('-' * 10)


if __name__ == "__main__":
  printContent('recordings')
  insertRow('recordings', ['meetingId', 'transcript', 'filtered_transcript', 'chat', 'filtered_chat'], ['/', '$','@', '.', "r"])
  # dropRow('recordings', 'meetingId', 'k')
  printContent('recordings')
