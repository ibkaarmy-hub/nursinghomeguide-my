"""
Update Jeta Care with phone, address, and append room types to Details tab.
"""
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import date

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE = 'token_sheets.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
FAC_TAB = 'google-sheets-facilities.csv'
DETAILS_TAB = 'Details'

creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
service = build('sheets', 'v4', credentials=creds)
ss = service.spreadsheets()

# --- Update Facilities tab ---
fac_data = ss.values().get(
    spreadsheetId=SPREADSHEET_ID, range=f"'{FAC_TAB}'"
).execute().get('values', [])

headers = fac_data[0]

def col_letter(n):
    s = ''
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s

def h(name):
    return headers.index(name) if name in headers else None

slug_i = h('slug')

updates = []
for i, row in enumerate(fac_data[1:], start=2):
    slug = row[slug_i] if slug_i < len(row) else ''
    if slug == 'jeta-care':
        fields = {
            'phone': '+60 7-663 6888',
            'area': 'Kulai, Johor',
            'google_maps_url': 'https://www.google.com/maps/search/Jeta+Care+Kulai+Johor',
            'last_updated': str(date.today()),
        }
        for field, value in fields.items():
            col_i = h(field)
            if col_i is not None:
                updates.append({'range': f"'{FAC_TAB}'!{col_letter(col_i+1)}{i}", 'values': [[value]]})
        print(f'  Queued {len(fields)} updates for jeta-care at row {i}')
        break

if updates:
    ss.values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={'valueInputOption': 'RAW', 'data': updates}
    ).execute()
    print('  Facilities tab updated.')

# --- Append room type rows to Details tab ---
room_rows = [
    ['jeta-care', 'rooms', 'Single room (shared toilet)', 'RM 3,001–4,000/mo (2020 — confirm current)'],
    ['jeta-care', 'rooms', 'Twin room (shared toilet)', 'RM 3,001–4,500/mo (2020 — confirm current)'],
    ['jeta-care', 'rooms', 'Twin room (attached toilet)', 'RM 4,000–5,500/mo (2020 — confirm current)'],
    ['jeta-care', 'rooms', 'Triple room', 'RM 3,001–4,000/mo (2020 — confirm current)'],
    ['jeta-care', 'rooms', 'Total beds', '62'],
]

existing = ss.values().get(
    spreadsheetId=SPREADSHEET_ID, range=f"'{DETAILS_TAB}'"
).execute().get('values', [])

# Check if room rows for jeta-care already exist
existing_labels = set()
for row in existing[1:]:
    if len(row) >= 3 and row[0] == 'jeta-care' and row[1] == 'rooms':
        existing_labels.add(row[2])

new_rows = [r for r in room_rows if r[2] not in existing_labels]

if new_rows:
    next_row = len(existing) + 1
    ss.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{DETAILS_TAB}'!A{next_row}",
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body={'values': new_rows}
    ).execute()
    print(f'  Appended {len(new_rows)} room rows to Details tab.')
else:
    print('  Room rows already exist — skipped.')

print('Done.')
