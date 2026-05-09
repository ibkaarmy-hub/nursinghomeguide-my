#!/usr/bin/env python3
"""
merge_apify_to_sheet.py
-----------------------
Downloads Apify Google Maps scraper results and writes missing data back
to the Google Sheet (only fills empty cells — never overwrites existing data).

Fields filled:
  area, latitude, longitude, phone, website, rating, review_count,
  hero_image, photos (pipe-separated)

Usage:
  python merge_apify_to_sheet.py --batch a          # process ~/apify_run_batch_a.json
  python merge_apify_to_sheet.py --batch b          # process ~/apify_run_batch_b.json
  python merge_apify_to_sheet.py --dataset-id XYZ   # explicit dataset ID (auto-detects mode)
  python merge_apify_to_sheet.py --dry-run          # preview, don't write
  python merge_apify_to_sheet.py --csv-only         # write updates CSV, skip sheet write

Batch B results are matched by searchString → slug using ~/batch_b_queries.json.
A name-similarity check (≥60% token overlap) filters out false matches.
"""
import argparse
import csv
import io
import json
import os
import re
import sys
import urllib.request
import warnings

warnings.filterwarnings('ignore')
sys.stdout.reconfigure(encoding='utf-8')

# Load .env file if present (key=value pairs, no quoting needed)
_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if os.path.exists(_env_path):
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith('#') and '=' in _line:
                _k, _v = _line.split('=', 1)
                os.environ.setdefault(_k.strip(), _v.strip())

APIFY_TOKEN = os.environ.get('APIFY_TOKEN', '')
if not APIFY_TOKEN:
    sys.exit('ERROR: APIFY_TOKEN not set. Add it to .env or set as environment variable.')
SHEET_ID     = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
SHEET_TAB    = 'google-sheets-facilities.csv'
FACILITIES_CSV = (
    'https://docs.google.com/spreadsheets/d/e/'
    '2PACX-1vQ4_BgHIjnlgmITzjyUuGDpgpNzPL7MfjOY2069i0PtbVbXSxIAJk1tmBejwNo8aBBeLuRi62szF2sh'
    '/pub?gid=292378871&single=true&output=csv'
)

# Fields to fill from Apify (only if empty in sheet)
FILLABLE = ['area', 'latitude', 'longitude', 'phone', 'website',
            'rating', 'review_count', 'hero_image', 'photos']

HOME = os.path.expanduser('~')


# ── Helpers ────────────────────────────────────────────────────────────────

def fetch_url(url, method='GET', body=None, headers=None):
    h = {'User-Agent': 'Mozilla/5.0'}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, data=body, headers=h, method=method)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode('utf-8', errors='replace')


def fetch_sheet_rows():
    text = fetch_url(FACILITIES_CSV)
    return list(csv.DictReader(io.StringIO(text)))


def fetch_apify_dataset(dataset_id):
    url = (f'https://api.apify.com/v2/datasets/{dataset_id}/items'
           f'?token={APIFY_TOKEN}&format=json&clean=true&limit=2000')
    text = fetch_url(url)
    return json.loads(text)


def extract_city(place):
    """
    Best-effort city/area extraction from Apify place record.
    Priority: neighborhood → city → addressParsed.city → first part of address.
    """
    nb = (place.get('neighborhood') or '').strip()
    if nb:
        return nb
    city = (place.get('city') or '').strip()
    if city:
        return city
    ap = place.get('addressParsed') or {}
    c = (ap.get('city') or ap.get('neighborhood') or '').strip()
    if c:
        return c
    addr = (place.get('address') or '').strip()
    parts = [p.strip() for p in re.split(r',', addr) if p.strip()]
    parts = [p for p in parts if not re.match(r'^\d{5}$', p) and p.lower() not in ('malaysia', 'my')]
    if len(parts) >= 2:
        return parts[-2]
    if parts:
        return parts[-1]
    return ''


def extract_fields(item):
    """Extract the fillable fields from an Apify result item."""
    area = extract_city(item)
    lat  = str(item.get('location', {}).get('lat') or '').strip()
    lng  = str(item.get('location', {}).get('lng') or '').strip()
    phone   = (item.get('phone') or '').strip()
    website = (item.get('website') or '').strip()
    rating  = str(item.get('totalScore') or '').strip()
    reviews = str(item.get('reviewsCount') or '').strip()

    imgs = []
    main_img = (item.get('imageUrl') or '').strip()
    if main_img:
        imgs.append(main_img)
    for img in (item.get('imageUrls') or []):
        url_img = (img.get('imageUrl') if isinstance(img, dict) else str(img)).strip()
        if url_img and url_img not in imgs:
            imgs.append(url_img)

    return {
        'area':         area,
        'latitude':     lat,
        'longitude':    lng,
        'phone':        phone,
        'website':      website,
        'rating':       rating,
        'review_count': reviews,
        'hero_image':   imgs[0] if imgs else '',
        'photos':       '|'.join(imgs[:10]),
    }


# ── Matching: Batch A (URL-based) ─────────────────────────────────────────

def build_apify_map_by_url(apify_items):
    """Build map: google_maps_url → extracted fields (Batch A)."""
    result = {}
    for item in apify_items:
        raw_url = (item.get('inputStartUrl') or item.get('url') or '').strip()
        if not raw_url:
            continue
        result[raw_url] = extract_fields(item)
    return result


# ── Matching: Batch B (name-query-based) ─────────────────────────────────

def tokenize(s):
    """Lowercase word tokens, strips punctuation."""
    return set(re.findall(r'[a-z0-9]+', s.lower()))


def name_similarity(a, b):
    """Fraction of tokens in the shorter string that appear in the longer."""
    ta, tb = tokenize(a), tokenize(b)
    if not ta or not tb:
        return 0.0
    shorter = ta if len(ta) <= len(tb) else tb
    longer  = ta if len(ta) > len(tb) else tb
    overlap = shorter & longer
    return len(overlap) / len(shorter)


def build_apify_map_by_query(apify_items, slug_map):
    """
    Build map: slug → extracted fields (Batch B).

    slug_map: dict of query_string → {slug, title} from batch_b_queries.json.
    Matches items by searchString (the query Apify used).
    Verifies by name similarity between result title and expected title.
    """
    result = {}
    unmatched = 0
    low_sim = 0

    for item in apify_items:
        search_str = (item.get('searchString') or '').strip()
        place_name = (item.get('title') or '').strip()

        if not search_str:
            unmatched += 1
            continue

        meta = slug_map.get(search_str)
        if not meta:
            # Try case-insensitive lookup
            meta = next((v for k, v in slug_map.items()
                         if k.lower() == search_str.lower()), None)
        if not meta:
            unmatched += 1
            continue

        sim = name_similarity(place_name, meta['title'])
        if sim < 0.4:
            low_sim += 1
            print(f"  LOW SIM ({sim:.2f}): query={search_str!r}, "
                  f"got={place_name!r}, expected={meta['title']!r}")
            continue

        result[meta['slug']] = extract_fields(item)

    if unmatched:
        print(f"  {unmatched} items had no matching query in slug_map")
    if low_sim:
        print(f"  {low_sim} items skipped (name similarity too low)")
    return result


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--batch',       choices=['a', 'b'], help='Which batch run to process')
    parser.add_argument('--dry-run',     action='store_true', help='Print updates, do not write')
    parser.add_argument('--csv-only',    action='store_true', help='Write updates CSV only')
    parser.add_argument('--dataset-id',  help='Override dataset ID')
    args = parser.parse_args()

    # Determine dataset ID and mode
    dataset_id = args.dataset_id
    batch_mode = args.batch  # 'a', 'b', or None

    if not dataset_id:
        if batch_mode == 'a':
            run_file = os.path.join(HOME, 'apify_run_batch_a.json')
        elif batch_mode == 'b':
            run_file = os.path.join(HOME, 'apify_run_batch_b.json')
        else:
            # Legacy: fall back to ~/apify_run.json
            run_file = os.path.join(HOME, 'apify_run.json')

        if not os.path.exists(run_file):
            sys.exit(f'ERROR: {run_file} not found. Pass --dataset-id explicitly or --batch a/b.')
        with open(run_file) as f:
            dataset_id = json.load(f)['datasetId']

    # Auto-detect batch mode from dataset if not specified
    if not batch_mode:
        # Check if batch_b dataset matches
        b_file = os.path.join(HOME, 'apify_run_batch_b.json')
        a_file = os.path.join(HOME, 'apify_run_batch_a.json')
        if os.path.exists(b_file):
            with open(b_file) as f:
                if json.load(f).get('datasetId') == dataset_id:
                    batch_mode = 'b'
        if not batch_mode and os.path.exists(a_file):
            with open(a_file) as f:
                if json.load(f).get('datasetId') == dataset_id:
                    batch_mode = 'a'
        if not batch_mode:
            batch_mode = 'a'  # default: URL-based matching
        print(f'Auto-detected batch mode: {batch_mode.upper()}')

    print(f'Batch {batch_mode.upper()} — dataset {dataset_id}')
    print(f'Fetching Apify dataset…')
    apify_items = fetch_apify_dataset(dataset_id)
    print(f'  {len(apify_items)} items returned')

    # Fetch sheet data
    print('Fetching current sheet data…')
    sheet_rows = fetch_sheet_rows()
    live = [r for r in sheet_rows
            if r.get('title') and r.get('status', '').strip() not in ('unverified', 'removed')
            and (r.get('slug') or '').strip()]
    print(f'  {len(live)} live facilities')

    # Build updates
    updates = {}  # slug → {field: new_value}

    if batch_mode == 'a':
        apify_map = build_apify_map_by_url(apify_items)
        print(f'  {len(apify_map)} unique URLs mapped')
        for row in live:
            maps_url = (row.get('google_maps_url') or '').strip()
            if not maps_url or maps_url not in apify_map:
                continue
            apify = apify_map[maps_url]
            slug  = row['slug'].strip()
            changed = {}
            for field in FILLABLE:
                current = (row.get(field) or '').strip()
                new_val  = (apify.get(field) or '').strip()
                if not current and new_val:
                    changed[field] = new_val
            if changed:
                updates[slug] = changed

    else:  # batch_mode == 'b'
        # Build slug_map from batch_b_queries.json
        b_queries_path = os.path.join(HOME, 'batch_b_queries.json')
        if not os.path.exists(b_queries_path):
            sys.exit(f'ERROR: {b_queries_path} not found.')
        with open(b_queries_path) as f:
            b_queries = json.load(f)
        slug_map = {item['query']: {'slug': item['slug'], 'title': item['title']}
                    for item in b_queries}
        print(f'  {len(slug_map)} query→slug mappings loaded')

        apify_map = build_apify_map_by_query(apify_items, slug_map)
        print(f'  {len(apify_map)} slugs matched')

        # Build row lookup: slug → row
        row_by_slug = {r['slug'].strip(): r for r in live if r.get('slug')}

        for slug, apify in apify_map.items():
            row = row_by_slug.get(slug)
            if not row:
                continue
            changed = {}
            for field in FILLABLE:
                current = (row.get(field) or '').strip()
                new_val  = (apify.get(field) or '').strip()
                if not current and new_val:
                    changed[field] = new_val
            if changed:
                updates[slug] = changed

    print(f'\nFacilities with updates: {len(updates)}')
    field_counts = {}
    for u in updates.values():
        for k in u:
            field_counts[k] = field_counts.get(k, 0) + 1
    for k, v in sorted(field_counts.items(), key=lambda x: -x[1]):
        print(f'  {k:<15} {v}')

    if args.dry_run:
        print('\nDRY RUN — no changes written.')
        for slug, u in list(updates.items())[:5]:
            print(f'  {slug}: {list(u.keys())}')
        return

    # Write CSV of updates
    csv_path = f'updates_apify_batch_{batch_mode}.csv'
    all_fields = ['slug'] + FILLABLE
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=all_fields, extrasaction='ignore')
        w.writeheader()
        for slug, changed in updates.items():
            row = {'slug': slug}
            row.update(changed)
            w.writerow(row)
    print(f'\nWrote {csv_path} ({len(updates)} rows)')

    if args.csv_only:
        print('CSV written. Import into Google Sheets manually if needed.')
        return

    # Write to Google Sheet via Sheets API
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        import googleapiclient.discovery

        token_file = os.path.join(os.path.dirname(__file__), 'token_sheets.json')
        with open(token_file) as f:
            t = json.load(f)
        creds = Credentials(
            token=t['token'], refresh_token=t['refresh_token'],
            token_uri=t['token_uri'], client_id=t['client_id'],
            client_secret=t['client_secret'], scopes=t['scopes'],
        )
        creds.refresh(Request())
        t['token']  = creds.token
        t['expiry'] = creds.expiry.isoformat() if creds.expiry else t.get('expiry', '')
        with open(token_file, 'w') as f:
            json.dump(t, f, indent=2)

        service = googleapiclient.discovery.build('sheets', 'v4', credentials=creds)

        result = service.spreadsheets().values().get(
            spreadsheetId=SHEET_ID,
            range=f"'{SHEET_TAB}'!1:1"
        ).execute()
        headers = result['values'][0]
        col_idx = {h: i for i, h in enumerate(headers)}

        slug_col = col_idx.get('slug', 1)
        slug_result = service.spreadsheets().values().get(
            spreadsheetId=SHEET_ID,
            range=f"'{SHEET_TAB}'!A:ZZ"
        ).execute()
        all_vals = slug_result.get('values', [])

        slug_to_row = {}
        for i, row_vals in enumerate(all_vals):
            if i == 0:
                continue
            if len(row_vals) > slug_col:
                s = row_vals[slug_col].strip()
                if s:
                    slug_to_row[s] = i + 1

        def col_letter(idx):
            result = ''
            idx += 1
            while idx:
                idx, r = divmod(idx - 1, 26)
                result = chr(65 + r) + result
            return result

        batch_data = []
        for slug, changed in updates.items():
            row_num = slug_to_row.get(slug)
            if not row_num:
                continue
            for field, val in changed.items():
                if field not in col_idx:
                    continue
                ci = col_idx[field]
                cell = f"'{SHEET_TAB}'!{col_letter(ci)}{row_num}"
                batch_data.append({'range': cell, 'values': [[val]]})

        if batch_data:
            print(f'Writing {len(batch_data)} cells to sheet…')
            service.spreadsheets().values().batchUpdate(
                spreadsheetId=SHEET_ID,
                body={'valueInputOption': 'USER_ENTERED', 'data': batch_data}
            ).execute()
            print(f'Done. {len(updates)} facilities updated in sheet.')
        else:
            print('No matching rows found in sheet.')

    except Exception as e:
        print(f'\nSheet write failed: {e}')
        print(f'Use --csv-only flag and import {csv_path} manually.')


if __name__ == '__main__':
    main()
