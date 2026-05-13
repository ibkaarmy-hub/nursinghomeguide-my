"""Reclassify 6 facilities whose care_types routes them to the wrong category.

Each fix is hand-verified against the editorial text. See commit message
for the reasoning per facility.
"""

import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_PATH = r'C:\Users\ibkaa\nursinghomeguide-my\Nursing Home Guide Malaysia\token_sheets.json'
TAB = 'google-sheets-facilities.csv'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# (slug, new care_types value). Each verified by reading the editorial.
FIXES = [
    ('eden-retirement-village', 'Assisted Living'),
    ('noble-care-retirement-resort', 'Assisted Living'),
    ('sri-seronok-retirement-village', 'Assisted Living'),
    ('pusat-jagaan-harian-chan', 'Day Care'),
    ('pusat-jagaan-harian-pertubuhan-dimensia-pe', 'Day Care'),
    ('sayang-nursing-home-care', 'Home Care'),
]


def col_letter(n):
    s = ''
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def find_row_by_slug(svc, slug):
    col_b = svc.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=f"'{TAB}'!B:B"
    ).execute().get('values', [])
    for i, row in enumerate(col_b, 1):
        if row and row[0].strip() == slug:
            return i
    return None


def main():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    svc = build('sheets', 'v4', credentials=creds)
    hdr = svc.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=f"'{TAB}'!1:1"
    ).execute().get('values', [[]])[0]
    ct_col = col_letter(hdr.index('care_types') + 1)
    upd_col = col_letter(hdr.index('last_updated') + 1)

    print(f"Reclassifying {len(FIXES)} facilities (slug-safe writes, 2.5s rate)...\n")
    done, drifted = 0, 0
    for slug, new_ct in FIXES:
        row = find_row_by_slug(svc, slug)
        if row is None:
            print(f"  ✗ NOT FOUND: {slug}")
            continue
        svc.spreadsheets().values().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={'valueInputOption': 'RAW', 'data': [
                {'range': f"'{TAB}'!{ct_col}{row}", 'values': [[new_ct]]},
                {'range': f"'{TAB}'!{upd_col}{row}", 'values': [['2026-05-13']]},
            ]}
        ).execute()
        verify = svc.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range=f"'{TAB}'!B{row}"
        ).execute().get('values', [['']])[0][0].strip()
        if verify != slug:
            print(f"  ⚠ DRIFT row {row}: expected {slug}, got {verify}")
            drifted += 1
            continue
        done += 1
        print(f"  ✓ row {row}: {slug} → {new_ct}")
        time.sleep(2.5)
    print(f"\nDone. {done} written, {drifted} drift.")


if __name__ == '__main__':
    main()
