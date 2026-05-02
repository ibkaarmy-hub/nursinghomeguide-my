"""
Hand-fix for slug `multicare-nursing-home-johor`:
  - state: Selangor → Johor (real JB branch opened Aug 2025; coords confirm JB metro)
  - editorial_summary: full rewrite (no meta-line, real published pricing tiers)
  - pricing_display: full chain tier headline
  - photos: prepend 8 operator-hosted images (with attribution Details row)
  - photo_count: 5 → 13
  - four_bed_price: blank → RM 2,300
  - last_updated: today
  - Details: 7 rooms tiers + included items + Pricing source + Photo credits
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import date

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE     = 'token_sheets.json'
SCOPES         = ['https://www.googleapis.com/auth/spreadsheets']
FAC_TAB        = 'google-sheets-facilities.csv'
DETAILS_TAB    = 'Details'
SLUG           = 'multicare-nursing-home-johor'

creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
service = build('sheets', 'v4', credentials=creds)
ss = service.spreadsheets()

TODAY = str(date.today())

EDITORIAL = (
    "Multicare Nursing Home opened its Johor Bahru branch in August 2025 — the "
    "chain's first expansion outside the Klang Valley. The parent home in "
    "Petaling Jaya has roughly 32 years of operating history, which makes "
    "Multicare one of the longer-established private nursing groups in "
    "Malaysia. The JB site sits in the western Johor Bahru metro (Skudai/"
    "Iskandar Puteri area); the operator's published material describes a "
    "fully residential nursing facility rather than a light assisted-living "
    "setup, with day and night caregiver coverage and an on-call doctor for "
    "emergencies."
    "\n\n"
    "The chain's published service scope covers assisted living, elderly "
    "care, nursing care, stroke rehabilitation, post-operative care, "
    "palliative care, dementia care and respite care, with 24-hour registered "
    "nurses and caregivers, medication administration, physiotherapy, "
    "occupational therapy activities, and oxygen and ventilator support where "
    "required. Multicare publishes a full pricing tier list — uncommon among "
    "Malaysian nursing homes — at RM 3,500/month for a VIP single room, "
    "RM 3,000 for a single, RM 2,800 for 2-bed sharing, RM 2,500 for 3-bed, "
    "RM 2,300 for 4-bed, RM 2,000 for 5-bed and RM 1,800 for 6-bed. All "
    "tiers are described as AC rooms with TV and Wifi, an attached bathroom, "
    "meals delivered to the room and a personal caregiver included. Treat "
    "those as starting rates — the actual monthly fee will scale with "
    "dependency level, PEG/oxygen needs, wound care and any extras, and "
    "chain-wide rates are always worth re-confirming on the call for the "
    "specific branch."
    "\n\n"
    "Useful things to confirm before placing: the on-duty nurse-to-resident "
    "ratio for both day and night, broken out between RNs and caregivers; "
    "how many current residents are bed-bound or PEG-fed (those skew "
    "workload heavily); halal and dietary handling; language coverage among "
    "caregivers; the JKM licence number for the JB premises; and the exact "
    "street address and neighbourhood, since the operator hasn't yet "
    "published the JB branch address on its main site."
)

PRICING_DISPLAY = (
    'From RM 1,800 (6-bed shared) to RM 3,500 (VIP single) — '
    'published on operator website'
)

OPERATOR_PHOTOS = [
    'https://multicarehomes.com/img/image1.jpg',
    'https://multicarehomes.com/img/image2.jpg',
    'https://multicarehomes.com/img/image3.jpg',
    'https://multicarehomes.com/img/image4.jpg',
    'https://multicarehomes.com/img/pf1.png',
    'https://multicarehomes.com/img/pf02.png',
    'https://multicarehomes.com/img/pf3.png',
    'https://multicarehomes.com/img/pf4.png',
]

# ─────────────────────────────────────────────────────────────────────────────
# Read existing data
# ─────────────────────────────────────────────────────────────────────────────
fac_data = ss.values().get(
    spreadsheetId=SPREADSHEET_ID, range=f"'{FAC_TAB}'"
).execute().get('values', [])
headers = fac_data[0]

def col_letter(n):
    s = ''
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s

def h(name): return headers.index(name) if name in headers else None

slug_i = h('slug')
photos_i = h('photos')

# Find target row
target_row_i = None
existing_photos = ''
for i, row in enumerate(fac_data[1:], start=2):
    if slug_i < len(row) and row[slug_i].strip() == SLUG:
        target_row_i = i
        if photos_i is not None and photos_i < len(row):
            existing_photos = row[photos_i] or ''
        break

if target_row_i is None:
    raise SystemExit(f"Slug not found: {SLUG}")

# Build merged photos: operator photos first, then existing Google CDN photos
existing_list = [p for p in existing_photos.split('|') if p.strip()]
# Don't double-add if any operator URL is already there (defensive)
merged_photos = OPERATOR_PHOTOS + [p for p in existing_list if p not in OPERATOR_PHOTOS]
new_photos_str = '|'.join(merged_photos)
new_photo_count = str(len(merged_photos))

UPDATES = {
    'state':            'Johor',
    'editorial_summary': EDITORIAL,
    'pricing_display':  PRICING_DISPLAY,
    'four_bed_price':   'RM 2,300',
    'photos':           new_photos_str,
    'photo_count':      new_photo_count,
    'last_updated':     TODAY,
}

print(f"Target row: {target_row_i}")
print(f"Existing photos: {len(existing_list)} → new total: {len(merged_photos)}")

# ─────────────────────────────────────────────────────────────────────────────
# Build batch updates for facilities tab
# ─────────────────────────────────────────────────────────────────────────────
batch_data = []
for field, value in UPDATES.items():
    col_i = h(field)
    if col_i is None:
        print(f"  WARN: missing column '{field}'"); continue
    batch_data.append({
        'range': f"'{FAC_TAB}'!{col_letter(col_i+1)}{target_row_i}",
        'values': [[value]]
    })

ss.values().batchUpdate(
    spreadsheetId=SPREADSHEET_ID,
    body={'valueInputOption': 'RAW', 'data': batch_data}
).execute()
print(f"✅ Applied {len(batch_data)} facility updates")

# ─────────────────────────────────────────────────────────────────────────────
# Details rows: append rooms tiers, included items, pricing source, photo credits
# ─────────────────────────────────────────────────────────────────────────────
details_data = ss.values().get(
    spreadsheetId=SPREADSHEET_ID, range=f"'{DETAILS_TAB}'"
).execute().get('values', [])

existing_keys = {(r[0], r[1], r[2]) for r in details_data[1:] if len(r) >= 3}

ROOMS = [
    ('VIP single (RM/mo)',      '3,500'),
    ('Single (RM/mo)',          '3,000'),
    ('2-bed shared (RM/mo)',    '2,800'),
    ('3-bed shared (RM/mo)',    '2,500'),
    ('4-bed shared (RM/mo)',    '2,300'),
    ('5-bed shared (RM/mo)',    '2,000'),
    ('6-bed shared (RM/mo)',    '1,800'),
]
INCLUDED = [
    ('AC',                      'Yes'),
    ('TV with Wifi',            'Yes'),
    ('Attached bathroom',       'Yes'),
    ('Meals delivered to room', 'Yes'),
    ('Personal caregiver',      'Included'),
]
PRICING_SOURCE = (
    'https://multicarehomes.com/packages.html — '
    'chain rates; final fee depends on care needs'
)
PHOTO_CREDIT = 'Facility photos courtesy of multicarehomes.com'

new_rows = []
for label, val in ROOMS:
    if (SLUG, 'rooms', label) not in existing_keys:
        new_rows.append([SLUG, 'rooms', label, val])
if (SLUG, 'rooms', 'Pricing source') not in existing_keys:
    new_rows.append([SLUG, 'rooms', 'Pricing source', PRICING_SOURCE])
for label, val in INCLUDED:
    if (SLUG, 'included', label) not in existing_keys:
        new_rows.append([SLUG, 'included', label, val])
if (SLUG, 'policies', 'Photo credits') not in existing_keys:
    new_rows.append([SLUG, 'policies', 'Photo credits', PHOTO_CREDIT])

if new_rows:
    ss.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{DETAILS_TAB}'!A:D",
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body={'values': new_rows}
    ).execute()
    print(f"✅ Appended {len(new_rows)} Details rows")
    for r in new_rows:
        print(f"  + [{r[1]}] {r[2]} = {r[3][:60]}")
else:
    print("ℹ️  No new Details rows needed (all already exist)")

print("\n🎉 Multicare Johor revision complete.")
