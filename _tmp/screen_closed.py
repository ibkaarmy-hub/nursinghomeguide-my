"""
Screen every live facility that has a query_place_id against Google's
business_status, and (with --apply) fix the closed ones:

  * re-search each closed row; if a confident OPERATIONAL match is found
    (e.g. the facility relocated and has a fresh listing) -> reassign
    google_maps_url + rating + review_count and leave it live;
  * otherwise -> clear place_id/rating/reviews and set status=unverified
    so a permanently-closed home stops showing on the live site.

Read-only by default. Caches Place Details (business_status field) to
_tmp/closed_screen_cache.json. Run from the repo root; pass --apply to write.
Writes target rows by number with a col A+B identity check (19 duplicate
slugs exist), matching the fix_audit_round.py safety pattern.
"""
import os, sys, csv, json, re, time, urllib.parse, urllib.request

sys.path.insert(0, os.path.dirname(__file__))
from fix_audit_round import (resolve_correct_place, col_letter, COL, TAB,
                             SPREADSHEET_ID, TOKEN_PATH)

sys.stdout = __import__('io').TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
CSV_PATH = 'facilities_local.csv'
CACHE = '_tmp/closed_screen_cache.json'
MAPS_KEY = os.environ.get('GOOGLE_MAPS_KEY', '').strip()
APPLY = '--apply' in sys.argv


def place_id_of(u):
    m = re.search(r'query_place_id=([A-Za-z0-9_-]+)', u or '')
    return m.group(1) if m else ''


def details(pid):
    url = ('https://maps.googleapis.com/maps/api/place/details/json'
           f'?place_id={urllib.parse.quote(pid)}&fields=name,business_status&key={MAPS_KEY}')
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.load(r)


def main():
    rows = list(csv.DictReader(open(CSV_PATH, encoding='utf-8')))
    cache = json.load(open(CACHE, encoding='utf-8')) if os.path.exists(CACHE) else {}

    live = [(i + 2, r) for i, r in enumerate(rows)
            if (r.get('slug') or '').strip()
            and (r.get('status') or '').strip().lower() not in ('unverified', 'removed')]
    targets = [(rn, r, place_id_of(r.get('google_maps_url', '')))
               for rn, r in live]
    targets = [(rn, r, p) for rn, r, p in targets if p]

    todo = [(rn, r, p) for rn, r, p in targets if p not in cache]
    print(f'{len(targets)} live rows with a place_id; {len(todo)} to fetch, '
          f'{len(targets) - len(todo)} cached', file=sys.stderr)
    for n, (rn, r, p) in enumerate(todo, 1):
        try:
            d = details(p)
            cache[p] = {'status': d.get('status'),
                        'business_status': d.get('result', {}).get('business_status', ''),
                        'name': d.get('result', {}).get('name', '')}
        except Exception as e:
            cache[p] = {'status': 'FETCH_ERROR', 'error': str(e)}
        if n % 50 == 0:
            json.dump(cache, open(CACHE, 'w', encoding='utf-8'))
            print(f'  ...{n}/{len(todo)}', file=sys.stderr)
        time.sleep(0.1)
    json.dump(cache, open(CACHE, 'w', encoding='utf-8'))

    closed_perm, closed_temp, errors = [], [], []
    for rn, r, p in targets:
        c = cache.get(p, {})
        bs = c.get('business_status', '')
        if bs == 'CLOSED_PERMANENTLY':
            closed_perm.append((rn, r, p, c.get('name', '')))
        elif bs == 'CLOSED_TEMPORARILY':
            closed_temp.append((rn, r, p, c.get('name', '')))
        elif c.get('status') not in ('OK', None) and c.get('status'):
            errors.append((rn, r, p, c.get('status')))

    print(f'\n=== CLOSED_PERMANENTLY: {len(closed_perm)} live rows ===')
    for rn, r, p, name in sorted(closed_perm, key=lambda x: x[1]['slug']):
        print(f"  row {rn:>4}  {r['slug']:<55} state={r.get('state','')!r:<18} google=\"{name}\"")
    print(f'\n=== CLOSED_TEMPORARILY: {len(closed_temp)} live rows ===')
    for rn, r, p, name in sorted(closed_temp, key=lambda x: x[1]['slug']):
        print(f"  row {rn:>4}  {r['slug']:<55} google=\"{name}\"")
    if errors:
        print(f'\n=== place_id lookup errors: {len(errors)} ===')
        for rn, r, p, st in errors[:30]:
            print(f"  row {rn:>4}  {r['slug']:<55} {st}")

    # ── decide a fix for every closed row ────────────────────────────────────
    g = lambda r, k: (r.get(k) or '').strip()
    STATUS_COL = 56  # `status` column (1-based) in the live sheet
    writes = []  # (row, slug, title, {col: val}, note)
    for rn, r, old_pid, name in closed_perm + closed_temp:
        new_pid, new_url, rating, revcount, new_name = resolve_correct_place(
            r['slug'], g(r, 'title'), g(r, 'state'))
        if new_pid not in (None, 'ERROR') and new_pid != old_pid:
            # re-search found a confident OPERATIONAL listing (best_match already
            # rejects closed results) -> the facility likely just relocated.
            writes.append((rn, r['slug'], g(r, 'title'),
                           {'google_maps_url': new_url, 'rating': rating,
                            'review_count': revcount},
                           f"closed -> re-found operational listing {new_pid} ({new_name})"))
        else:
            writes.append((rn, r['slug'], g(r, 'title'),
                           {'google_maps_url': '', 'rating': '', 'review_count': '',
                            'status': 'unverified'},
                           "closed, no operational match -> cleared + status=unverified"))

    print(f"\n{'APPLY' if APPLY else 'DRY-RUN'} — {len(writes)} closed-row fixes\n")
    for rn, slug, title, upd, note in writes:
        print(f"  row {rn:>4}  {slug}\n          {note}")
        for k, v in upd.items():
            shown = repr(v) if v != '' else '<clear>'
            print(f"            {k} = {shown}")
    if not APPLY:
        print("\nDry run only. Re-run with --apply to write.")
        return

    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    svc = build('sheets', 'v4', credentials=Credentials.from_authorized_user_file(TOKEN_PATH))
    col_idx = dict(COL); col_idx['status'] = STATUS_COL

    def call(req):
        for attempt in range(6):
            try:
                return req.execute()
            except HttpError as e:
                if e.resp.status == 429:
                    w = 30 * (attempt + 1)
                    print(f"     ...429, sleeping {w}s", flush=True); time.sleep(w); continue
                raise
        raise RuntimeError('repeated 429s')

    ok = 0
    for rn, slug, title, upd, note in writes:
        cur = call(svc.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range=f"'{TAB}'!A{rn}:B{rn}")).get('values', [['', '']])[0]
        ct, cs = (cur[0] if cur else '').strip(), (cur[1] if len(cur) > 1 else '').strip()
        if cs != slug or ct.lower() != title.lower():
            print(f"  !! row {rn}: DRIFT expected ({title!r},{slug!r}) found ({ct!r},{cs!r}) — SKIPPED")
            continue
        data = [{'range': f"'{TAB}'!{col_letter(col_idx[k])}{rn}", 'values': [[v]]}
                for k, v in upd.items()]
        call(svc.spreadsheets().values().batchUpdate(
            spreadsheetId=SPREADSHEET_ID, body={'valueInputOption': 'RAW', 'data': data}))
        verify = call(svc.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range=f"'{TAB}'!B{rn}")).get('values', [['']])[0][0].strip()
        assert verify == slug, f"POST-WRITE DRIFT row {rn}"
        ok += 1
        print(f"  ok  row {rn}  {slug}", flush=True)
        time.sleep(3.2)
    print(f"\nWrote {ok}/{len(writes)} rows.")


if __name__ == '__main__':
    main()
