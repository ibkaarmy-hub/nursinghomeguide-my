"""Fetch photos via Google Places API for facilities missing them, then
update sheet using the safe find_row_by_slug pattern.

Inputs: live sheet (Facilities tab).
For each live facility with empty `hero_image`:
  1. Use existing google_maps_url placeId if available; otherwise text-search.
  2. Call Place Details (fields: photos) → photo names.
  3. Resolve each photo via /media?skipHttpRedirect=true → photoUri (CDN URL).
  4. Take up to 10 photos. hero_image = first; photos = pipe-separated.
  5. Batch-update sheet (editorial_summary untouched).
"""

import sys, io, json, re, time, urllib.request, urllib.parse, csv
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

GOOGLE_KEY = 'AIzaSyByxYJcVmaRaqcKevouJX0QdK7VETV_9fg'
SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_PATH = r'C:\Users\ibkaa\nursinghomeguide-my\Nursing Home Guide Malaysia\token_sheets.json'
TAB = 'google-sheets-facilities.csv'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SHEET_URL = f'https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=292378871'

MAX_PHOTOS = 10
PHOTO_WIDTH = 1600


def col_letter(n):
    s = ''
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def find_row_by_slug(svc, slug):
    col_b = svc.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{TAB}'!B:B"
    ).execute().get('values', [])
    for i, row in enumerate(col_b, start=1):
        if row and row[0].strip() == slug:
            return i
    return None


def extract_placeid_from_url(url):
    m = re.search(r'query_place_id=([^&]+)', url or '')
    return m.group(1) if m else None


def places_text_search(query):
    body = {'textQuery': query, 'languageCode': 'en', 'maxResultCount': 3}
    req = urllib.request.Request(
        'https://places.googleapis.com/v1/places:searchText',
        data=json.dumps(body).encode(),
        headers={
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': GOOGLE_KEY,
            'X-Goog-FieldMask': 'places.id,places.displayName,places.formattedAddress,places.types',
        },
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {'error': e.code, 'body': e.read().decode('utf-8', errors='replace')}


def place_photos(place_id):
    url = f'https://places.googleapis.com/v1/places/{place_id}'
    req = urllib.request.Request(url, headers={
        'X-Goog-Api-Key': GOOGLE_KEY,
        'X-Goog-FieldMask': 'photos',
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read()).get('photos', [])
    except urllib.error.HTTPError as e:
        print(f"    place_photos error: {e.code} {e.read().decode('utf-8', errors='replace')[:200]}")
        return []


def resolve_photo_uri(photo_name):
    media_url = f'https://places.googleapis.com/v1/{photo_name}/media?maxWidthPx={PHOTO_WIDTH}&skipHttpRedirect=true'
    req = urllib.request.Request(media_url, headers={'X-Goog-Api-Key': GOOGLE_KEY})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read()).get('photoUri')
    except urllib.error.HTTPError as e:
        return None


def fetch_sheet():
    req = urllib.request.Request(SHEET_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return list(csv.reader(io.TextIOWrapper(r, encoding='utf-8')))


def main():
    print("Loading live sheet...")
    rows = fetch_sheet()
    headers = rows[0]
    idx = {h: i for i, h in enumerate(headers)}

    def g(row, col):
        i = idx.get(col)
        return (row[i] if i is not None and i < len(row) else '').strip()

    # Collect candidates with no hero_image
    candidates = []
    for r in rows[1:]:
        slug = g(r, 'slug')
        if not slug:
            continue
        if g(r, 'status').lower() in ('unverified', 'removed'):
            continue
        if g(r, 'hero_image'):
            continue
        candidates.append({
            'slug': slug,
            'title': g(r, 'title'),
            'state': g(r, 'state'),
            'maps_url': g(r, 'google_maps_url'),
        })

    print(f"Found {len(candidates)} facilities missing photos\n")

    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    svc = build('sheets', 'v4', credentials=creds)
    live_header = svc.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{TAB}'!1:1"
    ).execute().get('values', [[]])[0]
    hero_col = col_letter(live_header.index('hero_image') + 1)
    photos_col = col_letter(live_header.index('photos') + 1)
    count_col = col_letter(live_header.index('photo_count') + 1)
    upd_col = col_letter(live_header.index('last_updated') + 1)
    maps_col = col_letter(live_header.index('google_maps_url') + 1)

    done, skipped, drifted = [], [], []
    today = '2026-05-12'

    for i, fac in enumerate(candidates, start=1):
        slug = fac['slug']
        title = fac['title']
        state = fac['state']
        print(f"[{i}/{len(candidates)}] {slug} ({state})")

        # Step 1: get a placeId
        pid = extract_placeid_from_url(fac['maps_url'])
        new_maps_url = None
        if not pid:
            # Text-search
            q = f"{title} {state} Malaysia"
            search = places_text_search(q)
            if 'error' in search:
                print(f"    search error: {search}")
                skipped.append((slug, 'search error'))
                continue
            places = search.get('places', [])
            if not places:
                print(f"    no search results")
                skipped.append((slug, 'no Places match'))
                continue
            top = places[0]
            pid = top.get('id')
            new_maps_url = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(title)}&query_place_id={pid}"
            print(f"    resolved placeId via search: {pid}")

        # Step 2: get photo refs
        photos = place_photos(pid)
        if not photos:
            print(f"    no photos for placeId {pid}")
            skipped.append((slug, 'no photos on Maps'))
            continue
        print(f"    {len(photos)} photos available")

        # Step 3: resolve photo URIs
        uris = []
        for ph in photos[:MAX_PHOTOS]:
            name = ph.get('name')
            if not name:
                continue
            uri = resolve_photo_uri(name)
            if uri:
                uris.append(uri)
            time.sleep(0.05)
        if not uris:
            print(f"    all photo resolutions failed")
            skipped.append((slug, 'photo resolution failed'))
            continue

        # Step 4: write to sheet (safe slug lookup + post-write verify)
        row = find_row_by_slug(svc, slug)
        if row is None:
            print(f"    NOT FOUND in sheet")
            skipped.append((slug, 'not in sheet'))
            continue

        data = [
            {'range': f"'{TAB}'!{hero_col}{row}", 'values': [[uris[0]]]},
            {'range': f"'{TAB}'!{photos_col}{row}", 'values': [['|'.join(uris)]]},
            {'range': f"'{TAB}'!{count_col}{row}", 'values': [[str(len(uris))]]},
            {'range': f"'{TAB}'!{upd_col}{row}", 'values': [[today]]},
        ]
        if new_maps_url:
            data.append({'range': f"'{TAB}'!{maps_col}{row}", 'values': [[new_maps_url]]})

        svc.spreadsheets().values().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={'valueInputOption': 'RAW', 'data': data}
        ).execute()

        verify = svc.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"'{TAB}'!B{row}"
        ).execute().get('values', [['']])[0][0].strip()
        if verify != slug:
            print(f"    ⚠ ROW DRIFT row {row}: expected {slug}, got {verify}")
            drifted.append((row, slug, verify))
            continue

        done.append((slug, len(uris)))
        print(f"    wrote {len(uris)} photos to row {row}")
        time.sleep(0.4)

    print(f"\nDone. {len(done)} written, {len(skipped)} skipped, {len(drifted)} drifted.")
    if skipped:
        print("\nSkipped:")
        for s, reason in skipped:
            print(f"  {s}: {reason}")
    if drifted:
        print("\nDrifted (NOT written):")
        for r, want, got in drifted:
            print(f"  row {r}: expected {want}, got {got}")


if __name__ == '__main__':
    main()
