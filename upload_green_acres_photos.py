"""Upload Green Acres Home Care photos (row 328) to Google Sheet.

Hero: slide_bg.jpg
Photos: gallery/01-12.webp + slide_bg2.png + slide03.jpg + teaser02/03.jpg
"""
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE = 'token_sheets.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
TAB = 'google-sheets-facilities.csv'

ROW = 328  # green-acres-home-care
BASE = 'https://www.greenacreshome.com/example'

HERO = f'{BASE}/slide_bg.jpg'
GALLERY = [f'{BASE}/gallery/{i:02d}.webp' for i in range(1, 13)]
EXTRAS = [f'{BASE}/slide_bg2.png', f'{BASE}/slide03.jpg',
          f'{BASE}/teaser02.jpg', f'{BASE}/teaser03.jpg']
PHOTOS = GALLERY + EXTRAS  # 16 total
PHOTO_STR = '|'.join(PHOTOS)

def main():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    sheet = build('sheets', 'v4', credentials=creds).spreadsheets()
    body = {'valueInputOption': 'RAW', 'data': [
        {'range': f"'{TAB}'!AZ{ROW}", 'values': [[HERO]]},
        {'range': f"'{TAB}'!BA{ROW}", 'values': [[PHOTO_STR]]},
        {'range': f"'{TAB}'!BB{ROW}", 'values': [[len(PHOTOS)]]},
    ]}
    resp = sheet.values().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
    print(f"Updated {resp.get('totalUpdatedCells')} cells:")
    print(f"  AZ{ROW} hero_image  -> {HERO}")
    print(f"  BA{ROW} photos      -> {len(PHOTOS)} URLs (pipe-separated)")
    print(f"  BB{ROW} photo_count -> {len(PHOTOS)}")

if __name__ == '__main__':
    main()
