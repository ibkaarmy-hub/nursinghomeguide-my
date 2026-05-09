"""
update_fcc_johor.py — Enrichment update for FCC Family Care Centre Johor Bahru
Slug: fcc-family-care-centre-johor-bahru
Run: 2026-05-10

Sources:
  - Operator website: https://www.familycarecentre.co/
  - Google Maps (Apify): 4.9 / 154 reviews
  - Instagram: @fccfamilycarecentre (1,460 followers, 498 posts)
  - JKM licence: J/PJBWT066/2024 (expiry 04.12.2029) — already in sheet

Updates applied:
  1. whatsapp (col Y) — confirmed +60 17-709 7909 (same as phone, from website + IG bio)
  2. care_palliative (col AC) — Yes (operator website lists palliative/cancer/coma/Parkinson's)
  3. care_respite (col AE) — Yes (operator website lists staycation / respite stays)
  4. total_beds (col AS) — 52 (36 CHS Home + 16 MemoryCare Home, from /homes/ page)
  5. private_price (col I) — 4300 (Advanced care, already correct — no change)
  6. pricing_display (col G) — updated with full tier range
  7. google_maps_url (col T) — updated to clean place_id URL from Apify
  8. facebook (col Z) — left blank (not found; Instagram is main social)
  9. editorial_summary (col AY) — full rewrite
 10. last_updated (col U) — today
 11. Details tab — pricing tiers, rooms, staffing, included services, policies rows
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import date

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE     = r'C:\Users\ibkaa\nursinghomeguide-my\Nursing Home Guide Malaysia\token_sheets.json'
SCOPES         = ['https://www.googleapis.com/auth/spreadsheets']
FAC_TAB        = 'google-sheets-facilities.csv'
DETAILS_TAB    = 'Details'
SLUG           = 'fcc-family-care-centre-johor-bahru'
TODAY          = str(date.today())

# ─────────────────────────────────────────────────────────────────────────────
# Editorial — 3 paragraphs, verified facts only
# JKM confirmed (jkm_data_source = "JKM 2026"), so use JKM licence bullet.
# ─────────────────────────────────────────────────────────────────────────────

EDITORIAL = """\
FCC Family Care Centre is a JKM-licensed senior care facility in Ulu Tiram, Johor Bahru, operating from a campus at 17 Jalan Resam, Taman Bukit Tiram. The centre runs two distinct residential units: the CHS Home (36 beds, named after its first resident Mdm. Chia Hui Siam), which accommodates residents from independent to fully bed-bound, and the dedicated MemoryCare Home (16 beds) for residents diagnosed with dementia. Together the two homes provide 52 licensed beds. FCC also offers day care, post-operative recovery stays, and a home-based mobile care service for residents who prefer to remain in their own homes.

The operator's website lists the following care categories with published monthly fees: Basic Care (standard nursing, ADL assistance, medication management) from RM 3,500; Intermediate Care (adds dementia care and fall management) from RM 3,800; Advanced Care (includes palliative care for cancer, Parkinson's, and coma conditions, plus physiotherapy and occupational therapy) from RM 4,300; Home-Based Care from RM 4,300; and Day Care at RM 200 per day. Meals are provided five times daily (breakfast, lunch, high tea, dinner, supper) and are included in residential packages. The published staff-to-resident ratio is 1:6, with nurses on duty 24 hours and a bi-monthly doctor visit schedule plus an on-call emergency doctor. The campus deploys SmartPeep, a vision AI monitoring system that provides 24/7 fall detection and staff alerts using privacy-blurred imaging rather than live video recording.

The natural setting is a genuine differentiator: the compound includes an organic farm and edible garden whose produce goes to resident meals, outdoor areas for walking and birdwatching, a greenhouse, gazebo, and farm animals used in animal-assisted therapy sessions. FCC's Instagram feed (@fccfamilycarecentre, nearly 500 posts) shows regular resident activities — ketupat weaving, table-tennis coordination games, garden harvests, and school-community visits. Reviews on Google Maps are consistently positive about cleanliness, outdoor space, and attentive front-of-house staff; one older review flagged that viewing inside rooms requires a prior appointment and that walk-ins may only see the compound. Families should schedule a formal visit in advance via WhatsApp to see both homes and confirm room availability. On visit: confirm the room type and care tier that fits your relative's current clinical needs, as the pricing tiers differ meaningfully across the three care levels.

**Licence & verification**
- JKM Registered — licence number: J/PJBWT066/2024 (valid to 04 December 2029).

**What to ask on your visit**
- Which home (CHS or MemoryCare) suits my relative's current needs, and can I see both?
- What does the 1:6 staffing ratio look like on a night shift versus a day shift?
- How are care tier upgrades (e.g. Basic to Advanced) handled if needs change?
- Is the SmartPeep system active in all rooms or only common areas?
- When was the last JKM inspection, and can I see the result?\
"""

# Verify no straight double-quotes in editorial body
assert '"' not in EDITORIAL, "Straight double-quote found in editorial — aborting"

# ─────────────────────────────────────────────────────────────────────────────
# Sheet helpers
# ─────────────────────────────────────────────────────────────────────────────
creds   = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
service = build('sheets', 'v4', credentials=creds)
ss      = service.spreadsheets()


def get_all_rows(tab):
    result = ss.values().get(spreadsheetId=SPREADSHEET_ID, range=tab).execute()
    return result.get('values', [])


def col_index(headers, name):
    return headers.index(name)


def batch_update_cells(tab, updates):
    """updates = list of (row_1based, col_1based, value)"""
    data = []
    for row, col, value in updates:
        col_letter = col_to_letter(col)
        data.append({
            'range': f"'{tab}'!{col_letter}{row}",
            'values': [[value]]
        })
    ss.values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={'valueInputOption': 'RAW', 'data': data}
    ).execute()


def col_to_letter(n):
    """1-based int → Excel-style column letter (A, B, ... Z, AA, ...)"""
    result = ''
    while n:
        n, remainder = divmod(n - 1, 26)
        result = chr(65 + remainder) + result
    return result


def append_details_rows(rows):
    """Append rows to Details tab. rows = list of [slug, section, label, value]"""
    ss.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{DETAILS_TAB}'!A1",
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body={'values': rows}
    ).execute()


# ─────────────────────────────────────────────────────────────────────────────
# Load facility row
# ─────────────────────────────────────────────────────────────────────────────
print("Loading facilities tab...")
rows = get_all_rows(FAC_TAB)
headers = rows[0]
print(f"  {len(rows)-1} data rows, {len(headers)} columns")

# Find slug row
fac_row_idx = None
for i, row in enumerate(rows[1:], start=2):  # 1-based, row 1 = headers
    slug_val = row[col_index(headers, 'slug')] if len(row) > col_index(headers, 'slug') else ''
    if slug_val == SLUG:
        fac_row_idx = i
        fac_row = row
        break

if fac_row_idx is None:
    print(f"ERROR: slug '{SLUG}' not found in sheet!")
    sys.exit(1)

print(f"  Found row {fac_row_idx}: {fac_row[0]}")

# Dump raw check for corruption
print("\n--- Raw row sanity check ---")
for i, h in enumerate(headers):
    val = fac_row[i] if i < len(fac_row) else ''
    if val:
        print(f"  {h}: {val[:80]}")
print("--- End sanity check ---\n")

# ─────────────────────────────────────────────────────────────────────────────
# Build facilities tab updates
# ─────────────────────────────────────────────────────────────────────────────
def cidx(name):
    return col_index(headers, name) + 1  # 1-based

updates = [
    # WhatsApp — confirmed from website + IG bio
    (fac_row_idx, cidx('whatsapp'), '+60 17-709 7909'),
    # care_palliative — confirmed (palliative/cancer/coma/Parkinson's on services page)
    (fac_row_idx, cidx('care_palliative'), 'Yes'),
    # care_respite — confirmed (staycation / short-term stays listed)
    (fac_row_idx, cidx('care_respite'), 'Yes'),
    # total_beds — confirmed (36 CHS + 16 MemoryCare = 52)
    (fac_row_idx, cidx('total_beds'), '52'),
    # pricing_display — full tier range from operator website
    (fac_row_idx, cidx('pricing_display'), 'Day Care: RM 200/day | Basic from RM 3,500 | Intermediate from RM 3,800 | Advanced from RM 4,300 — published on operator website'),
    # shared_price — use Basic floor as shared reference
    (fac_row_idx, cidx('shared_price'), '3500'),
    # private_price — Advanced tier (already 4300, confirming)
    (fac_row_idx, cidx('private_price'), '4300'),
    # google_maps_url — clean place_id URL from Apify
    (fac_row_idx, cidx('google_maps_url'), 'https://www.google.com/maps/search/?api=1&query=FCC+Family+Care+Centre+Johor+Bahru&query_place_id=ChIJk_DuiRNv2jERKIfHDxs3Vck'),
    # editorial
    (fac_row_idx, cidx('editorial_summary'), EDITORIAL),
    # last_updated
    (fac_row_idx, cidx('last_updated'), TODAY),
]

print("Applying facilities tab updates...")
batch_update_cells(FAC_TAB, updates)
print(f"  {len(updates)} cells updated for row {fac_row_idx}")

# ─────────────────────────────────────────────────────────────────────────────
# Details tab — check existing rows first
# ─────────────────────────────────────────────────────────────────────────────
print("\nLoading Details tab...")
det_rows = get_all_rows(DETAILS_TAB)
existing = [(r[0], r[1], r[2]) for r in det_rows if len(r) >= 3 and r[0] == SLUG]
existing_keys = {(r[1], r[2]) for r in existing}  # (section, label)
print(f"  Found {len(existing)} existing Details rows for {SLUG}")
for r in existing:
    print(f"    {r}")

# Build new Details rows (skip if already exist)
new_detail_rows = [
    # ── rooms: published pricing tiers ──────────────────────────────────────
    [SLUG, 'rooms', 'Day Care (RM/day)',               '200'],
    [SLUG, 'rooms', 'Basic Care (RM/mo)',               'From 3,500'],
    [SLUG, 'rooms', 'Intermediate Care (RM/mo)',        'From 3,800'],
    [SLUG, 'rooms', 'Advanced Care (RM/mo)',            'From 4,300'],
    [SLUG, 'rooms', 'Home-Based Care (RM/mo)',          'From 4,300'],
    [SLUG, 'rooms', 'Pricing source',                   'https://www.familycarecentre.co/services/ — operator-published tiers; final fee depends on care level'],
    [SLUG, 'rooms', 'Total beds',                       '52 (36 CHS Home + 16 MemoryCare Home)'],
    # ── included services ───────────────────────────────────────────────────
    [SLUG, 'included', 'Meals (5/day)',                 'yes'],
    [SLUG, 'included', 'Laundry',                       'yes'],
    [SLUG, 'included', 'Medication management',         'yes'],
    [SLUG, 'included', 'Daily activities',              'yes'],
    [SLUG, 'included', 'Nursing care',                  'yes'],
    # ── staffing ────────────────────────────────────────────────────────────
    [SLUG, 'staffing', 'Staff-to-resident ratio',       '1:6'],
    [SLUG, 'staffing', 'Nursing coverage',              '24/7 (nurses on duty)'],
    [SLUG, 'staffing', 'Doctor visits',                 'Bi-monthly; emergency on-call available'],
    # ── clinical ────────────────────────────────────────────────────────────
    [SLUG, 'clinical', 'Dementia unit',                 'yes — dedicated MemoryCare Home (16 beds)'],
    [SLUG, 'clinical', 'Palliative / end-of-life',      'yes — listed in Advanced Care tier'],
    [SLUG, 'clinical', 'Physiotherapy',                 'yes'],
    [SLUG, 'clinical', 'Occupational therapy',          'yes — Advanced Care tier'],
    [SLUG, 'clinical', 'SmartPeep AI monitoring',       'yes — fall detection, 24/7 alerts, privacy-blurred'],
    # ── policies ────────────────────────────────────────────────────────────
    [SLUG, 'policies', 'Visiting hours',                '11 AM – 5 PM daily (advance WhatsApp booking required)'],
    [SLUG, 'policies', 'Admission process',             '6 steps: fix date, documents, signing, payment, nursing assessment, RTK test'],
    [SLUG, 'policies', 'Photo credits',                 'Facility activity photos courtesy of familycarecentre.co and @fccfamilycarecentre (Instagram)'],
    # ── activities ──────────────────────────────────────────────────────────
    [SLUG, 'activities', 'Organic farm & edible garden', 'yes — produce used in resident meals'],
    [SLUG, 'activities', 'Animal-assisted therapy',       'yes'],
    [SLUG, 'activities', 'Aquatic therapy',               'yes'],
    [SLUG, 'activities', 'Art & craft room',              'yes'],
    [SLUG, 'activities', 'Library',                       'yes — books, movies, interactive materials'],
    [SLUG, 'activities', 'Outdoor walking / birdwatching','yes'],
]

# Filter out rows that already exist
rows_to_add = [
    r for r in new_detail_rows
    if (r[1], r[2]) not in existing_keys
]

if rows_to_add:
    print(f"\nAppending {len(rows_to_add)} new Details rows...")
    append_details_rows(rows_to_add)
    for r in rows_to_add:
        print(f"  + {r[1]} / {r[2]} / {r[3]}")
else:
    print("\nAll Details rows already exist — nothing to append.")

print(f"\n✓ Done. Row {fac_row_idx} ({SLUG}) updated. last_updated = {TODAY}")
