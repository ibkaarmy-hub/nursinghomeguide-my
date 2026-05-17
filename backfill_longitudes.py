"""
backfill_longitudes.py — repair 188 facility rows where column S (longitude)
was overwritten with editorial prose due to a column-letter bug in two now-
deleted scripts (write_johor_editorials.py, write_kl_sel_editorials.py).

For each affected live row:
  - If google_maps_url contains query_place_id → fetch fresh lat/lng from
    Places Details API (free tier), write longitude to column S.
  - If no place_id → clear column S to empty.

After all writes, re-read column B for affected rows to verify integrity per
the sheet-write rule in CLAUDE.md.

One-off repair script — safe to delete after a successful run.
"""

import csv, io, sys, time, urllib.parse, urllib.request
from pathlib import Path

import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout.reconfigure(encoding='utf-8')

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TAB = 'google-sheets-facilities.csv'
TOKEN_PATH = r'C:\Users\ibkaa\nursinghomeguide-my\Nursing Home Guide Malaysia\token_sheets.json'
ENV_PATH = r'C:\Users\ibkaa\nursinghomeguide-my\Nursing Home Guide Malaysia\.env'

def _read_env(key):
    for line in Path(ENV_PATH).read_text().splitlines():
        if line.startswith(f'{key}='):
            return line.split('=', 1)[1].strip()
    raise RuntimeError(f'{key} missing from .env')

KEY = _read_env('GOOGLE_MAPS_KEY')

MY_LAT_RANGE = (0.0, 8.0)
MY_LNG_RANGE = (99.0, 120.0)

def isnum(x):
    try: float(x); return True
    except: return False

def lat_ok(v):
    try: x = float(v)
    except (ValueError, TypeError): return False
    return MY_LAT_RANGE[0] <= x <= MY_LAT_RANGE[1]

def lng_ok(v):
    try: x = float(v)
    except (ValueError, TypeError): return False
    return MY_LNG_RANGE[0] <= x <= MY_LNG_RANGE[1]

def sheets():
    creds = Credentials.from_authorized_user_file(
        TOKEN_PATH, ['https://www.googleapis.com/auth/spreadsheets']
    )
    return build('sheets', 'v4', credentials=creds)

def fetch_grid():
    svc = sheets()
    data = svc.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{TAB}'!A1:BV900"
    ).execute().get('values', [])
    hdr = data[0]
    return svc, hdr, data

def place_location(place_id):
    r = requests.get(
        f'https://places.googleapis.com/v1/places/{place_id}',
        headers={'X-Goog-Api-Key': KEY, 'X-Goog-FieldMask': 'id,location'},
        timeout=20
    )
    if r.status_code != 200:
        return None, f'http {r.status_code}: {r.text[:120]}'
    loc = r.json().get('location') or {}
    if 'longitude' not in loc:
        return None, 'no location in response'
    return (loc.get('latitude'), loc.get('longitude')), None

def main():
    svc, hdr, data = fetch_grid()
    ci = {h: i for i, h in enumerate(hdr)}
    SLUG, LNG, LAT, GMU, STATUS = ci['slug'], ci['longitude'], ci['latitude'], ci['google_maps_url'], ci['status']

    # Targets: any live row where lng or lat is non-numeric or outside the
    # Malaysia plausible range. (Mainland MY ~[1.0, 7.4] lat, [99.6, 119.4] lng.)
    targets = []  # list of (row_num, slug, place_id_or_None, cur_lat, cur_lng)
    for i, row in enumerate(data[1:], start=2):
        if len(row) <= LNG: continue
        if (row[STATUS] if len(row) > STATUS else '').strip(): continue
        cur_lng = row[LNG].strip() if len(row) > LNG else ''
        cur_lat = row[LAT].strip() if len(row) > LAT else ''
        lng_bad = bool(cur_lng) and not lng_ok(cur_lng)
        lat_bad = bool(cur_lat) and not lat_ok(cur_lat)
        if not (lng_bad or lat_bad):
            continue
        gmu = row[GMU] if len(row) > GMU else ''
        pid = None
        if 'query_place_id=' in gmu:
            pid = gmu.split('query_place_id=')[1].split('&')[0]
        targets.append((i, row[SLUG], pid, cur_lat, cur_lng))

    print(f'Targets: {len(targets)}  (with placeId: {sum(1 for t in targets if t[2])}, without: {sum(1 for t in targets if not t[2])})')

    updates = []  # batchUpdate entries
    fetched = 0; cleared = 0; failed = 0
    for row_num, slug, pid, cur_lat, cur_lng in targets:
        lat_bad = bool(cur_lat) and not lat_ok(cur_lat)
        lng_bad = bool(cur_lng) and not lng_ok(cur_lng)
        if not pid:
            if lng_bad:
                updates.append({'range': f"'{TAB}'!S{row_num}", 'values': [['']]})
            if lat_bad:
                updates.append({'range': f"'{TAB}'!R{row_num}", 'values': [['']]})
            cleared += 1
            print(f'  R{row_num:>3} {slug:50s} → clear (no place_id)')
            continue
        loc, err = place_location(pid)
        if err:
            failed += 1
            print(f'  R{row_num:>3} {slug:50s} → SKIP ({err})')
            continue
        lat, lng = loc
        fetched += 1
        # Overwrite whichever cells are bad with the freshly fetched value.
        if lng_bad or not cur_lng:
            updates.append({'range': f"'{TAB}'!S{row_num}", 'values': [[str(lng)]]})
        if lat_bad or not cur_lat:
            updates.append({'range': f"'{TAB}'!R{row_num}", 'values': [[str(lat)]]})
        print(f'  R{row_num:>3} {slug:50s} → lat={lat}, lng={lng}')
        time.sleep(0.05)

    print(f'\nFetched: {fetched}, Cleared: {cleared}, Failed: {failed}')
    if not updates:
        print('Nothing to write.')
        return

    print(f'\nWriting {len(updates)} cells in batch...')
    svc.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={'valueInputOption': 'RAW', 'data': updates}
    ).execute()
    print('Batch write complete.')

    # Verify slug→row alignment hasn't drifted (sheet-write rule).
    print('\nVerifying column B (slug) for affected rows...')
    affected_rows = sorted({int(u['range'].split('!')[1][1:]) for u in updates})
    ranges = [f"'{TAB}'!B{r}" for r in affected_rows]
    resp = svc.spreadsheets().values().batchGet(
        spreadsheetId=SPREADSHEET_ID, ranges=ranges
    ).execute().get('valueRanges', [])
    expected = {t[0]: t[1] for t in targets}
    drift = 0
    for r, vr in zip(affected_rows, resp):
        got = (vr.get('values') or [['']])[0][0].strip()
        want = expected[r]
        if got != want:
            drift += 1
            print(f'  DRIFT R{r}: expected {want!r}, got {got!r}')
    print(f'Drift detected: {drift} rows')

if __name__ == '__main__':
    main()
