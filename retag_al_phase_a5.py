"""
retag_al_phase_a5.py
Phase A.5: re-tag existing facilities with service_type values for the
upcoming /assisted-living/ section, and add Sunway Sanctuary + ReU Living
as hidden (status=unverified) seed AL entries.

Decisions sourced from _research/assisted-living-segment.md §4 and §6
(heuristic table) plus editorial content read from the Sheet on 2026-05-03.

Re-tag list (12 facilities):
  Acacia by Pacific Senior Living           -> assisted_living
  Capella Senior Living                     -> assisted_living
  Komune Care                               -> assisted_living
  Komune Care Senior Day Club               -> assisted_living|day_care
  Sri Seronok Retirement Village            -> assisted_living
  LYC Senior Living Care Center             -> assisted_living
  Haywood Senior Living Bangsar             -> nursing_home|assisted_living
  Haywood Senior Living Medini              -> nursing_home|assisted_living
  Meridian Care Living Centre               -> nursing_home|assisted_living
  Eden retirement village                   -> nursing_home|assisted_living
  Care Luxe Ampang (Care Concierge)         -> nursing_home|assisted_living
  Care Concierge Malaysia                   -> home_care

New entries (added with status=unverified, to be unhidden when an AL
editorial is written in the new voice — see assisted-living-segment.md §5):
  Sunway Sanctuary       -> assisted_living   (Selangor)
  ReU Living KLCC        -> nursing_home|assisted_living  (Kuala Lumpur)
"""

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TAB = 'google-sheets-facilities.csv'
TOKEN_FILE = 'token_sheets.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# (slug substring | title substring) keyed retags. Slug match preferred where unique.
# Use exact slug when possible to avoid mismatching.
RETAGS = [
    # exact title match (case-insensitive)
    ('Acacia by Pacific Senior Living', 'assisted_living'),
    ('Capella Senior Living', 'assisted_living'),
    ('Komune Care', 'assisted_living'),  # exact
    ('Komune Care Senior Day Club', 'assisted_living|day_care'),
    ('Sri Seronok Retirement Village', 'assisted_living'),
    ('LYC Senior Living Care Center', 'assisted_living'),
    ('HAYWOOD SENIOR LIVING @ BANGSAR', 'nursing_home|assisted_living'),
    ('Haywood Senior Living Medini Johor Bahru', 'nursing_home|assisted_living'),
    ('Meridian Care Living Centre', 'nursing_home|assisted_living'),
    ('Eden retirement village', 'nursing_home|assisted_living'),
    ('Care Concierge | Care Luxe Ampang', 'nursing_home|assisted_living'),
    ('Care Concierge Malaysia', 'home_care'),
]

NEW_FACILITIES = [
    {
        'title': 'Sunway Sanctuary',
        'slug': 'sunway-sanctuary',
        'area': 'Sunway City',
        'state': 'Selangor',
        'status': 'unverified',  # hidden until AL editorial is written
        'care_types': 'Assisted living facility',
        'service_type': 'assisted_living',
        'license_category': 'Unverified',
        'verification_tier': '0',
        'last_verified_on': '',
        'verified_by': '',
        'outreach_status': 'pending',
    },
    {
        'title': 'ReU Living',
        'slug': 'reu-living-klcc',
        'area': 'KLCC',
        'state': 'Kuala Lumpur',
        'status': 'unverified',  # hidden until AL editorial is written
        'care_types': 'Assisted living facility, Nursing home',
        'service_type': 'nursing_home|assisted_living',
        'license_category': 'Unverified',
        'verification_tier': '0',
        'last_verified_on': '',
        'verified_by': '',
        'outreach_status': 'pending',
    },
]


def col_letter(n):
    s = ''
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def main():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    svc = build('sheets', 'v4', credentials=creds).spreadsheets()

    data = svc.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{TAB}'",
    ).execute()['values']

    header = data[0]
    idx = {h: i for i, h in enumerate(header)}
    if 'service_type' not in idx:
        raise SystemExit("'service_type' column not present — run add_phase_a_columns.py first.")

    title_col = col_letter(idx['title'] + 1)
    service_col = col_letter(idx['service_type'] + 1)

    # --- 1. Re-tag existing rows ---
    title_to_row = {}
    for r_idx, row in enumerate(data[1:], start=2):
        if len(row) > idx['title'] and row[idx['title']].strip():
            title_to_row[row[idx['title']].strip().lower()] = r_idx

    print("=== Re-tagging existing rows ===")
    retag_updates = []
    for title, value in RETAGS:
        r = title_to_row.get(title.strip().lower())
        if not r:
            print(f"  MISS: {title!r}")
            continue
        retag_updates.append({
            'range': f"'{TAB}'!{service_col}{r}",
            'values': [[value]],
        })
        print(f"  r{r:4} -> {value:40s} | {title}")

    if retag_updates:
        svc.values().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={'valueInputOption': 'RAW', 'data': retag_updates},
        ).execute()
        print(f"applied {len(retag_updates)} re-tags")

    # --- 2. Add new facilities ---
    print("\n=== Adding new AL facilities (hidden) ===")
    new_rows = []
    for fac in NEW_FACILITIES:
        # Build a row sized to the full header, mapping known fields.
        row = [''] * len(header)
        for k, v in fac.items():
            if k in idx:
                row[idx[k]] = v
        # Keep verification defaults blank so the new entries don't claim
        # "Original source scrape" attribution they never had.
        new_rows.append(row)
        print(f"  + {fac['slug']:30s} | {fac['title']} | status={fac['status']}")

    if new_rows:
        svc.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=f"'{TAB}'",
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body={'values': new_rows},
        ).execute()
        print(f"appended {len(new_rows)} new rows (hidden, status=unverified)")

    print("\ndone.")


if __name__ == '__main__':
    main()
