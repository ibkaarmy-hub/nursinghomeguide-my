"""
process_new_mdac_results.py
Fetch Apify Google Maps results for the 82 new MDAC facilities,
match each search result to the correct facility, then update the sheet with:
  rating, review_count, hero_image, photos, photo_count,
  latitude, longitude, google_maps_url, website, area (if improved)

Matching strategy (per search, up to 3 results):
  1. Phone last-8-digit match (strongest)
  2. Name token overlap score (pick highest)
  Falls back to best-name-match if no phone match.

Usage:
  python process_new_mdac_results.py
"""

import json, re, urllib.request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

APIFY_TOKEN    = 'YOUR_APIFY_TOKEN'
SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE     = 'token_sheets.json'
SCOPES         = ['https://www.googleapis.com/auth/spreadsheets']
TAB            = 'google-sheets-facilities.csv'

# ── Load run metadata ─────────────────────────────────────────────────────────

run_meta = json.load(open('run_new_mdac.json'))
run_id   = run_meta['run_id']
ds_id    = run_meta['dataset_id']

# Check status
status_url = f'https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_TOKEN}'
with urllib.request.urlopen(status_url) as r:
    run_data = json.loads(r.read())['data']

status = run_data['status']
print(f"Run status: {status}")
if status not in ('SUCCEEDED', 'FINISHED'):
    print(f"Run not complete yet. Retry when status = SUCCEEDED.")
    exit(1)

# ── Fetch dataset ─────────────────────────────────────────────────────────────

dataset_url = (f'https://api.apify.com/v2/datasets/{ds_id}/items'
               f'?token={APIFY_TOKEN}&format=json&clean=true&limit=2000')
with urllib.request.urlopen(dataset_url) as r:
    items = json.loads(r.read())

print(f"Apify returned {len(items)} place records")

# Group items by searchString (the query that generated them)
by_query = {}
for item in items:
    q = item.get('searchString', '')
    by_query.setdefault(q, []).append(item)

# ── Load our facility list ────────────────────────────────────────────────────

mdac_rows   = list(__import__('csv').DictReader(open('mdac_confirmed_new.csv', encoding='utf-8')))
slug_data   = json.load(open('mdac_added_slugs.json', encoding='utf-8'))
slug_index  = {d['title']: d for d in slug_data}

# Rebuild query → facility mapping (mirrors apify_scrape_new_mdac.py)
def clean_name(raw):
    return re.sub(r'\s*-\s*MYS\s*$', '', raw.strip()).strip()

def make_query(row):
    name  = clean_name(row['name'])
    addr  = row['address'].strip()
    state = row['state_detected']
    if re.search(r'(jalan|taman|lorong|persiaran|lebuh)', addr, re.I):
        return f"{name}, {addr}, Malaysia"
    city_map = {'Johor': 'Johor Bahru', 'Selangor': 'Selangor', 'KL/Selangor': 'Kuala Lumpur'}
    city = city_map.get(state, 'Malaysia')
    return f"{name}, {city}, Malaysia"

seen = set()
facility_by_query = {}
for row in mdac_rows:
    key = (row['name'].strip(), row['phone'].strip())
    if key in seen:
        continue
    seen.add(key)
    q = make_query(row)
    facility_by_query[q] = row

# ── Helper functions ──────────────────────────────────────────────────────────

def norm_phone(phone):
    digits = re.sub(r'\D', '', phone or '')
    return digits[-8:] if len(digits) >= 8 else ''

def norm_name_tokens(name):
    s = name.lower()
    s = re.sub(r'[^a-z0-9\s]', ' ', s)
    stop = {'sdn', 'bhd', 'care', 'home', 'nursing', 'centre', 'center',
            'senior', 'the', 'and', 'for', 'malaysia', 'mys'}
    return set(t for t in s.split() if len(t) >= 3 and t not in stop)

ADDRESS_PAT = re.compile(r'^\d+[,\s]|^jalan|^lorong|^taman|^lot\s', re.I)

def is_address_title(title):
    """True if the GM result title looks like a street address, not a business."""
    return bool(ADDRESS_PAT.match(title.strip()))

def pick_best_result(results, facility_row):
    """Pick the most likely match from up to 3 Apify results."""
    fac_phone = norm_phone(facility_row.get('phone', ''))
    fac_name  = clean_name(facility_row['name'])
    fac_toks  = norm_name_tokens(fac_name)

    # Filter out address-only titles
    valid = [r for r in results if not is_address_title(r.get('title', ''))]

    # Phone match first (from phoneUnformatted field)
    for item in valid:
        ph = item.get('phoneUnformatted', '') or item.get('phone', '') or ''
        if fac_phone and norm_phone(ph) == fac_phone:
            return item, 'phone'

    # Name overlap
    best_item, best_score = None, 0
    for item in valid:
        gm_name  = item.get('title', '')
        gm_toks  = norm_name_tokens(gm_name)
        score    = len(fac_toks & gm_toks)
        if score > best_score:
            best_score, best_item = score, item

    if best_item and best_score >= 2:
        return best_item, f'name ({best_score} tokens)'
    # Don't accept low-confidence matches that look totally wrong
    return None, 'no confident match'


def pipe_photos(photos_list, limit=20):
    """Pipe-separated photo URLs from list of strings or dicts."""
    urls = []
    for p in (photos_list or [])[:limit]:
        if isinstance(p, str):
            urls.append(p)
        elif isinstance(p, dict):
            url = p.get('imageUrl') or p.get('url') or ''
            if url:
                urls.append(url)
    return '|'.join(urls)


# ── Fetch sheet ───────────────────────────────────────────────────────────────

creds   = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
service = build('sheets', 'v4', credentials=creds)
ss      = service.spreadsheets()

data    = ss.values().get(
    spreadsheetId=SPREADSHEET_ID,
    range=f"'{TAB}'"
).execute().get('values', [])

headers  = data[0]
rows     = data[1:]
col      = {h: i for i, h in enumerate(headers)}
# Build slug → row_number index
slug_to_row = {}
for i, row in enumerate(rows):
    sl = row[col['slug']] if col['slug'] < len(row) else ''
    slug_to_row[sl] = i + 2  # 1-based + header

print(f"Sheet rows: {len(rows)}")

# ── Match and build updates ───────────────────────────────────────────────────

updates   = []
no_match  = []
low_conf  = []

for query, fac_row in facility_by_query.items():
    results = by_query.get(query, [])
    item, reason = pick_best_result(results, fac_row)

    fac_title = clean_name(fac_row['name'])
    # Look up slug
    slug_info = slug_index.get(fac_title)
    if not slug_info:
        # Try cleaned match
        for k, v in slug_index.items():
            if k.lower().strip() == fac_title.lower().strip():
                slug_info = v
                break

    if not slug_info:
        print(f"  WARNING: slug not found for '{fac_title}'")
        continue

    slug    = slug_info['slug']
    row_num = slug_to_row.get(slug)
    if not row_num:
        print(f"  WARNING: row not found for slug '{slug}'")
        continue

    if item is None:
        no_match.append(fac_title)
        continue

    if 'low confidence' in reason:
        low_conf.append((fac_title, item.get('title', ''), reason))

    # Extract fields from Apify result
    rating       = str(item.get('totalScore', '') or '')
    review_count = str(item.get('reviewsCount', '') or '')
    lat          = str((item.get('location') or {}).get('lat', '') or '')
    lng          = str((item.get('location') or {}).get('lng', '') or '')
    gm_url       = item.get('url', '') or ''
    website      = item.get('website', '') or ''
    # Photos: imageUrl = single hero; imageUrls = list of strings
    hero         = item.get('imageUrl', '') or ''
    photos_list  = item.get('imageUrls') or []
    photos_str   = pipe_photos(photos_list)
    photo_count  = str(len(photos_list)) if photos_list else ''

    # Neighbourhood for area improvement
    gm_area = (item.get('neighborhood') or
               item.get('subLocality') or
               item.get('city') or '')

    def cell(col_name, value):
        if not value:
            return None
        c = col.get(col_name)
        if c is None:
            return None
        col_letter = chr(64 + c + 1)
        return {
            'range': f"'{TAB}'!{col_letter}{row_num}",
            'values': [[value]]
        }

    for upd in [
        cell('rating',       rating),
        cell('review_count', review_count),
        cell('latitude',     lat),
        cell('longitude',    lng),
        cell('google_maps_url', gm_url),
        cell('website',      website),
        cell('hero_image',   hero),
        cell('photos',       photos_str),
        cell('photo_count',  photo_count),
        cell('area',         gm_area),
    ]:
        if upd:
            updates.append(upd)

# ── Report ────────────────────────────────────────────────────────────────────

print(f"\nResults:")
print(f"  Cells to update:   {len(updates)}")
print(f"  No Apify result:   {len(no_match)}")
print(f"  Low confidence:    {len(low_conf)}")

if no_match:
    print("\nNo results found for:")
    for t in no_match:
        print(f"  {t}")

if low_conf:
    print("\nLow-confidence matches (verify manually):")
    for fac, gm, reason in low_conf:
        print(f"  Our: {fac[:40]}")
        print(f"  GM:  {gm[:40]} ({reason})")

# ── Upload ────────────────────────────────────────────────────────────────────

if not updates:
    print("\nNothing to update.")
else:
    confirm = input(f"\nUpdate {len(updates)} cells in sheet? [y/N]: ").strip().lower()
    if confirm != 'y':
        print("Aborted.")
        exit()

    CHUNK = 50
    total = 0
    for i in range(0, len(updates), CHUNK):
        chunk = updates[i:i+CHUNK]
        body  = {'valueInputOption': 'RAW', 'data': chunk}
        result = ss.values().batchUpdate(
            spreadsheetId=SPREADSHEET_ID, body=body
        ).execute()
        total += result.get('totalUpdatedCells', 0)
        print(f"  Chunk {i//CHUNK+1}: {result.get('totalUpdatedCells',0)} cells")

    print(f"\nDone. {total} cells updated.")
