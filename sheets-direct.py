#!/usr/bin/env python3
"""
Direct Sheets API client using urllib (bypasses google client lib SSL issues
in some sandboxed environments).

Usage:
  python3 sheets-direct.py refresh                # refresh access token
  python3 sheets-direct.py headers                # show current headers
  python3 sheets-direct.py refactor --apply       # apply schema refactor
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
import csv
import io

REPO = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(REPO, 'token.json')
SHEET_ID = "1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk"
TAB_NAME = "google-sheets-facilities.csv"
TAB_ID = 292378871

DROP = [
    'license_number', 'license_category', 'license_expiry_warning',
    'pricing_model', 'nurse_in_charge', 'acuity_level', 'evidence_ref',
    'outreach_last_attempt', 'outreach_notes', 'hidden_costs',
]

RENAME = {
    'license_expiry': 'licence_expiry',
    'license_verification_date': 'licence_last_checked',
}

ADD = ['address', 'email', 'jkm_data_source']


def load_token():
    with open(TOKEN_FILE) as f:
        return json.load(f)


def save_token(t):
    with open(TOKEN_FILE, 'w') as f:
        json.dump(t, f, indent=2)


def refresh_access_token():
    t = load_token()
    if not t.get('refresh_token'):
        print("❌ No refresh_token in token.json — re-run oauth-init.py")
        sys.exit(1)

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
    print(f"✅ Refreshed (expires in {resp.get('expires_in', '?')}s)")
    return t['token']


def api_request(method, path, body=None):
    """Make a request to the Sheets API. Auto-refreshes token on 401."""
    t = load_token()
    token = t.get('token')

    def _do(token):
        url = f"https://sheets.googleapis.com{path}"
        data = json.dumps(body).encode() if body else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header('Authorization', f'Bearer {token}')
        if body:
            req.add_header('Content-Type', 'application/json')
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode()) if r.read else {}

    try:
        url = f"https://sheets.googleapis.com{path}"
        data = json.dumps(body).encode() if body else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header('Authorization', f'Bearer {token}')
        if body:
            req.add_header('Content-Type', 'application/json')
        with urllib.request.urlopen(req, timeout=30) as r:
            content = r.read().decode()
            return json.loads(content) if content else {}
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("🔄 Token expired, refreshing...")
            token = refresh_access_token()
            req = urllib.request.Request(
                f"https://sheets.googleapis.com{path}",
                data=json.dumps(body).encode() if body else None,
                method=method
            )
            req.add_header('Authorization', f'Bearer {token}')
            if body:
                req.add_header('Content-Type', 'application/json')
            with urllib.request.urlopen(req, timeout=30) as r:
                content = r.read().decode()
                return json.loads(content) if content else {}
        else:
            print(f"❌ HTTP {e.code}: {e.read().decode()[:300]}")
            raise


def get_headers():
    """Get header row (row 1) from Facilities tab."""
    # Sheet title contains special chars (dots) — wrap in single quotes
    rng = urllib.parse.quote(f"'{TAB_NAME}'!A1:CC1", safe='')
    resp = api_request('GET', f"/v4/spreadsheets/{SHEET_ID}/values/{rng}")
    return resp.get('values', [[]])[0]


def col_letter(idx):
    s = ''
    n = idx
    while True:
        s = chr(ord('A') + n % 26) + s
        n = n // 26 - 1
        if n < 0:
            break
    return s


def cmd_headers():
    headers = get_headers()
    print(f"📊 {len(headers)} columns:\n")
    for i, h in enumerate(headers):
        print(f"  {col_letter(i):>3}  {h}")


def cmd_refactor(apply_changes):
    headers = get_headers()
    print(f"📊 Current: {len(headers)} columns\n")

    # 1. Find columns to delete
    to_delete = []
    print(f"🗑️  DELETE columns:")
    for col_name in DROP:
        if col_name in headers:
            idx = headers.index(col_name)
            to_delete.append((idx, col_name))
            print(f"   {col_letter(idx):>3}  {col_name}")
        else:
            print(f"     ✗ {col_name} (not found)")

    # 2. Renames
    print(f"\n✏️  RENAME columns:")
    for old, new in RENAME.items():
        if old in headers:
            idx = headers.index(old)
            print(f"   {col_letter(idx):>3}  {old} → {new}")
        else:
            print(f"     ✗ {old} (not found)")

    # 3. Additions
    print(f"\n➕ ADD columns:")
    for col_name in ADD:
        if col_name in headers:
            print(f"     ✓ {col_name} (already exists)")
        else:
            print(f"      {col_name}")

    expected = len(headers) - len(to_delete) + len([c for c in ADD if c not in headers])
    print(f"\n📊 Result: {len(headers)} - {len(to_delete)} + {len([c for c in ADD if c not in headers])} = {expected} columns")

    if not apply_changes:
        print("\n💡 Run with --apply to execute these changes")
        return

    print(f"\n⚙️  APPLYING CHANGES...\n")

    # Sort deletions right-to-left to avoid index shifting
    to_delete.sort(reverse=True, key=lambda x: x[0])

    for idx, col_name in to_delete:
        print(f"   Deleting {col_letter(idx)} ({col_name})...", end=' ', flush=True)
        try:
            api_request('POST', f"/v4/spreadsheets/{SHEET_ID}:batchUpdate", body={
                'requests': [{
                    'deleteDimension': {
                        'range': {
                            'sheetId': TAB_ID,
                            'dimension': 'COLUMNS',
                            'startIndex': idx,
                            'endIndex': idx + 1
                        }
                    }
                }]
            })
            print("✅")
        except Exception as e:
            print(f"❌ {e}")
            raise

    # Re-fetch headers after deletions
    headers = get_headers()
    print(f"\n   Headers after deletions: {len(headers)}")

    # Renames
    print(f"\n   Renaming columns...")
    for old, new in RENAME.items():
        if old in headers:
            idx = headers.index(old)
            cell = f"{col_letter(idx)}1"
            print(f"      {cell} {old} → {new}...", end=' ', flush=True)
            try:
                rng = urllib.parse.quote(f"'{TAB_NAME}'!{cell}", safe='')
                url_path = f"/v4/spreadsheets/{SHEET_ID}/values/{rng}?valueInputOption=RAW"
                api_request('PUT', url_path, body={'values': [[new]]})
                print("✅")
            except Exception as e:
                print(f"❌ {e}")

    # Additions — append new columns at end
    headers = get_headers()
    cols_to_add = [c for c in ADD if c not in headers]
    if cols_to_add:
        print(f"\n   Adding {len(cols_to_add)} new columns at end...")
        # Use values append on row 1 starting after last column
        start_col = col_letter(len(headers))
        cell_range = f"'{TAB_NAME}'!{start_col}1"
        print(f"      Writing to {cell_range}: {cols_to_add}")
        try:
            rng = urllib.parse.quote(cell_range, safe='')
            url_path = f"/v4/spreadsheets/{SHEET_ID}/values/{rng}?valueInputOption=RAW"
            api_request('PUT', url_path, body={'values': [cols_to_add]})
            print("      ✅")
        except Exception as e:
            print(f"      ❌ {e}")

    # Final summary
    headers = get_headers()
    print(f"\n✅ Done! Sheet now has {len(headers)} columns")
    print(f"\nNext step: python3 apply-enrichments-direct.py --apply")


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['refresh', 'headers', 'refactor'])
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()

    if args.cmd == 'refresh':
        refresh_access_token()
    elif args.cmd == 'headers':
        cmd_headers()
    elif args.cmd == 'refactor':
        cmd_refactor(args.apply)
