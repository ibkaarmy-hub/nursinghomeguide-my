"""
List facilities that have a website URL but no editorial_summary yet.
These are the candidates for the next research batch.
"""
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE = 'token_sheets.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
FAC_TAB = 'google-sheets-facilities.csv'

ALREADY_DONE = {
    'woon-ho-family-care-centre',
    'eha-parkview-eldercare-perling',
    'fcc-family-care-centre',
    'jeta-care',
    'gentle-hill-elder-care',
    'haywood-senior-living-medini-johor-bahru',
}

creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
service = build('sheets', 'v4', credentials=creds)
ss = service.spreadsheets()

fac_data = ss.values().get(
    spreadsheetId=SPREADSHEET_ID, range=f"'{FAC_TAB}'"
).execute().get('values', [])

headers = fac_data[0]

def g(row, col):
    i = headers.index(col) if col in headers else None
    return (row[i] if i is not None and i < len(row) else '').strip()

with_website = []
no_website = []

for row in fac_data[1:]:
    slug = g(row, 'slug')
    if not slug or slug in ALREADY_DONE:
        continue
    title = g(row, 'title')
    website = g(row, 'website')
    url = g(row, 'url')
    area = g(row, 'area')
    phone = g(row, 'phone')
    hero = g(row, 'hero_image')
    rating = g(row, 'rating')
    review_count = g(row, 'review_count')
    maps_url = g(row, 'google_maps_url')

    site = website or url
    entry = {
        'slug': slug, 'title': title, 'area': area,
        'website': site, 'phone': phone,
        'rating': rating, 'reviews': review_count,
        'has_hero': bool(hero), 'maps_url': maps_url,
    }
    if site:
        with_website.append(entry)
    else:
        no_website.append(entry)

print(f'=== WITH WEBSITE ({len(with_website)}) ===')
for e in with_website:
    print(f'  [{e["slug"]}]')
    print(f'    title:   {e["title"]}')
    print(f'    area:    {e["area"]}')
    print(f'    website: {e["website"]}')
    print(f'    rating:  {e["rating"]} ({e["reviews"]} reviews)')
    print()

print(f'=== NO WEBSITE ({len(no_website)}) ===')
for e in no_website:
    stars = f'{e["rating"]}★ ({e["reviews"]} reviews)' if e['rating'] else 'no rating'
    print(f'  {e["title"]} | {e["area"]} | {stars} | phone: {e["phone"]}')
