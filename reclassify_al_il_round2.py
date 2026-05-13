"""Reclassify 9 facilities where editorial lists Independent Living or
Assisted Living as a service but care_types didn't reflect it.

User rule:
  - "Independent living" listed as a service → also Assisted Living
  - "24-hour" or "overnight" residential → also Nursing Home
  - Both → Mixed NH+AL (+ DC if also listed)

Mixed (NH+AL+DC) — stay in /nursing-homes/ but care_types now reflects AL/DC:
  d-palace-care-centre
  starshine-care-centre
  moon-care-centre-sdn-bhd-cawangan-kedua
  pusat-jagaan-kanaan-nursing-home
  bidadari-retreat-care-centre

Move to /assisted-living/ (no 24h or NH service in editorial body):
  aim-health-care-centre                                Assisted Living + Day Care
  ara-woods-senior-care-centre                          Assisted Living + Day Care
  takahashi-legend-care-centre                          Assisted Living
  pusat-jagaan-persatuan-penjagaan-kebajikan-sherun     Assisted Living
"""

import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SS = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN = r'C:\Users\ibkaa\nursinghomeguide-my\Nursing Home Guide Malaysia\token_sheets.json'
TAB = 'google-sheets-facilities.csv'

FIXES = [
    ('d-palace-care-centre', 'Nursing Home + Assisted Living + Day Care'),
    ('starshine-care-centre', 'Nursing Home + Assisted Living + Day Care'),
    ('moon-care-centre-sdn-bhd-cawangan-kedua', 'Nursing Home + Assisted Living + Day Care'),
    ('pusat-jagaan-kanaan-nursing-home', 'Nursing Home + Assisted Living + Day Care'),
    ('bidadari-retreat-care-centre', 'Nursing Home + Assisted Living + Day Care'),
    ('aim-health-care-centre', 'Assisted Living + Day Care'),
    ('ara-woods-senior-care-centre', 'Assisted Living + Day Care'),
    ('takahashi-legend-care-centre', 'Assisted Living'),
    ('pusat-jagaan-persatuan-penjagaan-kebajikan-sherun', 'Assisted Living'),
]


def cl(n):
    s = ''
    while n > 0: n, r = divmod(n - 1, 26); s = chr(65 + r) + s
    return s


def find_row(svc, slug):
    rs = svc.spreadsheets().values().get(spreadsheetId=SS, range=f"'{TAB}'!B:B").execute().get('values', [])
    for i, r in enumerate(rs, 1):
        if r and r[0].strip() == slug:
            return i
    return None


def main():
    creds = Credentials.from_authorized_user_file(TOKEN, ['https://www.googleapis.com/auth/spreadsheets'])
    svc = build('sheets', 'v4', credentials=creds)
    hdr = svc.spreadsheets().values().get(spreadsheetId=SS, range=f"'{TAB}'!1:1").execute()['values'][0]
    ct = cl(hdr.index('care_types') + 1)
    upd = cl(hdr.index('last_updated') + 1)

    done = drifted = 0
    for slug, new in FIXES:
        row = find_row(svc, slug)
        if row is None:
            print(f"  ✗ NOT FOUND: {slug}")
            continue
        svc.spreadsheets().values().batchUpdate(
            spreadsheetId=SS,
            body={'valueInputOption': 'RAW', 'data': [
                {'range': f"'{TAB}'!{ct}{row}", 'values': [[new]]},
                {'range': f"'{TAB}'!{upd}{row}", 'values': [['2026-05-13']]},
            ]}
        ).execute()
        v = svc.spreadsheets().values().get(spreadsheetId=SS, range=f"'{TAB}'!B{row}").execute()['values'][0][0].strip()
        if v != slug:
            print(f"  ⚠ DRIFT row {row}: expected {slug}, got {v}")
            drifted += 1
            continue
        done += 1
        print(f"  ✓ row {row}: {slug} → {new}")
        time.sleep(2.5)
    print(f"\nDone. {done} written, {drifted} drift.")


if __name__ == '__main__':
    main()
