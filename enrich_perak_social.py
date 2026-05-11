"""
enrich_perak_social.py
Batch social media & web presence enrichment for all 119 live Perak facilities.

Passes:
  1. Google Maps placeId verification (facilities missing one)
  2. Social media discovery via Google search (all 119)
  3. Profile scraping (Instagram / Facebook / TikTok for confirmed hits)
  4. Batch Google Sheets update
  5. Summary report

Résumable: progress saved to _enrich_cache/perak_social_results.json after each facility.

Run:
  python enrich_perak_social.py             # all passes
  python enrich_perak_social.py --pass 1    # only Maps pass
  python enrich_perak_social.py --pass 2    # only Social discovery
  python enrich_perak_social.py --pass 3    # only Profile scraping
  python enrich_perak_social.py --push      # only sheet update (reads from cache)
"""

import argparse, csv, io, json, os, re, sys, time, unicodedata, urllib.parse, urllib.request
from pathlib import Path

import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout.reconfigure(encoding='utf-8')

# ─── Constants ────────────────────────────────────────────────────────────────

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_PATH     = r'C:\Users\ibkaa\nursinghomeguide-my\Nursing Home Guide Malaysia\token_sheets.json'
ENV_PATH       = r'C:\Users\ibkaa\nursinghomeguide-my\Nursing Home Guide Malaysia\.env'
FAC_TAB        = 'google-sheets-facilities.csv'
DET_TAB        = 'Details'
LOCAL_CSV      = Path('facilities_local.csv')
CACHE_DIR      = Path('_enrich_cache')
RESULTS_FILE   = CACHE_DIR / 'perak_social_results.json'

LIVE_CSV_URL = (
    'https://docs.google.com/spreadsheets/d/e/'
    '2PACX-1vQ4_BgHIjnlgmITzjyUuGDpgpNzPL7MfjOY2069i0PtbVbXSxIAJk1tmBejwNo8aBBeLuRi62szF2sh'
    '/pub?gid=292378871&single=true&output=csv'
)

APIFY_TOKEN = open(ENV_PATH).read().split('APIFY_TOKEN=')[1].split()[0].strip()

APIFY_BASE  = 'https://api.apify.com/v2/acts/{actor}/run-sync-get-dataset-items?token={token}&timeout=90'

# Column indices (1-based) in Facilities tab
COL_AREA     = 4   # D
COL_WEBSITE  = 6   # F
COL_MAPS_URL = 20  # T
COL_WHATSAPP = 25  # Y
COL_FACEBOOK = 26  # Z

# Known Perak area keywords for Maps address validation
PERAK_AREAS = {
    'perak', 'ipoh', 'taiping', 'teluk intan', 'manjung', 'sitiawan',
    'lumut', 'kampar', 'batu gajah', 'gopeng', 'slim river', 'tanjung malim',
    'kuala kangsar', 'bidor', 'sungai siput', 'gerik', 'lenggong',
    'pengkalan hulu', 'parit buntar', 'beruas', 'ayer tawar', 'pantai remis',
    'rapat', 'bercham', 'meru', 'falim', 'jelapang', 'chemor', 'lahat',
    'langkap', 'mambang di awan', 'hilir perak',
}

SLEEP = 1.5  # seconds between Apify calls

# ─── Helpers ──────────────────────────────────────────────────────────────────

def normalise(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9 ]', ' ', s.lower()).strip()

def title_match(a, b):
    drop = {'sdn', 'bhd', 'plt', 'enterprise', 'resources', 'management',
            'care', 'centre', 'home', 'senior', 'elderly', 'pusat', 'jagaan'}
    wa = set(normalise(a).split()) - drop
    wb = set(normalise(b).split()) - drop
    if not wa or not wb:
        return False
    return len(wa & wb) / max(len(wa), len(wb)) >= 0.35

def address_in_perak(address):
    if not address:
        return True  # can't verify, allow
    addr_lower = address.lower()
    return any(k in addr_lower for k in PERAK_AREAS)

def apify_post(actor, payload):
    url = APIFY_BASE.format(actor=actor.replace('/', '~'), token=APIFY_TOKEN)
    try:
        r = requests.post(url, json=payload, timeout=120)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return [{'_error': str(e)}]

def build_maps_url(title, place_id):
    return (f'https://www.google.com/maps/search/?api=1'
            f'&query={urllib.parse.quote(title)}'
            f'&query_place_id={place_id}')

def has_place_id(url):
    return url and ('query_place_id=' in url or '!1s' in url)

def load_cache():
    if RESULTS_FILE.exists():
        return json.loads(RESULTS_FILE.read_text(encoding='utf-8'))
    return {}

def save_cache(cache):
    RESULTS_FILE.parent.mkdir(exist_ok=True)
    RESULTS_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding='utf-8')

def load_facilities():
    """Fetch live published CSV, return (list_of_live_perak_rows, slug_to_row_num dict)."""
    print(f'Fetching live CSV from Google Sheets...')
    with urllib.request.urlopen(LIVE_CSV_URL) as r:
        data = r.read().decode('utf-8')
    rows = list(csv.DictReader(io.StringIO(data)))
    perak_live = []
    slug_to_rownum = {}
    for i, row in enumerate(rows, start=2):  # row 1 = header
        if row.get('state', '').strip().lower() != 'perak':
            continue
        if row.get('status', '').strip() in ('unverified', 'removed'):
            continue
        slug = row.get('slug', '').strip()
        if not slug:
            continue
        perak_live.append(row)
        slug_to_rownum[slug] = i
    return perak_live, slug_to_rownum

def sheets_svc():
    creds = Credentials.from_authorized_user_file(
        TOKEN_PATH, ['https://www.googleapis.com/auth/spreadsheets'])
    return build('sheets', 'v4', credentials=creds)

def sheet_update(svc, col_letter, row_num, value, tab=FAC_TAB):
    for attempt in range(3):
        try:
            svc.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=f"'{tab}'!{col_letter}{row_num}",
                valueInputOption='RAW',
                body={'values': [[value]]}
            ).execute()
            return True
        except Exception as e:
            print(f'  sheet write retry {attempt+1}: {e}', flush=True)
            time.sleep(8)
    return False

def col_letter(n):
    """Convert 1-based column index to letter (1=A, 26=Z, 27=AA)."""
    result = ''
    while n:
        n, r = divmod(n - 1, 26)
        result = chr(65 + r) + result
    return result

def extract_ig_username(url):
    m = re.search(r'instagram\.com/([^/?#]+)', url)
    if m:
        handle = m.group(1).strip('/')
        if handle not in ('p', 'reel', 'stories', 'explore', 'accounts', 'tv'):
            return handle
    return None

def extract_wa_number(url):
    m = re.search(r'wa\.me/(\d+)', url or '')
    return '+' + m.group(1) if m else None

def parse_social_from_search(results, facility_title):
    """Extract valid social media URLs from RAG web browser search results."""
    found = {'facebook': None, 'instagram': None, 'tiktok': None, 'reddit': None}
    title_words = set(normalise(facility_title).split()) - {'care', 'centre', 'home', 'senior', 'elderly'}

    reject_patterns = re.compile(
        r'facebook\.com/(people|groups|events|marketplace|ads|business|sharer|share|dialog)|'
        r'instagram\.com/(p/|reel/|explore/|tags/)|'
        r'tiktok\.com/(tag/|search\?)|'
        r'yellowpages|fave\.com|foursquare|tripadvisor|booking|airbnb|google\.com/maps|'
        r'nursinghomeguide|mymedic|hospitallist|caregivermsia'
    )

    for item in results:
        # RAG web browser nests the URL in searchResult.url / metadata.url
        url = (item.get('searchResult', {}).get('url', '')
               or item.get('metadata', {}).get('url', '')
               or item.get('url', ''))
        snippet = (item.get('markdown', '') + ' '
                   + item.get('searchResult', {}).get('description', '') + ' '
                   + item.get('searchResult', {}).get('title', '') + ' '
                   + (item.get('metadata', {}).get('title', '') or '')).lower()

        if reject_patterns.search(url):
            continue

        # Facebook business page
        if 'facebook.com/' in url and not found['facebook']:
            # Must have at least one title word in url or snippet
            if title_words and any(w in url.lower() + snippet for w in title_words):
                found['facebook'] = url.split('?')[0].rstrip('/')

        # Instagram profile
        if 'instagram.com/' in url and not found['instagram']:
            ig = extract_ig_username(url)
            if ig and title_words and any(w in ig.lower() + snippet for w in title_words):
                found['instagram'] = f'https://www.instagram.com/{ig}/'

        # TikTok profile
        if 'tiktok.com/@' in url and not found['tiktok']:
            m = re.search(r'tiktok\.com/@([^/?#]+)', url)
            if m and title_words and any(w in m.group(1).lower() + snippet for w in title_words):
                found['tiktok'] = f'https://www.tiktok.com/@{m.group(1)}'

        # Reddit mention
        if 'reddit.com/' in url and not found['reddit']:
            found['reddit'] = url

    return found

# ─── Pass 1: Google Maps ──────────────────────────────────────────────────────

def pass1_maps(facilities, slug_to_rownum, cache, svc):
    print('\n' + '='*60)
    print('PASS 1 — Google Maps placeId verification')
    print('='*60)

    targets = [f for f in facilities if not has_place_id(f.get('google_maps_url', ''))]
    already_done = [slug for slug in [f['slug'] for f in targets]
                    if cache.get(slug, {}).get('maps', {}).get('status') in ('updated', 'skipped', 'no_result', 'wrong_result')]
    remaining = [f for f in targets if f['slug'] not in already_done]

    print(f'Need placeId: {len(targets)} | Already cached: {len(already_done)} | To process: {len(remaining)}')

    updated = skipped = errors = 0

    for idx, f in enumerate(remaining, 1):
        slug  = f['slug']
        title = f['title']
        lat   = f.get('latitude', '').strip()
        lng   = f.get('longitude', '').strip()

        print(f'[{idx}/{len(remaining)}] {slug}', end=' ... ', flush=True)

        payload = {
            'searchStringsArray': [title],
            'maxCrawledPlacesPerSearch': 3,
            'language': 'en',
        }
        try:
            payload['lat'] = float(lat)
            payload['lng'] = float(lng)
            payload['zoom'] = 15
        except (ValueError, TypeError):
            pass

        items = apify_post('compass/crawler-google-places', payload)
        entry = cache.setdefault(slug, {})

        if not items or '_error' in (items[0] if items else {}):
            err = items[0].get('_error', 'no result') if items else 'no result'
            print(f'ERROR: {err}')
            entry['maps'] = {'status': 'no_result', 'error': err}
            errors += 1
        else:
            item = items[0]
            maps_title   = item.get('title', '')
            maps_address = item.get('address', '')
            place_id     = item.get('placeId', '')
            website      = item.get('website', '')

            t_ok = title_match(title, maps_title)
            a_ok = address_in_perak(maps_address)

            if not t_ok or not a_ok:
                print(f'SKIP — wrong result: "{maps_title}" / {maps_address}')
                entry['maps'] = {'status': 'wrong_result',
                                 'maps_title': maps_title, 'maps_address': maps_address}
                skipped += 1
            elif not place_id:
                print('no placeId')
                entry['maps'] = {'status': 'no_result', 'maps_title': maps_title}
                skipped += 1
            else:
                new_url  = build_maps_url(title, place_id)
                row_num  = slug_to_rownum.get(slug)
                write_ok = sheet_update(svc, col_letter(COL_MAPS_URL), row_num, new_url) if row_num else False
                print(f'OK → {place_id[:24]}... {"✓ sheet" if write_ok else "⚠ write failed"}')
                entry['maps'] = {
                    'status': 'updated' if write_ok else 'write_failed',
                    'place_id': place_id, 'new_url': new_url,
                    'maps_title': maps_title, 'maps_address': maps_address,
                    'website': website,
                    'rating': item.get('totalScore'),
                    'review_count': item.get('reviewsCount'),
                }
                if write_ok:
                    updated += 1
                else:
                    errors += 1

        save_cache(cache)
        time.sleep(SLEEP)

    print(f'\nPass 1 done — updated: {updated} | skipped: {skipped} | errors: {errors}')
    return cache

# ─── Pass 2: Social media discovery ──────────────────────────────────────────

def pass2_social_discovery(facilities, cache):
    print('\n' + '='*60)
    print('PASS 2 — Social media discovery (Google search)')
    print('='*60)

    already_done = [f['slug'] for f in facilities
                    if cache.get(f['slug'], {}).get('social', {}).get('discovery_status')]
    remaining = [f for f in facilities if f['slug'] not in already_done]

    print(f'Total: {len(facilities)} | Cached: {len(already_done)} | To search: {len(remaining)}')

    found_any = 0

    for idx, f in enumerate(remaining, 1):
        slug  = f['slug']
        title = f['title']
        print(f'[{idx}/{len(remaining)}] {slug}', end=' ... ', flush=True)

        query = (f'"{title}" (facebook.com OR instagram.com OR tiktok.com OR reddit.com) Malaysia')
        items = apify_post('apify/rag-web-browser', {'query': query, 'maxResults': 5})

        entry = cache.setdefault(slug, {})
        if not items or '_error' in (items[0] if items else {}):
            err = items[0].get('_error', 'no result') if items else 'no result'
            print(f'search error: {err}')
            entry['social'] = {'discovery_status': 'error', 'error': err}
        else:
            found = parse_social_from_search(items, title)
            has_any = any(v for v in found.values())
            found['discovery_status'] = 'found' if has_any else 'not_found'
            entry['social'] = found
            hits = [k for k, v in found.items() if v and k != 'discovery_status']
            print('found: ' + (', '.join(hits) if hits else 'nothing'))
            if has_any:
                found_any += 1

        save_cache(cache)
        time.sleep(SLEEP)

    print(f'\nPass 2 done — social presence found: {found_any} / {len(facilities)} facilities')
    return cache

# ─── Pass 3: Profile scraping ─────────────────────────────────────────────────

def pass3_scrape(facilities, cache):
    print('\n' + '='*60)
    print('PASS 3 — Profile scraping')
    print('='*60)

    to_scrape = [f for f in facilities
                 if cache.get(f['slug'], {}).get('social', {}).get('discovery_status') == 'found'
                 and not cache.get(f['slug'], {}).get('scraped')]

    print(f'Facilities with social hits: {len(to_scrape)}')

    for idx, f in enumerate(to_scrape, 1):
        slug  = f['slug']
        entry = cache[slug]
        social = entry.get('social', {})
        scraped = entry.setdefault('scraped', {})

        print(f'\n[{idx}/{len(to_scrape)}] {slug}')

        # Instagram
        ig_url = social.get('instagram')
        if ig_url:
            handle = extract_ig_username(ig_url)
            if handle and 'instagram' not in scraped:
                print(f'  Scraping Instagram @{handle}', end=' ... ', flush=True)
                items = apify_post('apify/instagram-profile-scraper', {'usernames': [handle]})
                if items and '_error' not in items[0]:
                    ig = items[0]
                    bio = ig.get('biography', '')
                    ext_url = ig.get('externalUrl', '') or ''
                    ext_urls = ig.get('externalUrls', []) or []
                    # Find WhatsApp number in external URLs
                    wa = extract_wa_number(ext_url)
                    if not wa:
                        for eu in ext_urls:
                            wa = extract_wa_number(eu.get('url', ''))
                            if wa:
                                break
                    # Collect post captions for service detection
                    posts = ig.get('latestPosts', []) or []
                    captions = [p.get('caption', '') for p in posts[:5] if p.get('caption')]
                    # Don't save CDN image URLs — they expire
                    scraped['instagram'] = {
                        'handle': handle,
                        'bio': bio,
                        'whatsapp': wa,
                        'posts_count': ig.get('postsCount'),
                        'captions': captions,
                        'website': ig.get('externalUrl') if ig.get('externalUrl') and 'fbcdn' not in (ig.get('externalUrl') or '') else None,
                    }
                    print(f'bio={len(bio)} chars, wa={wa}, posts={len(captions)}')
                else:
                    err = items[0].get('_error', 'no data') if items else 'no data'
                    scraped['instagram'] = {'error': err}
                    print(f'error: {err}')
                time.sleep(SLEEP)

        # Facebook
        fb_url = social.get('facebook')
        if fb_url and 'facebook' not in scraped:
            print(f'  Scraping Facebook {fb_url}', end=' ... ', flush=True)
            items = apify_post('apify/facebook-pages-scraper',
                               {'startUrls': [{'url': fb_url}], 'maxPosts': 3})
            if items and '_error' not in items[0]:
                fb = items[0]
                scraped['facebook'] = {
                    'about': fb.get('about', '') or fb.get('info', ''),
                    'website': fb.get('website', ''),
                    'phone': fb.get('phone', ''),
                    'categories': fb.get('categories', []),
                    'likes': fb.get('likes'),
                }
                print(f"about={len(scraped['facebook'].get('about') or '')} chars")
            else:
                err = items[0].get('_error', 'no data') if items else 'no data'
                scraped['facebook'] = {'error': err}
                print(f'error: {err}')
            time.sleep(SLEEP)

        # TikTok (best-effort, skip on error)
        tt_url = social.get('tiktok')
        if tt_url and 'tiktok' not in scraped:
            m = re.search(r'tiktok\.com/@([^/?#]+)', tt_url)
            if m:
                handle = m.group(1)
                print(f'  Scraping TikTok @{handle}', end=' ... ', flush=True)
                items = apify_post('clockworks/tiktok-profile-scraper',
                                   {'profiles': [handle], 'resultsPerPage': 5})
                if items and '_error' not in items[0]:
                    tt = items[0]
                    scraped['tiktok'] = {
                        'bio': tt.get('bioLink', {}).get('text', '') or tt.get('signature', ''),
                        'video_count': tt.get('videoCount'),
                        'followers': tt.get('fans'),
                    }
                    print(f"followers={scraped['tiktok'].get('followers')}")
                else:
                    err = items[0].get('_error', 'no data') if items else 'no data'
                    scraped['tiktok'] = {'error': err}
                    print(f'error (skipping): {err}')
                time.sleep(SLEEP)

        # Website (from Maps or Facebook)
        website_url = (
            entry.get('maps', {}).get('website') or
            scraped.get('facebook', {}).get('website') or
            scraped.get('instagram', {}).get('website')
        )
        if website_url and 'fbcdn' not in website_url and 'website' not in scraped:
            print(f'  Crawling website {website_url}', end=' ... ', flush=True)
            items = apify_post('apify/rag-web-browser',
                               {'startUrls': [{'url': website_url}], 'maxCrawlDepth': 1, 'maxResults': 3})
            if not items or '_error' in items[0]:
                # Fallback: just fetch the homepage content
                items = apify_post('apify/rag-web-browser', {'query': website_url, 'maxResults': 1})
            if items and '_error' not in items[0]:
                text = ' '.join(i.get('text', '') for i in items)
                wa   = extract_wa_number(text)
                email = re.search(r'[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}', text)
                scraped['website'] = {
                    'url': website_url,
                    'whatsapp': wa,
                    'email': email.group(0) if email else None,
                    'text_length': len(text),
                }
                print(f'chars={len(text)}, wa={wa}, email={email.group(0) if email else None}')
            else:
                err = items[0].get('_error', 'no data') if items else 'no data'
                scraped['website'] = {'error': err, 'url': website_url}
                print(f'error: {err}')
            time.sleep(SLEEP)

        save_cache(cache)

    print(f'\nPass 3 done')
    return cache

# ─── Pass 4: Sheet update ─────────────────────────────────────────────────────

def pass4_sheet_update(facilities, slug_to_rownum, cache, svc):
    print('\n' + '='*60)
    print('PASS 4 — Google Sheets update')
    print('='*60)

    fac_updates = 0
    det_rows    = []

    for f in facilities:
        slug    = f['slug']
        entry   = cache.get(slug, {})
        row_num = slug_to_rownum.get(slug)
        if not row_num:
            continue

        social  = entry.get('social', {})
        scraped = entry.get('scraped', {})
        maps    = entry.get('maps', {})

        # ── Facilities tab ──────────────────────────────────────

        # Col T: Maps URL (already written in Pass 1, skip)
        # Col F: website
        existing_website = f.get('website', '').strip()
        new_website = (
            maps.get('website') or
            scraped.get('facebook', {}).get('website') or
            scraped.get('instagram', {}).get('website')
        )
        if new_website and not existing_website and 'fbcdn' not in new_website:
            if sheet_update(svc, col_letter(COL_WEBSITE), row_num, new_website):
                print(f'  {slug}: website → {new_website}')
                fac_updates += 1
            time.sleep(0.5)

        # Col Y: WhatsApp
        existing_wa = f.get('whatsapp', '').strip()
        new_wa = (
            scraped.get('instagram', {}).get('whatsapp') or
            scraped.get('website', {}).get('whatsapp')
        )
        if new_wa and not existing_wa:
            if sheet_update(svc, col_letter(COL_WHATSAPP), row_num, new_wa):
                print(f'  {slug}: whatsapp → {new_wa}')
                fac_updates += 1
            time.sleep(0.5)

        # Col Z: Facebook (prefer) or Instagram URL
        existing_fb = f.get('facebook', '').strip()
        new_fb = social.get('facebook') or social.get('instagram')
        if new_fb and not existing_fb:
            if sheet_update(svc, col_letter(COL_FACEBOOK), row_num, new_fb):
                print(f'  {slug}: facebook/ig → {new_fb}')
                fac_updates += 1
            time.sleep(0.5)

        # ── Details tab rows ────────────────────────────────────

        # Social URLs (both FB and IG go to details even if only one goes to col Z)
        if social.get('facebook'):
            det_rows.append([slug, 'social', 'Facebook', social['facebook']])
        if social.get('instagram'):
            det_rows.append([slug, 'social', 'Instagram', social['instagram']])
        if social.get('tiktok'):
            det_rows.append([slug, 'social', 'TikTok', social['tiktok']])
        if social.get('reddit'):
            det_rows.append([slug, 'social', 'Reddit mention', social['reddit']])

        if maps.get('maps_address'):
            det_rows.append([slug, 'policies', 'Address', maps['maps_address']])

        email = scraped.get('website', {}).get('email')
        if email:
            det_rows.append([slug, 'policies', 'Email', email])

    # Deduplicate Details rows (avoid re-adding existing rows)
    # Fetch current Details tab to check what's already there
    print(f'\nFetching existing Details tab to deduplicate...')
    try:
        existing = svc.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"'{DET_TAB}'!A:D"
        ).execute().get('values', [])
        existing_set = {(r[0], r[1], r[2]) for r in existing if len(r) >= 3}
    except Exception as e:
        print(f'  Warning: could not read Details tab: {e}')
        existing_set = set()

    new_rows = [r for r in det_rows if (r[0], r[1], r[2]) not in existing_set]
    print(f'Details rows to append: {len(new_rows)} (of {len(det_rows)} total)')

    if new_rows:
        for attempt in range(3):
            try:
                svc.spreadsheets().values().append(
                    spreadsheetId=SPREADSHEET_ID,
                    range=f"'{DET_TAB}'!A:D",
                    valueInputOption='RAW',
                    insertDataOption='INSERT_ROWS',
                    body={'values': new_rows}
                ).execute()
                print(f'✓ Appended {len(new_rows)} rows to Details tab')
                break
            except Exception as e:
                print(f'  Details append retry {attempt+1}: {e}')
                time.sleep(10)

    print(f'\nPass 4 done — {fac_updates} Facilities tab cells updated, {len(new_rows)} Details rows added')
    return fac_updates, len(new_rows)

# ─── Pass 5: Summary ──────────────────────────────────────────────────────────

def pass5_summary(facilities, cache):
    print('\n' + '='*60)
    print('PERAK SOCIAL ENRICHMENT — SUMMARY')
    print('='*60)
    print(f'Facilities processed: {len(facilities)}')
    print()

    # Maps stats
    maps_updated = sum(1 for f in facilities if cache.get(f['slug'], {}).get('maps', {}).get('status') == 'updated')
    maps_had     = sum(1 for f in facilities if has_place_id(f.get('google_maps_url', '')))
    maps_skipped = sum(1 for f in facilities if cache.get(f['slug'], {}).get('maps', {}).get('status') in ('wrong_result', 'no_result', 'no_placeid'))
    print(f'MAPS')
    print(f'  Already had placeId:  {maps_had}')
    print(f'  Updated with placeId: {maps_updated}')
    print(f'  Skipped/no result:    {maps_skipped}')
    print()

    # Social stats
    fb_count  = sum(1 for f in facilities if cache.get(f['slug'], {}).get('social', {}).get('facebook'))
    ig_count  = sum(1 for f in facilities if cache.get(f['slug'], {}).get('social', {}).get('instagram'))
    tt_count  = sum(1 for f in facilities if cache.get(f['slug'], {}).get('social', {}).get('tiktok'))
    rd_count  = sum(1 for f in facilities if cache.get(f['slug'], {}).get('social', {}).get('reddit'))
    any_count = sum(1 for f in facilities if cache.get(f['slug'], {}).get('social', {}).get('discovery_status') == 'found')
    print(f'SOCIAL MEDIA FOUND')
    print(f'  Facebook:   {fb_count}')
    print(f'  Instagram:  {ig_count}')
    print(f'  TikTok:     {tt_count}')
    print(f'  Reddit:     {rd_count}')
    print(f'  Any online presence: {any_count} / {len(facilities)} ({100*any_count//len(facilities) if facilities else 0}%)')
    print()

    # Facilities needing editorial (new data found)
    needs_editorial = [
        f['slug'] for f in facilities
        if cache.get(f['slug'], {}).get('social', {}).get('discovery_status') == 'found'
        or cache.get(f['slug'], {}).get('maps', {}).get('status') == 'updated'
    ]
    print(f'NEEDS EDITORIAL (run nh-profiles.md next): {len(needs_editorial)} facilities')
    for slug in needs_editorial[:20]:
        print(f'  - {slug}')
    if len(needs_editorial) > 20:
        print(f'  ... and {len(needs_editorial)-20} more')
    print()
    print(f'Results cache: {RESULTS_FILE}')

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pass', dest='only_pass', type=int,
                        help='Run only this pass number (1-4)')
    parser.add_argument('--push', action='store_true',
                        help='Only run Pass 4 (sheet update) from cached results')
    args = parser.parse_args()

    facilities, slug_to_rownum = load_facilities()
    print(f'Loaded {len(facilities)} live Perak facilities')

    cache = load_cache()
    print(f'Cache: {len(cache)} slugs already have data')

    svc = sheets_svc()

    only = args.only_pass
    push_only = args.push

    if push_only or only == 4:
        pass4_sheet_update(facilities, slug_to_rownum, cache, svc)
        pass5_summary(facilities, cache)
        return

    if not only or only == 1:
        cache = pass1_maps(facilities, slug_to_rownum, cache, svc)

    if not only or only == 2:
        cache = pass2_social_discovery(facilities, cache)

    if not only or only == 3:
        cache = pass3_scrape(facilities, cache)

    if not only:
        pass4_sheet_update(facilities, slug_to_rownum, cache, svc)
        pass5_summary(facilities, cache)

if __name__ == '__main__':
    main()
