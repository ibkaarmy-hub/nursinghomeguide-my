"""
Find and remove duplicate rows for jeta-care, keeping the most enriched one.
"""
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

# Find all rows for jeta-care
jeta_rows = [(i + 2, row) for i, row in enumerate(fac_data[1:])
             if (row[slug_i] if slug_i < len(row) else '') == 'jeta-care']

print(f'Found {len(jeta_rows)} jeta-care rows:')
for sheet_row, row in jeta_rows:
    title = row[headers.index('title')] if 'title' in headers and headers.index('title') < len(row) else ''
    editorial = row[headers.index('editorial_summary')] if 'editorial_summary' in headers and headers.index('editorial_summary') < len(row) else ''
    hero = row[headers.index('hero_image')] if 'hero_image' in headers and headers.index('hero_image') < len(row) else ''
    print(f'  Row {sheet_row}: title="{title}" | hero="{hero[:60]}" | editorial="{editorial[:80]}"')

# The most enriched row is the one with a hero_image set
# Keep that one, delete the others by clearing their slug so we can identify
# Actually safer: delete rows from bottom up to preserve row numbers
# Row with hero_image is the keeper; delete the others

hero_i = headers.index('hero_image') if 'hero_image' in headers else None
keeper_row = None
rows_to_delete = []

for sheet_row, row in jeta_rows:
    hero = row[hero_i] if hero_i is not None and hero_i < len(row) else ''
    if hero and not keeper_row:
        keeper_row = sheet_row
    else:
        rows_to_delete.append(sheet_row)

print(f'\nKeeping row {keeper_row}, deleting rows: {rows_to_delete}')

if not rows_to_delete:
    print('Nothing to delete.'); exit()

# Get sheet ID for Facilities tab
meta = ss.get(spreadsheetId=SPREADSHEET_ID).execute()
sheet_id = None
for s in meta['sheets']:
    if s['properties']['title'] == FAC_TAB:
        sheet_id = s['properties']['sheetId']
        break

print(f'Sheet ID: {sheet_id}')

# Delete rows from bottom up (so row indices stay valid)
requests = []
for row_num in sorted(rows_to_delete, reverse=True):
    requests.append({
        'deleteDimension': {
            'range': {
                'sheetId': sheet_id,
                'dimension': 'ROWS',
                'startIndex': row_num - 1,  # 0-indexed
                'endIndex': row_num          # exclusive
            }
        }
    })

ss.batchUpdate(
    spreadsheetId=SPREADSHEET_ID,
    body={'requests': requests}
).execute()

print(f'Deleted {len(rows_to_delete)} duplicate row(s). Done.')
