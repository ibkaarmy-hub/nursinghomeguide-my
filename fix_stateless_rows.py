"""Fix the 31 facilities with literal '(unknown)' in the state column.

For each row:
  1. If lat/lng exists → decode region from coords (tightened bands)
  2. Else → Places API text search by title; extract state from
     formattedAddress; also capture placeId + address as a bonus.
  3. Write state via find_row_by_slug + post-write verify (slug-safe rule).

State values match the existing convention in the sheet exactly:
'Selangor', 'Kuala Lumpur', 'Johor', 'Perak', 'Negeri Sembilan',
'Penang', 'Pahang', 'Kedah', 'Melaka', 'Sabah', 'Sarawak',
'Terengganu', 'Kelantan', 'Perlis', 'Labuan'.
"""

import sys, io, csv, json, re, time, urllib.request, urllib.parse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

ENV_PATH = r'C:\Users\ibkaa\nursinghomeguide-my\Nursing Home Guide Malaysia\.env'


def _read_env(key):
    with open(ENV_PATH, 'r', encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, _, v = line.partition('=')
            if k.strip() == key:
                return v.strip().strip('"').strip("'")
    raise RuntimeError(f"{key} not found in {ENV_PATH}")


GOOGLE_KEY = _read_env('GOOGLE_MAPS_KEY')
SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_PATH = r'C:\Users\ibkaa\nursinghomeguide-my\Nursing Home Guide Malaysia\token_sheets.json'
TAB = 'google-sheets-facilities.csv'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SHEET_URL = f'https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=292378871'

STATE_NAMES = {
    'selangor', 'kuala lumpur', 'wilayah persekutuan kuala lumpur', 'johor', 'perak',
    'negeri sembilan', 'pulau pinang', 'penang', 'pahang', 'kedah', 'melaka', 'malacca',
    'sabah', 'sarawak', 'terengganu', 'kelantan', 'perlis', 'labuan',
    'wilayah persekutuan labuan', 'putrajaya', 'wilayah persekutuan putrajaya'
}
STATE_NORMALIZE = {
    'pulau pinang': 'Penang',
    'malacca': 'Melaka',
    'wilayah persekutuan kuala lumpur': 'Kuala Lumpur',
    'wilayah persekutuan labuan': 'Labuan',
    'wilayah persekutuan putrajaya': 'Kuala Lumpur',  # treat Putrajaya as KL for site purposes
    'putrajaya': 'Kuala Lumpur',
}


def classify_coords(lat, lng):
    try:
        la = float(lat); ln = float(lng)
    except (ValueError, TypeError):
        return None
    # Tightened bands (some overlaps resolved by checking more specific first)
    if 1.0 <= la <= 7.5 and 109.0 <= ln <= 116.0:
        # East Malaysia
        if 5.5 <= la and 115.0 <= ln <= 116.5: return 'Sabah'
        if 4.0 <= la <= 6.5 and 113.0 <= ln <= 117.0: return 'Sabah'
        return 'Sarawak'
    if 1.2 <= la <= 1.8 and 103.3 <= ln <= 104.5: return 'Johor'
    if 1.8 <= la <= 2.1 and 102.5 <= ln <= 103.3: return 'Johor'  # Batu Pahat region
    if 2.0 <= la <= 2.5 and 102.0 <= ln <= 102.6: return 'Melaka'
    if 2.4 <= la <= 3.0 and 101.6 <= ln <= 102.5: return 'Negeri Sembilan'
    if 3.0 <= la <= 3.4 and 101.3 <= ln <= 101.85: return 'Kuala Lumpur'
    if 2.8 <= la <= 3.5 and 101.0 <= ln <= 101.85: return 'Selangor'
    if 3.5 <= la <= 4.5 and 100.7 <= ln <= 101.85: return 'Perak'
    if 3.8 <= la <= 5.1 and 100.4 <= ln <= 101.3: return 'Perak'
    if 5.2 <= la <= 5.6 and 100.1 <= ln <= 100.5: return 'Penang'
    if 5.5 <= la <= 6.4 and 100.0 <= ln <= 100.8: return 'Kedah'
    if 6.4 <= la <= 6.9 and 100.0 <= ln <= 100.6: return 'Perlis'
    if 3.5 <= la <= 5.0 and 101.7 <= ln <= 103.5: return 'Pahang'
    if 5.5 <= la <= 6.4 and 101.8 <= ln <= 102.6: return 'Kelantan'
    if 4.0 <= la <= 5.8 and 102.6 <= ln <= 103.8: return 'Terengganu'
    return None


def derive_state_from_address(addr):
    """Find a Malaysian state name in a Google formatted-address string."""
    a = (addr or '').lower()
    for canonical in STATE_NAMES:
        if canonical in a:
            return STATE_NORMALIZE.get(canonical, canonical.title() if canonical not in ('johor',) else canonical.title())
    return None


def places_text_search(query):
    body = {'textQuery': query, 'languageCode': 'en', 'maxResultCount': 3}
    req = urllib.request.Request(
        'https://places.googleapis.com/v1/places:searchText',
        data=json.dumps(body).encode(),
        headers={
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': GOOGLE_KEY,
            'X-Goog-FieldMask': 'places.id,places.displayName,places.formattedAddress,places.location,places.types',
        },
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {'error': e.code, 'body': e.read().decode('utf-8', errors='replace')}


def fetch_sheet():
    req = urllib.request.Request(SHEET_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return list(csv.reader(io.TextIOWrapper(r, encoding='utf-8')))


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
    for i, row in enumerate(col_b, start=1):
        if row and row[0].strip() == slug:
            return i
    return None


def main():
    rows = fetch_sheet()
    headers = rows[0]
    idx = {h: i for i, h in enumerate(headers)}
    g = lambda r, c: (r[idx[c]] if c in idx and idx[c] < len(r) else '').strip()

    # Identify (unknown)-state rows
    candidates = []
    for r in rows[1:]:
        slug = g(r, 'slug')
        if not slug: continue
        if g(r, 'status').lower() in ('unverified', 'removed'): continue
        if g(r, 'state') != '(unknown)': continue
        candidates.append({
            'slug': slug,
            'title': g(r, 'title'),
            'lat': g(r, 'latitude'),
            'lng': g(r, 'longitude'),
            'area': g(r, 'area'),
            'maps_url': g(r, 'google_maps_url'),
        })
    print(f"Found {len(candidates)} (unknown)-state rows\n")

    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    svc = build('sheets', 'v4', credentials=creds)
    live_header = svc.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=f"'{TAB}'!1:1"
    ).execute().get('values', [[]])[0]
    state_col = col_letter(live_header.index('state') + 1)
    upd_col = col_letter(live_header.index('last_updated') + 1)
    maps_col = col_letter(live_header.index('google_maps_url') + 1)
    lat_col = col_letter(live_header.index('latitude') + 1)
    lng_col = col_letter(live_header.index('longitude') + 1)
    area_col = col_letter(live_header.index('area') + 1)

    done = []
    skipped = []
    today = '2026-05-12'

    for i, fac in enumerate(candidates, 1):
        slug = fac['slug']
        title = fac['title']
        print(f"\n[{i}/{len(candidates)}] {slug}")
        print(f"  title: {title[:80]}")

        # Path A: classify by coords
        state_guess = classify_coords(fac['lat'], fac['lng'])
        extra_updates = {}

        # Path B: if no coords or no classification, query Places API
        if not state_guess:
            q = title + ' Malaysia'
            print(f"  no coord match — Places search: {q[:60]}")
            res = places_text_search(q)
            if 'error' in res:
                print(f"    search error: {res}")
                skipped.append((slug, 'search error'))
                continue
            places = res.get('places', [])
            if not places:
                print(f"    no Places match")
                skipped.append((slug, 'no Places match'))
                continue
            top = places[0]
            addr = top.get('formattedAddress', '')
            print(f"    match: {top.get('displayName', {}).get('text')} | {addr}")
            state_guess = derive_state_from_address(addr)
            if not state_guess:
                print(f"    couldn't extract state from address")
                skipped.append((slug, 'state not in address'))
                continue
            # Bonus: capture placeId, lat/lng, area
            loc = top.get('location') or {}
            if loc.get('latitude') and not fac['lat']:
                extra_updates['latitude'] = str(loc['latitude'])
                extra_updates['longitude'] = str(loc['longitude'])
            place_id = top.get('id')
            if place_id and 'query_place_id=' not in fac['maps_url']:
                title_enc = urllib.parse.quote(title)
                extra_updates['google_maps_url'] = f"https://www.google.com/maps/search/?api=1&query={title_enc}&query_place_id={place_id}"
            # If area is missing, try to derive (last comma segment minus state/postcode)
            if not fac['area'] and addr:
                parts = [p.strip() for p in addr.split(',')]
                # area = the most specific neighbourhood — typically parts[-3] before postcode+state
                for p in parts[:-1]:
                    if not re.match(r'^\d{5}', p) and p.lower() not in {state_guess.lower(), 'malaysia'}:
                        # Strip leading postcode from a "12345 Locality" pattern
                        cleaned = re.sub(r'^\d{5}\s+', '', p)
                        if cleaned and len(cleaned) <= 40:
                            extra_updates['area'] = cleaned
                            break
        else:
            print(f"  classified by coords: {state_guess}")

        # Resolve target row LIVE
        row = find_row_by_slug(svc, slug)
        if row is None:
            print(f"  NOT FOUND in sheet")
            skipped.append((slug, 'not in sheet'))
            continue

        # Build batch update
        data = [
            {'range': f"'{TAB}'!{state_col}{row}", 'values': [[state_guess]]},
            {'range': f"'{TAB}'!{upd_col}{row}", 'values': [[today]]},
        ]
        for col_name, val in extra_updates.items():
            c = col_letter(live_header.index(col_name) + 1)
            data.append({'range': f"'{TAB}'!{c}{row}", 'values': [[val]]})

        svc.spreadsheets().values().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={'valueInputOption': 'RAW', 'data': data}
        ).execute()

        # Post-write verify (slug-lookup safety)
        verify = svc.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range=f"'{TAB}'!B{row}"
        ).execute().get('values', [['']])[0][0].strip()
        if verify != slug:
            print(f"  ⚠ ROW DRIFT row {row}: expected {slug}, got {verify}")
            skipped.append((slug, f'drift: {verify}'))
            continue

        done.append((slug, state_guess, sorted(extra_updates.keys())))
        print(f"  ✅ wrote row {row}: state={state_guess}, extras={list(extra_updates.keys()) or '-'}")
        time.sleep(0.4)

    print(f"\n=== Done. {len(done)} written, {len(skipped)} skipped ===")
    for s, st, extras in done:
        extra_str = (' + ' + ', '.join(extras)) if extras else ''
        print(f"  ✓ {s} → {st}{extra_str}")
    if skipped:
        print(f"\nSkipped:")
        for s, reason in skipped:
            print(f"  ✗ {s}: {reason}")


if __name__ == '__main__':
    main()
