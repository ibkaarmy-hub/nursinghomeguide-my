"""
1. Copy all rows from 'details_seed' tab (Woon Ho data) into 'Details' tab
2. Fix typo: fcc-family-care-suite → fcc-family-care-centre in Details tab
3. Print the GID of the Details tab (for data.js update)
"""
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
CREDS_FILE = r'C:\Users\ibkaa\Downloads\client_secret_143384304189-mhk3bu1ai83nqip0kt78e8q2ukibe7ek.apps.googleusercontent.com.json'
TOKEN_FILE = 'token_sheets.json'

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

    meta = ss.get(spreadsheetId=SPREADSHEET_ID).execute()
    sheets = {s['properties']['title']: s['properties']['sheetId'] for s in meta['sheets']}
    print('Tabs found:', list(sheets.keys()))

    # --- Step 1: Read Woon Ho data from details_seed ---
    if 'details_seed' in sheets:
        seed_data = ss.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range="'details_seed'"
        ).execute().get('values', [])
        print(f'details_seed rows (incl. header): {len(seed_data)}')
        # Skip header (row 0), copy data rows
        woon_ho_rows = seed_data[1:] if len(seed_data) > 1 else []
        print(f'  Woon Ho data rows to copy: {len(woon_ho_rows)}')
    else:
        print('details_seed tab not found — skipping copy')
        woon_ho_rows = []

    # --- Step 2: Append Woon Ho rows to Details tab ---
    if woon_ho_rows:
        existing = ss.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range="'Details'"
        ).execute().get('values', [])
        next_row = len(existing) + 1
        print(f'Details tab currently has {len(existing)} rows. Appending Woon Ho at row {next_row}...')
        ss.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=f"'Details'!A{next_row}",
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body={'values': woon_ho_rows}
        ).execute()
        print(f'  Appended {len(woon_ho_rows)} Woon Ho rows.')

    # --- Step 3: Fix typo fcc-family-care-suite → fcc-family-care-centre ---
    all_details = ss.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="'Details'"
    ).execute().get('values', [])

    typo_fixes = []
    for i, row in enumerate(all_details, start=1):
        if row and row[0] == 'fcc-family-care-suite':
            typo_fixes.append({
                'range': f"'Details'!A{i}",
                'values': [['fcc-family-care-centre']]
            })

    if typo_fixes:
        ss.values().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={'valueInputOption': 'RAW', 'data': typo_fixes}
        ).execute()
        print(f'Fixed {len(typo_fixes)} typo row(s): fcc-family-care-suite → fcc-family-care-centre')
    else:
        print('No typo rows found (already correct or not present).')

    # --- Step 4: Report GID of Details tab ---
    meta2 = ss.get(spreadsheetId=SPREADSHEET_ID).execute()
    for s in meta2['sheets']:
        if s['properties']['title'] == 'Details':
            gid = s['properties']['sheetId']
            print(f'\n✅ Details tab GID = {gid}')
            print(f'   CSV URL: https://docs.google.com/spreadsheets/d/e/2PACX-1vQ4_BgHIjnlgmITzjyUuGDpgpNzPL7MfjOY2069i0PtbVbXSxIAJk1tmBejwNo8aBBeLuRi62szF2sh/pub?gid={gid}&single=true&output=csv')
            print(f'   (Update DETAILS_TAB_GID in data.js with: {gid})')

    # --- Step 5: Summary ---
    final = ss.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="'Details'"
    ).execute().get('values', [])
    print(f'\nDetails tab total rows: {len(final)} (incl. header)')
    from collections import Counter
    slugs = Counter(r[0] for r in final[1:] if r)
    print('Rows per facility:')
    for slug, count in sorted(slugs.items()):
        print(f'  {slug}: {count} rows')

if __name__ == '__main__':
    main()
