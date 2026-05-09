"""Fix 15 facilities whose google_maps_url contains an lh3.googleusercontent.com photo URL.
Replace with a google.com/maps/search URL constructed from the facility title."""
import sys, urllib.parse
sys.stdout.reconfigure(encoding='utf-8')
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE = 'token_sheets.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
TAB = 'google-sheets-facilities.csv'

# slug → title (title used for the search query)
TARGETS = {
    'columbia-asia-extended-care-hospital':                       'Columbia Asia Extended Care Hospital',
    'mintygreen-nursing-home-eldercare-center':                   'Mintygreen Nursing Home ElderCare Center',
    'pusat-jagaan-al-fikrah-malaysia':                            'Pusat Jagaan Al Fikrah Malaysia',
    'amazing-grace-caring-home':                                  'Amazing Grace Caring Home',
    'amitabha-malaysia-old-folks-home-kl':                        'Amitabha Malaysia Old Folks Home KL',
    'rumah-seri-kenangan-johor-bahru':                            'Rumah Seri Kenangan Johor Bahru',
    'rumah-victory-elderly-home':                                 'Rumah Victory Elderly Home',
    'pusat-jagaan-rumah-kebajikan-warga-emas-st-mark':            'Pusat Jagaan Rumah Kebajikan Warga Emas St Mark',
    'pusat-jagaan-chik-sin-thong-klang-dan-pantai-selangor':      'Pusat Jagaan Chik Sin Thong Klang Dan Pantai Selangor',
    'tai-kuk-wah-si-buddist-society':                             'Tai Kuk Wah Si Buddist Society',
    'persatuan-kebajikan-dan-social-kim-loo-ting':                'Persatuan Kebajikan Dan Social Kim Loo Ting',
    'pj-mentalink-care-pj-old-folks':                             'PJ Mentalink Care PJ Old Folks',
    'pusat-jagaan-sri-sentosa':                                   'Pusat Jagaan Sri Sentosa',
    'pusat-jagaan-en-yuan-cheras':                                'Pusat Jagaan En Yuan Cheras',
    'pusat-jagaan-mahmudah-malaysia':                             'Pusat Jagaan Mahmudah Malaysia',
}

def maps_search_url(title):
    return 'https://www.google.com/maps/search/?api=1&query=' + urllib.parse.quote(title)

def col_letter(n):  # 1-based column index → A, B, ..., Z, AA, ...
    s = ''
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s

def main():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    sheet = build('sheets', 'v4', credentials=creds).spreadsheets()

    data = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{TAB}'"
    ).execute().get('values', [])

    headers = data[0]
    slug_col = headers.index('slug')
    maps_col = headers.index('google_maps_url')
    maps_col_letter = col_letter(maps_col + 1)  # +1 for 1-based

    print(f"slug col: {slug_col} ({col_letter(slug_col+1)}), google_maps_url col: {maps_col} ({maps_col_letter})")

    updates = []
    found = set()

    for i, row in enumerate(data[1:], start=2):  # row 2 is first data row (1-indexed in Sheets)
        slug = row[slug_col] if len(row) > slug_col else ''
        if slug not in TARGETS:
            continue
        current_url = row[maps_col] if len(row) > maps_col else ''
        new_url = maps_search_url(TARGETS[slug])
        print(f"  Row {i}  {slug}")
        print(f"    OLD: {current_url[:80]}")
        print(f"    NEW: {new_url}")
        updates.append({
            'range': f"'{TAB}'!{maps_col_letter}{i}",
            'values': [[new_url]]
        })
        found.add(slug)

    missing = set(TARGETS) - found
    if missing:
        print(f"\nWARNING: {len(missing)} slug(s) not found in sheet:")
        for s in sorted(missing):
            print(f"  {s}")

    if not updates:
        print("Nothing to update.")
        return

    body = {'valueInputOption': 'RAW', 'data': updates}
    resp = sheet.values().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
    print(f"\nDone — updated {resp.get('totalUpdatedCells')} cells.")

if __name__ == '__main__':
    main()
