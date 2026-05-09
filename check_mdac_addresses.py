"""
check_mdac_addresses.py
Compare 84 "new" MDAC facilities against existing sheet to catch duplicates
that slipped past phone matching (different/missing phone number).

The sheet has no address column, so we compare on:
  1. Name token overlap (primary) — normalized title vs MDAC name
  2. Address keywords vs sheet 'area' column (secondary)

Output files:
  mdac_confirmed_new.csv   — no name match found (safe to add)
  mdac_possible_dupes.csv  — name overlap found (manual review needed)
"""

import csv
import re
import sys
from collections import defaultdict

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE = 'token_sheets.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
TAB = 'google-sheets-facilities.csv'

# Token overlap threshold: how many address tokens must match to flag as duplicate
# Higher = fewer false positives, more false negatives
THRESHOLD = 3


def normalize_name(name):
    """Normalize a facility name for comparison."""
    if not name:
        return set()
    s = name.lower()
    # Remove common suffixes/noise
    s = re.sub(r'\s*-\s*mys\b', '', s)          # " - MYS" MDAC suffix
    s = re.sub(r'\bsdn\s*bhd\b', '', s)
    s = re.sub(r'\b(nursing home|old folks home|care centre|care center|'
               r'home care|senior home|warga emas|orang tua|warga tua|'
               r'pusat jagaan|rumah jagaan|rumah orang tua|'
               r'persatuan kebajikan)\b', '', s)
    s = re.sub(r'[,.\-/#&\'\"()]', ' ', s)
    # Tokenize: keep tokens 3+ chars, skip generic words
    stop = {'dan', 'the', 'and', 'for', 'sdn', 'bhd', 'centre', 'center',
            'home', 'care', 'nursing', 'senior', 'malaysia', 'kuala',
            'lumpur', 'selangor', 'johor'}
    tokens = set(t for t in s.split() if len(t) >= 3 and t not in stop)
    return tokens


def token_overlap(a, b):
    """Number of tokens in common between two normalized name sets."""
    return len(a & b)


# ── Load MDAC new facilities ──────────────────────────────────────────────────
mdac_rows = list(csv.DictReader(open('mdac_new.csv', encoding='utf-8')))
print(f"Loaded {len(mdac_rows)} MDAC new facilities")

# ── Fetch sheet data ──────────────────────────────────────────────────────────
creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
service = build('sheets', 'v4', credentials=creds)
ss = service.spreadsheets()

data = ss.values().get(
    spreadsheetId=SPREADSHEET_ID,
    range=f"'{TAB}'"
).execute().get('values', [])

headers = data[0]
rows = data[1:]

# Find relevant columns
try:
    slug_col    = headers.index('slug')
    title_col   = headers.index('title')
    area_col    = headers.index('area')
    state_col   = headers.index('state')
    status_col  = headers.index('status')
except ValueError as e:
    print(f"ERROR: column not found: {e}")
    sys.exit(1)

# Build list of sheet facilities (skip permanently removed)
sheet_facilities = []
for row in rows:
    status = row[status_col] if status_col < len(row) else ''
    if status == 'removed':
        continue
    slug  = row[slug_col]   if slug_col  < len(row) else ''
    title = row[title_col]  if title_col < len(row) else ''
    area  = row[area_col]   if area_col  < len(row) else ''
    state = row[state_col]  if state_col < len(row) else ''
    sheet_facilities.append({
        'slug': slug, 'title': title, 'area': area,
        'state': state, 'status': status,
        '_tokens': normalize_name(title)
    })

print(f"Loaded {len(sheet_facilities)} sheet facilities (excl. removed)")
print()

# ── Compare addresses ─────────────────────────────────────────────────────────
confirmed_new   = []
possible_dupes  = []

for mrow in mdac_rows:
    mname  = mrow['name']
    mstate = mrow['state_detected']
    mtoks  = normalize_name(mname)

    best_overlap = 0
    best_match   = None

    for sf in sheet_facilities:
        overlap = token_overlap(mtoks, sf['_tokens'])
        if overlap > best_overlap:
            best_overlap = overlap
            best_match   = sf

    if best_overlap >= THRESHOLD:
        mrow['_match_reason'] = f'{best_overlap} name tokens overlap'
        mrow['_sheet_slug']   = best_match['slug']
        mrow['_sheet_title']  = best_match['title']
        mrow['_sheet_area']   = best_match['area']
        mrow['_overlap']      = best_overlap
        possible_dupes.append(mrow)
    else:
        mrow['_match_reason'] = f'best overlap only {best_overlap}'
        mrow['_sheet_slug']   = best_match['slug'] if best_match else ''
        mrow['_sheet_title']  = best_match['title'] if best_match else ''
        mrow['_sheet_area']   = best_match['area'] if best_match else ''
        mrow['_overlap']      = best_overlap
        confirmed_new.append(mrow)

# ── Print report ──────────────────────────────────────────────────────────────
print("=" * 70)
print(f"POSSIBLE DUPLICATES ({len(possible_dupes)}) — manual review needed")
print("=" * 70)
for r in possible_dupes:
    print(f"\n  MDAC: {r['name']}")
    print(f"        addr: {r['address']}")
    print(f"  SHEET ({r['_match_reason']}): {r['_sheet_title']}")
    print(f"        area: {r['_sheet_area']}")

print()
print("=" * 70)
print(f"CONFIRMED NEW ({len(confirmed_new)}) — not in sheet")
print("=" * 70)
for r in confirmed_new:
    print(f"  [{r['state_detected']:12}] {r['name'][:45]:45} | {r['address'][:50]}")

# ── Write CSV outputs ─────────────────────────────────────────────────────────
extra_cols = ['_match_reason', '_sheet_slug', '_sheet_title', '_sheet_area', '_overlap']
base_fields = list(mdac_rows[0].keys()) if mdac_rows else []
all_fields = base_fields + [c for c in extra_cols if c not in base_fields]

with open('mdac_confirmed_new.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=all_fields, extrasaction='ignore')
    w.writeheader()
    w.writerows(confirmed_new)

with open('mdac_possible_dupes.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=all_fields, extrasaction='ignore')
    w.writeheader()
    w.writerows(possible_dupes)

print()
print(f"Written: mdac_confirmed_new.csv ({len(confirmed_new)} rows)")
print(f"Written: mdac_possible_dupes.csv ({len(possible_dupes)} rows)")
