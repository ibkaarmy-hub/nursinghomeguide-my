"""
Clear editorial_summary on rows where the editorial is misplaced (wrong facility).
Detection logic is the same as verify_editorial_match.py.

Follows the slug-by-slug live row resolution rule:
- find_row_by_slug() is called once per slug, immediately before the write
- After each write, column B is read back to verify the row hasn't drifted
"""

import sys, io, csv, urllib.request, re, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_PATH = r'C:\Users\ibkaa\nursinghomeguide-my\Nursing Home Guide Malaysia\token_sheets.json'
TAB = 'google-sheets-facilities.csv'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
FAC_URL = f'https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=292378871'

DRY_RUN = False  # set True to preview without clearing

STATE_MARKERS = {
    'Kedah': ['alor setar', 'kulim', 'sungai petani', 'langkawi', 'jitra', 'pokok sena', 'lunas', 'kuala nerang', 'kuala kedah', 'kedah'],
    'Kelantan': ['kota bharu', 'pengkalan chepa', 'machang', 'tumpat', 'kemumin', 'kelantan'],
    'Perlis': ['kangar', 'bohor mali', 'kaki bukit', 'batu bertangkup', 'perlis'],
    'Labuan': ['labuan'],
    'Sabah': ['kota kinabalu', 'sandakan', 'papar', 'likas', 'putatan', 'penampang', 'tawau', 'sabah', ' kk ', '(kk)', 'harrington', 'sibuga', 'pak tak'],
    'Sarawak': ['kuching', 'sibu', 'bintulu', 'miri', 'sarawak'],
    'Terengganu': ['kuala terengganu', 'dungun', 'marang', 'besut', 'jerteh', 'hulu terengganu', 'kg raja', 'terengganu'],
    'Pahang': ['kuantan', 'bentong', 'mentakab', 'pekan ', 'gambang', 'jengka', ' bera', 'raub', 'temerloh', 'pahang'],
    'Perak': ['ipoh', 'taiping', 'kampar', 'gopeng', 'tapah', 'kuala kangsar', 'sitiawan', 'teluk intan', 'parit buntar', 'perak'],
    'Johor': ['johor bahru', 'skudai', 'pasir gudang', 'kulai', 'batu pahat', 'muar', 'yong peng', 'pontian', 'tampoi', 'johor', ' jb ', '(jb)', 'medini', 'mount austin'],
    'Selangor': ['petaling jaya', ' pj ', '(pj)', 'subang', 'shah alam', 'klang', 'kajang', 'sungai long', 'rawang', 'ampang', 'puchong', 'cyberjaya', 'kepong', 'selangor', 'damansara', 'setia alam', 'kota kemuning'],
    'Kuala Lumpur': ['kuala lumpur', ' kl ', '(kl)', 'wangsa maju', 'setapak', 'bangsar', 'mont kiara', 'desa parkcity', 'bukit jalil', 'sri petaling', 'pandan'],
    'Negeri Sembilan': ['seremban', 'port dickson', 'nilai', 'senawang', 'mantin', 'negeri sembilan'],
    'Penang': ['george town', 'butterworth', 'bukit mertajam', 'sungai ara', 'bayan lepas', 'penang', 'pulau pinang'],
    'Melaka': ['melaka', 'malacca', 'ayer keroh', 'bukit beruang', 'muhibbah'],
}

TITLE_STOPWORDS = {
    'care', 'centre', 'center', 'home', 'homes', 'pusat', 'jagaan', 'sdn', 'bhd',
    'nursing', 'senior', 'elderly', 'elder', 'aged', 'orang', 'tua', 'warga', 'emas',
    'old', 'folks', 'folk', 'rumah', 'kebajikan', 'house', 'and', 'for', 'the', 'of',
    'a', 'an', 'in', 'at', 'by', 'pte', 'ltd', 'plt', 'enterprise', 'group', 'services',
    'service', 'aktiviti', 'pawe', 'malaysia', 'retirement', 'living', 'residence',
    'residences', 'cawangan', 'branch', 'no', 'sdn.', 'bhd.', 'sendirian', 'berhad',
    'persatuan', 'pertubuhan', 'limited', 'co', 'company',
}


def fetch_csv(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return list(csv.reader(io.TextIOWrapper(r, encoding='utf-8')))


def col_letter(n):
    result = ''
    while n > 0:
        n, r = divmod(n - 1, 26)
        result = chr(65 + r) + result
    return result


def significant_words(title):
    tokens = re.split(r'[^a-z0-9]+', title.lower())
    return [t for t in tokens if t and len(t) >= 3 and t not in TITLE_STOPWORDS]


def find_row_by_slug(svc, slug):
    """Live slug lookup. Returns 1-based sheet row or None."""
    col_b = svc.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{TAB}'!B:B"
    ).execute().get('values', [])
    for i, row in enumerate(col_b, start=1):
        if row and row[0].strip() == slug:
            return i
    return None


def main():
    print("Fetching Facilities tab...", file=sys.stderr)
    rows = fetch_csv(FAC_URL)
    headers = rows[0]
    idx = {h: i for i, h in enumerate(headers)}

    def g(row, col):
        i = idx.get(col)
        return (row[i] if i is not None and i < len(row) else '').strip()

    # Identify rows to clear
    to_clear = []
    for row in rows[1:]:
        slug = g(row, 'slug')
        if not slug:
            continue
        status = g(row, 'status').lower()
        if status in ('unverified', 'removed'):
            continue
        editorial = g(row, 'editorial_summary')
        if not editorial or len(editorial) < 100:
            continue

        title = g(row, 'title')
        state = g(row, 'state')
        editorial_lc = editorial.lower()

        flagged = False
        reason = None

        # Check 1: cross-state contamination
        own_markers = STATE_MARKERS.get(state, [])
        own_hit = any(m in editorial_lc for m in own_markers)
        for other_state, markers in STATE_MARKERS.items():
            if other_state == state:
                continue
            if {state, other_state} == {'Selangor', 'Kuala Lumpur'}:
                continue
            hits = [m for m in markers if m in editorial_lc]
            if hits and not own_hit:
                flagged = True
                reason = f"foreign={other_state}: {hits[:3]}"
                break

        # Check 2: title-word match
        if not flagged:
            words = significant_words(title)
            if words and not any(w in editorial_lc for w in words):
                flagged = True
                reason = f"no-title-words: {words[:5]}"

        if flagged:
            to_clear.append((slug, title, state, reason))

    print(f"\nFound {len(to_clear)} rows with misplaced editorials.\n")
    for slug, title, state, reason in to_clear:
        print(f"  [{state}] {slug}")
        print(f"    title: {title[:80]}")
        print(f"    reason: {reason}")

    if DRY_RUN:
        print("\nDRY_RUN=True — no changes made. Set DRY_RUN=False to clear.")
        return

    # --- Clear phase ---
    print(f"\nClearing {len(to_clear)} rows via live slug lookup...")
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    svc = build('sheets', 'v4', credentials=creds)

    # Get header row to find column letters
    live_headers = svc.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{TAB}'!1:1"
    ).execute().get('values', [[]])[0]
    ed_col = col_letter(live_headers.index('editorial_summary') + 1)
    upd_col = col_letter(live_headers.index('last_updated') + 1)
    print(f"editorial_summary column: {ed_col}, last_updated column: {upd_col}")

    cleared, not_found, drifted = [], [], []

    for slug, title, state, reason in to_clear:
        row = find_row_by_slug(svc, slug)
        if row is None:
            not_found.append(slug)
            print(f"  NOT FOUND: {slug}")
            continue

        svc.spreadsheets().values().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={'valueInputOption': 'RAW', 'data': [
                {'range': f"'{TAB}'!{ed_col}{row}", 'values': [['']]},
                {'range': f"'{TAB}'!{upd_col}{row}", 'values': [['']]},
            ]}
        ).execute()

        # Post-write verification
        verify = svc.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"'{TAB}'!B{row}"
        ).execute().get('values', [['']])[0][0].strip()
        if verify != slug:
            drifted.append((row, slug, verify))
            print(f"  ⚠ ROW DRIFT row {row}: expected '{slug}', got '{verify}'")
            continue

        cleared.append((row, slug))
        print(f"  cleared row {row}: {slug}")
        time.sleep(1)

    print(f"\nDone. Cleared {len(cleared)}, not found {len(not_found)}, drift {len(drifted)}.")
    if not_found:
        print("Not found slugs:")
        for s in not_found:
            print(f"  {s}")
    if drifted:
        print("Drifted rows (NOT cleared — investigate manually):")
        for r, want, got in drifted:
            print(f"  row {r}: expected {want}, got {got}")


if __name__ == '__main__':
    main()
