"""Screen facility titles in column A and convert ALL-CAPS entries to Title Case.

Detection mirrors smart_title_case() in generate_facility_pages.py: a title is
considered ALL-CAPS only if it contains no Latin lowercase letter. Mixed-case
titles (e.g. "EHA Parkview Eldercare") are left untouched.

Usage:
  python fix_title_case.py            # dry-run, prints diff + writes _tmp/title_case_proposal.json
  python fix_title_case.py --apply    # writes fixes to the sheet using slug-safe pattern
"""

import sys, io, os, json, time, csv, urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Reuse the canonical implementation + acronym allowlist
from generate_facility_pages import smart_title_case

ENV_PATH = r'C:\Users\ibkaa\nursinghomeguide-my\Nursing Home Guide Malaysia\.env'
SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_PATH = r'C:\Users\ibkaa\nursinghomeguide-my\Nursing Home Guide Malaysia\token_sheets.json'
TAB = 'google-sheets-facilities.csv'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SHEET_URL = f'https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=292378871'
TITLE_COL = 'A'
SLUG_COL = 'B'


def find_row_by_slug(svc, slug):
    col_b = svc.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{TAB}'!{SLUG_COL}:{SLUG_COL}"
    ).execute().get('values', [])
    for i, row in enumerate(col_b, start=1):
        if row and row[0].strip() == slug:
            return i
    return None


def fetch_sheet():
    req = urllib.request.Request(SHEET_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return list(csv.reader(io.TextIOWrapper(r, encoding='utf-8')))


def is_all_caps(s):
    return bool(s) and not any('a' <= c <= 'z' for c in s) and any('A' <= c <= 'Z' for c in s)


def collect_proposals():
    rows = fetch_sheet()
    headers = rows[0]
    t_idx = headers.index('title')
    s_idx = headers.index('slug')
    state_idx = headers.index('state') if 'state' in headers else None
    status_idx = headers.index('status') if 'status' in headers else None

    proposals = []
    for r in rows[1:]:
        if len(r) <= max(t_idx, s_idx):
            continue
        title = r[t_idx].strip()
        slug = r[s_idx].strip()
        if not title or not slug:
            continue
        if not is_all_caps(title):
            continue
        new_title = smart_title_case(title)
        if new_title == title:
            continue
        proposals.append({
            'slug': slug,
            'old_title': title,
            'new_title': new_title,
            'state': r[state_idx].strip() if state_idx is not None and state_idx < len(r) else '',
            'status': r[status_idx].strip() if status_idx is not None and status_idx < len(r) else '',
        })
    return proposals


def main():
    apply = '--apply' in sys.argv
    mode = 'APPLY' if apply else 'DRY-RUN'
    print(f"=== fix_title_case.py [{mode}] ===\n")

    print("Fetching live sheet...")
    proposals = collect_proposals()
    print(f"Found {len(proposals)} ALL-CAPS titles to fix\n")

    for i, p in enumerate(proposals, 1):
        flag = f" [{p['status']}]" if p['status'] else ''
        print(f"[{i:3d}] {p['slug']} ({p['state']}){flag}")
        print(f"      OLD: {p['old_title']}")
        print(f"      NEW: {p['new_title']}")

    os.makedirs('_tmp', exist_ok=True)
    with open('_tmp/title_case_proposal.json', 'w', encoding='utf-8') as fh:
        json.dump(proposals, fh, indent=2, ensure_ascii=False)
    print(f"\nProposal written to _tmp/title_case_proposal.json ({len(proposals)} rows)")

    if not apply:
        print("\nDry-run only. Re-run with --apply to write to the sheet.")
        return

    print(f"\n--- Applying {len(proposals)} writes ---\n")
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    svc = build('sheets', 'v4', credentials=creds)

    # Single upfront read of A:B to build slug -> (row, current_title).
    ab = svc.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{TAB}'!A:B"
    ).execute().get('values', [])
    slug_map = {}
    for i, row in enumerate(ab, start=1):
        if len(row) >= 2 and row[1].strip():
            slug_map[row[1].strip()] = (i, row[0].strip() if row[0] else '')

    done, drifted, missing, already, retried = [], [], [], [], 0
    for i, p in enumerate(proposals, 1):
        slug = p['slug']
        entry = slug_map.get(slug)
        if entry is None:
            print(f"[{i:3d}] {slug}: NOT FOUND in sheet")
            missing.append(slug)
            continue
        row, current_title = entry
        if current_title == p['new_title']:
            print(f"[{i:3d}] {slug}: already fixed (skip)")
            already.append(slug)
            continue

        # Write title with retry on rate-limit
        for attempt in range(3):
            try:
                svc.spreadsheets().values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range=f"'{TAB}'!{TITLE_COL}{row}",
                    valueInputOption='RAW',
                    body={'values': [[p['new_title']]]},
                ).execute()
                break
            except Exception as e:
                if '429' in str(e) or 'RATE_LIMIT' in str(e):
                    print(f"      rate-limited, sleeping 30s and retrying...")
                    time.sleep(30)
                    retried += 1
                else:
                    raise
        else:
            print(f"[{i:3d}] {slug}: write failed after 3 retries")
            continue

        # Per-write verify (single read at B{row}) with retry
        verify_slug = ''
        for attempt in range(3):
            try:
                verify_slug = svc.spreadsheets().values().get(
                    spreadsheetId=SPREADSHEET_ID,
                    range=f"'{TAB}'!{SLUG_COL}{row}"
                ).execute().get('values', [['']])[0][0].strip()
                break
            except Exception as e:
                if '429' in str(e) or 'RATE_LIMIT' in str(e):
                    time.sleep(30)
                    retried += 1
                else:
                    raise

        if verify_slug != slug:
            print(f"[{i:3d}] {slug}: ROW DRIFT (row {row} now has slug '{verify_slug}')")
            drifted.append((slug, row, verify_slug))
            continue
        print(f"[{i:3d}] {slug}: wrote row {row}")
        done.append(slug)
        time.sleep(1.2)

    print(f"\nDone. {len(done)} written, {len(already)} already fixed, {len(missing)} missing, {len(drifted)} drifted, {retried} rate-limit retries.")
    if drifted:
        print("\nDrifted rows (title may have landed on wrong facility — investigate):")
        for slug, row, got in drifted:
            print(f"  row {row}: expected {slug}, got {got}")
    print("\nNext steps:")
    print("  1. python audit_state_enrichment.py   # sanity")
    print("  2. python generate_facility_pages.py && python generate_sitemap.py")
    print("  3. Commit + push.")


if __name__ == '__main__':
    main()
