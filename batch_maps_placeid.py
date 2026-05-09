"""
batch_maps_placeid.py
Verify and update Google Maps placeId URLs for all licensed facilities missing one.
Cost: ~$0.21 total (Apify, max 1 result per facility).

Run: python batch_maps_placeid.py
Writes results to: batch_maps_results.json
"""

import csv, io, json, os, re, sys, time, unicodedata, urllib.request
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout.reconfigure(encoding='utf-8')

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_PATH     = r'C:\Users\ibkaa\nursinghomeguide-my\Nursing Home Guide Malaysia\token_sheets.json'
TAB            = 'google-sheets-facilities.csv'
RESULTS_FILE   = 'batch_maps_results.json'
APIFY_TOKEN    = open(r'C:\Users\ibkaa\nursinghomeguide-my\Nursing Home Guide Malaysia\.env').read().split('APIFY_TOKEN=')[1].split()[0].strip()

CSV_URL = (
    'https://docs.google.com/spreadsheets/d/e/'
    '2PACX-1vQ4_BgHIjnlgmITzjyUuGDpgpNzPL7MfjOY2069i0PtbVbXSxIAJk1tmBejwNo8aBBeLuRi62szF2sh'
    '/pub?gid=292378871&single=true&output=csv'
)

STATE_MAP = {
    'johor': 'johor', 'kuala lumpur': 'kuala lumpur', 'kl': 'kuala lumpur',
    'selangor': 'selangor', 'perak': 'perak', 'penang': 'penang',
    'pulau pinang': 'penang', 'negeri sembilan': 'negeri sembilan',
    'pahang': 'pahang', 'kedah': 'kedah', 'melaka': 'melaka',
    'malacca': 'melaka', 'sabah': 'sabah', 'sarawak': 'sarawak',
    'terengganu': 'terengganu', 'kelantan': 'kelantan',
    'perlis': 'perlis', 'labuan': 'labuan',
}

def normalise(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii','ignore').decode()
    return re.sub(r'[^a-z0-9 ]', ' ', s.lower()).strip()

def title_match(sheet_title, maps_title):
    a, b = normalise(sheet_title), normalise(maps_title)
    # Drop common suffixes for comparison
    for suffix in ['sdn bhd', 'plt', 'enterprise', 'resources', 'management']:
        a = a.replace(suffix, '').strip()
        b = b.replace(suffix, '').strip()
    words_a = set(a.split())
    words_b = set(b.split())
    if not words_a or not words_b:
        return False
    overlap = len(words_a & words_b) / max(len(words_a), len(words_b))
    return overlap >= 0.4

def state_match(facility_state, maps_address):
    if not facility_state or not maps_address:
        return True  # can't verify, allow
    fs = normalise(facility_state)
    ma = normalise(maps_address)
    return any(s in ma for s in [fs] + [k for k, v in STATE_MAP.items() if v == STATE_MAP.get(fs, fs)])

def query_maps(title, lat, lng):
    payload = {
        'searchStringsArray': [title],
        'maxCrawledPlacesPerSearch': 1,
        'language': 'en',
    }
    # Only include coordinates if valid — some rows have bad CSV data in lat/lng
    if lat is not None and lng is not None:
        payload.update({'lat': lat, 'lng': lng, 'zoom': 15})
    try:
        r = requests.post(
            f'https://api.apify.com/v2/acts/compass~crawler-google-places'
            f'/run-sync-get-dataset-items?token={APIFY_TOKEN}&timeout=60',
            json=payload,
            timeout=90
        )
        items = r.json()
        return items[0] if items else None
    except Exception as e:
        return {'_error': str(e)}

def build_place_url(title, place_id):
    import urllib.parse
    return (f'https://www.google.com/maps/search/?api=1'
            f'&query={urllib.parse.quote(title)}'
            f'&query_place_id={place_id}')

def main():
    print('Fetching facilities CSV...')
    with urllib.request.urlopen(CSV_URL) as r:
        data = r.read().decode('utf-8')
    reader = csv.DictReader(io.StringIO(data))
    headers = list(reader.fieldnames)
    col_maps = headers.index('google_maps_url') + 1  # T

    rows = list(reader)
    targets = []
    for i, row in enumerate(rows, start=2):
        if row.get('status','').strip() in ('unverified','removed'):
            continue
        if not row.get('licence_number','').strip():
            continue
        maps_url = row.get('google_maps_url','').strip()
        if maps_url and 'query_place_id' in maps_url:
            continue  # already has placeId
        slug = row.get('slug','').strip()
        if not slug:
            continue
        lat = row.get('latitude','').strip()
        lng = row.get('longitude','').strip()
        try:
            lat_f, lng_f = float(lat), float(lng)
        except (ValueError, TypeError):
            lat_f, lng_f = None, None  # search by name only, no coords
        targets.append({
            'row': i, 'slug': slug,
            'title': row.get('title','').strip(),
            'state': row.get('state','').strip(),
            'lat': lat_f, 'lng': lng_f,
            'current_maps': maps_url,
        })

    print(f'Facilities needing placeId: {len(targets)}')

    # Load existing results to allow resuming
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, encoding='utf-8') as f:
            results = json.load(f)
        done_slugs = {r['slug'] for r in results}
        print(f'Resuming — {len(done_slugs)} already done')
    else:
        results = []
        done_slugs = set()

    creds = Credentials.from_authorized_user_file(TOKEN_PATH, ['https://www.googleapis.com/auth/spreadsheets'])
    svc   = build('sheets', 'v4', credentials=creds)
    col_letter = 'T'  # google_maps_url

    updated = 0
    skipped_wrong = 0
    skipped_error = 0

    remaining = [t for t in targets if t['slug'] not in done_slugs]
    print(f'Remaining to process: {len(remaining)}')

    for idx, t in enumerate(remaining, 1):
        print(f'[{idx}/{len(remaining)}] {t["slug"]}', end=' ... ', flush=True)

        item = query_maps(t['title'], t['lat'], t['lng'])

        if not item:
            print('no result')
            results.append({**t, 'status': 'no_result'})
            skipped_wrong += 1

        elif '_error' in item:
            print(f'error: {item["_error"]}')
            results.append({**t, 'status': 'error', 'error': item['_error']})
            skipped_error += 1

        else:
            maps_title   = item.get('title', '')
            maps_address = item.get('address', '')
            place_id     = item.get('placeId', '')
            rating       = item.get('totalScore')
            review_count = item.get('reviewsCount')

            t_match = title_match(t['title'], maps_title)
            s_match = state_match(t['state'], maps_address)

            if not t_match or not s_match:
                print(f'SKIP (wrong result: "{maps_title}" / {maps_address})')
                results.append({**t, 'status': 'wrong_result',
                                'maps_title': maps_title, 'maps_address': maps_address})
                skipped_wrong += 1
            elif not place_id:
                print('no placeId in result')
                results.append({**t, 'status': 'no_placeid', 'maps_title': maps_title})
                skipped_wrong += 1
            else:
                new_url = build_place_url(t['title'], place_id)
                print(f'OK → {place_id[:20]}...')

                # Update sheet (retry up to 3x on transient 5xx, skip if still failing)
                updates = [[new_url]]
                body = {'values': updates}
                write_ok = False
                for _attempt in range(3):
                    try:
                        svc.spreadsheets().values().update(
                            spreadsheetId=SPREADSHEET_ID,
                            range=f"'{TAB}'!{col_letter}{t['row']}",
                            valueInputOption='RAW', body=body
                        ).execute()
                        write_ok = True
                        break
                    except Exception as _e:
                        print(f'  sheet write retry {_attempt+1}: {_e}', flush=True)
                        time.sleep(10)

                if write_ok:
                    results.append({**t, 'status': 'updated', 'place_id': place_id,
                                    'new_url': new_url, 'maps_title': maps_title,
                                    'maps_address': maps_address,
                                    'rating': rating, 'review_count': review_count})
                    updated += 1
                else:
                    print(f'  WRITE FAILED — will need manual retry for row {t["row"]}')
                    results.append({**t, 'status': 'write_failed', 'place_id': place_id,
                                    'new_url': new_url, 'maps_title': maps_title,
                                    'maps_address': maps_address})
                    skipped_error += 1

        # Save progress after every facility
        with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        time.sleep(1.2)  # polite rate limit

    print('\n' + '='*60)
    print(f'MAPS BATCH COMPLETE')
    print(f'  Updated:       {updated}')
    print(f'  Wrong/no result: {skipped_wrong}')
    print(f'  Errors:        {skipped_error}')
    print(f'  Results saved: {RESULTS_FILE}')

if __name__ == '__main__':
    main()
