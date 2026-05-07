#!/usr/bin/env python3
"""
Apply JKM enrichments to live Google Sheet via direct urllib API calls.
Bypasses google client library SSL issues in sandbox environments.

Reads:
  jkm-results/enrichment_proposed.json — 67 facilities, ~170 field updates

Writes:
  Direct cell updates via Sheets API batchUpdate

Usage:
  python3 apply-enrichments-direct.py            # dry run
  python3 apply-enrichments-direct.py --apply    # actually write
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request

REPO = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(REPO, 'token.json')
ENRICH_FILE = os.path.join(REPO, 'jkm-results', 'enrichment_proposed.json')
SHEET_ID = "1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk"
TAB_NAME = "google-sheets-facilities.csv"
TAB_ID = 292378871

# Map enrichment fields → sheet column names (after refactor)
# Some fields in enrichment JSON refer to old names — translate to new
FIELD_MAP = {
    'license_number': 'licence_number',  # old US spelling → new (already renamed)
    'license_expiry': 'licence_expiry',
    'validity_date': 'licence_expiry',  # JKM stores as range, goes into licence_expiry
    'license_verification_date': 'licence_last_checked',
    # Direct fields (no rename needed)
    'licence_number': 'licence_number',
    'licence_expiry': 'licence_expiry',
    'address': 'address',
    'email': 'email',
    'phone': 'phone',
    'latitude': 'latitude',
    'longitude': 'longitude',
    'google_maps_url': 'google_maps_url',
    'jkm_data_source': 'jkm_data_source',
    'website': 'website',
    'ownership_type': 'ownership_type',
    'area': 'area',
    'state': 'state',
}


def load_token():
    with open(TOKEN_FILE) as f:
        return json.load(f)


def save_token(t):
    with open(TOKEN_FILE, 'w') as f:
        json.dump(t, f, indent=2)


def refresh_access_token():
    t = load_token()
    data = urllib.parse.urlencode({
        'refresh_token': t['refresh_token'],
        'client_id': t['client_id'],
        'client_secret': t['client_secret'],
        'grant_type': 'refresh_token',
    }).encode()
    req = urllib.request.Request('https://oauth2.googleapis.com/token', data=data)
    with urllib.request.urlopen(req, timeout=15) as r:
        resp = json.loads(r.read().decode())
    t['token'] = resp['access_token']
    save_token(t)
    return t['token']


def api_request(method, path, body=None):
    t = load_token()
    token = t.get('token')

    def _try(token):
        url = f"https://sheets.googleapis.com{path}"
        data = json.dumps(body).encode() if body else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header('Authorization', f'Bearer {token}')
        if body:
            req.add_header('Content-Type', 'application/json')
        with urllib.request.urlopen(req, timeout=30) as r:
            content = r.read().decode()
            return json.loads(content) if content else {}

    try:
        return _try(token)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("🔄 Refreshing token...")
            token = refresh_access_token()
            return _try(token)
        else:
            print(f"❌ HTTP {e.code}: {e.read().decode()[:300]}")
            raise


def col_letter(idx):
    s = ''
    n = idx
    while True:
        s = chr(ord('A') + n % 26) + s
        n = n // 26 - 1
        if n < 0:
            break
    return s


def get_all_data():
    """Fetch all data including headers + slugs map."""
    rng = urllib.parse.quote(f"'{TAB_NAME}'!A1:CC", safe='')
    resp = api_request('GET', f"/v4/spreadsheets/{SHEET_ID}/values/{rng}")
    rows = resp.get('values', [])
    headers = rows[0]

    # Build slug → row_index map (1-based row number for sheets)
    slug_idx = headers.index('slug')
    slug_to_row = {}
    for i, row in enumerate(rows[1:], start=2):  # row 2 = first data row
        if len(row) > slug_idx:
            slug_to_row[row[slug_idx]] = i

    return headers, slug_to_row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true', help='Actually write changes (default: dry run)')
    args = ap.parse_args()

    print(f"📥 Loading enrichments from {ENRICH_FILE}")
    with open(ENRICH_FILE) as f:
        enrichments = json.load(f)
    print(f"   {len(enrichments)} facilities to enrich")

    print(f"\n📖 Fetching sheet data...")
    headers, slug_to_row = get_all_data()
    print(f"   {len(headers)} columns, {len(slug_to_row)} facilities")

    # Build update list
    updates = []  # list of (cell_range, value) tuples
    skipped_fields = set()
    matched = 0
    unmatched = []

    for e in enrichments:
        slug = e['slug']
        if slug not in slug_to_row:
            unmatched.append(slug)
            continue

        row = slug_to_row[slug]
        matched += 1

        # Mark as JKM-sourced
        if 'jkm_data_source' in headers:
            jkm_col = col_letter(headers.index('jkm_data_source'))
            updates.append((f"{jkm_col}{row}", 'JKM 2026'))

        for field, change in e.get('updates', {}).items():
            target_field = FIELD_MAP.get(field, field)
            if target_field not in headers:
                skipped_fields.add(field)
                continue

            col_idx = headers.index(target_field)
            cell = f"{col_letter(col_idx)}{row}"
            new_val = change.get('new', '')
            updates.append((cell, new_val))

    print(f"\n📊 Plan:")
    print(f"   Matched: {matched}/{len(enrichments)} facilities")
    if unmatched:
        print(f"   ⚠️  Unmatched slugs: {len(unmatched)} (showing first 5)")
        for s in unmatched[:5]:
            print(f"      • {s}")
    print(f"   Updates to write: {len(updates)} cells")
    if skipped_fields:
        print(f"   ⚠️  Skipped fields (not in schema): {sorted(skipped_fields)}")

    if not args.apply:
        print("\n💡 Run with --apply to execute these updates")
        # Show sample updates
        print(f"\n📝 Sample updates (first 10):")
        for cell, val in updates[:10]:
            preview = val[:60] + '...' if len(str(val)) > 60 else val
            print(f"   {cell}: {preview}")
        return

    # Apply updates in batches of 100 cells using batchUpdate (values API)
    print(f"\n⚙️  Applying {len(updates)} updates in batches...")
    batch_size = 100
    for i in range(0, len(updates), batch_size):
        batch = updates[i:i + batch_size]
        data = []
        for cell, val in batch:
            rng = f"'{TAB_NAME}'!{cell}"
            data.append({'range': rng, 'values': [[val]]})

        try:
            resp = api_request(
                'POST',
                f"/v4/spreadsheets/{SHEET_ID}/values:batchUpdate",
                body={'valueInputOption': 'RAW', 'data': data}
            )
            n_done = resp.get('totalUpdatedCells', len(batch))
            print(f"   Batch {i // batch_size + 1}: {n_done} cells updated")
        except Exception as ex:
            print(f"   ❌ Batch {i // batch_size + 1} failed: {ex}")
            raise

    print(f"\n✅ Enrichments applied: {len(updates)} cells across {matched} facilities")
    print(f"\nNext: Append 388 new JKM facilities (jkm-results/new_facilities_for_sheet.csv)")


if __name__ == '__main__':
    main()
