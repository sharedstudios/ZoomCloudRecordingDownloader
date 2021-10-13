from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

fl = open('api.txt', 'r')
apis = fl.readlines()
zoomRecordingsFolderId = apis[6].replace("\n", "")
# to get folder id, run getFolderId function below and place it at line 7 of api.txt

# place google drive api client_secrets.json under same directory

gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)



def containsFile(title):
    #check if drive contains file or not
    query = f"title = '{title}'"
    file_list = drive.ListFile({'q': query}).GetList()
    return len(file_list) != 0

def containsFolder(folderName):
    folders = drive.ListFile({'q': "title='" + folderName + "' and trashed=false"}).GetList()
    for folder in folders:
        if folder['title'] == folderName:
            return folder['id']
    return False

def createFolder(folderName, parentFolderId):
    file_meta = {
        'title': folderName,
        'parents': [{"id": parentFolderId}],
        'mimeType': 'application/vnd.google-apps.folder'
    }

    folder = drive.CreateFile(file_meta)
    folder.Upload()
    return containsFolder(folderName)

def uploadFile(fileName, folderName):
    if(containsFile(fileName)):
        print(fileName + " exists in Google Drive, folder")
        return
    if not containsFolder(folderName):
        print("Folder not exist, creating folder for " + folderName)
        userFolderId = createFolder(folderName, zoomRecordingsFolderId)
    print("Uploading file")
    file2 = drive.CreateFile({'parents': [{'id': containsFolder(folderName)}]})
    file2.SetContentFile(fileName)
    file2.Upload()
    print("Uploaded to Google Drive")

# uploadFile('40138.jpeg', 'maria')
# sample folder id = 1M6sMgwAx1UJgKB8OijRvgd8hTRMT5qoM

def getFolderId():
    file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
    for file1 in file_list:
        print('title: %s, id: %s' % (file1['title'], file1['id']))