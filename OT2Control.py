from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime, date

SCOPES = ['https://www.googleapis.com/auth/drive']
historySheetID = '1jh0VXNLf4xDI_EBh3MpPcBh9_DD8PSCfM-UtKAMwLYk'

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
    
    service = build('sheets', 'v4', credentials=creds)
    return service

def saveHistory(protocol):
    service = getService()
    list = [[protocol['name']], [protocol['id']], [date.today().strftime("%d/%m/%Y")], [datetime.now().strftime("%H:%M:%S")]]
    resource = {
        "majorDimension": "COLUMNS",
        "values": list
    }
    range = "Sheet1!A:A"
    service.spreadsheets().values().append(
        spreadsheetId=historySheetID,
        range=range,
        body=resource,
        valueInputOption="USER_ENTERED"
    ).execute()
    print('history saved')

def sendOT2(protocol):
    saveHistory(protocol)
    return None
