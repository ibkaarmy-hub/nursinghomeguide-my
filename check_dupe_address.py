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

def get(row, col):
    i = headers.index(col) if col in headers else None
    return (row[i] if i is not None and i < len(row) else '').strip()

groups = {
    'Roseville Villa': [56, 118],
    'Pusat Sri Kenangan': [78, 81, 123],
}

for name, rows in groups.items():
    print(f'\n{name}:')
    for rn in rows:
        row = fac_data[rn - 1]
        print(f'  Row {rn}:')
        print(f'    slug     = {get(row, "slug")}')
        print(f'    phone    = {get(row, "phone")}')
        print(f'    area     = {get(row, "area")}')
        print(f'    maps_url = {get(row, "google_maps_url")[:80]}')
