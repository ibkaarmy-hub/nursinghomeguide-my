"""
normalize_rn_24_7.py
Normalise the legacy rn_24_7 column to the strict 2-state spec:
  Confirmed  - positive evidence on file
  Unverified - default / no evidence

Per regulatory-framework.md §9: "Confirm RN-staffing claims against MOH
staffing standards before publishing as a badge." So legacy 'yes'/'Yes'
values from the original scrape (operator marketing) do NOT auto-promote
to 'Confirmed' — they fall back to 'Unverified' until verified by IK or
helper outreach (Phase B).

Pre-normalisation distribution (audited 2026-05-03):
  394 blank
   20 'Yes'
    6 'yes'

Post-normalisation: 420 'Unverified'.

The 26 facilities that previously claimed RN 24/7 are listed below for
Phase B outreach prioritisation:
  EHA Golfview, EHA Lakeview Permas, EHA Parkview Perling (x2),
  Loving Mansion Care Centre, ECON Medicare Taman Perling,
  Woon Ho Family Care Centre, Multicare Nursing Home Johor,
  Genesis Life Care Centre JB, Prestige Residence Care Group,
  Evergreen ElderCare Centre, EHA Sunview Kempas, EHA Elder Care Kluang,
  Gentle Hill Elder Care, Noble Care, Green Acres Elderly Care,
  Lee Nursing, JR Segamat Care Centre, Haywood Senior Living Medini,
  Golden Age Tangkak, Green Acres Home Care, Golden Age Batu Pahat,
  Elderia Care Center, Green Garden Care, FCC Family Care, Jeta Care.

Helper should ask these operators to confirm RN 24/7 coverage as
priority candidates for Tier 1 verification.
"""

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TAB = 'google-sheets-facilities.csv'
TOKEN_FILE = 'token_sheets.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


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
    if 'rn_24_7' not in idx:
        raise SystemExit("'rn_24_7' column missing")

    letter = col_letter(idx['rn_24_7'] + 1)
    n = len(data) - 1  # data rows under header

    # Set every populated row to 'Unverified'. We only touch rows that
    # actually have a title to avoid expanding the data range with
    # 'Unverified' on empty trailing rows.
    body = []
    for r_idx, row in enumerate(data[1:], start=2):
        if not (len(row) > idx['title'] and row[idx['title']].strip()):
            continue
        body.append({
            'range': f"'{TAB}'!{letter}{r_idx}",
            'values': [['Unverified']],
        })

    if not body:
        print("no rows to update")
        return

    # Batch in chunks to avoid request size limits.
    chunk = 200
    for k in range(0, len(body), chunk):
        svc.values().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={'valueInputOption': 'RAW', 'data': body[k:k + chunk]},
        ).execute()

    print(f"normalised rn_24_7 to 'Unverified' on {len(body)} rows")


if __name__ == '__main__':
    main()
