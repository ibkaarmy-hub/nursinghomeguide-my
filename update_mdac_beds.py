"""
Update total_beds from MDAC data for confirmed matches.
Skips: Magna Resort (bad match), Jeta Care (sheet has 62; MDAC 50 may be older),
       ECON Medicare (194 vs 199 — minor discrepancy, keep existing).
Uses Google Sheets API (OAuth).
"""

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE = 'token_sheets.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
TAB = 'google-sheets-facilities.csv'

# slug -> total_beds from MDAC (confirmed phone matches, sheet currently blank)
BEDS_TO_UPDATE = {
    'pusat-jagaan-vr-melodies-old-folks-home':          75,
    'persatuan-kebajikan-orang-tua-ceria':             100,
    'green-garden-care-center-sdn-bhd':                 50,
    'pusat-jagaan-warga-emas-banang':                   30,
    'rumah-sejahtera-yong-peng':                        13,
    'miriam-home-prefer-donation-address':              50,
    'pusat-jagaan-pawana-sutera':                       35,
    'pusat-jagaan-ler-lin':                             26,
    'lecadia-primacare-centre':                        150,
    'pusat-jagaan-husna-arrashid':                      30,
    'pusat-jagaan-little-sisters-of-the-poor':          70,
    'sunshine-nursing-home':                            24,
    'pusat-jagaan-persatuan-kebajikan-warga-emas-chan-kl': 30,
    'ampang-old-folks-home':                            50,
    'apple-nursery-home':                               34,
    'noble-care-nursing-home-nursing-home-subang-jaya-selangor': 20,
    'pusat-jagaan-warga-tua-damai':                     30,
    'gam-yam-senior-home-in-ampang-kuala-lumpur-malaysia': 50,
    'pusat-jagaan-rumah-orang-tua-wesley':              24,
    'bandar-damai-home-care':                           27,   # combined male+female
    'bait-al-mawaddah-pusat-jagaan-warga-emas-lembaga-zakat-selangor': 52,
    'pusat-jagaan-warga-tua':                           30,
    'love-and-care-centre-kajang':                      21,   # 15+6 beds across 2 branches
    'sincere-care-home':                                23,
}

creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
service = build('sheets', 'v4', credentials=creds)
ss = service.spreadsheets()

# Fetch current sheet
data = ss.values().get(
    spreadsheetId=SPREADSHEET_ID,
    range=f"'{TAB}'"
).execute().get('values', [])

headers = data[0]
rows = data[1:]

try:
    slug_col   = headers.index('slug')
    beds_col   = headers.index('total_beds')
except ValueError as e:
    print(f"ERROR: column not found: {e}")
    raise

print(f"Sheet has {len(rows)} data rows")
print(f"slug col={slug_col}, total_beds col={beds_col}")
print()

updates = []  # (row_index_1based, col_index_1based, new_value)

for row_idx, row in enumerate(rows):
    slug = row[slug_col] if slug_col < len(row) else ''
    if slug in BEDS_TO_UPDATE:
        current_beds = row[beds_col] if beds_col < len(row) else ''
        new_beds = str(BEDS_TO_UPDATE[slug])
        print(f"  {slug[:45]}")
        print(f"    current beds: '{current_beds}' -> new: {new_beds}")
        if current_beds and current_beds != new_beds:
            print(f"    ** WARNING: overwriting existing value {current_beds} -> {new_beds}")
        # +2: 1 for header row, 1 for 0-index to 1-index
        updates.append((row_idx + 2, beds_col + 1, new_beds))

print(f"\n{len(updates)} cells to update (out of {len(BEDS_TO_UPDATE)} targets)")
missing = set(BEDS_TO_UPDATE.keys()) - {rows[r-2][slug_col] for r, _, _ in updates if r-2 < len(rows) and slug_col < len(rows[r-2])}
if missing:
    print(f"Slugs NOT found in sheet: {missing}")

if not updates:
    print("Nothing to update.")
else:
    confirm = input("\nProceed with update? [y/N]: ").strip().lower()
    if confirm != 'y':
        print("Aborted.")
        exit()

    # Batch update
    body = {
        'valueInputOption': 'RAW',
        'data': [
            {
                'range': f"'{TAB}'!{chr(64 + col)}{row}",
                'values': [[val]]
            }
            for row, col, val in updates
        ]
    }
    result = ss.values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body=body
    ).execute()

    updated = result.get('totalUpdatedCells', 0)
    print(f"\nDone. {updated} cells updated.")
    print("Source: MDAC.my (MyAgeing directory)")
