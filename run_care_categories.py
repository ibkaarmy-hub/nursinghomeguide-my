"""
run_care_categories.py
======================
1. Adds 'care_category' header to column BE of the Facilities sheet
2. Classifies every existing row (Nursing Home / Home Care / Day Care /
   Assisted Living / Mixed) and writes to BE
3. Appends 7 new anchor home-care / day-care provider rows

Run: py run_care_categories.py
"""

import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE     = 'token_sheets.json'
SCOPES         = ['https://www.googleapis.com/auth/spreadsheets']
TAB            = 'google-sheets-facilities.csv'
CAT_COL        = 'BE'   # column 57 — new care_category column

# ── Column indices (0-based) from the header row ─────────────────────────
COL = {
    'title':      0,   # A
    'slug':       1,   # B
    'url':        2,   # C
    'area':       3,   # D
    'phone':      4,   # E
    'website':    5,   # F
    'care_types': 9,   # J
    'state':      54,  # BC
    'status':     55,  # BD
}

# ── Known home-care slugs (non-residential) ───────────────────────────────
HOME_CARE_SLUGS = {
    "serim-home-nursing",
    "sam-wound-and-home-nursing-care",
    "aurora-home-care-centre",
    "cality-care-malaysia",
    "caregiver-in-kl",
    "sunway-home-healthcare",
    "aliz-nursing-care",
    "pusat-jagaan-nurul-jannah",
    "dr-teo-keng-huat-home-care",
    "dynamic-home-care-james",
    "rebina-home-care-centre-sdn-bhd",
}

# ── Known day-care-only slugs ─────────────────────────────────────────────
DAY_CARE_SLUGS = {
    "amitabha-foundation-amitabha-malaysia",
    "pusat-jagaan-harian-warga-tua-cheras-baru",
    "pusat-jagaan-harian-warga-tua-kluang",
}


def classify(slug, title, care_types):
    s = slug.lower().strip()
    t = title.lower()
    c = care_types.lower()

    # Hard-coded known slugs first
    if s in HOME_CARE_SLUGS or any(s.startswith(k) for k in HOME_CARE_SLUGS):
        return "Home Care"
    if s in DAY_CARE_SLUGS:
        return "Day Care"

    # care_types field
    has_nh        = "nursing home" in c or "rumah jagaan" in c
    has_day       = "day care" in c or "adult day care" in c or "pusat jagaan harian" in c
    has_home      = ("home care" in c or "home health care" in c or
                     "home nursing" in c or "nursing agency" in c)
    has_assisted  = "assisted living" in c or ("assisted" in c and not has_nh)
    has_palliative = "palliative" in c

    if has_home and not has_nh:
        return "Home Care"
    if has_day and not has_nh and not has_home:
        return "Day Care"
    if has_assisted and not has_nh:
        return "Assisted Living"
    if has_nh and has_day:
        return "Mixed"
    if has_nh:
        return "Nursing Home"

    # Fallback: default to Nursing Home
    return "Nursing Home"


# ── New provider rows to append ───────────────────────────────────────────
# Order must match sheet columns A..BD (56 cols) then BE = care_category
# Blank strings for columns we don't have data for
def make_row(d):
    """Build a 57-element list matching columns A..BE."""
    row = [''] * 57
    row[COL['title']]      = d.get('title', '')
    row[COL['slug']]       = d.get('slug', '')
    row[COL['area']]       = d.get('area', '')
    row[COL['phone']]      = d.get('phone', '')
    row[COL['website']]    = d.get('website', '')
    row[COL['care_types']] = d.get('care_types', '')
    row[COL['state']]      = d.get('state', '')
    row[COL['status']]     = d.get('status', '')
    row[50]                = d.get('editorial_summary', '')   # AY = editorial_summary
    row[56]                = d.get('care_category', '')       # BE
    return row


NEW_PROVIDERS = [
    {
        "title": "Homage Malaysia",
        "slug": "homage-malaysia",
        "state": "Kuala Lumpur",
        "area": "Kuala Lumpur (Nationwide)",
        "care_types": "Home Care",
        "care_category": "Home Care",
        "phone": "+60 16-299 3863",
        "website": "https://www.homage.com.my",
        "status": "",
        "editorial_summary": (
            "Malaysia's largest professional home care platform, matching families with trained "
            "caregivers and registered nurses for in-home elderly care. Services include personal "
            "care, wound care, post-surgical recovery, dementia support, and palliative home care. "
            "App-based matching with real-time caregiver tracking. Operates in KL, Selangor, Johor, "
            "Penang, Ipoh, Kedah, and Melaka. From RM29-40/hour; monthly packages available."
        ),
    },
    {
        "title": "Care Concierge Malaysia",
        "slug": "care-concierge-malaysia",
        "state": "Selangor",
        "area": "Petaling Jaya",
        "care_types": "Home Care|Palliative",
        "care_category": "Home Care",
        "phone": "+60 3-7660 1803",
        "website": "https://www.mycareconcierge.com",
        "status": "",
        "editorial_summary": (
            "Premium home care provider based in Petaling Jaya offering live-in 24-hour care, "
            "post-stroke rehabilitation packages, palliative home care, and hospital-to-home "
            "transition programmes. Run by nurses and social workers. Covers KL, Selangor, Johor, "
            "Penang, Ipoh, and Melaka. Live-in stroke care from RM10,800/month."
        ),
    },
    {
        "title": "Noble Care Malaysia",
        "slug": "noble-care-malaysia",
        "state": "Kuala Lumpur",
        "area": "Kuala Lumpur",
        "care_types": "Home Care",
        "care_category": "Home Care",
        "phone": "+60 3-7728 2886",
        "website": "https://www.noblecare.com.my",
        "status": "",
        "editorial_summary": (
            "Family-run home care agency established in 2005. Provides trained caregivers and "
            "nurses for elderly care at home across KL, Selangor, Johor, Ipoh, Negeri Sembilan, "
            "and Penang. Services include personal care, companionship, medication reminders, "
            "and nursing procedures."
        ),
    },
    {
        "title": "Pillar Care",
        "slug": "pillar-care",
        "state": "Selangor",
        "area": "Petaling Jaya",
        "care_types": "Home Care|Nursing",
        "care_category": "Home Care",
        "phone": "",
        "website": "https://www.pillarcare.com.my",
        "status": "",
        "editorial_summary": (
            "Doctor-managed home care service based in Petaling Jaya. Structured care packages "
            "combining caregivers, registered nurses, physiotherapists, and occupational therapists "
            "for home-based elderly care. Packages from RM4,600 for 20 days. Covers Klang Valley "
            "and Johor."
        ),
    },
    {
        "title": "WhereWeCare",
        "slug": "whereweare-malaysia",
        "state": "Kuala Lumpur",
        "area": "Kuala Lumpur",
        "care_types": "Home Care|Nursing",
        "care_category": "Home Care",
        "phone": "",
        "website": "https://www.wherewecaremalaysia.com",
        "status": "",
        "editorial_summary": (
            "Home care platform providing certified caregivers and registered nurses for elderly "
            "care at home. Operates in KL, Johor Bahru, Penang, Ipoh, and Melaka. Services "
            "include personal care, medication management, wound care, and companionship."
        ),
    },
    {
        "title": "Komune Care Senior Day Club",
        "slug": "komune-care-cheras",
        "state": "Kuala Lumpur",
        "area": "Cheras",
        "care_types": "Day Care|Assisted Living",
        "care_category": "Day Care",
        "phone": "+60 11-2688 6080",
        "website": "https://www.komunecare.com",
        "status": "",
        "editorial_summary": (
            "Malaysia's largest senior day club in Cheras, KL. The Senior Day Club (RM125/day, "
            "8am-6pm) provides supervised activities, meals, physical exercise, cognitive "
            "stimulation, and health monitoring for mobile seniors. Also offers assisted living "
            "studios from RM6,800/month and independent living from RM2,100/month. Strong "
            "physiotherapy and occupational therapy programming."
        ),
    },
    {
        "title": "Seniora Elderly Day Care Johor Bahru",
        "slug": "seniora-johor-bahru",
        "state": "Johor",
        "area": "Johor Bahru",
        "care_types": "Day Care",
        "care_category": "Day Care",
        "phone": "",
        "website": "https://www.seniora.com.my",
        "status": "",
        "editorial_summary": (
            "Private elderly day care centre with branches in Johor Bahru and Penang. Structured "
            "daily programmes including exercise, cognitive activities, meals, and health "
            "monitoring. Trial day available for RM80. Monthly packages up to RM3,580. Suitable "
            "for mobile seniors with mild to moderate care needs including early-stage dementia. "
            "Seniors return home each evening."
        ),
    },
]


def main():
    print("Connecting to Google Sheets API...")
    creds   = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    sheet   = service.spreadsheets()

    # ── Step 1: Fetch all data ────────────────────────────────────────────
    print("Fetching all rows...")
    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{TAB}'!A1:BD"
    ).execute()
    all_rows = result.get('values', [])
    print(f"  {len(all_rows)} rows (including header)")

    header = all_rows[0]
    data_rows = all_rows[1:]   # rows 2..N (0-indexed here = sheet row 2..N)

    # ── Step 2: Expand the sheet by 1 column then add header in BE1 ────────
    SHEET_ID = 292378871   # sheetId for 'google-sheets-facilities.csv'
    print(f"\nExpanding sheet to 57 columns...")
    service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={'requests': [{'appendDimension': {
            'sheetId':    SHEET_ID,
            'dimension':  'COLUMNS',
            'length':     1
        }}]}
    ).execute()

    print(f"Writing 'care_category' header to {CAT_COL}1...")
    sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{TAB}'!{CAT_COL}1",
        valueInputOption='RAW',
        body={'values': [['care_category']]}
    ).execute()

    # ── Step 3: Classify and write care_category for existing rows ────────
    print("Classifying all rows...")
    updates = []
    counts  = {}

    for i, row in enumerate(data_rows):
        sheet_row = i + 2   # sheet row number (1-indexed, row 1 = header)

        slug       = row[COL['slug']]       if len(row) > COL['slug']       else ''
        title      = row[COL['title']]      if len(row) > COL['title']      else ''
        care_types = row[COL['care_types']] if len(row) > COL['care_types'] else ''

        cat = classify(slug, title, care_types)
        counts[cat] = counts.get(cat, 0) + 1

        updates.append({
            'range':  f"'{TAB}'!{CAT_COL}{sheet_row}",
            'values': [[cat]]
        })

    print(f"  Classification summary:")
    for cat, n in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"    {cat:<20} {n}")

    # Write in batches of 500 to stay within API limits
    BATCH = 500
    total_written = 0
    for start in range(0, len(updates), BATCH):
        chunk = updates[start:start + BATCH]
        body  = {'valueInputOption': 'RAW', 'data': chunk}
        resp  = sheet.values().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body=body
        ).execute()
        total_written += resp.get('totalUpdatedCells', 0)
        print(f"  Wrote rows {start+2}..{start+len(chunk)+1}")

    print(f"  Total cells written: {total_written}")

    # ── Step 4: Append new provider rows ─────────────────────────────────
    print(f"\nAppending {len(NEW_PROVIDERS)} new provider rows...")
    new_rows = [make_row(p) for p in NEW_PROVIDERS]

    resp = sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{TAB}'!A1",
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body={'values': new_rows}
    ).execute()

    appended = resp.get('updates', {}).get('updatedRows', 0)
    print(f"  Appended {appended} rows")

    for p in NEW_PROVIDERS:
        print(f"    + [{p['care_category']:<15}] {p['title']}")

    print("\nDone.")


if __name__ == '__main__':
    main()
