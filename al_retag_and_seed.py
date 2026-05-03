"""
al_retag_and_seed.py
====================
Phase A.5 — assisted-living split

1. Re-tag 5 facilities currently miscategorised (per assisted-living-segment.md §4):
   - komune-care:                Nursing Home → Assisted Living
   - haywood-senior-living-bangsar: Nursing Home → Assisted Living
   - haywood-senior-living-medini-johor-bahru: Day Care → Assisted Living
   - meridian-care-living-centre:   Home Care → Mixed
   - care-concierge-care-luxe-ampang: Nursing Home → Assisted Living

2. Add 2 seed AL facilities not currently in the directory:
   - Sunway Sanctuary (Sunway City, Selangor) → Assisted Living
   - ReU Living (KLCC) → Mixed

(Pacific Senior Living main is intentionally skipped — the assisted-living-segment.md
spec says "verify whether already covered by Acacia entry"; without independent
verification of an additional PSL location it is safer not to invent a row.)

Run: python al_retag_and_seed.py
"""

import io
import os
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Force UTF-8 stdout (Windows console default cp1252 chokes on arrows / em-dash)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
# Token is stored at the repo root, two levels above this worktree
TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'token_sheets.json')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
TAB = 'google-sheets-facilities.csv'
CAT_COL = 'BE'   # care_category column

COL = {
    'title': 0, 'slug': 1, 'url': 2, 'area': 3,
    'phone': 4, 'website': 5,
    'care_types': 9,
    'editorial_summary': 50,   # AY
    'state': 54, 'status': 55,
    'care_category': 56,       # BE
}

RETAGS = {
    'komune-care':                                 'Assisted Living',
    'haywood-senior-living-bangsar':               'Assisted Living',
    'haywood-senior-living-medini-johor-bahru':    'Assisted Living',
    'meridian-care-living-centre':                 'Mixed',
    'care-concierge-care-luxe-ampang':             'Assisted Living',
}

# Editorial voice for AL: lifestyle-led, community character, dining, financial
# model, what happens if care escalates. Verification rigour preserved.
SUNWAY_SANCTUARY_ED = (
    "Sunway Sanctuary is the senior-living arm of Sunway Group's integrated township "
    "in Bandar Sunway, Selangor — a purpose-built community offering hotel-grade "
    "apartments and suites for older adults who want to remain independent while "
    "having medical backup nearby. The community is annexed to Sunway Medical Centre, "
    "which is the practical reason most families consider it: residents have priority "
    "access to one of the country's largest private hospitals without leaving the "
    "compound. Suites are configured for ageing-in-place — wide doorways, level "
    "thresholds, grab rails as standard — and the campus shares amenities with the "
    "wider Sunway township, putting the pyramid mall, monorail, and parks within a "
    "covered walkway. "
    "\n\n"
    "Daily life leans active rather than clinical. Residents have a calendar of group "
    "exercise, art and music programmes, and outings; meals are served in a communal "
    "dining room with dietary options. The community is licensed and openly published "
    "as part of Sunway's healthcare arm, which is unusual transparency for the segment "
    "and helpful for families used to opaque smaller operators. "
    "\n\n"
    "Pricing sits at the premium end of the Klang Valley AL market — expect five-figure "
    "monthly fees with the model evolving (some suites have been offered as memberships "
    "rather than month-to-month rentals), so the financial model is the question to ask "
    "first on a tour. Other call-time questions: what happens if a resident's care "
    "needs escalate beyond AL (does the community have a nursing wing, or is the "
    "transfer path to Sunway Medical and then out), what is and isn't included in the "
    "fee (utilities, meal tiers, additional carer hours), and minimum tenancy."
)

REU_LIVING_ED = (
    "ReU Living is a hybrid senior-living and post-hospitalisation residence on the "
    "edge of KLCC, positioned by its operators as a 'hotel-in-a-hospital' concept. "
    "It serves two adjacent populations under one roof: older adults who want serviced "
    "apartment living with concierge medical support, and patients in the post-acute "
    "window who need structured recovery — typically post-stroke, post-surgical, or "
    "after a chemotherapy cycle — without staying on a hospital ward. The dual-track "
    "model is deliberate, and worth understanding before booking, because it shapes "
    "everything from the staffing pattern to the daily rhythm. "
    "\n\n"
    "Suites are hotel-style with private bathrooms and city views; residents have "
    "access to in-house Traditional Chinese Medicine, physiotherapy, and a doctor on "
    "call. Meals follow tiered dietary plans (Western, Asian, therapeutic) and the "
    "concierge layer covers the small things — laundry, transport to appointments, "
    "guest hosting — that families end up doing themselves at less integrated "
    "communities. The KLCC location is genuinely useful: most major specialists and "
    "private hospitals are within ten minutes, which matters more for the post-"
    "hospitalisation track than the lifestyle one. "
    "\n\n"
    "Pricing is premium, billed monthly, with shorter post-acute stays priced "
    "differently from long-stay residency — confirm both rates and what's bundled. "
    "Useful call-time questions: how is care escalation handled (is there an in-house "
    "nursing capability for higher acuity or is transfer to a partnered hospital the "
    "expected path), what's the actual mix of long-stay vs. short-stay residents on a "
    "typical floor, and how are meal/care additions billed."
)

NEW_FACILITIES = [
    {
        'title': 'Sunway Sanctuary',
        'slug': 'sunway-sanctuary',
        'url': 'https://www.sunwaymedical.com/sunway-sanctuary',
        'area': 'Bandar Sunway',
        'phone': '+60 3-7491 9191',
        'website': 'https://www.sunwaymedical.com/sunway-sanctuary',
        'care_types': 'Assisted Living|Senior Living',
        'editorial_summary': SUNWAY_SANCTUARY_ED,
        'state': 'Selangor',
        'status': '',
        'care_category': 'Assisted Living',
    },
    {
        'title': 'ReU Living',
        'slug': 'reu-living',
        'url': 'https://reuliving.com',
        'area': 'KLCC',
        'phone': '+60 3-2181 8888',
        'website': 'https://reuliving.com',
        'care_types': 'Assisted Living|Post-Hospitalisation|Rehab',
        'editorial_summary': REU_LIVING_ED,
        'state': 'Kuala Lumpur',
        'status': '',
        'care_category': 'Mixed',
    },
]


def make_row(d):
    """Build a 57-cell row in column order."""
    row = [''] * 57
    row[COL['title']]             = d.get('title', '')
    row[COL['slug']]              = d.get('slug', '')
    row[COL['url']]               = d.get('url', '')
    row[COL['area']]              = d.get('area', '')
    row[COL['phone']]             = d.get('phone', '')
    row[COL['website']]           = d.get('website', '')
    row[COL['care_types']]        = d.get('care_types', '')
    row[COL['editorial_summary']] = d.get('editorial_summary', '')
    row[COL['state']]             = d.get('state', '')
    row[COL['status']]            = d.get('status', '')
    row[COL['care_category']]     = d.get('care_category', '')
    return row


def main():
    if not os.path.exists(TOKEN_FILE):
        print(f"ERROR: token file not found at {TOKEN_FILE}", file=sys.stderr)
        sys.exit(1)

    print("Connecting to Google Sheets API...")
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    # ── Step 1: Fetch slug → row index ───────────────────────────────────
    print("Fetching all rows...")
    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{TAB}'!A1:BE"
    ).execute()
    all_rows = result.get('values', [])
    print(f"  {len(all_rows)} rows total (incl. header)")

    slug_to_sheet_row = {}
    for i, row in enumerate(all_rows[1:], start=2):
        if len(row) > COL['slug'] and row[COL['slug']]:
            slug_to_sheet_row[row[COL['slug']].strip()] = i

    # ── Step 2: Re-tag ───────────────────────────────────────────────────
    print(f"\nRe-tagging {len(RETAGS)} facilities...")
    updates = []
    missing = []
    for slug, new_cat in RETAGS.items():
        if slug not in slug_to_sheet_row:
            missing.append(slug)
            continue
        sheet_row = slug_to_sheet_row[slug]
        # Read current value
        cur_row = all_rows[sheet_row - 1]
        cur_cat = cur_row[COL['care_category']] if len(cur_row) > COL['care_category'] else ''
        print(f"  {slug:<48s}  {cur_cat or '(blank)':<15s} → {new_cat}")
        updates.append({
            'range': f"'{TAB}'!{CAT_COL}{sheet_row}",
            'values': [[new_cat]],
        })

    if missing:
        print(f"  ! WARNING: {len(missing)} slugs not found in sheet:", file=sys.stderr)
        for s in missing:
            print(f"    {s}", file=sys.stderr)

    if updates:
        sheet.values().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={'valueInputOption': 'RAW', 'data': updates},
        ).execute()
        print(f"  Re-tag write OK ({len(updates)} rows).")

    # ── Step 3: Append seed facilities (skip if slug already exists) ─────
    print(f"\nAdding {len(NEW_FACILITIES)} seed AL facilities...")
    rows_to_append = []
    for f in NEW_FACILITIES:
        if f['slug'] in slug_to_sheet_row:
            print(f"  ! skip {f['slug']} — already in sheet (row {slug_to_sheet_row[f['slug']]})")
            continue
        rows_to_append.append(make_row(f))
        print(f"  + [{f['care_category']}] {f['title']} ({f['state']})")

    if rows_to_append:
        resp = sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=f"'{TAB}'!A1",
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body={'values': rows_to_append},
        ).execute()
        appended = resp.get('updates', {}).get('updatedRows', 0)
        print(f"  Appended {appended} rows.")

    print("\nDone.")


if __name__ == '__main__':
    main()
