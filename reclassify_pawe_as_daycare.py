"""Reclassify all PAWE (Pusat Aktiviti Warga Emas) facilities as Day Care.

PAWE centres are JKM-administered senior-citizens activity centres — daytime
gathering places for retired seniors, not 24-hour residential nursing homes.
They were all written into the sheet with care_types = 'Elderly Care', which
the static generator routes to /nursing-homes/ by default. Wrong category.

This script:
  1. Finds every live facility whose title contains 'PAWE' or 'Pusat Aktiviti
     Warga Emas' or 'Aktiviti Warga'
  2. Sets care_types = 'Day Care'
  3. Sets care_assisted = 'yes' if currently blank
  4. Clears care_nursing if it was set to 'yes' by the capability filler
     (a PAWE community centre does NOT provide 24-hour nursing care)
  5. Slug-safe writes (find_row_by_slug + post-write verify)
"""

import sys, io, csv, time, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_PATH = r'C:\Users\ibkaa\nursinghomeguide-my\Nursing Home Guide Malaysia\token_sheets.json'
TAB = 'google-sheets-facilities.csv'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SHEET_URL = f'https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=292378871'
TODAY = '2026-05-13'


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


def fetch_sheet():
    req = urllib.request.Request(SHEET_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return list(csv.reader(io.TextIOWrapper(r, encoding='utf-8')))


def main():
    rows = fetch_sheet()
    headers = rows[0]
    idx = {h: i for i, h in enumerate(headers)}
    g = lambda r, c: (r[idx[c]] if c in idx and idx[c] < len(r) else '').strip()

    candidates = []
    for r in rows[1:]:
        slug = g(r, 'slug')
        if not slug: continue
        if g(r, 'status').lower() in ('unverified', 'removed'): continue
        title_l = g(r, 'title').lower()
        # Match: contains 'pawe' OR 'pusat aktiviti warga emas' OR 'aktiviti warga emas'
        if not (
            'pawe' in title_l
            or 'pusat aktiviti warga emas' in title_l
            or 'aktiviti warga emas' in title_l
            or 'pusat  aktiviti warga' in title_l
        ):
            continue
        candidates.append({
            'slug': slug, 'title': g(r, 'title'),
            'state': g(r, 'state'),
            'care_types': g(r, 'care_types'),
            'care_assisted': g(r, 'care_assisted'),
            'care_nursing': g(r, 'care_nursing'),
        })

    print(f"Found {len(candidates)} PAWE facilities to reclassify\n")
    for c in candidates:
        print(f"  {c['slug']:<55} {c['state']:<18} care_types='{c['care_types']}'")

    if '--dry' in sys.argv:
        return

    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    svc = build('sheets', 'v4', credentials=creds)
    live_header = svc.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=f"'{TAB}'!1:1"
    ).execute().get('values', [[]])[0]
    ct_col = col_letter(live_header.index('care_types') + 1)
    ca_col = col_letter(live_header.index('care_assisted') + 1)
    cn_col = col_letter(live_header.index('care_nursing') + 1)
    upd_col = col_letter(live_header.index('last_updated') + 1)

    done, drifted, skipped = 0, 0, 0
    print(f"\nWriting (slug-safe + post-write verify, 2.5s rate limit)...\n")

    for i, c in enumerate(candidates, 1):
        slug = c['slug']
        row = find_row_by_slug(svc, slug)
        if row is None:
            print(f"  ✗ NOT FOUND: {slug}")
            skipped += 1
            continue

        data = [
            {'range': f"'{TAB}'!{ct_col}{row}", 'values': [['Day Care']]},
            {'range': f"'{TAB}'!{upd_col}{row}", 'values': [[TODAY]]},
        ]
        # Set care_assisted=yes if not already
        if c['care_assisted'].lower() not in ('yes', 'true', 'y', '1'):
            data.append({'range': f"'{TAB}'!{ca_col}{row}", 'values': [['yes']]})
        # Clear care_nursing if set — PAWE centres don't provide 24h nursing
        if c['care_nursing'].lower() in ('yes', 'true', 'y', '1'):
            data.append({'range': f"'{TAB}'!{cn_col}{row}", 'values': [['']]})

        svc.spreadsheets().values().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={'valueInputOption': 'RAW', 'data': data}
        ).execute()

        verify = svc.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range=f"'{TAB}'!B{row}"
        ).execute().get('values', [['']])[0][0].strip()
        if verify != slug:
            print(f"  ⚠ DRIFT row {row}: expected {slug}, got {verify}")
            drifted += 1
            continue

        actions = ['care_types=Day Care']
        if c['care_assisted'].lower() not in ('yes', 'true', 'y', '1'):
            actions.append('care_assisted=yes')
        if c['care_nursing'].lower() in ('yes', 'true', 'y', '1'):
            actions.append('cleared care_nursing')
        print(f"  [{i}/{len(candidates)}] {slug} → {', '.join(actions)}")
        done += 1
        time.sleep(2.5)

    print(f"\n=== Done. {done} written, {drifted} drift, {skipped} not-found ===")


if __name__ == '__main__':
    main()
