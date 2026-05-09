"""Mark all 4 Cozzi confinement entries as 'removed' (column BD).
These are postnatal confinement centres, not eldercare facilities."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE = 'token_sheets.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
TAB = 'google-sheets-facilities.csv'

# (row_idx, slug)
ROWS = [
    (39, 'cozzi-confinement-center-yong-peng'),
    (80, 'cozzi-confinement-center-muar'),
    (91, 'cozzi-confinement-center-sri-jaya'),
    (92, 'cozzi-confinement-center-tanah-merah'),
]

def main():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    sheet = build('sheets', 'v4', credentials=creds).spreadsheets()
    data = []
    for row, slug in ROWS:
        data.append({'range': f"'{TAB}'!BD{row}", 'values': [['removed']]})
        print(f'  BD{row}  {slug}  -> removed')
    body = {'valueInputOption': 'RAW', 'data': data}
    resp = sheet.values().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
    print(f"\nUpdated {resp.get('totalUpdatedCells')} cells.")

if __name__ == '__main__':
    main()
