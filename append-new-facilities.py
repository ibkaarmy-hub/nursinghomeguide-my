#!/usr/bin/env python3
"""
Append 388 new JKM facilities to live Google Sheet.

Aligns CSV schema (81 cols, with old license_* names) with refactored sheet (74 cols).
Sets status=unverified so they're hidden from site until manually reviewed.

Usage:
  python3 append-new-facilities.py            # dry run
  python3 append-new-facilities.py --apply    # actually append rows
"""
import argparse
import csv
import json
import os
import sys
import urllib.parse
import urllib.request

REPO = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(REPO, 'token.json')
NEW_CSV = os.path.join(REPO, 'jkm-results', 'new_facilities_for_sheet.csv')
SHEET_ID = "1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk"
TAB_NAME = "google-sheets-facilities.csv"
TAB_ID = 292378871

# Schema mapping: CSV column → sheet column (post-refactor)
RENAME = {
    'license_number': 'licence_number',  # old US → existing British (already in sheet)
    'license_expiry': 'licence_expiry',
    'license_verification_date': 'licence_last_checked',
}

# Columns dropped from sheet — skip these in CSV
DROPPED = {
    'license_number',  # Was duplicate; now using licence_number directly (handled by RENAME)
    'license_category',
    'license_expiry_warning',
    'pricing_model',
    'nurse_in_charge',
    'acuity_level',
    'evidence_ref',
    'outreach_last_attempt',
    'outreach_notes',
    'hidden_costs',
}

# Reserved: only RENAME'd license_* are kept; others dropped
# license_number is in DROPPED but RENAME maps it → licence_number, that's correct
# Actually the CSV may have two license_number columns... let's check


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


def get_sheet_headers():
    rng = urllib.parse.quote(f"'{TAB_NAME}'!A1:CC1", safe='')
    resp = api_request('GET', f"/v4/spreadsheets/{SHEET_ID}/values/{rng}")
    return resp.get('values', [[]])[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()

    # Load new facilities CSV
    print(f"📥 Loading {NEW_CSV}")
    with open(NEW_CSV, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        csv_rows = list(reader)
        csv_headers = reader.fieldnames
    print(f"   {len(csv_rows)} rows, {len(csv_headers)} CSV columns")

    # Get current sheet headers
    print(f"\n📖 Fetching sheet headers...")
    sheet_headers = get_sheet_headers()
    print(f"   {len(sheet_headers)} sheet columns")

    # Map CSV → sheet rows
    print(f"\n🔄 Aligning CSV to sheet schema...")

    # Detect duplicate license_number in CSV (Britsh + US spelling)
    license_count = sum(1 for h in csv_headers if h in ('license_number', 'licence_number'))
    print(f"   licence/license_number columns in CSV: {license_count}")

    aligned_rows = []
    for row in csv_rows:
        out_row = []
        for col in sheet_headers:
            # Find value in CSV — try direct, then via RENAME, then empty
            val = row.get(col, '')
            if not val:
                # Check if there's an old-spelling version
                for old, new in RENAME.items():
                    if new == col and old in row:
                        val = row[old]
                        break
            out_row.append(val)

        # Force status=unverified so they're hidden until reviewed
        if 'status' in sheet_headers:
            status_idx = sheet_headers.index('status')
            out_row[status_idx] = 'unverified'

        # Mark JKM source
        if 'jkm_data_source' in sheet_headers:
            jkm_idx = sheet_headers.index('jkm_data_source')
            out_row[jkm_idx] = 'JKM 2026'

        aligned_rows.append(out_row)

    # Sample preview
    print(f"\n📝 Sample aligned row (slug={aligned_rows[0][sheet_headers.index('slug')]}):")
    for i, h in enumerate(sheet_headers):
        v = aligned_rows[0][i]
        if v:
            preview = str(v)[:60] + ('...' if len(str(v)) > 60 else '')
            print(f"   {h:30s} {preview}")

    # Show counts
    populated = {h: 0 for h in sheet_headers}
    for row in aligned_rows:
        for i, v in enumerate(row):
            if v:
                populated[sheet_headers[i]] += 1
    print(f"\n📊 Field fill rates (top filled):")
    for h in sorted(populated, key=lambda x: -populated[x])[:15]:
        if populated[h] > 0:
            print(f"   {h:30s} {populated[h]:>4}/{len(aligned_rows)}  ({100*populated[h]//len(aligned_rows)}%)")

    if not args.apply:
        print(f"\n💡 Run with --apply to append {len(aligned_rows)} rows to sheet")
        return

    # Append rows in batches of 100 to avoid 30s timeout
    print(f"\n⚙️  Appending {len(aligned_rows)} rows...")
    batch_size = 100
    rng = urllib.parse.quote(f"'{TAB_NAME}'!A:A", safe='')
    for i in range(0, len(aligned_rows), batch_size):
        batch = aligned_rows[i:i + batch_size]
        try:
            resp = api_request(
                'POST',
                f"/v4/spreadsheets/{SHEET_ID}/values/{rng}:append?valueInputOption=RAW&insertDataOption=INSERT_ROWS",
                body={'values': batch}
            )
            updates = resp.get('updates', {})
            n = updates.get('updatedRows', len(batch))
            print(f"   Batch {i // batch_size + 1}: {n} rows appended")
        except Exception as ex:
            print(f"   ❌ Batch {i // batch_size + 1} failed: {ex}")
            raise

    print(f"\n✅ Appended {len(aligned_rows)} new JKM facilities (all status=unverified)")
    print(f"\nNext steps:")
    print(f"  1. Manually review/verify facilities, change status to '' (live)")
    print(f"  2. python3 generate_facility_pages.py")
    print(f"  3. python3 generate_sitemap.py")


if __name__ == '__main__':
    main()
