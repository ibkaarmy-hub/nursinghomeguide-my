import os, json
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

    # Get all sheet metadata
    meta = ss.get(spreadsheetId=SPREADSHEET_ID).execute()
    sheets = {s['properties']['title']: s['properties']['sheetId'] for s in meta['sheets']}
    print('Tabs found:', list(sheets.keys()))

    fac_name = 'google-sheets-facilities.csv'
    photos_name = 'sheet_filtered_photos'

    if fac_name not in sheets:
        print(f'ERROR: "{fac_name}" tab not found'); return
    if photos_name not in sheets:
        print(f'ERROR: "{photos_name}" tab not found'); return

    # Read photos sheet
    photos_data = ss.values().get(
        spreadsheetId=SPREADSHEET_ID, range=f"'{photos_name}'"
    ).execute().get('values', [])
    p_headers = photos_data[0]
    p_slug_i = p_headers.index('slug')
    p_hero_i = p_headers.index('hero_image')
    p_photos_i = p_headers.index('photos')
    p_count_i = p_headers.index('photo_count')

    photo_map = {}
    for row in photos_data[1:]:
        slug = row[p_slug_i] if p_slug_i < len(row) else ''
        if slug:
            photo_map[slug] = {
                'hero': row[p_hero_i] if p_hero_i < len(row) else '',
                'photos': row[p_photos_i] if p_photos_i < len(row) else '',
                'count': row[p_count_i] if p_count_i < len(row) else '',
            }
    print(f'Photo map built: {len(photo_map)} slugs')

    # Read facilities sheet
    fac_data = ss.values().get(
        spreadsheetId=SPREADSHEET_ID, range=f"'{fac_name}'"
    ).execute().get('values', [])
    f_headers = fac_data[0]
    f_slug_i = f_headers.index('slug')

    # Find or create photo columns
    def ensure_col(headers, name):
        if name in headers:
            return headers.index(name)
        idx = len(headers)
        headers.append(name)
        return idx

    hero_col = ensure_col(f_headers, 'hero_image')
    photos_col = ensure_col(f_headers, 'photos')
    count_col = ensure_col(f_headers, 'photo_count')

    # Write headers if new columns were added
    ss.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{fac_name}'!1:1",
        valueInputOption='RAW',
        body={'values': [f_headers]}
    ).execute()

    # Build batch update for photo values
    updates = []
    matched = 0
    for i, row in enumerate(fac_data[1:], start=2):
        slug = row[f_slug_i] if f_slug_i < len(row) else ''
        if slug in photo_map:
            p = photo_map[slug]
            # Pad row if needed
            while len(row) <= max(hero_col, photos_col, count_col):
                row.append('')
            updates.append({'range': f"'{fac_name}'!{col_letter(hero_col+1)}{i}",
                            'values': [[p['hero']]]})
            updates.append({'range': f"'{fac_name}'!{col_letter(photos_col+1)}{i}",
                            'values': [[p['photos']]]})
            updates.append({'range': f"'{fac_name}'!{col_letter(count_col+1)}{i}",
                            'values': [[p['count']]]})
            matched += 1

    if updates:
        ss.values().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={'valueInputOption': 'RAW', 'data': updates}
        ).execute()
    print(f'Updated {matched} facilities with photos')

    # Delete the extra sheet
    ss.batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={'requests': [{'deleteSheet': {'sheetId': sheets[photos_name]}}]}
    ).execute()
    print(f'Deleted "{photos_name}" tab. Done!')

def col_letter(n):
    s = ''
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s

if __name__ == '__main__':
    main()
