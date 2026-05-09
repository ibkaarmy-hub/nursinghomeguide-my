"""
Set hero_image, website, and fix known fields for EHA Parkview, FCC, Jeta Care.
Also marks Jeta Care dementia care as confirmed and updates area for Jeta Care (Kulai).
"""
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import date

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE = 'token_sheets.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
FAC_TAB = 'google-sheets-facilities.csv'
TODAY = str(date.today())

creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
service = build('sheets', 'v4', credentials=creds)
ss = service.spreadsheets()

fac_data = ss.values().get(
    spreadsheetId=SPREADSHEET_ID,
    range=f"'{FAC_TAB}'"
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

updates_map = {
    'eha-parkview-eldercare-perling': {
        'hero_image': 'https://ehaeldercare.com.my/wp-content/uploads/2024/08/EHA-Parkview-Eldercare-front-view.jpg',
        'photos': '|'.join([
            'https://ehaeldercare.com.my/wp-content/uploads/2024/08/EHA-Parkview-Eldercare-front-view.jpg',
            'https://ehaeldercare.com.my/wp-content/uploads/2024/08/EHA-Parkview-Eldercare-facilities.jpg',
            'https://ehaeldercare.com.my/wp-content/uploads/2024/08/EHA-Parkview-Eldercare-toilet.jpg',
            'https://ehaeldercare.com.my/wp-content/uploads/2023/02/IMG_3986-1.jpg',
            'https://ehaeldercare.com.my/wp-content/uploads/2023/02/IMG_5683.jpg',
        ]),
        'photo_count': '5',
        'website': 'https://ehaeldercare.com.my/our-locations/eha-parkview-eldercare-perling-jb/',
        'care_dementia': 'yes',
        'last_updated': TODAY,
    },
    'fcc-family-care-centre': {
        'hero_image': 'https://www.familycarecentre.co/wp-content/uploads/2026/04/Natural-green-environment.jpg',
        'photos': '|'.join([
            'https://www.familycarecentre.co/wp-content/uploads/2026/04/Natural-green-environment.jpg',
            'https://www.familycarecentre.co/wp-content/uploads/2026/04/Lifestyle-and-community.jpg',
            'https://www.familycarecentre.co/wp-content/uploads/2026/04/Care-farming.jpg',
            'https://www.familycarecentre.co/wp-content/uploads/2026/04/Our-care-approach.jpg',
        ]),
        'photo_count': '4',
        'website': 'https://www.familycarecentre.co',
        'last_updated': TODAY,
    },
    'jeta-care': {
        'hero_image': 'http://www.jetacare.com/images/hero-banner.jpg',
        'photos': '|'.join([
            'http://www.jetacare.com/images/hero-banner.jpg',
            'http://www.jetacare.com/images/index-about2.jpg',
            'http://www.jetacare.com/images/index-about.jpg',
            'http://www.jetacare.com/images/index-about1.jpg',
            'http://www.jetacare.com/images/index-about3.jpg',
            'http://www.jetacare.com/images/index-about4.jpg',
        ]),
        'photo_count': '6',
        'website': 'http://www.jetacare.com/',
        'area': 'Kulai, Johor',
        'care_dementia': 'yes',   # confirmed on their website
        'licence_number': 'JKM licensed (see jetacare.com) + MOH CKAPS (valid Feb 2028)',
        'last_updated': TODAY,
    },
}

updates = []
for i, row in enumerate(fac_data[1:], start=2):
    slug = row[slug_i] if slug_i < len(row) else ''
    if slug in updates_map:
        for field, value in updates_map[slug].items():
            col_i = h(field)
            if col_i is not None:
                updates.append({
                    'range': f"'{FAC_TAB}'!{col_letter(col_i + 1)}{i}",
                    'values': [[value]]
                })
        print(f'  Queued {len(updates_map[slug])} updates for {slug}')

if updates:
    ss.values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={'valueInputOption': 'RAW', 'data': updates}
    ).execute()
    print(f'Applied {len(updates)} updates.')
else:
    print('Nothing updated.')
