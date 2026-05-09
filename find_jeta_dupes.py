from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE = 'token_sheets.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
FAC_TAB = 'google-sheets-facilities.csv'

creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
service = build('sheets', 'v4', credentials=creds)
ss = service.spreadsheets()

fac_data = ss.values().get(
    spreadsheetId=SPREADSHEET_ID,
    range=f"'{FAC_TAB}'"
).execute().get('values', [])

headers = fac_data[0]
slug_i = headers.index('slug')
title_i = headers.index('title') if 'title' in headers else 0

# Find anything with "jeta" in slug or title
for i, row in enumerate(fac_data[1:], start=2):
    slug = row[slug_i] if slug_i < len(row) else ''
    title = row[title_i] if title_i < len(row) else ''
    if 'jeta' in slug.lower() or 'jeta' in title.lower():
        print(f'Row {i}: slug="{slug}" | title="{title}"')
