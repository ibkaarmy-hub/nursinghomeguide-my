from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE = 'token_sheets.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
service = build('sheets', 'v4', credentials=creds)
ss = service.spreadsheets()

fac_data = ss.values().get(
    spreadsheetId=SPREADSHEET_ID,
    range="'google-sheets-facilities.csv'"
).execute().get('values', [])

headers = fac_data[0]
print('Headers:', headers)
print('Total rows:', len(fac_data) - 1)

slug_i = headers.index('slug') if 'slug' in headers else 0
slugs = [r[slug_i] if slug_i < len(r) else '' for r in fac_data[1:]]

targets = [
    'eha-parkview-eldercare-perling',
    'fcc-family-care-centre',
    'jeta-care',
    'gentle-hill-elder-care',
    'haywood-senior-living-medini-johor-bahru'
]
for t in targets:
    print(f'  {t}: {"EXISTS" if t in slugs else "NOT FOUND"}')
