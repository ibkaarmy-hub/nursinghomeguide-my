"""
write_kl_sel_editorials.py
Generate honest, template-based editorial summaries for 269 KL/Selangor facilities
that currently have no editorial_summary.

Only states verified facts from the sheet — never invents details.
Batch-uploads to Google Sheet.
"""

import json, re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE     = 'token_sheets.json'
SCOPES         = ['https://www.googleapis.com/auth/spreadsheets']
TAB            = 'google-sheets-facilities.csv'

# ── Care type mapping ─────────────────────────────────────────────────────────

CARE_MAP = {
    'nursing home':          'nursing home',
    'assisted living':       'assisted living centre',
    'old people':            'care home for elderly residents',
    'retirement':            'retirement home',
    'rehabilitation':        'rehabilitation centre',
    'home health':           'home care service',
    'home care':             'home care service',
    'day care':              'senior day care centre',
    'hospice':               'hospice care centre',
    'dementia':              'dementia care home',
    'mental health':         'residential care home',
    'palliative':            'palliative care centre',
    'convalescent':          'convalescent home',
    'disability':            'care home',
    'welfare':               'welfare home',
    'shelter':               'residential shelter',
    'respite':               'respite care centre',
}

def get_care_label(care_types):
    """Return a clean care label from the care_types string."""
    if not care_types:
        return 'care home'
    ct = care_types.lower()
    for key, label in CARE_MAP.items():
        if key in ct:
            return label
    return 'care home'


def format_area(area, state):
    """Return a sensible location string, avoiding 'Selangor, Selangor'."""
    skip = {state.lower(), 'wilayah persekutuan', 'wp', ''}
    if not area or area.lower() in skip:
        return state
    return f"{area}, {state}"


def format_rating(rating, review_count):
    """Return rating sentence if data present."""
    try:
        r = float(rating)
        rc = int(review_count) if review_count else 0
        if r > 0:
            if rc > 0:
                return f"It holds a {r:.1f}/5 rating on Google Maps from {rc:,} reviews."
            else:
                return f"It holds a {r:.1f}/5 rating on Google Maps."
    except (ValueError, TypeError):
        pass
    return ''


def format_beds(beds):
    """Return bed count sentence if data present."""
    try:
        b = int(beds)
        if b > 0:
            return f"The home accommodates up to {b} residents."
    except (ValueError, TypeError):
        pass
    return ''


def format_subsidy(subsidy):
    if not subsidy:
        return ''
    s = subsidy.lower()
    if any(w in s for w in ['yes', 'available', 'jkm', 'government', 'subsidised', 'subsidized', 'oku']):
        return 'Subsidised placement may be available for eligible residents.'
    return ''


def format_religion(religion, title):
    if not religion:
        return ''
    r = religion.lower()
    label = None
    if 'christian' in r or 'church' in r or 'catholic' in r or 'methodist' in r:
        label = 'Christian'
    elif 'buddhist' in r or 'buddha' in r:
        label = 'Buddhist'
    elif 'islam' in r or 'muslim' in r:
        label = 'Muslim'
    elif 'hindu' in r or 'temple' in r:
        label = 'Hindu'
    elif 'multi' in r or 'all' in r:
        label = None  # don't specify — most homes accept all
    if label:
        return f"This is a {label}-affiliated home."
    return ''


def write_editorial(r):
    """Compose a 2–4 sentence editorial from sheet data."""
    name   = r['title']
    state  = r['state']
    area   = r.get('area', '')
    care   = r.get('care_types', '')
    beds   = r.get('total_beds', '')
    rating = r.get('rating', '')
    reviews = r.get('review_count', '')
    subsidy = r.get('subsidy', '')
    religion = r.get('religion', '')

    care_label = get_care_label(care)
    location   = format_area(area, state)

    sentences = []

    # Sentence 1: What it is and where
    article = 'an' if care_label[0] in 'aeiou' else 'a'
    sentences.append(f"{name} is {article} {care_label} located in {location}.")

    # Sentence 2: Beds (if known)
    beds_s = format_beds(beds)
    if beds_s:
        sentences.append(beds_s)

    # Sentence 3: Rating (if present)
    rating_s = format_rating(rating, reviews)
    if rating_s:
        sentences.append(rating_s)

    # Sentence 4: Subsidy or religion affiliation (pick one)
    subsidy_s = format_subsidy(subsidy)
    if subsidy_s:
        sentences.append(subsidy_s)
    else:
        rel_s = format_religion(religion, name)
        if rel_s:
            sentences.append(rel_s)

    return ' '.join(sentences)


# ── Load facilities ───────────────────────────────────────────────────────────

facilities = json.load(open('kl_sel_no_editorial.json', encoding='utf-8'))
print(f"Facilities to write editorials for: {len(facilities)}")

# ── Fetch sheet to get editorial_summary column index ────────────────────────

creds   = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
service = build('sheets', 'v4', credentials=creds)
ss      = service.spreadsheets()

data    = ss.values().get(
    spreadsheetId=SPREADSHEET_ID,
    range=f"'{TAB}'"
).execute().get('values', [])

headers = data[0]
col     = {h: i for i, h in enumerate(headers)}
ed_col  = col['editorial_summary']
print(f"editorial_summary col index: {ed_col} (col {chr(64 + ed_col + 1)})")
print()

# ── Generate editorials ───────────────────────────────────────────────────────

updates = []
for r in facilities:
    ed = write_editorial(r)
    row_num = r['row_idx']
    updates.append({
        'range': f"'{TAB}'!{chr(64 + ed_col + 1)}{row_num}",
        'values': [[ed]]
    })

# Preview first 10
print("SAMPLE EDITORIALS:")
for r, u in zip(facilities[:10], updates[:10]):
    print(f"\n  [{r['state']:15}] {r['title'][:45]}")
    print(f"  -> {u['values'][0][0]}")

# ── Upload ────────────────────────────────────────────────────────────────────

print(f"\n{len(updates)} editorials to upload")
confirm = input("Proceed? [y/N]: ").strip().lower()
if confirm != 'y':
    print("Aborted.")
    exit()

# Batch in chunks of 50 to avoid API limits
CHUNK = 50
total_updated = 0
for i in range(0, len(updates), CHUNK):
    chunk = updates[i:i+CHUNK]
    body = {'valueInputOption': 'RAW', 'data': chunk}
    result = ss.values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body=body
    ).execute()
    n = result.get('totalUpdatedCells', 0)
    total_updated += n
    print(f"  Chunk {i//CHUNK + 1}: {n} cells updated")

print(f"\nDone. {total_updated} editorials written.")
