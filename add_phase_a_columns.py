"""
add_phase_a_columns.py
Add Phase A schema columns to the Facilities tab. Idempotent — re-running
skips columns that already exist. Backfills defaults for existing data rows.

Spec: _research/phase-a-schema-upgrade.md
"""

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TAB = 'google-sheets-facilities.csv'  # gid 292378871
TOKEN_FILE = 'token_sheets.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

NEW_COLUMNS = [
    ('service_type', 'nursing_home'),
    ('license_category', 'Unverified'),
    ('license_number', ''),
    ('license_verification_date', ''),
    ('license_expiry', ''),
    ('license_expiry_warning', 'FALSE'),
    ('acuity_level', ''),
    ('rn_24_7', 'Unverified'),
    ('nurse_in_charge', 'Unverified'),
    ('doctor_visit_frequency', 'Unverified'),
    ('pricing_model', 'Unverified'),
    ('hidden_costs', ''),
    ('sg_transfer_ready', 'Unverified'),
    ('verification_tier', '1'),
    ('last_verified_on', '2026-01-01'),
    ('verified_by', 'Original source scrape'),
    ('evidence_ref', ''),
    ('outreach_status', 'pending'),
    ('outreach_last_attempt', ''),
    ('outreach_notes', ''),
    ('tier_2_review_pending', 'FALSE'),
]


def col_letter(n):
    """1 -> A, 27 -> AA, etc."""
    s = ''
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def main():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    svc = build('sheets', 'v4', credentials=creds).spreadsheets()

    # 1. Read header row + slug column to count actual data rows.
    header = svc.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{TAB}'!1:1",
    ).execute().get('values', [[]])[0]
    existing = set(h.strip() for h in header if h.strip())

    # Find slug column to count real data rows (rather than the 1292 grid rows).
    if 'slug' not in existing:
        raise SystemExit("Couldn't find 'slug' column in header row — aborting.")
    slug_col = col_letter(header.index('slug') + 1)
    slug_vals = svc.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{TAB}'!{slug_col}2:{slug_col}",
    ).execute().get('values', [])
    n_data_rows = sum(1 for r in slug_vals if r and r[0].strip())
    print(f"existing columns: {len(header)}  data rows (with slug): {n_data_rows}")

    # Expand the grid if we don't have room for all new columns.
    needed_cols = len(header) + sum(1 for c, _ in NEW_COLUMNS if c not in existing)
    meta = svc.get(
        spreadsheetId=SPREADSHEET_ID,
        fields='sheets(properties(title,sheetId,gridProperties))',
    ).execute()
    sheet_id = next(s['properties']['sheetId'] for s in meta['sheets']
                    if s['properties']['title'] == TAB)
    current_cols = next(s['properties']['gridProperties']['columnCount']
                        for s in meta['sheets'] if s['properties']['title'] == TAB)
    if current_cols < needed_cols:
        svc.batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={'requests': [{
                'appendDimension': {
                    'sheetId': sheet_id,
                    'dimension': 'COLUMNS',
                    'length': needed_cols - current_cols,
                }
            }]},
        ).execute()
        print(f"expanded grid: {current_cols} -> {needed_cols} columns")

    next_col_idx = len(header) + 1
    added = []
    skipped = []

    for col_name, default in NEW_COLUMNS:
        if col_name in existing:
            skipped.append(col_name)
            continue

        letter = col_letter(next_col_idx)
        # Write header.
        svc.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=f"'{TAB}'!{letter}1",
            valueInputOption='RAW',
            body={'values': [[col_name]]},
        ).execute()

        # Backfill default for every existing data row.
        if default and n_data_rows > 0:
            svc.values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=f"'{TAB}'!{letter}2:{letter}{n_data_rows + 1}",
                valueInputOption='RAW',
                body={'values': [[default]] * n_data_rows},
            ).execute()

        added.append(col_name)
        next_col_idx += 1
        print(f"  added: {col_name:30s} default={default!r}")

    print(f"\ndone. added={len(added)}  skipped={len(skipped)}")
    if skipped:
        print(f"skipped (already existed): {', '.join(skipped)}")


if __name__ == '__main__':
    main()
