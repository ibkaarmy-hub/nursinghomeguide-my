"""
enrich_places_free.py — free-tier facility enrichment via Google Places API.

For each live facility in given state:
  1. Text search → placeId, verified address, phone, website, rating, review count
  2. Place Details → up to 5 reviews + photos
  3. Save photos via skipHttpRedirect=true (returns googleusercontent URL)
  4. Batch-write to Sheet:
     - F  website          (only if empty)
     - T  google_maps_url  (with query_place_id, always)
     - P  rating           (always)
     - Q  review_count     (always)
     - U  last_updated     (always)
     - AZ hero_image       (only if empty)
     - BA photos           (only if empty)
     - BB photo_count      (only if empty)
  5. Append Details rows: policies/Address, policies/Photo credits, social/Reviews snippets

Costs $0 — Places API Pro SKU free tier: 5K text searches + 10K details/month.

Usage:
  python enrich_places_free.py Perak
  python enrich_places_free.py Perak --limit 5     # test on a small batch
  python enrich_places_free.py Perak --slug NAME   # one facility
"""
import argparse, csv, io, json, os, re, sys, time, urllib.parse
from pathlib import Path

import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout.reconfigure(encoding='utf-8')

# ─── Constants ───────────────────────────────────────────────────────────────
SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TAB = 'google-sheets-facilities.csv'
DETAILS_TAB = 'Details'
TOKEN_PATH = r'C:\Users\ibkaa\nursinghomeguide-my\Nursing Home Guide Malaysia\token_sheets.json'
ENV_PATH = r'C:\Users\ibkaa\nursinghomeguide-my\Nursing Home Guide Malaysia\.env'
CACHE_DIR = Path('_enrich_cache')
CACHE_DIR.mkdir(exist_ok=True)

LIVE_CSV_URL = (
    'https://docs.google.com/spreadsheets/d/e/'
    '2PACX-1vQ4_BgHIjnlgmITzjyUuGDpgpNzPL7MfjOY2069i0PtbVbXSxIAJk1tmBejwNo8aBBeLuRi62szF2sh'
    '/pub?gid=292378871&single=true&output=csv'
)

def load_key():
    for line in open(ENV_PATH).readlines():
        if line.startswith('GOOGLE_MAPS_KEY='):
            return line.split('=',1)[1].strip()
    raise RuntimeError('GOOGLE_MAPS_KEY missing from .env')

KEY = load_key()
TODAY = time.strftime('%Y-%m-%d')

# Column letters (looked up from sheet headers at runtime)
COL_NEEDED = ['website','google_maps_url','rating','review_count','last_updated',
              'hero_image','photos','photo_count','facebook','whatsapp']

def col_letter(idx):
    """0-based column index → A, B, ..., Z, AA, AB"""
    if idx < 26: return chr(65+idx)
    return chr(64+idx//26) + chr(65+idx%26)

# ─── Sheets helpers ──────────────────────────────────────────────────────────
def sheets():
    creds = Credentials.from_authorized_user_file(
        TOKEN_PATH, ['https://www.googleapis.com/auth/spreadsheets']
    )
    return build('sheets','v4',credentials=creds)

def fetch_state_facilities(state):
    r = requests.get(LIVE_CSV_URL, headers={'User-Agent':'Mozilla/5.0'}, timeout=30)
    rows = list(csv.DictReader(io.StringIO(r.text)))
    # We need row numbers too. The published CSV row index doesn't directly map
    # to sheet row. Pull from Sheets API instead to get authoritative rows.
    svc = sheets()
    data = svc.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{TAB}'!A1:BV900"
    ).execute().get('values',[])
    hdr = data[0]
    ci = {h:i for i,h in enumerate(hdr)}
    results = []
    for i, row in enumerate(data[1:], start=2):
        row += [''] * (len(hdr)-len(row))
        if row[ci['state']].strip() != state: continue
        if row[ci['status']].strip().lower() in ('removed','unverified'): continue
        results.append({
            'sheet_row': i, **{h: row[ci[h]] for h in hdr}
        })
    return results, ci, hdr

# ─── Places API ──────────────────────────────────────────────────────────────
def places_text_search(query, lat=None, lng=None, radius=10000):
    body = {'textQuery': query}
    if lat and lng:
        try:
            body['locationBias'] = {'circle': {
                'center': {'latitude': float(lat), 'longitude': float(lng)},
                'radius': radius,
            }}
        except (ValueError, TypeError):
            pass
    r = requests.post(
        'https://places.googleapis.com/v1/places:searchText',
        headers={
            'Content-Type':'application/json',
            'X-Goog-Api-Key':KEY,
            'X-Goog-FieldMask':'places.id,places.displayName,places.formattedAddress,'
                               'places.websiteUri,places.nationalPhoneNumber,'
                               'places.rating,places.userRatingCount,places.types',
        },
        json=body, timeout=30
    )
    if r.status_code != 200:
        return {'_error': f'http {r.status_code}: {r.text[:200]}'}
    return r.json().get('places', [])

def place_details(place_id):
    r = requests.get(
        f'https://places.googleapis.com/v1/places/{place_id}',
        headers={
            'X-Goog-Api-Key':KEY,
            'X-Goog-FieldMask':'id,displayName,formattedAddress,nationalPhoneNumber,'
                              'websiteUri,rating,userRatingCount,reviews,photos,'
                              'regularOpeningHours,types',
        },
        timeout=30
    )
    if r.status_code != 200:
        return {'_error': f'http {r.status_code}: {r.text[:200]}'}
    return r.json()

def photo_url(photo_name, max_width=1200):
    """Return real lh3.googleusercontent.com URL for a photo name."""
    try:
        r = requests.get(
            f'https://places.googleapis.com/v1/{photo_name}/media',
            params={'key':KEY,'maxWidthPx':max_width,'skipHttpRedirect':'true'},
            timeout=20
        )
        if r.status_code == 200:
            return r.json().get('photoUri','')
    except Exception:
        pass
    return ''

# ─── Validation ──────────────────────────────────────────────────────────────
def normalize(s): return re.sub(r'[^a-z0-9]','',(s or '').lower())

def title_matches(a, b):
    """Loose title match — at least one ≥3-char word in common (ignoring stop)."""
    STOP = {'pusat','jagaan','rumah','warga','tua','centre','center','care','home',
            'nursing','elderly','senior','sdn','bhd','the','of','for','and'}
    def tokens(s):
        return {w for w in re.sub(r'[^a-z0-9 ]',' ',(s or '').lower()).split()
                if len(w)>=3 and w not in STOP}
    return bool(tokens(a) & tokens(b))

def address_in_state(addr, state):
    if not addr: return False
    return state.lower() in addr.lower()

# ─── Main per-facility processor ─────────────────────────────────────────────
def process_facility(f, state, ci, force_photos=False):
    """Return updates dict or None if skipped/failed."""
    slug = f['slug']
    title = f['title']
    print(f'  → search: "{title}" near ({f.get("latitude","")}, {f.get("longitude","")})', flush=True)

    # Step 1: text search
    results = places_text_search(f"{title} {state} Malaysia", f.get('latitude'), f.get('longitude'))
    if isinstance(results, dict) and '_error' in results:
        print(f'    ERROR: {results["_error"]}')
        return None
    if not results:
        print('    no results')
        return None

    # Pick first match that passes validation
    place = None
    for r in results:
        rt = (r.get('displayName',{}) or {}).get('text','')
        ra = r.get('formattedAddress','')
        if title_matches(title, rt) and address_in_state(ra, state):
            place = r
            break
    if not place:
        # Last resort: take top result if address is in state
        if address_in_state(results[0].get('formattedAddress',''), state):
            place = results[0]
            print(f'    warn: weak title match — top result "{(place.get("displayName",{}) or {}).get("text")}"')
        else:
            print(f'    SKIP — no match in {state}: top "{(results[0].get("displayName",{}) or {}).get("text")}"  / {results[0].get("formattedAddress","")[:80]}')
            return None

    pid = place['id']
    print(f'    placeId={pid[:30]}  rating={place.get("rating","?")}/{place.get("userRatingCount","?")}')

    # Step 2: get details (for reviews + photos)
    det = place_details(pid)
    if '_error' in det:
        print(f'    DETAILS ERROR: {det["_error"]}')
        det = {}

    # Build updates
    updates = {}
    maps_url = (f'https://www.google.com/maps/search/?api=1'
                f'&query={urllib.parse.quote(title)}'
                f'&query_place_id={pid}')
    updates['T'] = maps_url
    updates['U'] = TODAY

    if place.get('rating') is not None:
        updates['P'] = str(place['rating'])
    if place.get('userRatingCount') is not None:
        updates['Q'] = str(place['userRatingCount'])
    if place.get('websiteUri') and not f['website'].strip():
        updates['F'] = place['websiteUri']

    # Photos — only if empty
    photos = []
    hero = ''
    if not f.get('photos','').strip() and not f.get('hero_image','').strip():
        photo_refs = det.get('photos', [])[:8]  # cap at 8 to keep fetches small
        for pr in photo_refs:
            u = photo_url(pr['name'], 1200)
            if u:
                photos.append(u)
            time.sleep(0.3)
        if photos:
            hero = photos[0]
            updates['AZ'] = hero
            updates['BA'] = '|'.join(photos)
            updates['BB'] = str(len(photos))
            print(f'    fetched {len(photos)} photos')

    # Reviews — return them so caller can save snippets to Details
    reviews = []
    for rv in det.get('reviews', [])[:5]:
        text = (rv.get('text') or {}).get('text','') or ''
        reviews.append({
            'rating': rv.get('rating'),
            'text': text,
            'author': (rv.get('authorAttribution') or {}).get('displayName',''),
            'when': rv.get('publishTime',''),
        })

    return {
        'updates': updates,
        'place_id': pid,
        'address': place.get('formattedAddress',''),
        'phone': place.get('nationalPhoneNumber',''),
        'reviews': reviews,
        'hero': hero,
        'photo_count': len(photos),
    }

# ─── Main ────────────────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser()
    p.add_argument('state', help='State name e.g. Perak')
    p.add_argument('--limit', type=int, default=0, help='Process at most N facilities')
    p.add_argument('--slug', help='Process only this slug (skip all others)')
    p.add_argument('--force-photos', action='store_true', help='Overwrite existing photos')
    args = p.parse_args()

    cache_path = CACHE_DIR / f'places_{args.state.lower()}.json'
    cache = json.loads(cache_path.read_text(encoding='utf-8')) if cache_path.exists() else {}

    print(f'Loading {args.state} facilities...')
    facilities, ci, hdr = fetch_state_facilities(args.state)
    print(f'  loaded {len(facilities)} live facilities')

    if args.slug:
        facilities = [f for f in facilities if f['slug']==args.slug]
    if args.limit:
        facilities = facilities[:args.limit]
    print(f'  processing {len(facilities)} facility(ies)\n')

    svc = sheets()
    all_updates = []
    detail_rows = []
    summary = {'placeId':0, 'reviews':0, 'photos':0, 'skipped':0}

    for i, f in enumerate(facilities, 1):
        slug = f['slug']
        print(f'[{i}/{len(facilities)}] {slug}', flush=True)
        if slug in cache and not args.force_photos:
            cached = cache[slug]
            if cached.get('status') == 'ok':
                print('    skip (cached)')
                continue
        result = process_facility(f, args.state, ci, args.force_photos)
        if not result:
            cache[slug] = {'status': 'skipped'}
            summary['skipped'] += 1
            cache_path.write_text(json.dumps(cache, indent=2), encoding='utf-8')
            time.sleep(0.5)
            continue

        # Build batchUpdate ranges for this row
        for col, val in result['updates'].items():
            all_updates.append({
                'range': f"'{TAB}'!{col}{f['sheet_row']}",
                'values': [[val]]
            })
        summary['placeId'] += 1
        if result['photo_count']: summary['photos'] += 1
        if result['reviews']:
            summary['reviews'] += 1
            # Add a single Details row capturing review snippets (limit to 350 chars total)
            quoted = ' / '.join(
                f'[{r["rating"]}*] {r["text"][:150]}' for r in result['reviews'] if r['text']
            )[:600]
            if quoted:
                detail_rows.append([slug, 'social', 'Google reviews', quoted])

        # Add verified address as Details policies row (only if not already present? caller will append)
        if result['address']:
            detail_rows.append([slug, 'policies', 'Address (Google-verified)', result['address']])
        if result['photo_count']:
            detail_rows.append([slug, 'policies', 'Photo credits', 'Photos via Google Places (lh3.googleusercontent.com)'])

        cache[slug] = {'status':'ok', 'place_id':result['place_id'],
                       'photo_count':result['photo_count'],
                       'review_count': len(result['reviews'])}
        cache_path.write_text(json.dumps(cache, indent=2), encoding='utf-8')
        time.sleep(0.4)

    # Flush sheet writes in chunks of 100 (well below quota)
    print(f'\nWriting {len(all_updates)} cell updates...')
    for chunk_start in range(0, len(all_updates), 100):
        chunk = all_updates[chunk_start:chunk_start+100]
        svc.spreadsheets().values().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={'valueInputOption':'RAW','data':chunk}
        ).execute()
        print(f'  wrote {min(chunk_start+100, len(all_updates))} / {len(all_updates)}')
        time.sleep(1)

    if detail_rows:
        print(f'\nAppending {len(detail_rows)} Details rows...')
        svc.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=f"'{DETAILS_TAB}'!A:D",
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body={'values': detail_rows}
        ).execute()

    print(f'\n=== SUMMARY ({args.state}) ===')
    for k, v in summary.items():
        print(f'  {k}: {v}')
    print(f'\nCache: {cache_path}')

if __name__ == '__main__':
    main()
