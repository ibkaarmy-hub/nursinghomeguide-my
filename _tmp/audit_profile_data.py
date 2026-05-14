"""
Deep profile-data audit for nursinghomeguide-my.

Reads facilities_local.csv (Facilities tab snapshot) and runs these checks:
  1. Editorial cross-leak
       1a. cross-state markers (editorial mentions another state's towns)
       1b. editorial shares no significant words with the facility title
     (a 1c "foreign brand phrase" sub-check was prototyped and dropped — facility
      titles contain town names, so editorials legitimately mentioning their own
      town produced ~95% false positives. Check 7a is the reliable identity check.)
  2. Address completeness proxy (no place_id / no area / unknown state)
  3. Website cross-leak (shared domain / foreign brand token across non-chain slugs)
  4. Shared assets across non-chain slugs (phone, place_id, hero_image, website)
  5. Unknown-state rows
  6. Title vs slug incoherence
  7. Places API ground-truth re-verify -- needs GOOGLE_MAPS_KEY
       7a. wrong-facility place_id  (Google name != sheet title)        P0
       7b. dead / not-found place_id                                   P1
       7c. sheet state wrong        (name matches, state differs)       P1
       7d. phone / website drift    (name+state ok, contact differs)    P2
  8. Address recovery suggestions for rows missing place_id -- needs GOOGLE_MAPS_KEY

Writes audit_report_2026-05-14.md. Read-only: no sheet writes, no fixes.
Places API responses are cached to _tmp/audit_places_cache.json so re-runs are fast.

STATE_MARKERS / TITLE_STOPWORDS / significant_words copied verbatim from
verify_editorial_match.py (lines 19-67).
"""

import sys, io, os, csv, re, json, time, difflib, urllib.request, urllib.parse
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

CSV_PATH = 'facilities_local.csv'
DATA_JS = 'data.js'
REPORT_PATH = 'audit_report_2026-05-14.md'
PLACES_CACHE = '_tmp/audit_places_cache.json'
CSV_SNAPSHOT = '2026-05-12 13:56 +0800'
MAPS_KEY = os.environ.get('GOOGLE_MAPS_KEY', '').strip()

# ── copied verbatim from verify_editorial_match.py lines 19-46 ──────────────
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

# Extra stopwords for the cross-row brand-phrase check: generic care vocabulary and
# place names that legitimately appear in many editorials. A brand phrase built only
# from these is not distinctive.
GENERIC_EDITORIAL_WORDS = {
    'post', 'stroke', 'rehabilitation', 'rehab', 'surgery', 'recovery', 'palliative',
    'dementia', 'day', 'respite', 'assisted', 'medical', 'health', 'healthcare',
    'family', 'loving', 'happy', 'golden', 'green', 'sunshine', 'grace', 'caring',
    'private', 'licensed', 'jkm', 'malaysian', 'community', 'taman', 'jalan', 'bandar',
    'kampung', 'klang', 'valley', 'peninsular', 'east', 'west', 'north', 'south',
}


def significant_words(title):
    """Strip stopwords, return list of meaningful words from a facility title."""
    tokens = re.split(r'[^a-z0-9]+', (title or '').lower())
    return [t for t in tokens if t and len(t) >= 3 and t not in TITLE_STOPWORDS]
# ───────────────────────────────────────────────────────────────────────────


def load_groups():
    """Parse GROUPS branch slug lists from data.js -> slug -> group_index map."""
    src = open(DATA_JS, encoding='utf-8').read()
    start = src.index('const GROUPS = {')
    end = src.index('const GROUPS_BY_SLUG')
    block = src[start:end]
    by_slug = {}
    for gi, b in enumerate(re.findall(r"branches:\s*\[(.*?)\]", block, re.S)):
        for s in re.findall(r"'([^']+)'", b):
            by_slug[s] = gi
    return by_slug


def same_chain(slug_a, slug_b, groups):
    ga, gb = groups.get(slug_a), groups.get(slug_b)
    return ga is not None and ga == gb


def domain_of(url):
    if not url:
        return ''
    u = url.strip().lower()
    u = re.sub(r'^https?://', '', u)
    u = re.sub(r'^www\.', '', u)
    return u.split('/')[0].split('?')[0]


def phone_digits(p):
    d = re.sub(r'\D', '', p or '').lstrip('0')
    if d.startswith('60'):
        d = d[2:]
    return d


def place_id_of(maps_url):
    m = re.search(r'query_place_id=([A-Za-z0-9_-]+)', maps_url or '')
    return m.group(1) if m else ''


def places_get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.load(r)


def places_details(pid):
    fields = 'name,formatted_address,formatted_phone_number,international_phone_number,website'
    url = ('https://maps.googleapis.com/maps/api/place/details/json'
           f'?place_id={urllib.parse.quote(pid)}&fields={fields}&key={MAPS_KEY}')
    return places_get(url)


def places_textsearch(query):
    url = ('https://maps.googleapis.com/maps/api/place/textsearch/json'
           f'?query={urllib.parse.quote(query)}&key={MAPS_KEY}')
    return places_get(url)


# Maps the state component of a Google formatted_address to our canonical state name.
STATE_ALIASES = {
    'pulau pinang': 'Penang', 'penang': 'Penang',
    'johor': 'Johor', 'johor darul takzim': 'Johor', "johor darul ta'zim": 'Johor',
    'kuala lumpur': 'Kuala Lumpur', 'wilayah persekutuan kuala lumpur': 'Kuala Lumpur',
    'wp kuala lumpur': 'Kuala Lumpur', 'federal territory of kuala lumpur': 'Kuala Lumpur',
    'negeri sembilan': 'Negeri Sembilan',
    'melaka': 'Melaka', 'malacca': 'Melaka',
    'selangor': 'Selangor', 'selangor darul ehsan': 'Selangor',
    'perak': 'Perak', 'perak darul ridzuan': 'Perak',
    'pahang': 'Pahang', 'pahang darul makmur': 'Pahang',
    'kedah': 'Kedah', 'kedah darul aman': 'Kedah',
    'kelantan': 'Kelantan', 'kelantan darul naim': 'Kelantan',
    'terengganu': 'Terengganu', 'terengganu darul iman': 'Terengganu',
    'perlis': 'Perlis', 'perlis indera kayangan': 'Perlis',
    'sabah': 'Sabah', 'sarawak': 'Sarawak',
    'labuan': 'Labuan', 'wp labuan': 'Labuan', 'wilayah persekutuan labuan': 'Labuan',
}


def state_in_address(addr):
    """Return the Malaysian state from a Google formatted_address, or ''.
    Google addresses end '..., <City>, <State>, Malaysia' — parse the comma
    components from the end so street names like 'Jln Perak' don't false-match."""
    if not addr:
        return ''
    parts = [p.strip().lower() for p in addr.split(',')]
    for p in reversed(parts):
        if not p or p == 'malaysia':
            continue
        p = re.sub(r'^\d{4,6}\s*', '', p).strip()  # drop leading postcode
        if p in STATE_ALIASES:
            return STATE_ALIASES[p]
        for alias, st in STATE_ALIASES.items():
            if alias in p:
                return st
    return ''


def names_match(sheet_title, g_name):
    """True if a Google Places displayName plausibly refers to the same facility
    as the sheet title. Tolerant of: all-stopword titles ('The Senior Care'),
    substring names ('Kenneth Care Home' vs 'Pusat Jagaan Kenneth Care Home PLT'),
    appended Chinese, and punctuation ('G.M' vs 'GM'). A False here means the
    place_id genuinely points at a differently-named facility."""
    norm = lambda s: re.sub(r'[^a-z0-9]+', ' ', (s or '').lower()).strip()
    ns, ng = norm(sheet_title), norm(g_name)
    if not ns or not ng:
        return True  # can't judge
    nsc, ngc = ns.replace(' ', ''), ng.replace(' ', '')
    if nsc in ngc or ngc in nsc:
        return True
    ts = [t for t in ns.split() if len(t) >= 3 and t not in TITLE_STOPWORDS]
    tg = [t for t in ng.split() if len(t) >= 3 and t not in TITLE_STOPWORDS]

    def tok_match(a, b):
        if a == b:
            return True
        if len(a) >= 4 and len(b) >= 4 and (a in b or b in a):
            return True
        return difflib.SequenceMatcher(None, a, b).ratio() >= 0.85

    if ts and tg:
        small, large = (ts, tg) if len(ts) <= len(tg) else (tg, ts)
        matched = sum(1 for a in small if any(tok_match(a, b) for b in large))
        return matched / len(small) >= 0.5
    # one or both distinctive sets empty (all-stopword title) -> char-level
    return difflib.SequenceMatcher(None, nsc, ngc).ratio() >= 0.80


def fetch_places(live, g):
    """Fetch (or load from cache) Places Details for place_id rows and Text Search
    for rows without one. Returns (details_by_pid, textsearch_by_slug, places_ok)."""
    cache = {}
    if os.path.exists(PLACES_CACHE):
        cache = json.load(open(PLACES_CACHE, encoding='utf-8'))
        print(f'Loaded Places cache ({len(cache)} entries)', file=sys.stderr)

    if not MAPS_KEY and not cache:
        return {}, {}, False

    # probe only if we have a key and need to fetch anything
    details_by_pid, textsearch_by_slug = {}, {}
    with_pid = [(r, place_id_of(g(r, 'google_maps_url'))) for r in live]
    with_pid = [(r, p) for r, p in with_pid if p]
    without_pid = [r for r in live if not place_id_of(g(r, 'google_maps_url'))]

    need_fetch = any(f'd:{p}' not in cache for _, p in with_pid) or \
                 any(f't:{r["slug"]}' not in cache for r in without_pid)
    places_ok = bool(cache)

    if need_fetch and MAPS_KEY:
        try:
            probe = places_details('ChIJ9w8kKOpLzDERD1E50h7wAoE')
            places_ok = probe.get('status') == 'OK'
        except Exception as e:
            print(f'Places probe failed: {e}', file=sys.stderr)
            places_ok = bool(cache)

    if places_ok and MAPS_KEY:
        todo_d = [(r, p) for r, p in with_pid if f'd:{p}' not in cache]
        print(f'Check 7: fetching {len(todo_d)} place_id lookups '
              f'({len(with_pid) - len(todo_d)} cached)...', file=sys.stderr)
        for r, pid in todo_d:
            try:
                cache[f'd:{pid}'] = places_details(pid)
            except Exception as e:
                cache[f'd:{pid}'] = {'status': 'FETCH_ERROR', 'error': str(e)}
            time.sleep(0.12)

        todo_t = [r for r in without_pid if f't:{r["slug"]}' not in cache]
        print(f'Check 8: fetching {len(todo_t)} text searches '
              f'({len(without_pid) - len(todo_t)} cached)...', file=sys.stderr)
        for r in todo_t:
            q = f"{g(r,'title')}, {g(r,'state')}, Malaysia"
            try:
                cache[f't:{r["slug"]}'] = places_textsearch(q)
            except Exception as e:
                cache[f't:{r["slug"]}'] = {'status': 'FETCH_ERROR', 'error': str(e)}
            time.sleep(0.12)

        os.makedirs(os.path.dirname(PLACES_CACHE), exist_ok=True)
        json.dump(cache, open(PLACES_CACHE, 'w', encoding='utf-8'))
        print(f'Saved Places cache ({len(cache)} entries)', file=sys.stderr)

    for r, pid in with_pid:
        if f'd:{pid}' in cache:
            details_by_pid[r['slug']] = (pid, cache[f'd:{pid}'])
    for r in without_pid:
        if f't:{r["slug"]}' in cache:
            textsearch_by_slug[r['slug']] = cache[f't:{r["slug"]}']

    return details_by_pid, textsearch_by_slug, bool(cache)


def main():
    rows = list(csv.DictReader(open(CSV_PATH, encoding='utf-8')))
    groups = load_groups()

    live = []
    for i, r in enumerate(rows):
        r['_csvrow'] = i + 2
        st = (r.get('status') or '').strip().lower()
        if st in ('unverified', 'removed'):
            continue
        if not (r.get('slug') or '').strip():
            continue
        live.append(r)

    g = lambda r, k: (r.get(k) or '').strip()

    # ── CHECK 1: editorial cross-leak ──────────────────────────────────────
    c1_crossstate, c1_titlemis = [], []
    for r in live:
        ed = g(r, 'editorial_summary')
        if not ed or len(ed) < 100:
            continue
        title, state = g(r, 'title'), g(r, 'state')
        ed_lc = ed.lower()

        own = STATE_MARKERS.get(state, [])
        own_hit = any(m in ed_lc for m in own)
        for other, markers in STATE_MARKERS.items():
            if other == state:
                continue
            if {state, other} == {'Selangor', 'Kuala Lumpur'}:
                continue
            hits = [m for m in markers if m in ed_lc]
            if hits and not own_hit:
                c1_crossstate.append((r, other, hits))
                break

        words = significant_words(title)
        if words and not any(w in ed_lc for w in words):
            c1_titlemis.append((r, words))

    # ── CHECK 2: address completeness proxy ────────────────────────────────
    c2 = []
    for r in live:
        reasons = []
        if not place_id_of(g(r, 'google_maps_url')):
            reasons.append('no place_id')
        if not g(r, 'area'):
            reasons.append('no area')
        if g(r, 'state') in ('', '(unknown)'):
            reasons.append('no/unknown state')
        if reasons:
            c2.append((r, reasons))

    # ── CHECK 3: website cross-leak ────────────────────────────────────────
    title_tokens = {r['slug']: set(significant_words(g(r, 'title'))) for r in live}
    c3 = []
    seen3 = set()
    dom_map = defaultdict(list)
    for r in live:
        d = domain_of(g(r, 'website'))
        if d and 'facebook' not in d:
            dom_map[d].append(r)
    for d, rs in dom_map.items():
        if len(rs) > 1:
            for a in rs:
                for b in rs:
                    if a['slug'] < b['slug'] and not same_chain(a['slug'], b['slug'], groups):
                        key = ('shared-domain', a['slug'], b['slug'])
                        if key not in seen3:
                            seen3.add(key)
                            c3.append(('shared-domain', d, a, b))
    for r in live:
        d = domain_of(g(r, 'website'))
        if not d:
            continue
        dtokens = set(re.split(r'[^a-z0-9]+', d))
        my = title_tokens[r['slug']]
        for other in live:
            if other['slug'] == r['slug'] or same_chain(r['slug'], other['slug'], groups):
                continue
            ot = title_tokens[other['slug']] - my
            hit = [t for t in ot if t in dtokens and len(t) >= 4
                   and t not in GENERIC_EDITORIAL_WORDS]
            if len(hit) >= 2:
                key = ('foreign-brand', r['slug'], other['slug'])
                if key not in seen3:
                    seen3.add(key)
                    c3.append(('foreign-brand', d, r, other))
                break

    # ── CHECK 4: shared assets across non-chain slugs ──────────────────────
    c4 = {}
    for field, extractor in [
        ('phone', lambda r: phone_digits(g(r, 'phone'))),
        ('place_id', lambda r: place_id_of(g(r, 'google_maps_url'))),
        ('hero_image', lambda r: g(r, 'hero_image')),
        ('website', lambda r: domain_of(g(r, 'website'))),
    ]:
        m = defaultdict(list)
        for r in live:
            v = extractor(r)
            if v and (field != 'website' or 'facebook' not in v):
                m[v].append(r)
        flagged = []
        for v, rs in m.items():
            if len(rs) < 2:
                continue
            slugs = [r['slug'] for r in rs]
            all_same = (groups.get(slugs[0]) is not None and
                        all(same_chain(slugs[0], s, groups) for s in slugs[1:]))
            if not all_same:
                flagged.append((v, rs))
        c4[field] = flagged

    # ── CHECK 5: unknown-state rows ────────────────────────────────────────
    c5 = [r for r in live if g(r, 'state') in ('', '(unknown)')]

    # ── CHECK 6: title vs slug incoherence ─────────────────────────────────
    c6 = []
    for r in live:
        tw = set(significant_words(g(r, 'title')))
        sw = set(t for t in re.split(r'[^a-z0-9]+', r['slug'].lower())
                 if len(t) >= 3 and t not in TITLE_STOPWORDS)
        if tw and len(tw & sw) < 2:
            c6.append((r, sorted(tw), sorted(sw)))

    # ── CHECK 7 & 8: Places API ────────────────────────────────────────────
    details_by_pid, textsearch_by_slug, places_ok = fetch_places(live, g)

    c7a, c7b, c7c, c7d = [], [], [], []   # wrong-facility / dead / state-wrong / drift
    c8 = []
    if places_ok:
        for r in live:
            if r['slug'] not in details_by_pid:
                continue
            pid, d = details_by_pid[r['slug']]
            status = d.get('status')
            if status != 'OK':
                c7b.append((r, pid, status, d.get('error', '')))
                continue
            res = d['result']
            g_name = res.get('name', '')
            g_addr = res.get('formatted_address', '')
            g_web = res.get('website', '')
            g_phone = res.get('international_phone_number', '') or res.get('formatted_phone_number', '')

            name_ok = names_match(g(r, 'title'), g_name)

            g_state = state_in_address(g_addr)
            state_bad = (g_state and g(r, 'state') not in ('', '(unknown)')
                         and g_state != g(r, 'state')
                         and {g_state, g(r, 'state')} != {'Selangor', 'Kuala Lumpur'})

            sheet_dom, g_dom = domain_of(g(r, 'website')), domain_of(g_web)
            web_bad = bool(sheet_dom and g_dom and sheet_dom != g_dom)
            sp, gp = phone_digits(g(r, 'phone')), phone_digits(g_phone)
            phone_bad = bool(sp and gp and sp[-8:] != gp[-8:])

            rec = (r, pid, g_name, g_addr, g_web, g_phone, g_state)
            if not name_ok:
                c7a.append(rec)
            elif state_bad:
                c7c.append(rec)
            elif web_bad or phone_bad:
                flags = ([] + (['WEBSITE'] if web_bad else []) + (['PHONE'] if phone_bad else []))
                c7d.append(rec + (','.join(flags),))

        for r in live:
            if r['slug'] not in textsearch_by_slug:
                continue
            d = textsearch_by_slug[r['slug']]
            if d.get('status') != 'OK' or not d.get('results'):
                c8.append((r, 'NO_RESULT', d.get('status', '?'), '', ''))
                continue
            top = d['results'][0]
            conf = 'OK' if names_match(g(r, 'title'), top.get('name', '')) else 'LOW_CONFIDENCE'
            c8.append((r, conf, top.get('name', ''), top.get('place_id', ''),
                       top.get('formatted_address', '')))

    write_report(rows, live, groups, g,
                 c1_crossstate, c1_titlemis,
                 c2, c3, c4, c5, c6, c7a, c7b, c7c, c7d, c8, places_ok)
    print(f'Wrote {REPORT_PATH}', file=sys.stderr)


def batch_blocks(P, title, items, render, perpage=100):
    if not items:
        P(f'### {title}\n\n_None._\n')
        return
    n = len(items)
    pages = (n + perpage - 1) // perpage
    for p in range(pages):
        chunk = items[p*perpage:(p+1)*perpage]
        lo, hi = p*perpage + 1, p*perpage + len(chunk)
        P(f'### {title} (batch {p+1} of {pages}, items {lo}–{hi})\n')
        for it in chunk:
            P(render(it))
        P('')


def write_report(rows, live, groups, g,
                  c1_crossstate, c1_titlemis,
                  c2, c3, c4, c5, c6, c7a, c7b, c7c, c7d, c8, places_ok):
    out = []
    P = out.append

    c1_total = len({r['slug'] for r, *_ in c1_crossstate} |
                   {r['slug'] for r, *_ in c1_titlemis})
    c3_total = len(c3)
    c4_total = sum(len(v) for v in c4.values())
    c8_low = sum(1 for x in c8 if x[1] == 'LOW_CONFIDENCE')

    P('# Profile data audit — 2026-05-14\n')
    P(f'**Source:** `facilities_local.csv` (snapshot {CSV_SNAPSHOT}, ~2 days stale at audit time).')
    P(f'**Live rows audited:** {len(live)} (status blank). Hidden rows (`unverified`/`removed`) excluded.')
    P('**Caveat:** the street address lives in the *Details* tab (gid 1104748854), which is not cached '
      'in-repo and was unreachable this round. Check 2 is a *proxy* (place_id / area / state presence); '
      'Check 7 surfaces Google\'s `formatted_address` for every place_id row — that is the dataset to '
      'seed real addresses from next round.')
    P('**Scope:** read-only audit. No sheet writes, no fixes applied. Fixes happen in a follow-up round, '
      'by slug-lookup against the live sheet (per CLAUDE.md hard rule).\n')

    P('## Summary — priority order\n')
    P('| Check | What it means | Severity | Count |')
    P('| --- | --- | --- | --- |')
    if places_ok:
        P(f'| 7a. Wrong-facility place_id | `query_place_id` resolves to a *different* facility — the megaway-class bug | P0 | {len(c7a)} |')
    P(f'| 3. Website cross-leak | a website domain shared by unrelated facilities, or carrying another brand | P0 | {c3_total} |')
    P(f'| 4. Shared assets | same phone / place_id / hero / website across non-chain slugs | P0 | {c4_total} groups |')
    P(f'| 1. Editorial cross-leak | editorial text points at another facility or state | P0 | {c1_total} |')
    if places_ok:
        P(f'| 7b. Dead place_id | `query_place_id` returns NOT_FOUND / error | P1 | {len(c7b)} |')
        P(f'| 7c. Sheet state wrong | place_id is correct but the sheet’s `state` disagrees with Google | P1 | {len(c7c)} |')
    P(f'| 2. Address proxy | live row missing place_id / area / state | P1 | {len(c2)} |')
    if places_ok:
        P(f'| 8. Address suggestions | top Places candidate for rows with no place_id ({c8_low} low-confidence) | P1 | {len(c8)} |')
        P(f'| 7d. Phone / website drift | place_id + name + state OK, only contact field differs (likely Google more current) | P2 | {len(c7d)} |')
    P(f'| 5. Unknown-state rows | live row with no usable `state` | P2 | {len(c5)} |')
    P(f'| 6. Title vs slug incoherence | slug shares < 2 significant tokens with title | P2 | {len(c6)} |')
    if not places_ok:
        P('| 7 + 8. Places checks | SKIPPED — Places API unavailable | — | — |')
    P('')

    # ── megaway diagnosis ──────────────────────────────────────────────────
    P('## Megaway vs Mega Senior Care — diagnosis\n')
    targets = ['house-of-megaway-care-centre-caw', 'house-of-megaways-care-centre',
               'mega-senior-care-centre']
    by_slug = {r['slug']: r for r in rows}
    P('| field | house-of-megaway-care-centre-caw | house-of-megaways-care-centre | mega-senior-care-centre |')
    P('| --- | --- | --- | --- |')
    for f in ['title', 'area', 'state', 'status', 'phone', 'website', 'google_maps_url', 'hero_image']:
        cells = []
        for s in targets:
            v = (by_slug.get(s, {}).get(f) or '').strip().replace('|', '\\|')
            cells.append(v[:90] if v else '*(empty)*')
        P(f'| {f} | {cells[0]} | {cells[1]} | {cells[2]} |')
    P('')
    for s in targets:
        ed = (by_slug.get(s, {}).get('editorial_summary') or '').strip()
        P(f'**`{s}` editorial:** ' + (f'{ed[:400]}…' if len(ed) > 400 else (ed or '*(empty)*')))
        P('')
    P('**Finding:** `house-of-megaways-care-centre` (title "HOUSE OF MEGAWAYS CARE CENTRE", state Negeri '
      'Sembilan) carries `website: https://www.megaseniorcarecentre.com/` and `area: Sek 9` — both belong '
      'to **Mega Senior Care Centre** (Petaling Jaya, Selangor). A third facility, '
      '`goldleaf-villa-care-centre`, *also* carries that same `megaseniorcarecentre.com` website. The two '
      'megaway rows additionally share phone `+60196219723` and are not a registered chain. This is a '
      'website/area cross-write — see Check 3 and Check 4. Neither megaway row has an editorial, so the '
      'visible wrong info on the live profile is the leaked website + area (plus whatever the Details tab '
      'holds, which this round could not read).\n')

    # ── Check 7a ───────────────────────────────────────────────────────────
    if places_ok:
        P('## Check 7a — Wrong-facility place_id (P0)\n')
        P(f'{len(c7a)} live rows whose `query_place_id` resolves to a facility with a *different name*. '
          'This is the megaway-class bug: the sheet row is wearing another facility’s Google identity '
          '(address, photos, rating, reviews all bleed through). **Fix priority 1.** For each, the sheet '
          'either has the wrong place_id or the wrong title.\n')
        batch_blocks(P, '7a. Wrong-facility place_id', c7a,
            lambda x: (f"- **`{x[0]['slug']}`** (row {x[0]['_csvrow']}, sheet state {g(x[0],'state')}) — "
                       f"sheet title: **{g(x[0],'title')}**\n"
                       f"  - place_id `{x[1]}` actually resolves to: **\"{x[2]}\"**\n"
                       f"  - Google address: {x[3] or '—'}"))

    # ── Check 3 ────────────────────────────────────────────────────────────
    P('## Check 3 — Website cross-leak (P0)\n')
    P(f'{c3_total} suspicious pairs. A website domain shared by unrelated facilities, or a domain '
      'carrying another facility’s brand name.\n')
    if not c3:
        P('_None._\n')
    else:
        for kind, dom, a, b in c3:
            if kind == 'shared-domain':
                P(f"- **shared domain** `{dom}` — `{a['slug']}` ({g(a,'title')}) "
                  f"AND `{b['slug']}` ({g(b,'title')}) — not a registered chain")
            else:
                P(f"- **foreign brand** `{a['slug']}` ({g(a,'title')}) has website `{dom}` which carries "
                  f"the brand of `{b['slug']}` ({g(b,'title')})")
        P('')

    # ── Check 4 ────────────────────────────────────────────────────────────
    P('## Check 4 — Shared assets across non-chain slugs (P0)\n')
    P('Same phone / place_id / hero image / website domain on slugs that are not in the same `GROUPS` '
      'chain. Legitimate chains are suppressed. A shared place_id or hero image almost always means a '
      'cross-write; a shared phone can be a real shared operator.\n')
    for field in ['place_id', 'hero_image', 'website', 'phone']:
        flagged = c4[field]
        P(f'### 4.{field} — {len(flagged)} shared values\n')
        if not flagged:
            P('_None._\n')
            continue
        for v, rs in sorted(flagged, key=lambda x: -len(x[1])):
            vshow = v if len(v) <= 70 else v[:67] + '…'
            slugs = ', '.join(f"`{r['slug']}`" for r in rs)
            P(f'- `{vshow}` → {slugs}')
        P('')

    # ── Check 1 ────────────────────────────────────────────────────────────
    P('## Check 1 — Editorial cross-leak (P0)\n')
    P(f'{c1_total} unique rows flagged. Editorial text that points at another facility or another '
      'state. (A third sub-check — "foreign brand phrase in editorial" — was prototyped and removed: '
      'facility titles contain town names, so editorials mentioning their own town false-positived '
      'heavily. Check 7a is the reliable facility-identity check.)\n')
    batch_blocks(P, '1a. Cross-state contamination', c1_crossstate,
        lambda x: (f"- **`{x[0]['slug']}`** (row {x[0]['_csvrow']}, state {g(x[0],'state')}) — "
                   f"{g(x[0],'title')}\n"
                   f"  - editorial mentions **{x[1]}** place names: {', '.join(x[2])}\n"
                   f"  - editorial[:200]: \"{g(x[0],'editorial_summary')[:200]}…\""))
    batch_blocks(P, '1b. Title mismatch (editorial shares no title words)', c1_titlemis,
        lambda x: (f"- **`{x[0]['slug']}`** (row {x[0]['_csvrow']}, state {g(x[0],'state')}) — "
                   f"{g(x[0],'title')}\n"
                   f"  - title words: {', '.join(x[1])}\n"
                   f"  - editorial[:200]: \"{g(x[0],'editorial_summary')[:200]}…\""))

    # ── Check 7b ───────────────────────────────────────────────────────────
    if places_ok:
        P('## Check 7b — Dead place_id (P1)\n')
        P(f'{len(c7b)} live rows whose `query_place_id` returns NOT_FOUND or an API error. The listing '
          'was probably removed from Google or the id was mistyped. Re-search and replace.\n')
        if not c7b:
            P('_None._\n')
        else:
            for r, pid, status, err in c7b:
                P(f"- **`{r['slug']}`** (row {r['_csvrow']}, {g(r,'state')}) — {g(r,'title')} — "
                  f"place_id `{pid}` → {status}{(' (' + err + ')') if err else ''}")
            P('')

        # ── Check 7c ───────────────────────────────────────────────────────
        P('## Check 7c — Sheet state wrong (P1)\n')
        P(f'{len(c7c)} live rows where the place_id is correct (name matches) but the sheet’s `state` '
          'column disagrees with the state in Google’s address. The facility is filed under the wrong '
          'state on the site.\n')
        batch_blocks(P, '7c. Sheet state wrong', c7c,
            lambda x: (f"- **`{x[0]['slug']}`** (row {x[0]['_csvrow']}) — {g(x[0],'title')}\n"
                       f"  - sheet state: **{g(x[0],'state')}** | Google says: **{x[6]}**\n"
                       f"  - Google address: {x[3]}"))

    # ── Check 2 ────────────────────────────────────────────────────────────
    P('## Check 2 — Address completeness proxy (P1)\n')
    P(f'{len(c2)} live rows missing address signals (place_id / area / state). True street-address '
      'coverage needs the Details tab — see caveat at the top. For rows missing place_id, Check 8 '
      'below proposes a candidate.\n')
    batch_blocks(P, '2. Address-incomplete rows', c2,
        lambda x: (f"- **`{x[0]['slug']}`** (row {x[0]['_csvrow']}, {g(x[0],'state') or '(no state)'}) — "
                   f"{g(x[0],'title')} — missing: {', '.join(x[1])}"))

    # ── Check 8 ────────────────────────────────────────────────────────────
    if places_ok:
        P('## Check 8 — Address recovery suggestions (P1)\n')
        P(f'{len(c8)} live rows have no `place_id`. Below is the top Places Text Search candidate for '
          'each — **suggestions only, not applied**. `LOW_CONFIDENCE` = candidate name does not clearly '
          'match the facility; verify before use.\n')
        batch_blocks(P, '8. Address suggestions', c8,
            lambda x: (f"- **`{x[0]['slug']}`** (row {x[0]['_csvrow']}, {g(x[0],'state') or '—'}) — "
                       f"{g(x[0],'title')} — **{x[1]}**\n"
                       f"  - suggested: name=\"{x[2]}\" | place_id=`{x[3]}`\n"
                       f"  - address: {x[4] or '—'}"))

    # ── Check 7d ───────────────────────────────────────────────────────────
    if places_ok:
        P('## Check 7d — Phone / website drift (P2, informational)\n')
        P(f'{len(c7d)} live rows where the place_id, name and state all check out, but the phone or '
          'website differs from Google’s record. Often Google is simply more current, or the sheet '
          'holds a mobile/WhatsApp while Google holds the landline. Review, do not bulk-apply.\n')
        batch_blocks(P, '7d. Phone / website drift', c7d,
            lambda x: (f"- **`{x[0]['slug']}`** (row {x[0]['_csvrow']}, {g(x[0],'state')}) — "
                       f"{g(x[0],'title')} — **[{x[7]}]**\n"
                       f"  - sheet: website={g(x[0],'website') or '—'} | phone={g(x[0],'phone') or '—'}\n"
                       f"  - google: website={x[4] or '—'} | phone={x[5] or '—'}"))

    # ── Check 5 ────────────────────────────────────────────────────────────
    P('## Check 5 — Unknown-state rows (P2)\n')
    P(f'{len(c5)} live rows with no usable `state`. Backfill from `area`/title.\n')
    batch_blocks(P, '5. Unknown-state rows', c5,
        lambda r: f"- **`{r['slug']}`** (row {r['_csvrow']}) — {g(r,'title')} — area: {g(r,'area') or '*(empty)*'}")

    # ── Check 6 ────────────────────────────────────────────────────────────
    P('## Check 6 — Title vs slug incoherence (P2)\n')
    P(f'{len(c6)} rows where the slug shares < 2 significant tokens with the title. Most are harmless '
      '(slug generated before a title edit), but a few indicate a wrong slug.\n')
    batch_blocks(P, '6. Title/slug mismatch', c6,
        lambda x: (f"- **`{x[0]['slug']}`** (row {x[0]['_csvrow']}) — {g(x[0],'title')}\n"
                   f"  - title tokens: {', '.join(x[1])} | slug tokens: {', '.join(x[2])}"))

    P('---')
    P('_Generated by `_tmp/audit_profile_data.py`. Places responses cached in '
      '`_tmp/audit_places_cache.json`. Re-run after refreshing `facilities_local.csv` from the live '
      'sheet for a current picture._')

    open(REPORT_PATH, 'w', encoding='utf-8').write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
