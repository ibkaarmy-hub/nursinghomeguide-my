"""
add_mdac_to_sheet.py
Append 82 verified-new MDAC facilities to the Google Sheet.
Drops: Sree Sai (already in sheet), Cahaya duplicate (exact copy).

Fields populated from MDAC data:
  title, slug, phone, total_beds, state
  area (parsed from address), website (if in MDAC)
  status = blank (live, same as existing KL/Selangor facilities)
"""

import csv
import re
from datetime import date
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE     = 'token_sheets.json'
SCOPES         = ['https://www.googleapis.com/auth/spreadsheets']
TAB            = 'google-sheets-facilities.csv'


# ── Helpers ───────────────────────────────────────────────────────────────────

def clean_name(raw):
    """Strip '- MYS' suffix and extra whitespace."""
    s = re.sub(r'\s*-\s*MYS\s*$', '', raw.strip())
    return s.strip()


def make_slug(name):
    """Convert name to URL slug."""
    s = name.lower()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'\s+', '-', s.strip())
    s = re.sub(r'-+', '-', s)
    return s[:80].rstrip('-')


def detect_state(row):
    """Assign state from MDAC state_detected + address heuristics."""
    sd = row['state_detected']
    if sd == 'Johor':
        return 'Johor'
    if sd == 'Selangor':
        return 'Selangor'
    # KL/Selangor — try to distinguish
    addr = row['address'].lower()
    # Postcode heuristic
    postcode = re.search(r'\b(\d{5})\b', addr)
    if postcode:
        pc = int(postcode.group(1))
        if 50000 <= pc <= 60999:
            return 'Kuala Lumpur'
        if (40000 <= pc <= 48999) or (63000 <= pc <= 68999):
            return 'Selangor'
    # Keyword heuristic
    kl_words = ['kuala lumpur', 'setapak', 'kepong', 'wangsa maju',
                 'cheras', 'titiwangsa', 'brickfields', 'bangsar',
                 'bukit bintang', 'ampang', 'awan dandan', 'segambut']
    sel_words = ['petaling jaya', 'pj', 'shah alam', 'subang', 'klang',
                 'kajang', 'sepang', 'rawang', 'selayang', 'puchong',
                 'kota damansara', 'damansara', 'bukit jalil']
    for w in kl_words:
        if w in addr:
            return 'Kuala Lumpur'
    for w in sel_words:
        if w in addr:
            return 'Selangor'
    return 'Selangor'  # default for unresolvable


def extract_area(address, state):
    """Extract a short area/district from the address."""
    if not address:
        return ''
    addr = address.lower()
    # Named district keywords (priority order)
    districts = [
        ('petaling jaya', 'Petaling Jaya'), ('shah alam', 'Shah Alam'),
        ('subang jaya', 'Subang Jaya'), ('subang', 'Subang'),
        ('klang', 'Klang'), ('kajang', 'Kajang'), ('puchong', 'Puchong'),
        ('ampang', 'Ampang'), ('cheras', 'Cheras'), ('kepong', 'Kepong'),
        ('setapak', 'Setapak'), ('wangsa maju', 'Wangsa Maju'),
        ('damansara', 'Damansara'), ('bangsar', 'Bangsar'),
        ('bukit jalil', 'Bukit Jalil'), ('kota damansara', 'Kota Damansara'),
        ('johor bahru', 'Johor Bahru'), ('jb', 'Johor Bahru'),
        ('batu pahat', 'Batu Pahat'), ('segamat', 'Segamat'),
        ('muar', 'Muar'), ('kluang', 'Kluang'), ('pontian', 'Pontian'),
        ('rawang', 'Rawang'), ('selayang', 'Selayang'), ('sepang', 'Sepang'),
        ('hulu langat', 'Hulu Langat'), ('ulu klang', 'Ulu Klang'),
    ]
    for key, label in districts:
        if key in addr:
            return label
    # Taman extraction
    taman = re.search(r'taman\s+([\w\s]{3,25}?)(?:\s*,|\s*\d)', address, re.I)
    if taman:
        return 'Taman ' + taman.group(1).strip().title()
    return state  # fallback to state name


# ── Load CSV ──────────────────────────────────────────────────────────────────

raw_rows = list(csv.DictReader(open('mdac_confirmed_new.csv', encoding='utf-8')))

# Deduplicate by (name, phone) — removes the Cahaya exact copy
seen = set()
rows = []
for r in raw_rows:
    key = (r['name'].strip(), r['phone'].strip())
    if key not in seen:
        seen.add(key)
        rows.append(r)

print(f"After dedup: {len(rows)} facilities (was {len(raw_rows)})")

# ── Fetch sheet ───────────────────────────────────────────────────────────────

creds   = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
service = build('sheets', 'v4', credentials=creds)
ss      = service.spreadsheets()

data    = ss.values().get(
    spreadsheetId=SPREADSHEET_ID,
    range=f"'{TAB}'"
).execute().get('values', [])

headers = data[0]
existing_rows = data[1:]

# Column indices
col = {h: i for i, h in enumerate(headers)}
print(f"Sheet has {len(existing_rows)} data rows")

# Collect existing slugs to detect conflicts
existing_slugs = {r[col['slug']] for r in existing_rows if col['slug'] < len(r)}
existing_phones = set()
for r in existing_rows:
    ph = r[col['phone']] if col['phone'] < len(r) else ''
    # last 8 digits
    digits = re.sub(r'\D', '', ph)
    if len(digits) >= 8:
        existing_phones.add(digits[-8:])

print(f"Existing slugs: {len(existing_slugs)}")
print()

# ── Build new rows ────────────────────────────────────────────────────────────

today    = date.today().strftime('%Y-%m-%d')
n_cols   = len(headers)
new_rows = []
skipped  = []

for r in rows:
    raw_name = r['name']
    title    = clean_name(raw_name)
    slug     = make_slug(title)
    phone    = r['phone'].strip()
    beds     = r['total_beds'].strip()
    website  = r['website'].strip()
    state    = detect_state(r)
    area     = extract_area(r['address'], state)

    # Conflict checks
    if slug in existing_slugs:
        # Append area suffix to make unique
        area_slug = re.sub(r'[^a-z0-9]', '-', area.lower())
        slug = f"{slug}-{area_slug}"
        slug = re.sub(r'-+', '-', slug)[:80].rstrip('-')
        if slug in existing_slugs:
            skipped.append((title, 'slug conflict even after suffix'))
            continue

    digits = re.sub(r'\D', '', phone)
    if len(digits) >= 8 and digits[-8:] in existing_phones:
        skipped.append((title, f'phone conflict: {phone}'))
        continue

    existing_slugs.add(slug)  # reserve

    # Build row (all columns, blank for unpopulated)
    row_data = [''] * n_cols
    row_data[col['title']]        = title
    row_data[col['slug']]         = slug
    row_data[col['area']]         = area
    row_data[col['phone']]        = phone
    row_data[col['total_beds']]   = beds
    row_data[col['last_updated']] = today
    row_data[col['state']]        = state
    row_data[col['status']]       = ''   # live
    if website:
        row_data[col['website']]  = website

    new_rows.append((title, slug, state, area, phone, beds, row_data))

# ── Print preview ─────────────────────────────────────────────────────────────

print(f"Facilities to add: {len(new_rows)}")
print(f"Skipped: {len(skipped)}")
if skipped:
    for t, reason in skipped:
        print(f"  SKIP: {t} — {reason}")

print()
for title, slug, state, area, phone, beds, _ in new_rows:
    print(f"  [{state:15}] {title[:45]:45} | {area:20} | {phone:15} | beds:{beds}")

# ── Append ────────────────────────────────────────────────────────────────────

if not new_rows:
    print("\nNothing to append.")
else:
    confirm = input(f"\nAppend {len(new_rows)} rows to sheet? [y/N]: ").strip().lower()
    if confirm != 'y':
        print("Aborted.")
        exit()

    values = [rd for _, _, _, _, _, _, rd in new_rows]
    result = ss.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{TAB}'",
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body={'values': values}
    ).execute()

    updated = result.get('updates', {}).get('updatedRows', 0)
    print(f"\nDone. {updated} rows appended.")
    print("Source: MDAC.my (MyAgeing directory), verified via address dedup check")

    # Save slugs for Apify scrape step
    with open('mdac_added_slugs.json', 'w') as f:
        import json
        out = [{'title': t, 'slug': s, 'state': st, 'area': a, 'phone': ph}
               for t, s, st, a, ph, _, _ in new_rows]
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"Slug list saved to mdac_added_slugs.json ({len(out)} entries)")
