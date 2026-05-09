"""
Upload details_seed_batch2.csv rows to the Details tab in Google Sheets.
Appends rows (does NOT replace existing data — Woon Ho rows are preserved).
"""
import csv, os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
CREDS_FILE = r'C:\Users\ibkaa\Downloads\client_secret_143384304189-mhk3bu1ai83nqip0kt78e8q2ukibe7ek.apps.googleusercontent.com.json'
TOKEN_FILE = 'token_sheets.json'
CSV_FILE = 'details_seed_batch2.csv'
DETAILS_TAB = 'Details'

def get_creds():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
    return creds

def main():
    service = build('sheets', 'v4', credentials=get_creds())
    ss = service.spreadsheets()

    # Get sheet metadata — find or create Details tab
    meta = ss.get(spreadsheetId=SPREADSHEET_ID).execute()
    sheets = {s['properties']['title']: s['properties']['sheetId'] for s in meta['sheets']}
    print('Tabs found:', list(sheets.keys()))

    if DETAILS_TAB not in sheets:
        print(f'Creating "{DETAILS_TAB}" tab...')
        ss.batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={'requests': [{'addSheet': {'properties': {'title': DETAILS_TAB}}}]}
        ).execute()
        # Write header row
        ss.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=f"'{DETAILS_TAB}'!A1",
            valueInputOption='RAW',
            body={'values': [['slug', 'section', 'label', 'value']]}
        ).execute()
        print(f'  Created "{DETAILS_TAB}" with headers.')
    else:
        print(f'"{DETAILS_TAB}" tab exists — will append rows.')

    # Read existing data to find the next empty row
    existing = ss.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{DETAILS_TAB}'"
    ).execute().get('values', [])
    next_row = len(existing) + 1
    print(f'  Existing rows (incl. header): {len(existing)} — will start at row {next_row}')

    # Read CSV
    with open(CSV_FILE, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)

    # Skip the header row from CSV
    data_rows = rows[1:]
    print(f'  CSV rows to upload: {len(data_rows)}')

    if not data_rows:
        print('Nothing to upload.'); return

    # Append rows
    ss.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{DETAILS_TAB}'!A{next_row}",
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body={'values': data_rows}
    ).execute()

    print(f'Done! Appended {len(data_rows)} rows to "{DETAILS_TAB}" tab.')

    # Summary by slug
    from collections import Counter
    slugs = Counter(r[0] for r in data_rows if r)
    print('\nRows per facility:')
    for slug, count in sorted(slugs.items()):
        print(f'  {slug}: {count} rows')

if __name__ == '__main__':
    main()
