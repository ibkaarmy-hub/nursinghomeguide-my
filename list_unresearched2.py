"""
Output facility list to a text file to avoid encoding issues.
Prioritise: has real website (not /facilities/...) + not already done + highest reviews.
"""
import sys, io
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

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
    # Apify duplicates / non-nursing homes
    'cozzi-confinement-center-yong-peng',
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

candidates = []

for row in fac_data[1:]:
    slug = g(row, 'slug')
    if not slug or slug in ALREADY_DONE:
        continue
    website = g(row, 'website') or g(row, 'url')
    # Skip internal /facilities/ placeholder URLs — those have no real website
    if not website or website.startswith('/facilities/'):
        continue
    title = g(row, 'title')
    area = g(row, 'area')
    phone = g(row, 'phone')
    rating = g(row, 'rating')
    reviews = g(row, 'review_count')
    editorial = g(row, 'editorial_summary')
    has_editorial = bool(editorial)
    try:
        rev_count = int(reviews) if reviews else 0
    except:
        rev_count = 0
    candidates.append({
        'slug': slug, 'title': title, 'area': area,
        'website': website, 'phone': phone,
        'rating': rating, 'reviews': rev_count,
        'has_editorial': has_editorial,
    })

# Sort: not done first, then by review count descending
candidates.sort(key=lambda x: (x['has_editorial'], -x['reviews']))

print(f'Total candidates with real websites: {len(candidates)}')
print(f'Already have editorial: {sum(1 for c in candidates if c["has_editorial"])}')
print(f'Still to do: {sum(1 for c in candidates if not c["has_editorial"])}')
print()

todo = [c for c in candidates if not c['has_editorial']]
print(f'=== NEXT BATCH (top 40 by review count) ===')
for i, e in enumerate(todo[:40], 1):
    print(f'{i:02d}. [{e["slug"]}]')
    print(f'    Title:   {e["title"]}')
    print(f'    Area:    {e["area"]}')
    print(f'    Website: {e["website"]}')
    print(f'    Rating:  {e["rating"]} ({e["reviews"]} reviews)')
    print(f'    Phone:   {e["phone"]}')
    print()
