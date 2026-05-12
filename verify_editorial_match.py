"""
Verify that each facility's editorial_summary actually describes that facility.

Detects two failure modes:
1. Editorial text contains place names from a different state (cross-state contamination)
2. Editorial text shares no significant words with the facility title (wrong-row write)

Output: flags rows that look misplaced so they can be restored or rewritten.
"""

import sys, io, csv, urllib.request, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
FAC_URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=292378871'

# Place markers per state (lowercase).
# Used to detect when an editorial mentions a place that doesn't belong to the row's state.
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

# Common stopwords from facility titles that don't help with matching
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


def make_getter(headers):
    idx = {h: i for i, h in enumerate(headers)}
    def g(row, col):
        i = idx.get(col)
        return (row[i] if i is not None and i < len(row) else '').strip()
    return g


def significant_words(title):
    """Strip stopwords, return list of meaningful words from a facility title."""
    # Normalise: lowercase, split on non-alphanumeric
    tokens = re.split(r'[^a-z0-9]+', title.lower())
    return [t for t in tokens if t and len(t) >= 3 and t not in TITLE_STOPWORDS]


def main():
    print("Fetching Facilities tab...", file=sys.stderr)
    rows = fetch_csv(FAC_URL)
    headers = rows[0]
    g = make_getter(headers)

    # CSV row index in sheet = data row index + 2 (header is row 1)
    flagged_cross_state = []  # editorial mentions another state's place names
    flagged_title_mismatch = []  # editorial shares no words with title
    total_checked = 0

    for i, row in enumerate(rows[1:], start=2):
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
        total_checked += 1

        editorial_lc = editorial.lower()

        # Check 1: cross-state contamination
        # For each other state, if its place markers appear AND none of the row's own state markers appear, flag.
        own_markers = STATE_MARKERS.get(state, [])
        own_hit = any(m in editorial_lc for m in own_markers)

        for other_state, markers in STATE_MARKERS.items():
            if other_state == state:
                continue
            # Skip Selangor/KL/Cheras overlap noise — they share urban geography
            if {state, other_state} == {'Selangor', 'Kuala Lumpur'}:
                continue
            hits = [m for m in markers if m in editorial_lc]
            if hits and not own_hit:
                flagged_cross_state.append({
                    'row': i, 'slug': slug, 'title': title, 'state': state,
                    'foreign_state': other_state, 'foreign_hits': hits,
                    'editorial_start': editorial[:200],
                })
                break  # one flag per row is enough

        # Check 2: title-word match in editorial
        words = significant_words(title)
        if words:
            matches = [w for w in words if w in editorial_lc]
            if not matches:
                flagged_title_mismatch.append({
                    'row': i, 'slug': slug, 'title': title, 'state': state,
                    'title_words': words,
                    'editorial_start': editorial[:200],
                })

    print(f"\n## Editorial integrity check — checked {total_checked} live rows with editorials\n")

    print(f"### Cross-state contamination ({len(flagged_cross_state)} rows)")
    print("Editorial mentions place names from a different Malaysian state, with no match to the row's own state.\n")
    for f in flagged_cross_state:
        print(f"- **Row {f['row']}** ({f['state']}) — `{f['slug']}`")
        print(f"  - Title: {f['title']}")
        print(f"  - Foreign state hits ({f['foreign_state']}): {', '.join(f['foreign_hits'])}")
        print(f"  - Editorial opening: \"{f['editorial_start']}...\"")
        print()

    print(f"\n### Title mismatch ({len(flagged_title_mismatch)} rows)")
    print("Editorial shares no significant words with the facility title — possibly wrong-row write.\n")
    for f in flagged_title_mismatch:
        print(f"- **Row {f['row']}** ({f['state']}) — `{f['slug']}`")
        print(f"  - Title: {f['title']}")
        print(f"  - Significant title words: {', '.join(f['title_words'])}")
        print(f"  - Editorial opening: \"{f['editorial_start']}...\"")
        print()

    # Union (rows flagged by either check)
    union_rows = {f['row'] for f in flagged_cross_state} | {f['row'] for f in flagged_title_mismatch}
    print(f"\n### Total unique flagged rows: {len(union_rows)}")
    print(f"### Rows OK: {total_checked - len(union_rows)} of {total_checked}")


if __name__ == '__main__':
    main()
