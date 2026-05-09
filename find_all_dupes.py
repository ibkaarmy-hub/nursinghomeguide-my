from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from collections import defaultdict

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE = 'token_sheets.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
FAC_TAB = 'google-sheets-facilities.csv'

creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
service = build('sheets', 'v4', credentials=creds)
ss = service.spreadsheets()

fac_data = ss.values().get(
    spreadsheetId=SPREADSHEET_ID,
    range=f"'{FAC_TAB}'"
).execute().get('values', [])

headers = fac_data[0]
slug_i = headers.index('slug')
title_i = headers.index('title') if 'title' in headers else 0

# Group by normalised title (lowercase, strip punctuation)
import re
def normalise(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())

groups = defaultdict(list)
for i, row in enumerate(fac_data[1:], start=2):
    slug = row[slug_i] if slug_i < len(row) else ''
    title = row[title_i] if title_i < len(row) else ''
    key = normalise(title)
    if key:
        groups[key].append((i, slug, title))

print('Potential duplicates (same normalised name):')
found = False
for key, entries in groups.items():
    if len(entries) > 1:
        found = True
        print(f'  "{key}":')
        for row_num, slug, title in entries:
            print(f'    Row {row_num}: slug="{slug}" | title="{title}"')

if not found:
    print('  None found.')

print(f'\nTotal facilities: {len(fac_data) - 1}')
