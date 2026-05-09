"""
1. Adds 'status' column to the sheet (if not present)
2. Sets status='unverified' for all Johor facilities with no care_types
3. Simultaneously adds known care_types for facilities we have already researched
   so they immediately flip back to live
"""
import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
creds = Credentials.from_authorized_user_file('token_sheets.json',
        ['https://www.googleapis.com/auth/spreadsheets'])
service = build('sheets', 'v4', credentials=creds)
ss = service.spreadsheets()

# ── Load sheet ────────────────────────────────────────────────────────────────
data = ss.values().get(spreadsheetId=SPREADSHEET_ID,
       range="'google-sheets-facilities.csv'").execute().get('values', [])
headers = data[0]

def col(name):
    return headers.index(name) if name in headers else None

def g(row, name):
    i = col(name)
    return (row[i] if i is not None and i < len(row) else '').strip()

# ── Add 'status' column if missing ───────────────────────────────────────────
STATUS_COL = col('status')
if STATUS_COL is None:
    # Get sheetId for facilities tab
    meta = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    sheet_id = next(s['properties']['sheetId'] for s in meta['sheets']
                    if 'facilities' in s['properties']['title'].lower())
    service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={'requests': [{'appendDimension': {
            'sheetId': sheet_id, 'dimension': 'COLUMNS', 'length': 1
        }}]}
    ).execute()
    # Re-fetch to get updated column count
    data = ss.values().get(spreadsheetId=SPREADSHEET_ID,
           range="'google-sheets-facilities.csv'").execute().get('values', [])
    headers = data[0]
    STATUS_COL = len(headers)  # will be the new last column

    def col_letter(n):
        result = ''
        n += 1
        while n:
            n, r = divmod(n-1, 26)
            result = chr(65+r) + result
        return result

    letter = col_letter(STATUS_COL)
    ss.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'google-sheets-facilities.csv'!{letter}1",
        valueInputOption='RAW',
        body={'values': [['status']]}
    ).execute()
    print(f"'status' column added at {letter}")
    headers.append('status')
    STATUS_COL = len(headers) - 1

# ── Known care_types for already-researched facilities ────────────────────────
# These had editorials written — we know they're nursing homes.
# Adding care_types instantly brings them back live.
KNOWN_CARE_TYPES = {
    'lee-nursing':                              'Nursing Home',
    'lotus-ville-care-centre':                  'Nursing Home + Assisted Living',
    'golden-age-care-centre':                   'Nursing Home + Rehabilitation',
    'ax-nursing-home-plt':                      'Nursing Home',
    'fu-ka-care-center':                        'Nursing Home + Assisted Living',
    'pusat-jagaan-warga-emas-nur-ehsan':        'Nursing Home + Assisted Living',
    'healthlife-old-folks-home':                'Nursing Home',
    'pusat-jagaan-wargatua-parit-bilal':        'Nursing Home',
    'pusat-jagaan-impian-syimah-jalan-kemaman': 'Nursing Home',
    'pusat-jagaan-impian-syimah-jalan-kemuncak':'Nursing Home + Assisted Living',
    'elim-nursing-home-batu-pahat':             'Nursing Home',
    'hang-nursing-home-gelang-patah-branch':    'Nursing Home',
    'yang-xin-nursing-home':                    'Nursing Home + Assisted Living',
    'master-care-centre':                       'Nursing Home + Assisted Living',
    'master-nursing-care-centre-daya':          'Nursing Home + Assisted Living',
    'master-care-centre-taman-abad':            'Nursing Home + Assisted Living',
    'rebina-home-care-centre-sdn-bhd':          'Day Care + Home Care',
    'pusat-perjagaan-orang-tua-ren-ai':         'Nursing Home',
    'pusat-jagaan-orang-tua-yeo-jb':            'Nursing Home',
    'graceville-senior-care-centre':            'Nursing Home',
    'graceville-care-centre-sungai-mati':       'Nursing Home',
    'pusat-jagaan-warga-emas-nur-ehsan-tangkak':'Nursing Home',
    'blissful-senior-care-centre-licensed-and-certified-by-gover': 'Nursing Home',
    'eha-parkview-eldercare-perling':           'Nursing Home + Day Care + Assisted Living + Rehabilitation',
    'fcc-family-care-centre':                   'Nursing Home + Day Care + Assisted Living + Rehabilitation',
    'pusat-jagaan-teduhan-zafrah-warga-emas-oku-lelaki': 'Nursing Home + Assisted Living',
    'pusat-jagaan-kebajikan-manna-sinar-cahaya':         'Nursing Home',
    'agape-care-centre':                        'Nursing Home',
    'alda-homes-eldercare':                     'Nursing Home + Assisted Living',
    'wcc-woundcare-nursing-centre':             'Nursing Home + Wound Care',
    'comfort-home-care-centre':                 'Nursing Home',
    'sincere-heart-care-centre':                'Nursing Home',
    'pusat-jagaan-warga-tua-hayati-care-centre':'Nursing Home',
}

# ── Mark obvious non-NH / truly unknown for REMOVAL ─────────────────────────
# These will get status='removed' — permanently hidden unless reviewed
NON_NH_SLUGS = {
    'magna-resort-sdn-bhd',         # Resort/hotel branding
    'khazanah-nursery',             # Nursery — likely children, not elderly
    'dion-confinement-center',      # Postpartum confinement only
    'mediqas-sdn-bhd',              # Medical supplier, not a care facility
}

# ── Build batch updates ───────────────────────────────────────────────────────
care_types_col   = col('care_types')
slug_col         = col('slug')

def col_letter(n):
    result = ''
    n += 1
    while n:
        n, r = divmod(n-1, 26)
        result = chr(65+r) + result
    return result

status_letter     = col_letter(STATUS_COL)
care_types_letter = col_letter(care_types_col)

updates = []  # list of {range, value}

unverified_count = 0
care_types_filled = 0
non_nh_count = 0

for row_idx, row in enumerate(data[1:], start=2):  # 1-based, row 1 = header
    slug       = g(row, 'slug')
    state_val  = g(row, 'state')
    care_types = g(row, 'care_types')
    curr_status = g(row, 'status')

    # Only process Johor (KL/Selangor were just added, handle separately)
    if state_val != 'Johor':
        continue

    # Skip if already has care_types — leave status alone
    if care_types:
        continue

    # Fill known care_types first
    if slug in KNOWN_CARE_TYPES:
        updates.append({
            'range': f"'google-sheets-facilities.csv'!{care_types_letter}{row_idx}",
            'values': [[KNOWN_CARE_TYPES[slug]]]
        })
        care_types_filled += 1
        # Status stays blank (live)
        continue

    # Non-NH: mark removed
    if slug in NON_NH_SLUGS:
        updates.append({
            'range': f"'google-sheets-facilities.csv'!{status_letter}{row_idx}",
            'values': [['removed']]
        })
        non_nh_count += 1
        continue

    # Everything else: mark unverified
    updates.append({
        'range': f"'google-sheets-facilities.csv'!{status_letter}{row_idx}",
        'values': [['unverified']]
    })
    unverified_count += 1

print(f"\nPlan:")
print(f"  Care types auto-filled (back to live): {care_types_filled}")
print(f"  Marked 'unverified' (hidden, pending contact): {unverified_count}")
print(f"  Marked 'removed' (clear non-NH): {non_nh_count}")
print(f"  Total updates: {len(updates)}")

# ── Apply all updates ─────────────────────────────────────────────────────────
if not updates:
    print("Nothing to update.")
else:
    resp = ss.values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={
            'valueInputOption': 'RAW',
            'data': [{'range': u['range'], 'values': u['values']} for u in updates]
        }
    ).execute()
    print(f"\n✅ {resp.get('totalUpdatedCells', 0)} cells updated")

# ── Summary of what remains hidden ───────────────────────────────────────────
print("\n--- Facilities now hidden (unverified) ---")
data2 = ss.values().get(spreadsheetId=SPREADSHEET_ID,
        range="'google-sheets-facilities.csv'").execute().get('values', [])
headers2 = data2[0]
def g2(row, name):
    i = headers2.index(name) if name in headers2 else None
    return (row[i] if i is not None and i < len(row) else '').strip()

hidden = [(g2(r,'title'), g2(r,'area'), g2(r,'rating'), g2(r,'review_count'))
          for r in data2[1:]
          if g2(r,'status') in ('unverified','removed') and g2(r,'state') == 'Johor']
for title, area, rat, rev in hidden:
    print(f"  ★{rat:3s}({rev:3s}r) {title}")
print(f"\nTotal hidden from Johor: {len(hidden)}")
