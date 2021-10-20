from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from urllib.error import HTTPError
import time

fl = open('api.txt', 'r')
apis = fl.readlines()
zoomRecordingsFolderId = apis[6].replace("\n", "")
# to get folder id, run getFolderId function below and place it at line 7 of api.txt

# place google drive api client_secrets.json under same directory

gauth = GoogleAuth()
# Try to load saved client credentials
gauth.LoadCredentialsFile("mycreds.txt")
if gauth.credentials is None:
    # Authenticate if they're not there
    gauth.GetFlow()
    gauth.flow.params.update({'access_type': 'offline'})
    gauth.flow.params.update({'approval_prompt': 'force'})

    gauth.CommandLineAuth()
    # gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    # Refresh them if expired
    gauth.Refresh()
else:
    # Initialize the saved creds
    gauth.Authorize()
# Save the current credentials to a file
gauth.SaveCredentialsFile("mycreds.txt")


drive = GoogleDrive(gauth)



def containsFile(title):
    #check if drive contains file or not
    query = f"title = '{title}'"
    file_list = drive.ListFile({'q': query}).GetList()
    # print(file_list)
    return len(file_list) != 0


def lookupFileId(title):
    # return file id given filename
    if(not containsFile(title)):
        return
    query = f"title = '{title}'"
    file_list = drive.ListFile({'q': query}).GetList()
    for file in file_list:
        return file['id']
    # assuming the filename is never repeatable


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
    try:
        file2.Upload()
    except HTTPError as e:
        # if e.code == 403: # google drive api limit 10000 per 100s
            print("Taking break ... (100s)")
            time.sleep(100)
            file2.Upload()


    print("Uploaded to Google Drive")

# uploadFile('40138.jpeg', 'maria')
# sample folder id = 1M6sMgwAx1UJgKB8OijRvgd8hTRMT5qoM

def getFolderId():
    folderIdList = []
    # folder id should be root folder's id
    file_list = drive.ListFile({'q': "'1M6sMgwAx1UJgKB8OijRvgd8hTRMT5qoM' in parents and trashed=false"}).GetList()
    for file1 in file_list:
        folderIdList.append(file1['id'])
        print('title: %s, id: %s' % (file1['title'], file1['id']))
    return folderIdList

def getFileIds(folderId):
    fileIdList = []
    file_list = drive.ListFile({'q': f"{folderId} in parents and trashed=false"}).GetList()
    for file1 in file_list:
        fileIdList.append(file1['id'])
        print('title: %s, id: %s' % (file1['title'], file1['id']))
    return fileIdList

def updateFileName(fileId, newName):
    a = drive.auth.service.files().get(fileId=fileId).execute()
    a['title'] = newName
    update = drive.auth.service.files().update(fileId=fileId, body=a).execute()
    print("Updated file name to " + newName)
    return update


# print(lookupFileId("AfricaCenterPortalsZoomMeeting-2019-01-08T161127Z-1.M4A"))