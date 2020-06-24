from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload
from apiclient import errors
import io
import os
import shutil

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

def getService():
    creds = None

    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    return service

# Takes file ID, returns gdrivefile
def getProtocol(file_id):
    items = getProtocolList()
    for protocol in items:
        if protocol['id'] == file_id:
            return protocol

# takes list of files and changes format and time zone
def adjustDate(items):
    for protocol in items:
        dateRFC339 = protocol['modifiedTime']
        date = dateRFC339[0:10]
        time = dateRFC339[11:19]
        protocol['modifiedTime'] = date + ' ' + time + ' GMT'
    return items

# Returns list of dict (id, name) of items in protocol folder
def getProtocolList():
    protocol_folder_id = '1YDW21_cOkcpA3sYsSO1GaYzdc3cj2W4l'
    service = getService()
    results = service.files().list(
        q="'{}' in parents".format(protocol_folder_id), fields="nextPageToken, files(id, name, modifiedTime)").execute()
    items = results.get('files', [])
    adjustDate(items)
    # #
    # if not items:
    #     print('No files found.')
    # else:
    #     print('Files:')
    #     for item in items:
    #         print(u'{0} ({1})'.format(item['name'], item['id']))

    # getDownload(items[1]['id'])
    # #

    return items

# Deletes downloaded protocol files
def deleteProtocolFiles():
    if os.path.exists('protocol_files'):
        shutil.rmtree('protocol_files')

# Downloads file and adds .py extension
def getDownload(file_id):
    service = getService()
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
    fh.seek(0)
    with open('{}.py'.format(file_id), 'wb') as f:
        shutil.copyfileobj(fh, f, length=131072)
    
    # if protocol_files folder doesn't exist, make directory
    if os.path.isdir('protocol_files') == False:
        os.mkdir('protocol_files')

    # move newly downloaded protocol file into protocol_files directory
    shutil.move('{}.py'.format(file_id), 'protocol_files\{}.py'.format(file_id))
    


