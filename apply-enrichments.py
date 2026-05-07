#!/usr/bin/env python3
"""
Apply JKM enrichments to live Google Sheet via Sheets API.

DRY RUN by default. Use --apply to actually write changes.

Setup:
  1. pip3 install google-auth google-auth-oauthlib google-api-python-client
  2. Place client_secret.json in repo root (or pass --creds path)
  3. First run will open browser for OAuth, then save token.json

Usage:
  python3 apply-enrichments.py                 # dry run, shows what would change
  python3 apply-enrichments.py --apply         # actually write changes
  python3 apply-enrichments.py --backup        # download current sheet first
"""
import argparse, csv, json, os, sys
from datetime import datetime

# Stdlib only — load creds without google libs first
SHEET_ID = "1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk"
TAB_NAME = "Facilities"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
ENRICH_FILE = os.path.join(REPO_ROOT, 'jkm-results', 'enrichment_proposed.json')

def get_service(client_secret_path, token_path):
    """OAuth flow + Sheets service. Caches token."""
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
    except ImportError:
        print("❌ Missing libraries. Run:")
        print("   pip3 install google-auth google-auth-oauthlib google-api-python-client")
        sys.exit(1)

    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(client_secret_path):
                print(f"❌ Client secret not found: {client_secret_path}")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as f:
            f.write(creds.to_json())
        print(f"✅ Token saved: {token_path}")

    return build('sheets', 'v4', credentials=creds)


def col_letter(idx):
    """0-based column index to A1 letter (A, B, ..., Z, AA, AB, ...)"""
    s = ''
    n = idx
    while True:
        s = chr(ord('A') + n % 26) + s
        n = n // 26 - 1
        if n < 0: break
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true', help='Actually write changes (default: dry run)')
    ap.add_argument('--backup', action='store_true', help='Download sheet to backup CSV first')
    ap.add_argument('--creds', default=os.path.join(REPO_ROOT, 'client_secret.json'),
                    help='Path to client_secret.json')
    ap.add_argument('--token', default=os.path.join(REPO_ROOT, 'token.json'),
                    help='Path to cache OAuth token')
    args = ap.parse_args()

    mode = '🔥 APPLY MODE' if args.apply else '🧪 DRY RUN'
    print(f"\n{mode}\n")

    # Load enrichments
    if not os.path.exists(ENRICH_FILE):
        print(f"❌ Run enrich-matches.py first to generate {ENRICH_FILE}")
        sys.exit(1)

    with open(ENRICH_FILE) as f:
        enrichments = json.load(f)
    print(f"📥 Loaded {len(enrichments)} enrichment plans")

    # Connect
    print(f"🔐 Authenticating...")
    svc = get_service(args.creds, args.token)
    sheets = svc.spreadsheets()

    # Read current sheet (header + all data)
    print(f"📥 Reading sheet '{TAB_NAME}'...")
    resp = sheets.values().get(spreadsheetId=SHEET_ID,
                                range=f"'{TAB_NAME}'!A:CC").execute()
    rows = resp.get('values', [])
    if not rows:
        print("❌ Sheet is empty?")
        sys.exit(1)

    headers = rows[0]
    data = rows[1:]
    print(f"   {len(data)} rows, {len(headers)} columns")

    # Backup
    if args.backup:
        backup_file = os.path.join(REPO_ROOT, f'sheet_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
        with open(backup_file, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerows(rows)
        print(f"💾 Backup saved: {backup_file}")

    # Add validity_date column if missing
    add_validity = 'validity_date' not in headers
    if add_validity:
        validity_col_idx = len(headers)
        print(f"➕ Adding 'validity_date' column at position {col_letter(validity_col_idx)}")
        if args.apply:
            sheets.values().update(
                spreadsheetId=SHEET_ID,
                range=f"'{TAB_NAME}'!{col_letter(validity_col_idx)}1",
                valueInputOption='RAW',
                body={'values': [['validity_date']]}
            ).execute()
            headers.append('validity_date')
    else:
        validity_col_idx = headers.index('validity_date')

    # Build slug → row index (1-based for sheet)
    try:
        slug_col = headers.index('slug')
    except ValueError:
        print("❌ No 'slug' column in sheet")
        sys.exit(1)

    slug_to_row = {}
    for i, r in enumerate(data, start=2):  # row 1 is header
        if slug_col < len(r):
            slug_to_row[r[slug_col]] = i

    print(f"📊 Indexed {len(slug_to_row)} rows by slug\n")

    # Build batch update requests
    batch_updates = []
    skipped = []

    for e in enrichments:
        slug = e['slug']
        if slug not in slug_to_row:
            skipped.append({'slug': slug, 'reason': 'slug not in sheet'})
            continue

        row_idx = slug_to_row[slug]

        for field, change in e['updates'].items():
            if field not in headers:
                if field == 'validity_date':  # we may have just added it
                    headers_now = headers
                else:
                    skipped.append({'slug': slug, 'reason': f'no column {field}'})
                    continue
            col_idx = headers.index(field)
            cell = f"'{TAB_NAME}'!{col_letter(col_idx)}{row_idx}"

            batch_updates.append({
                'range': cell,
                'values': [[change['new']]],
                '_meta': {  # not sent to API; for logging
                    'slug': slug,
                    'field': field,
                    'old': change['old'][:30] if change['old'] else '(empty)',
                    'new': change['new'][:40],
                }
            })

    print(f"🎯 {len(batch_updates)} cell updates queued")
    if skipped:
        print(f"⚠️  {len(skipped)} skipped:")
        for s in skipped[:5]:
            print(f"   {s['slug']}: {s['reason']}")

    # Show first 10 changes for sanity check
    print(f"\n📋 First 10 changes:")
    for u in batch_updates[:10]:
        m = u['_meta']
        print(f"   {m['slug'][:30]:30} {m['field']:20}  {m['old']:30} → {m['new']}")

    if not args.apply:
        print(f"\n🧪 DRY RUN — no changes applied. Re-run with --apply to write.")
        return

    # Apply batch update
    print(f"\n🔥 Writing {len(batch_updates)} changes...")
    body = {
        'valueInputOption': 'RAW',
        'data': [{'range': u['range'], 'values': u['values']} for u in batch_updates],
    }
    resp = sheets.values().batchUpdate(spreadsheetId=SHEET_ID, body=body).execute()
    print(f"✅ Updated {resp.get('totalUpdatedCells', 0)} cells across {resp.get('totalUpdatedRanges', 0)} ranges")
    print(f"   Total rows touched: {resp.get('totalUpdatedRows', 0)}")

if __name__ == '__main__':
    main()
