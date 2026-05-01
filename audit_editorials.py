import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

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
    spreadsheetId=SPREADSHEET_ID, range=f"'{FAC_TAB}'"
).execute().get('values', [])
headers = fac_data[0]

def g(row, col):
    i = headers.index(col) if col in headers else None
    return (row[i] if i is not None and i < len(row) else '').strip()

ALREADY_DONE = {
    'woon-ho-family-care-centre','eha-parkview-eldercare-perling',
    'fcc-family-care-centre','jeta-care','gentle-hill-elder-care',
    'haywood-senior-living-medini-johor-bahru',
}

print("=== FACILITIES WITH EDITORIALS (showing first 60 chars) ===")
with_ed = []
without_ed = []
for row in fac_data[1:]:
    slug = g(row,'slug')
    if not slug or slug in ALREADY_DONE: continue
    website = g(row,'website') or g(row,'url')
    if not website or website.startswith('/facilities/'): continue
    title = g(row,'title')
    editorial = g(row,'editorial_summary')
    rating = g(row,'rating')
    reviews = g(row,'review_count')
    if editorial:
        with_ed.append((title, slug, editorial[:80], website, rating, reviews))
    else:
        without_ed.append((title, slug, website, rating, reviews))

print(f"\nWITH editorial ({len(with_ed)}):")
for title, slug, ed, site, rating, reviews in with_ed:
    short_site = site[:50] if len(site)>50 else site
    print(f"  [{slug[:50]}]")
    print(f"    rating={rating}({reviews}r) site={short_site}")
    print(f"    editorial: {ed}")

print(f"\nWITHOUT editorial ({len(without_ed)}):")
for title, slug, site, rating, reviews in without_ed:
    print(f"  [{slug[:55]}] {rating}({reviews}r) {site[:60]}")
