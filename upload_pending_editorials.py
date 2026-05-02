"""
Ingest merged `pending_editorials/<date>-<n>.json` batch files and push their
`editorial_summary` text into the Google Sheet.

Workflow (after the editorial-rewrites routine has opened a PR and you've
merged it on GitHub):

    git pull --ff-only origin main
    python upload_pending_editorials.py            # dry-run preview
    python upload_pending_editorials.py --apply    # actually push to sheet
    git add pending_editorials && git commit -m "Archive uploaded editorial batches" && git push

Each processed batch file is moved to `pending_editorials/uploaded/` so it
isn't re-applied on the next run. Slugs that turned out to be missing or
already-removed in the sheet are reported but don't block the rest of the
batch.

The script is idempotent: re-running on already-uploaded data is a no-op
(the moved files won't match the glob pattern any more).
"""
import argparse
import csv
import io
import json
import shutil
import sys
from datetime import date
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE     = 'token_sheets.json'
SCOPES         = ['https://www.googleapis.com/auth/spreadsheets']
FAC_TAB        = 'google-sheets-facilities.csv'

PENDING_DIR    = Path('pending_editorials')
UPLOADED_DIR   = PENDING_DIR / 'uploaded'

META_FILES = {'_progress.json', '_blockers.json', '_done.json'}


def col_letter(n: int) -> str:
    s = ''
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true',
                    help='Actually push to the sheet. Default is a dry run.')
    args = ap.parse_args()

    if not PENDING_DIR.exists():
        print(f"Nothing to do — {PENDING_DIR}/ does not exist.")
        return

    batch_files = sorted(
        p for p in PENDING_DIR.glob('*.json')
        if p.name not in META_FILES and p.parent == PENDING_DIR
    )
    if not batch_files:
        print(f"No new batch files in {PENDING_DIR}/.")
        return

    print(f"Found {len(batch_files)} batch file(s) to ingest:")
    for p in batch_files:
        print(f"  {p}")

    # Collect all updates from all batch files
    updates = []  # list of dicts: {slug, title, editorial, source_file}
    for p in batch_files:
        try:
            data = json.loads(p.read_text(encoding='utf-8'))
        except Exception as e:
            print(f"  ⚠️  Skipping unreadable batch {p}: {e}")
            continue
        for f in data.get('facilities', []):
            slug = (f.get('slug') or '').strip()
            text = f.get('editorial_summary') or ''
            if not slug or not text:
                print(f"  ⚠️  {p.name}: skipping entry with missing slug or editorial")
                continue
            updates.append({
                'slug': slug,
                'title': f.get('title', ''),
                'editorial': text,
                'data_quality': f.get('data_quality', '?'),
                'source_file': p,
            })

    if not updates:
        print("Batch files contained no usable entries.")
        return

    print(f"\n{len(updates)} editorial(s) ready to upload.")

    # Authenticate + load sheet headers
    if not Path(TOKEN_FILE).exists():
        print(f"\n❌ {TOKEN_FILE} not found. Run from the repo root with the token in place.")
        sys.exit(1)

    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    ss = service.spreadsheets()

    fac = ss.values().get(
        spreadsheetId=SPREADSHEET_ID, range=f"'{FAC_TAB}'"
    ).execute().get('values', [])
    headers = fac[0]

    if 'editorial_summary' not in headers or 'slug' not in headers:
        print("❌ Expected 'slug' and 'editorial_summary' headers in facilities tab.")
        sys.exit(1)

    slug_i      = headers.index('slug')
    editorial_i = headers.index('editorial_summary')
    last_i      = headers.index('last_updated') if 'last_updated' in headers else None

    slug_to_row = {}
    for i, row in enumerate(fac[1:], start=2):
        if slug_i < len(row):
            slug_to_row[row[slug_i].strip()] = i

    # Build batch payload + report
    sheet_updates = []
    missing = []
    today = str(date.today())

    for u in updates:
        row_n = slug_to_row.get(u['slug'])
        if not row_n:
            missing.append(u['slug'])
            continue
        sheet_updates.append({
            'range': f"'{FAC_TAB}'!{col_letter(editorial_i+1)}{row_n}",
            'values': [[u['editorial']]]
        })
        if last_i is not None:
            sheet_updates.append({
                'range': f"'{FAC_TAB}'!{col_letter(last_i+1)}{row_n}",
                'values': [[today]]
            })

    print(f"\n  → {len(sheet_updates)} cell update(s) queued for {len(updates)-len(missing)} facilities")
    print(f"  → {len(missing)} slug(s) not found in sheet (likely removed or renamed)")
    if missing:
        for s in missing[:20]:
            print(f"      missing: {s}")
        if len(missing) > 20:
            print(f"      ... and {len(missing)-20} more")

    if not args.apply:
        print("\n[dry run] Re-run with --apply to push to the sheet.")
        return

    # Apply in chunks of 100
    print(f"\nPushing to sheet …")
    for start in range(0, len(sheet_updates), 100):
        batch = sheet_updates[start:start+100]
        ss.values().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={'valueInputOption': 'RAW', 'data': batch}
        ).execute()

    print(f"✅ Applied {len(sheet_updates)} cell updates")

    # Archive processed batch files so they don't get re-uploaded
    UPLOADED_DIR.mkdir(parents=True, exist_ok=True)
    archived = set()
    for u in updates:
        src = u['source_file']
        if src in archived: continue
        archived.add(src)
        dst = UPLOADED_DIR / src.name
        shutil.move(str(src), str(dst))
        print(f"  archived: {src.name} → {dst}")

    print(f"\n🎉 Done. Commit the moved files:")
    print(f"   git add pending_editorials && git commit -m 'Archive uploaded editorial batches' && git push")


if __name__ == '__main__':
    main()
