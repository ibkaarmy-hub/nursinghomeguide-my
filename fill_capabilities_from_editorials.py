"""Fill blank care_* and medical_* capability flags by regex-parsing the
editorial_summary text. Implements the Perak playbook (enrich_whatsapp_clinical.py
pattern documented in memory/feedback_patterns.md) site-wide.

Rules:
  - Only sets flags that are currently blank ('' or 'unknown')
  - Only sets to 'yes' on a confident regex match
  - Negation guard: skip match if preceded within 25 chars by "no ", "not ",
    "without ", "unable to", "doesn't ", "don't ", "cannot ", "lacks "
  - Slug-safe writes: find_row_by_slug + post-write verify (locked rule)
  - Conservative: false-negative >> false-positive (better to leave a flag
    blank than wrongly claim a facility provides a service it doesn't)
"""

import sys, io, re, csv, time, urllib.request
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

ENV_PATH = r'C:\Users\ibkaa\nursinghomeguide-my\Nursing Home Guide Malaysia\.env'
SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_PATH = r'C:\Users\ibkaa\nursinghomeguide-my\Nursing Home Guide Malaysia\token_sheets.json'
TAB = 'google-sheets-facilities.csv'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SHEET_URL = f'https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=292378871'

# Each pattern is intentionally specific enough to avoid generic mentions.
# Multiple patterns per flag = OR.
PATTERNS = {
    'care_nursing': [
        r'\bnursing\s+care\b',
        r'\b24[-\s]?hour\s+nursing\b',
        r'\bregistered\s+nurse',
        r'\b(?:rn|nurse)s?\s+on\s+(?:site|duty)',
        r'\bskilled\s+nursing\b',
    ],
    'care_dementia': [
        r'\bdementia\s+(?:care|residents|patients|unit|ward|sufferer|programme)',
        r'\balzheimer',
        r'\bmemory\s+care\b',
    ],
    'care_palliative': [
        r'\bpalliative\s+care\b',
        r'\bend[-\s]?of[-\s]?life\s+care\b',
        r'\bhospice\b',
    ],
    'care_rehab': [
        r'\bpost[-\s]?stroke\b',
        r'\brehabilitation\b',
        r'\bstroke\s+(?:recovery|patient|rehab)',
        r'\brehab\s+(?:services|programme|care|patient)',
        r'\bpost[-\s]?hospital(?:isation)?\s+(?:recovery|care)',
    ],
    'care_respite': [
        r'\brespite\s+care\b',
        r'\bshort[-\s]?term\s+stay',
        r'\bshort[-\s]?stay\b',
    ],
    'care_assisted': [
        r'\bday\s+care\b',
        r'\bassisted\s+living\b',
        r'\bday[-\s]?activity\s+(?:centre|center|programme)',
        r'\bdaytime\s+(?:programme|activities)',
    ],
    'medical_physio': [
        r'\bphysiotherapy\b',
        r'\bphysical\s+therapy\b',
        r'(?<![a-z])physio(?![a-z]|logy)',
    ],
    'medical_ot': [
        r'\boccupational\s+therapy\b',
    ],
    'medical_wound': [
        r'\bwound\s+(?:care|dressing|management|nursing)\b',
        r'\bpressure\s+sore\s+(?:management|care)',
        r'\bbedsore\s+(?:care|prevention|management)',
    ],
    'medical_peg': [
        r'\b(?:peg|nasogastric|nasal|nasogastric\s+tube|ryle)\s+(?:feeding|tube)',
        r'\btube[-\s]?fed',
        r'\bfeeding\s+tube\b',
        r'\bngt\b',
    ],
    'medical_dementia_unit': [
        r'\bdementia\s+(?:unit|ward|wing|floor|cluster)',
        r'\bmemory\s+care\s+(?:unit|ward|wing)',
    ],
    'medical_dialysis': [
        r'\bdialysis\b',
    ],
    'medical_oxygen': [
        r'\boxygen\s+(?:therapy|support|supply|concentrator|tank)',
        r'\bon\s+oxygen\b',
    ],
    'medical_meds': [
        r'\bmedication\s+(?:management|administration|monitoring)',
        r'\bdrug\s+administration\b',
    ],
}

NEGATION_PREFIX = re.compile(
    r'(?:^|[.\s])(?:no|not|without|unable\s+to|doesn[’\']t|don[’\']t|cannot|can[’\']t|lacks?|never)\s+\S*\s*$',
    re.IGNORECASE,
)


def _read_env(key):
    with open(ENV_PATH, 'r', encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line: continue
            k, _, v = line.partition('=')
            if k.strip() == key:
                return v.strip().strip('"').strip("'")
    raise RuntimeError(f"{key} not found")


def col_letter(n):
    s = ''
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def find_row_by_slug(svc, slug):
    col_b = svc.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=f"'{TAB}'!B:B"
    ).execute().get('values', [])
    for i, row in enumerate(col_b, 1):
        if row and row[0].strip() == slug:
            return i
    return None


def matches_with_negation_guard(text, pattern):
    """Return True if pattern matches text AND is NOT preceded by a negation
    within 25 chars."""
    for m in re.finditer(pattern, text, re.IGNORECASE):
        start = m.start()
        prefix = text[max(0, start - 25):start]
        if NEGATION_PREFIX.search(prefix):
            continue
        return True
    return False


def detect_capabilities(editorial):
    """Return set of flag names that should be set to 'yes'."""
    if not editorial or len(editorial) < 100:
        return set()
    text = editorial.lower()
    found = set()
    for flag, patterns in PATTERNS.items():
        for pat in patterns:
            if matches_with_negation_guard(text, pat):
                found.add(flag)
                break
    return found


def fetch_sheet():
    req = urllib.request.Request(SHEET_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return list(csv.reader(io.TextIOWrapper(r, encoding='utf-8')))


def main():
    rows = fetch_sheet()
    headers = rows[0]
    idx = {h: i for i, h in enumerate(headers)}
    g = lambda r, c: (r[idx[c]] if c in idx and idx[c] < len(r) else '').strip()

    def is_set(v):
        return v.strip().lower() in ('yes', 'true', 'y', '1')

    # First pass: identify all writes needed (don't open API connection yet)
    pending = []
    for r in rows[1:]:
        slug = g(r, 'slug')
        if not slug: continue
        if g(r, 'status').lower() in ('unverified', 'removed'): continue
        ed = g(r, 'editorial_summary')
        if not ed or len(ed) < 200: continue

        detected = detect_capabilities(ed)
        if not detected: continue

        # Only set flags that are currently NOT 'yes'
        to_set = {f for f in detected if not is_set(g(r, f))}
        if to_set:
            pending.append({'slug': slug, 'title': g(r, 'title'),
                            'state': g(r, 'state'), 'flags': sorted(to_set)})

    print(f"Detected {len(pending)} facilities with fillable capability flags")
    total_flags = sum(len(p['flags']) for p in pending)
    print(f"Total flag-writes: {total_flags}\n")

    by_flag = Counter()
    for p in pending:
        for f in p['flags']:
            by_flag[f] += 1
    print("Per-flag breakdown:")
    for f, n in by_flag.most_common():
        print(f"  {f:<25} {n}")
    print()

    # Confirm before writing
    if '--dry' in sys.argv:
        print("DRY RUN — no writes performed.")
        return

    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    svc = build('sheets', 'v4', credentials=creds)
    live_header = svc.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=f"'{TAB}'!1:1"
    ).execute().get('values', [[]])[0]
    upd_col = col_letter(live_header.index('last_updated') + 1)
    flag_cols = {f: col_letter(live_header.index(f) + 1) for f in PATTERNS}
    today = '2026-05-13'

    done, drifted, errored = 0, 0, 0
    for i, p in enumerate(pending, 1):
        slug = p['slug']
        row = find_row_by_slug(svc, slug)
        if row is None:
            print(f"  ✗ NOT FOUND: {slug}")
            errored += 1
            continue

        data = [{'range': f"'{TAB}'!{upd_col}{row}", 'values': [[today]]}]
        for flag in p['flags']:
            c = flag_cols[flag]
            data.append({'range': f"'{TAB}'!{c}{row}", 'values': [['yes']]})

        svc.spreadsheets().values().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={'valueInputOption': 'RAW', 'data': data}
        ).execute()

        verify = svc.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range=f"'{TAB}'!B{row}"
        ).execute().get('values', [['']])[0][0].strip()
        if verify != slug:
            print(f"  ⚠ DRIFT row {row}: expected {slug}, got {verify}")
            drifted += 1
            continue

        done += 1
        if i % 25 == 0:
            print(f"  [{i}/{len(pending)}] {slug} → {','.join(p['flags'])}")
        # Sleep ≥2.5s — Sheets API quota is 60 reads/min/user and each
        # row costs 2 reads (find_row_by_slug + post-write verify).
        time.sleep(2.5)

    print(f"\n=== Done. {done} written, {drifted} drift, {errored} not-found ===")


if __name__ == '__main__':
    main()
