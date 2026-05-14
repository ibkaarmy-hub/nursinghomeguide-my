"""
Fix round for audit_report_2026-05-14.md — scoped to:
  7a. Wrong-facility place_id   -> re-search; correct google_maps_url+rating+review_count, or clear
  7b. Dead place_id             -> re-search; correct, or clear
  7c. Sheet state wrong         -> set `state` to Google's state
  5.  Unknown-state rows        -> backfill `state` from place_id address or text search

Cross-leak / shared-asset checks (3, 4) are deliberately NOT touched — manual review.

Safety:
  * facilities_local.csv was refreshed from the live sheet immediately before this run,
    so CSV row N == sheet row N. Every write still re-reads col A (title) + col B (slug)
    at the target row and asserts they match the CSV before writing, then re-verifies B.
  * Targets duplicate-slug rows by ROW NUMBER, never by slug lookup (19 dup slugs exist).
  * Dry-run by default. Pass --apply to write.

Run from the repo root:  python .claude/worktrees/.../_tmp/fix_audit_round.py [--apply]
"""
import os, sys, csv, json, time, urllib.parse, urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
import audit_profile_data as A  # also rebinds sys.stdout to a utf-8 wrapper

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_PATH = r'C:\Users\ibkaa\nursinghomeguide-my\Nursing Home Guide Malaysia\token_sheets.json'
TAB = 'google-sheets-facilities.csv'
CSV_PATH = 'facilities_local.csv'
FIX_CACHE = '_tmp/fix_places_cache.json'
MAPS_KEY = os.environ.get('GOOGLE_MAPS_KEY', '').strip()
APPLY = '--apply' in sys.argv

# 1-based column indices in the live sheet (verified against the refreshed CSV header)
COL = {'title': 1, 'slug': 2, 'area': 4, 'rating': 16, 'review_count': 17,
       'google_maps_url': 20, 'state': 55}
REAL_STATES = set(A.STATE_MARKERS.keys())


def col_letter(n):
    s = ''
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def build_maps_url(title, place_id):
    return ('https://www.google.com/maps/search/?api=1&query='
            + urllib.parse.quote(title) + '&query_place_id=' + place_id)


_cache = {}
if os.path.exists(FIX_CACHE):
    _cache = json.load(open(FIX_CACHE, encoding='utf-8'))


def textsearch(query):
    key = f't:{query}'
    if key in _cache:
        return _cache[key]
    url = ('https://maps.googleapis.com/maps/api/place/textsearch/json?query='
           + urllib.parse.quote(query) + '&key=' + MAPS_KEY)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=25) as r:
        d = json.load(r)
    _cache[key] = d
    json.dump(_cache, open(FIX_CACHE, 'w', encoding='utf-8'))
    time.sleep(0.12)
    return d


def _normname(s):
    """Lowercase alnum-only, with center/centre and common spelling unified.
    Non-latin scripts (Chinese names Google appends) drop out — fine, we match
    on the latin portion."""
    s = (s or '').lower().replace('centre', 'center')
    return ''.join(ch for ch in s if ch.isalnum() and ord(ch) < 128)


def strict_match(sheet_title, g_name):
    """Strong identity check used to ACCEPT a re-found place_id. Deliberately
    much stricter than A.names_match (which accepts a single shared generic
    token like 'aged' or 'oasis', and matched 'De Home Care Centre' to
    'Verde Home Care Centre'). Two accept paths only:
      1. normalised names are identical (centre/centre & punctuation aside);
      2. both names have >= 2 distinctive (non-stopword) tokens and one
         distinctive-token set is a subset of the other by exact equality.
    Everything weaker -> caller clears the place_id rather than risk writing
    another facility's identity onto the row."""
    if _normname(sheet_title) == _normname(g_name) and _normname(sheet_title):
        return True
    ta = set(A.significant_words(sheet_title))
    tg = set(A.significant_words(g_name))
    if len(ta) >= 2 and len(tg) >= 2 and (ta <= tg or tg <= ta):
        return True
    return False


def best_match(title, sheet_state, results):
    """Pick the best Places result for `title`: a name match (A.names_match) that
    also passes strict_match, preferring one whose address state matches the
    sheet state. Returns the result dict or None."""
    hits = [r for r in results
            if A.names_match(title, r.get('name', ''))
            and strict_match(title, r.get('name', ''))]
    if not hits:
        return None
    if sheet_state in REAL_STATES:
        for r in hits:
            if A.state_in_address(r.get('formatted_address', '')) == sheet_state:
                return r
    return hits[0]


def resolve_correct_place(slug, title, sheet_state):
    """Return (place_id, maps_url, rating, review_count) for the correct facility,
    or (None, ...) if no confident match -> caller clears the fields."""
    q = f"{title}, {sheet_state}, Malaysia" if sheet_state in REAL_STATES else f"{title}, Malaysia"
    d = textsearch(q)
    if d.get('status') not in ('OK', 'ZERO_RESULTS'):
        return ('ERROR', d.get('status'), None, None, None)
    m = best_match(title, sheet_state, d.get('results', []))
    if not m:
        return (None, None, None, None, None)
    pid = m['place_id']
    return (pid, build_maps_url(title, pid),
            m.get('rating', ''), m.get('user_ratings_total', ''), m.get('name', ''))


def main():
    rows = list(csv.DictReader(open(CSV_PATH, encoding='utf-8')))
    for i, r in enumerate(rows):
        r['_row'] = i + 2  # sheet row
    g = lambda r, k: (r.get(k) or '').strip()
    live = [r for r in rows
            if g(r, 'slug') and g(r, 'status').lower() not in ('unverified', 'removed')]

    # Load the audit's Places cache directly and key by place_id (the audit's
    # details_by_pid is keyed by slug, which collides on the 19 duplicate slugs).
    assert os.path.exists(A.PLACES_CACHE), 'Places cache missing — run the audit first.'
    pcache = json.load(open(A.PLACES_CACHE, encoding='utf-8'))

    def detail_for(r):
        pid = A.place_id_of(g(r, 'google_maps_url'))
        return pid, pcache.get(f'd:{pid}') if pid else None

    # ── recompute 7a / 7b / 7c exactly as the audit does, per-row ─────────────
    c7a, c7b, c7c = [], [], []
    for r in live:
        pid, d = detail_for(r)
        if not pid or d is None:
            continue
        status = d.get('status')
        if status != 'OK':
            c7b.append((r, pid, status))
            continue
        res = d['result']
        g_name = res.get('name', '')
        g_state = A.state_in_address(res.get('formatted_address', ''))
        if not A.names_match(g(r, 'title'), g_name):
            c7a.append((r, pid, g_name))
        elif (g_state and g(r, 'state') not in ('', '(unknown)')
              and g_state != g(r, 'state')
              and {g_state, g(r, 'state')} != {'Selangor', 'Kuala Lumpur'}):
            c7c.append((r, pid, g_state, res.get('formatted_address', '')))

    c5 = [r for r in live if g(r, 'state') in ('', '(unknown)')]

    writes = []  # (row, slug, title, {col_name: value}, note)

    # ── 7a + 7b: re-resolve place_id ─────────────────────────────────────────
    targets = [('7a', r, p) for r, p, _ in c7a] + [('7b', r, p) for r, p, _ in c7b]
    print(f"recompute: 7a={len(c7a)} 7b={len(c7b)} 7c={len(c7c)} 5={len(c5)}", file=sys.stderr)

    # If the re-search returns the SAME id for two different targets, at least one
    # match is wrong — keep the first, clear the rest. (Collisions with a non-target
    # live row are left alone: usually a duplicate-slug sibling that is already
    # correct, otherwise Check 4's manual review will catch it.)
    claimed = set()

    for kind, r, pid in targets:
        new_pid, new_url, rating, revcount, new_name = resolve_correct_place(
            r['slug'], g(r, 'title'), g(r, 'state'))
        clear = {'google_maps_url': '', 'rating': '', 'review_count': ''}
        if new_pid == 'ERROR':
            print(f"  !! {kind} {r['slug']} row{r['_row']}: text search {new_url} — SKIPPED")
            continue
        if new_pid == pid:
            print(f"  ?? {kind} {r['slug']} row{r['_row']}: re-search returned the SAME id — SKIPPED")
        elif new_pid and new_pid in claimed:
            writes.append((r['_row'], r['slug'], g(r, 'title'), clear,
                           f"{kind} match {new_pid} already claimed by another target -> cleared"))
        elif new_pid:
            claimed.add(new_pid)
            writes.append((r['_row'], r['slug'], g(r, 'title'),
                           {'google_maps_url': new_url, 'rating': rating,
                            'review_count': revcount},
                           f"{kind} corrected -> {new_pid}  ({new_name})"))
        else:
            writes.append((r['_row'], r['slug'], g(r, 'title'), clear,
                           f"{kind} no confident match -> cleared place_id/rating/reviews"))

    # ── 7c: fix state ────────────────────────────────────────────────────────
    for r, pid, g_state, addr in c7c:
        writes.append((r['_row'], r['slug'], g(r, 'title'),
                       {'state': g_state}, f"7c state {g(r,'state')!r} -> {g_state}"))

    # ── 5: backfill unknown state ────────────────────────────────────────────
    # Sibling fallback: a duplicate-slug row that already carries a real state.
    sibling_state = {}
    for r in live:
        st = g(r, 'state')
        if st in REAL_STATES:
            sibling_state.setdefault(r['slug'], st)
    for r in c5:
        pid, d = detail_for(r)
        g_state = ''
        src = ''
        if pid and d and d.get('status') == 'OK':
            res = d['result']
            if A.names_match(g(r, 'title'), res.get('name', '')):
                g_state = A.state_in_address(res.get('formatted_address', ''))
                src = 'place_id address'
        if g_state not in REAL_STATES:
            q = f"{g(r,'title')}, {g(r,'area')}, Malaysia" if g(r, 'area') else f"{g(r,'title')}, Malaysia"
            d = textsearch(q)
            m = best_match(g(r, 'title'), '', d.get('results', []))
            if m:
                g_state = A.state_in_address(m.get('formatted_address', ''))
                src = 'text search'
        if g_state not in REAL_STATES and r['slug'] in sibling_state:
            g_state = sibling_state[r['slug']]
            src = 'duplicate-slug sibling row'
        if g_state in REAL_STATES:
            writes.append((r['_row'], r['slug'], g(r, 'title'),
                           {'state': g_state}, f"5 unknown-state -> {g_state} (via {src})"))
        else:
            print(f"  ?? 5 {r['slug']} row{r['_row']}: could not resolve state — SKIPPED")

    # ── report ───────────────────────────────────────────────────────────────
    print(f"\n{'APPLY' if APPLY else 'DRY-RUN'} — {len(writes)} row writes planned\n")
    for row, slug, title, upd, note in writes:
        print(f"  row {row:>4}  {slug}")
        print(f"          {note}")
        for k, v in upd.items():
            vs = repr(v) if v != '' else '<clear>'
            print(f"            {k} = {vs}")
    print()

    if not APPLY:
        print("Dry run only. Re-run with --apply to write.")
        return

    creds = Credentials.from_authorized_user_file(TOKEN_PATH)
    svc = build('sheets', 'v4', credentials=creds)

    from googleapiclient.errors import HttpError

    def call(req):
        """Execute a Sheets API request, backing off on 429 rate-limit errors.
        The read quota is 60/min/user; each row uses 3 ops so we also pace below."""
        for attempt in range(6):
            try:
                return req.execute()
            except HttpError as e:
                if e.resp.status == 429:
                    wait = 30 * (attempt + 1)
                    print(f"     ...429 rate-limited, sleeping {wait}s", flush=True)
                    time.sleep(wait)
                    continue
                raise
        raise RuntimeError('giving up after repeated 429s')

    ok = 0
    for row, slug, title, upd, note in writes:
        # verify identity at the target row before writing
        cur = call(svc.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range=f"'{TAB}'!A{row}:B{row}"
        )).get('values', [['', '']])[0]
        cur_title = (cur[0] if len(cur) > 0 else '').strip()
        cur_slug = (cur[1] if len(cur) > 1 else '').strip()
        if cur_slug != slug or cur_title.lower() != title.lower():
            print(f"  !! row {row}: DRIFT — expected ({title!r},{slug!r}) found ({cur_title!r},{cur_slug!r}) — SKIPPED")
            continue
        data = [{'range': f"'{TAB}'!{col_letter(COL[k])}{row}", 'values': [[v]]}
                for k, v in upd.items()]
        call(svc.spreadsheets().values().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={'valueInputOption': 'RAW', 'data': data}))
        verify = call(svc.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range=f"'{TAB}'!B{row}"
        )).get('values', [['']])[0][0].strip()
        assert verify == slug, f"POST-WRITE DRIFT row {row}: {verify!r} != {slug!r}"
        ok += 1
        print(f"  ok  row {row}  {slug}", flush=True)
        time.sleep(3.2)  # 3 ops/row, stay under the 60 reads/min user quota
    print(f"\nWrote {ok}/{len(writes)} rows.")


if __name__ == '__main__':
    main()
