"""
Deduplicate the two EHA Parkview Perling rows.

Migrate the unique-and-useful info from the short slug onto the canonical
long-slug row, then mark the short slug status='removed' (which only HIDES it
from the live site — all 44 of its Detail rows remain in the sheet for audit).

What the short slug uniquely had:
  - website: branch-specific URL (better than canonical's generic homepage)
  - hero_image: operator-hosted WordPress URL (potentially more durable than
    canonical's Google-CDN URL, but canonical has 8 photos vs short-slug's 5,
    so we DON'T overwrite — durability fix is a separate decision)
  - 44 Detail rows: mostly mangled or unverified (OT/speech claims not in
    EHA's group services list); we don't migrate these. They remain in the
    sheet attached to the removed slug for future audit.

What we change:
  1. CANONICAL: overwrite website with the branch-specific URL.
  2. SHORT slug: status='removed', last_updated bumped.
  3. SHORT slug: append a `policies` Details row noting why it was removed
     and pointing to the canonical slug, for future archaeology.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import date

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE    = 'token_sheets.json'
SCOPES        = ['https://www.googleapis.com/auth/spreadsheets']
FAC_TAB       = 'google-sheets-facilities.csv'
DETAILS_TAB   = 'Details'

SHORT = 'eha-parkview-eldercare-perling'
LONG  = 'eha-parkview-eldercare-perling-1-nursing-home-johor-bahru'
BRANCH_URL = 'https://ehaeldercare.com.my/our-locations/eha-parkview-eldercare-perling-jb/'

creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
service = build('sheets', 'v4', credentials=creds)
ss = service.spreadsheets()

fac = ss.values().get(
    spreadsheetId=SPREADSHEET_ID, range=f"'{FAC_TAB}'"
).execute().get('values', [])
headers = fac[0]

def col_letter(n):
    s = ''
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s
def h(name): return headers.index(name) if name in headers else None
slug_i = h('slug')

short_row, long_row = None, None
for i, row in enumerate(fac[1:], start=2):
    if slug_i >= len(row): continue
    s = row[slug_i].strip()
    if s == SHORT: short_row = i
    elif s == LONG: long_row = i

assert short_row and long_row, f"Could not find both rows: short={short_row}, long={long_row}"
print(f"SHORT row {short_row}, LONG row {long_row}")

TODAY = str(date.today())
batch = []

# 1. Migrate website URL onto canonical
batch.append({
    'range': f"'{FAC_TAB}'!{col_letter(h('website')+1)}{long_row}",
    'values': [[BRANCH_URL]]
})

# 2. Mark short slug status=removed, bump last_updated
batch.append({
    'range': f"'{FAC_TAB}'!{col_letter(h('status')+1)}{short_row}",
    'values': [['removed']]
})
batch.append({
    'range': f"'{FAC_TAB}'!{col_letter(h('last_updated')+1)}{short_row}",
    'values': [[TODAY]]
})

ss.values().batchUpdate(
    spreadsheetId=SPREADSHEET_ID,
    body={'valueInputOption': 'RAW', 'data': batch}
).execute()
print(f"✅ Applied {len(batch)} facilities-tab updates")

# 3. Append a policies Details row on the SHORT slug noting the dedupe (idempotent)
det = ss.values().get(
    spreadsheetId=SPREADSHEET_ID, range=f"'{DETAILS_TAB}'"
).execute().get('values', [])
existing = {(r[0], r[1], r[2]) for r in det[1:] if len(r) >= 3}

note_label = 'Removed reason'
note_value = (f'Duplicate sheet entry for the same facility. Canonical row: '
              f'{LONG}. Hidden from site via status=removed on {TODAY}. '
              f'All Detail rows preserved in sheet for audit.')

if (SHORT, 'policies', note_label) not in existing:
    ss.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{DETAILS_TAB}'!A:D",
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body={'values': [[SHORT, 'policies', note_label, note_value]]}
    ).execute()
    print(f"✅ Appended dedupe-note Details row")
else:
    print(f"  - dedupe note already exists, skipping")

print("\n🎉 Parkview dedupe complete.")
print(f"  - Live site now shows ONE Parkview profile (canonical long slug).")
print(f"  - Short-slug row hidden but all its data preserved in sheet.")
print(f"  - Canonical row's website URL upgraded to branch-specific URL.")
