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

def saveHistory(protocol, wellmap, modFields):
    service = getService()
    wellmapLink = ''
    wellmapName = ''
    if wellmap != None:
        wellmapName = wellmap['name']
        wellmapLink= 'docs.google.com/spreadsheets/d/' + wellmap['id']
    list = [[protocol['name']], [protocol['id']], [date.today().strftime("%d/%m/%Y")], [datetime.now().strftime("%H:%M:%S")], [wellmapName], [wellmapLink], [str(modFields)]]
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

# Takes rowdata, constructs 2D array of dict containing {cell color, cell value}
def make2dArray(rowdata):
    array = [] # pretty much a list of rows
    for row in range(len(rowdata)):
        temp_row = []
        for column in range(len(rowdata[row]['values'])):
            if 'userEnteredValue' in rowdata[row]['values'][column]:
                cell_value = rowdata[row]['values'][column]['userEnteredValue']['stringValue']
            else:
                cell_value = None
            if 'backgroundColor' in rowdata[row]['values'][column]['userEnteredFormat']:
                cell_color = rowdata[row]['values'][column]['userEnteredFormat']['backgroundColor']
            else:
                cell_color = None
            temp_row.append({'color':cell_color, 'value':cell_value})
        array.append(temp_row)
    return array

# Takes well map id, returns dictionary (different ranges) of dictionaries (range, values, etc)
def getWellMapData(wellmap_id):
    service = getService()
    sheet = service.spreadsheets()

    source1_range = "Sheet1!H5:M8"
    source2_range = "Sheet1!H12:S19"
    destination_range = "Sheet1!B5:E12"
    ranges = [source1_range, source2_range, destination_range]
    range_titles = ['Source1', 'Source2', 'Destination']

    include_grid_data = True

    range_no = 0
    sheet_info = {}

    for range in ranges:
        request = sheet.get(spreadsheetId=wellmap_id, ranges=range, includeGridData=include_grid_data)
        result = request.execute()
        rowdata = result['sheets'][0]['data'][0]['rowData']
        sheet_info[range_titles[range_no]] = make2dArray(rowdata)
        range_no = range_no + 1
    
    return(sheet_info)


