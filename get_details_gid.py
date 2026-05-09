import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from collections import Counter

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE = 'token_sheets.json'

creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
service = build('sheets', 'v4', credentials=creds)
ss = service.spreadsheets()

meta = ss.get(spreadsheetId=SPREADSHEET_ID).execute()
for s in meta['sheets']:
    title = s['properties']['title']
    gid = s['properties']['sheetId']
    print(f'{title}: gid={gid}')

data = ss.values().get(spreadsheetId=SPREADSHEET_ID, range="'Details'").execute().get('values', [])
print('Total rows incl header:', len(data))
slugs = Counter(r[0] for r in data[1:] if r)
for slug, count in sorted(slugs.items()):
    print(f'  {slug}: {count}')
