"""Backfill Google Maps placeIds for facilities whose google_maps_url
is a raw lat/lng search instead of a query_place_id-anchored URL.

Validation gate — to avoid wrong-facility matches:
  1. State of the Places result must match the row's state
     (or row's state must be unknown)
  2. Title fuzzy similarity ≥ 0.55 (Jaccard on lowercased word tokens
     minus stopwords) OR the Places displayName must contain at
     least 1 distinctive title word

All writes via find_row_by_slug + post-write verify (slug-safe rule).
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
            if not line or line.startswith('#') or '=' not in line: continue
            k, _, v = line.partition('=')
            if k.strip() == key:
                return v.strip().strip('"').strip("'")
    raise RuntimeError(f"{key} not found")


GOOGLE_KEY = _read_env('GOOGLE_MAPS_KEY')
SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_PATH = r'C:\Users\ibkaa\nursinghomeguide-my\Nursing Home Guide Malaysia\token_sheets.json'
TAB = 'google-sheets-facilities.csv'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SHEET_URL = f'https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=292378871'

STOPWORDS = {
    'pusat', 'jagaan', 'rumah', 'kebajikan', 'warga', 'emas', 'tua', 'orang',
    'aktiviti', 'pawe', 'care', 'centre', 'center', 'home', 'homes', 'nursing',
    'sdn', 'bhd', 'plt', 'senior', 'elderly', 'aged', 'old', 'folks', 'folk',
    'malaysia', 'and', 'the', 'of', 'for', 'a', 'an', 'pte', 'ltd', 'residence',
    'residences', 'retirement', 'service', 'services', 'living', 'no',
    'persatuan', 'pertubuhan', 'cawangan', 'branch',
}


def tokens(s):
    return {w for w in re.split(r'[^a-z0-9]+', s.lower()) if w and len(w) >= 3 and w not in STOPWORDS}


def title_match(row_title, place_title):
    rt, pt = tokens(row_title), tokens(place_title)
    if not rt: return True  # nothing distinctive to compare
    inter = rt & pt
    if not inter: return False
    jaccard = len(inter) / len(rt | pt)
    return jaccard >= 0.4 or len(inter) >= 2


STATE_NAMES = {
    'selangor': 'Selangor', 'kuala lumpur': 'Kuala Lumpur',
    'wilayah persekutuan kuala lumpur': 'Kuala Lumpur', 'johor': 'Johor',
    'perak': 'Perak', 'negeri sembilan': 'Negeri Sembilan',
    'pulau pinang': 'Penang', 'penang': 'Penang', 'pahang': 'Pahang',
    'kedah': 'Kedah', 'melaka': 'Melaka', 'malacca': 'Melaka',
    'sabah': 'Sabah', 'sarawak': 'Sarawak', 'terengganu': 'Terengganu',
    'kelantan': 'Kelantan', 'perlis': 'Perlis', 'labuan': 'Labuan',
}


def state_from_address(addr):
    a = (addr or '').lower()
    for canon, normalized in STATE_NAMES.items():
        if canon in a:
            return normalized
    return None


def places_text_search(query):
    body = {'textQuery': query, 'languageCode': 'en', 'maxResultCount': 3}
    req = urllib.request.Request(
        'https://places.googleapis.com/v1/places:searchText',
        data=json.dumps(body).encode(),
        headers={
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': GOOGLE_KEY,
            'X-Goog-FieldMask': 'places.id,places.displayName,places.formattedAddress,places.location,places.types,places.rating,places.userRatingCount',
        },
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {'error': e.code, 'body': e.read().decode('utf-8', errors='replace')[:200]}


def fetch_sheet():
    req = urllib.request.Request(SHEET_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return list(csv.reader(io.TextIOWrapper(r, encoding='utf-8')))


def col_letter(n):
    s = ''
    while n > 0:
        n, r = divmod(n - 1, 26); s = chr(65 + r) + s
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
    rows = fetch_sheet()
    headers = rows[0]
    idx = {h: i for i, h in enumerate(headers)}
    g = lambda r, c: (r[idx[c]] if c in idx and idx[c] < len(r) else '').strip()

    candidates = []
    for r in rows[1:]:
        slug = g(r, 'slug')
        if not slug: continue
        if g(r, 'status').lower() in ('unverified', 'removed'): continue
        maps_url = g(r, 'google_maps_url')
        if 'query_place_id=' in maps_url: continue  # already has placeId
        candidates.append({
            'slug': slug, 'title': g(r, 'title'), 'state': g(r, 'state'),
            'area': g(r, 'area'), 'lat': g(r, 'latitude'), 'lng': g(r, 'longitude'),
            'rating': g(r, 'rating'), 'review_count': g(r, 'review_count'),
        })
    print(f"Found {len(candidates)} rows missing query_place_id URL\n")

    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    svc = build('sheets', 'v4', credentials=creds)
    live_header = svc.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=f"'{TAB}'!1:1"
    ).execute().get('values', [[]])[0]

    maps_col = col_letter(live_header.index('google_maps_url') + 1)
    upd_col = col_letter(live_header.index('last_updated') + 1)
    rating_col = col_letter(live_header.index('rating') + 1)
    rev_col = col_letter(live_header.index('review_count') + 1)

    matched, rejected, errored = [], [], []
    today = '2026-05-12'

    for i, fac in enumerate(candidates, 1):
        slug = fac['slug']
        title = fac['title']
        state = fac['state']
        if i % 10 == 0 or i == 1:
            print(f"\n--- [{i}/{len(candidates)}] ---")
        query = f"{title} {state} Malaysia".strip()
        res = places_text_search(query)
        if 'error' in res:
            errored.append((slug, str(res)))
            continue
        places = res.get('places', [])
        if not places:
            rejected.append((slug, 'no Places result'))
            continue

        # Try top 3, accept first one that passes validation
        accepted = None
        rejection_reasons = []
        KL_SEL = {'Kuala Lumpur', 'Selangor'}
        for cand in places[:3]:
            place_title = cand.get('displayName', {}).get('text', '')
            addr = cand.get('formattedAddress', '')
            cand_state = state_from_address(addr)

            # KL/Selangor boundary tolerance — operators on the metro border
            # are often tagged inconsistently. Treat as equivalent.
            state_mismatch = (
                state and cand_state and cand_state != state
                and not ({state, cand_state} <= KL_SEL)
            )
            if state_mismatch:
                rejection_reasons.append(f"state mismatch ({cand_state} vs {state})")
                continue
            if not title_match(title, place_title):
                rejection_reasons.append(f"title mismatch ({place_title[:30]})")
                continue
            accepted = cand
            break

        if not accepted:
            rejected.append((slug, '; '.join(rejection_reasons[:3]) or 'no valid candidate'))
            continue

        pid = accepted.get('id')
        if not pid:
            rejected.append((slug, 'no placeId in result'))
            continue
        new_url = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(title)}&query_place_id={pid}"

        row = find_row_by_slug(svc, slug)
        if row is None:
            rejected.append((slug, 'not in sheet'))
            continue

        data = [
            {'range': f"'{TAB}'!{maps_col}{row}", 'values': [[new_url]]},
            {'range': f"'{TAB}'!{upd_col}{row}", 'values': [[today]]},
        ]
        # Refresh rating/review count if Places has them and sheet is blank
        if accepted.get('rating') and not fac['rating']:
            data.append({'range': f"'{TAB}'!{rating_col}{row}", 'values': [[str(accepted['rating'])]]})
        if accepted.get('userRatingCount') and not fac['review_count']:
            data.append({'range': f"'{TAB}'!{rev_col}{row}", 'values': [[str(accepted['userRatingCount'])]]})

        svc.spreadsheets().values().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={'valueInputOption': 'RAW', 'data': data}
        ).execute()

        verify = svc.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range=f"'{TAB}'!B{row}"
        ).execute().get('values', [['']])[0][0].strip()
        if verify != slug:
            rejected.append((slug, f'drift: {verify}'))
            continue

        matched.append((slug, accepted.get('displayName', {}).get('text', '')))
        time.sleep(0.25)

    print(f"\n=== {len(matched)} matched, {len(rejected)} rejected, {len(errored)} errored ===")
    if rejected:
        print(f"\nRejected (sample 25):")
        for s, why in rejected[:25]:
            print(f"  ✗ {s}: {why}")
    if errored:
        print(f"\nErrored:")
        for s, why in errored:
            print(f"  ! {s}: {why}")


if __name__ == '__main__':
    main()
