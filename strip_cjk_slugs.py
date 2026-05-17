"""
strip_cjk_slugs.py - clean facility rows whose title/slug contain CJK
(Han) characters or trailing dashes, then mirror the slug rename across
the Details tab.

Pre-push gate (validate.py) currently flags these as ERRORS because slugs
must match ^[a-z0-9]+(?:-[a-z0-9]+)*$.

What this does:
  1. Reads the Facilities tab and identifies rows where slug fails the
     validator regex.
  2. Strips Han characters from each title, normalises whitespace and
     punctuation, then derives a clean slug.
  3. Reports the rename map (old to new) for the operator to review.
  4. Writes title (col A) and slug (col B) to the sheet, slug-resolved
     per CLAUDE.md sheet-write rule.
  5. Mirrors the slug change in the Details tab.
  6. Prints the data.js branch references that still need a manual edit
     (GROUPS lists hard-coded slugs).

Run with --apply to actually write. Default is dry-run.
"""

import re, sys, time, unicodedata, argparse

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout.reconfigure(encoding='utf-8')

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
FAC_TAB = 'google-sheets-facilities.csv'
DETAILS_TAB = 'Details'
TOKEN_PATH = r'C:\Users\ibkaa\nursinghomeguide-my\Nursing Home Guide Malaysia\token_sheets.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

SLUG_RE = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')

# CJK Unified Ideographs + Extensions + CJK Symbols + Fullwidth Forms.
CJK_RE = re.compile(
    '[　-〿㐀-䶿一-鿿豈-﫿'
    '＀-￯㈀-㏿]'
)


def strip_cjk(s: str) -> str:
    return CJK_RE.sub('', s or '')


def clean_title(raw: str) -> str:
    """Strip CJK, fix common edge artefacts, collapse whitespace."""
    t = strip_cjk(raw)
    t = re.sub(r'\s*[|/]\s*', ' / ', t)
    t = re.sub(r'\(\s*\)', '', t)
    t = re.sub(r'\[\s*\]', '', t)
    # Collapse runs of stranded separators (e.g. " -  - " left by removed Hanzi).
    t = re.sub(r'(?:\s*[-/|]\s*){2,}', ' - ', t)
    # Drop a separator dangling between text and an opening bracket:
    # "Eldercare - (Cheras)" -> "Eldercare (Cheras)".
    t = re.sub(r'\s*[-/|,]\s*([(\[])', r' \1', t)
    # Insert a space when alnum butts directly against "(" after stripping.
    t = re.sub(r'(\w)\(', r'\1 (', t)
    t = re.sub(r'\(\s+', '(', t)
    t = re.sub(r'\s+\)', ')', t)
    t = re.sub(r'\s{2,}', ' ', t)
    t = t.strip(' \t /-|,')
    t = re.sub(r'\s*[\-/|,]+\s*$', '', t).strip()
    return t


def slugify(s: str) -> str:
    """Title to URL slug. ASCII-only, lowercase, dash-separated."""
    s = unicodedata.normalize('NFKD', s)
    s = s.encode('ascii', 'ignore').decode('ascii')
    s = s.lower()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    s = re.sub(r'-+', '-', s).strip('-')
    return s


def sheets():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    return build('sheets', 'v4', credentials=creds)


def fetch_facilities_grid(svc):
    return svc.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{FAC_TAB}'!A1:BV900"
    ).execute().get('values', [])


def build_rename_map(grid):
    hdr = grid[0]
    TITLE = hdr.index('title'); SLUG = hdr.index('slug'); STATUS = hdr.index('status')
    out = []
    all_live_slugs = set()
    for row in grid[1:]:
        row = row + [''] * (len(hdr) - len(row))
        if row[STATUS].strip(): continue
        s = row[SLUG]
        if s: all_live_slugs.add(s)
    for i, row in enumerate(grid[1:], start=2):
        row = row + [''] * (len(hdr) - len(row))
        if row[STATUS].strip(): continue
        s = row[SLUG]
        if not s or SLUG_RE.match(s):
            continue
        new_title = clean_title(row[TITLE])
        new_slug = slugify(new_title)
        if not new_slug:
            new_slug = slugify(strip_cjk(s))
        base = new_slug; n = 2
        while new_slug in all_live_slugs and new_slug != s:
            new_slug = f'{base}-{n}'; n += 1
        all_live_slugs.discard(s); all_live_slugs.add(new_slug)
        out.append((i, row[TITLE], new_title, s, new_slug))
    return out


def find_row_by_slug(svc, slug):
    col_b = svc.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{FAC_TAB}'!B:B"
    ).execute().get('values', [])
    for i, row in enumerate(col_b, start=1):
        if row and row[0].strip() == slug:
            return i
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true', help='Actually write to sheet (default: dry run)')
    args = ap.parse_args()

    svc = sheets()
    grid = fetch_facilities_grid(svc)
    renames = build_rename_map(grid)

    print(f'Affected rows: {len(renames)}\n')
    for row_num, ot, nt, os_, ns in renames:
        print(f'R{row_num:>3}')
        print(f'  title: {ot!r}')
        print(f'      -> {nt!r}')
        print(f'  slug:  {os_}')
        print(f'      -> {ns}')
        print()

    if not args.apply:
        print('Dry run. Re-run with --apply to write to the sheet.')
        return

    print('Writing to Facilities tab...')
    for row_num_csv, ot, nt, os_, ns in renames:
        live_row = find_row_by_slug(svc, os_)
        if not live_row:
            print(f'  SKIP {os_}: slug no longer in sheet (already renamed?)')
            continue
        if live_row != row_num_csv:
            print(f'  WARN row drift: csv said {row_num_csv}, live is {live_row}')
        svc.spreadsheets().values().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={
                'valueInputOption': 'RAW',
                'data': [
                    {'range': f"'{FAC_TAB}'!A{live_row}", 'values': [[nt]]},
                    {'range': f"'{FAC_TAB}'!B{live_row}", 'values': [[ns]]},
                ],
            }
        ).execute()
        verify = svc.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"'{FAC_TAB}'!B{live_row}"
        ).execute().get('values', [[None]])[0][0]
        if verify != ns:
            print(f'  FAIL R{live_row}: wrote {ns!r}, read {verify!r}')
        else:
            print(f'  ok   R{live_row}: {ns}')
        time.sleep(0.1)

    print('\nUpdating Details tab references...')
    details_grid = svc.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{DETAILS_TAB}'!A1:D2000"
    ).execute().get('values', [])
    if not details_grid:
        print('  Details tab empty?'); return
    dhdr = details_grid[0]
    DSLUG = dhdr.index('slug')
    rename_map = {os_: ns for _, _, _, os_, ns in renames}
    detail_updates = []
    for i, row in enumerate(details_grid[1:], start=2):
        if len(row) <= DSLUG: continue
        s = row[DSLUG].strip()
        if s in rename_map:
            new_s = rename_map[s]
            detail_updates.append({
                'range': f"'{DETAILS_TAB}'!A{i}",
                'values': [[new_s]],
            })
    if detail_updates:
        print(f'  {len(detail_updates)} Details rows to update')
        svc.spreadsheets().values().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={'valueInputOption': 'RAW', 'data': detail_updates}
        ).execute()
        print('  ok')
    else:
        print('  No Details rows referenced affected slugs.')

    print('\nManual follow-ups in data.js:')
    for os_, ns in rename_map.items():
        print(f"  s/{os_}/{ns}/")
    print('\nDone.')


if __name__ == '__main__':
    main()
