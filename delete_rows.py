"""
Delete specific row numbers from a sheet (1-indexed, bottom-up).
"""
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE = 'token_sheets.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
FAC_TAB = 'google-sheets-facilities.csv'

# Rows to delete (1-indexed, as shown in spreadsheet)
ROWS_TO_DELETE = [18, 126]

creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
service = build('sheets', 'v4', credentials=creds)
ss = service.spreadsheets()

meta = ss.get(spreadsheetId=SPREADSHEET_ID).execute()
sheet_id = next(s['properties']['sheetId'] for s in meta['sheets']
                if s['properties']['title'] == FAC_TAB)

# Delete bottom-up so indices stay valid
requests = []
for row_num in sorted(ROWS_TO_DELETE, reverse=True):
    requests.append({
        'deleteDimension': {
            'range': {
                'sheetId': sheet_id,
                'dimension': 'ROWS',
                'startIndex': row_num - 1,
                'endIndex': row_num
            }
        }
    })
    print(f'Queued delete: row {row_num}')

ss.batchUpdate(spreadsheetId=SPREADSHEET_ID, body={'requests': requests}).execute()
print(f'Done — deleted {len(ROWS_TO_DELETE)} rows.')
