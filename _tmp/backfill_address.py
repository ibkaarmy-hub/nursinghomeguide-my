"""
Backfill the `address` column from Google's formatted_address for every live
facility that has a name-matching place_id and an empty address cell.

The audit's Place Details cache (_tmp/audit_places_cache.json) already holds
formatted_address for ~624 place_ids; any current place_id missing from it is
fetched fresh. A row is only written if A.names_match(title, google_name) holds
— so a place_id pointing at the wrong facility never seeds a wrong address.

Efficiency: instead of per-row read/verify (would be ~600 * 3 API calls), this
reads the whole A:B range once, asserts it matches the freshly-refreshed CSV
(no drift), then writes every address cell in a single values.batchUpdate.

Dry-run by default; pass --apply to write. Run from the repo root.
"""
import os, sys, csv, json, time, urllib.parse, urllib.request

sys.path.insert(0, os.path.dirname(__file__))
import audit_profile_data as A
from fix_audit_round import col_letter, TAB, SPREADSHEET_ID, TOKEN_PATH

CSV_PATH = 'facilities_local.csv'
ADDRESS_COL = 72  # `address` (1-based)
MAPS_KEY = os.environ.get('GOOGLE_MAPS_KEY', '').strip()
APPLY = '--apply' in sys.argv


def details(pid):
    fields = 'name,formatted_address'
    url = ('https://maps.googleapis.com/maps/api/place/details/json'
           f'?place_id={urllib.parse.quote(pid)}&fields={fields}&key={MAPS_KEY}')
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.load(r)


def main():
    rows = list(csv.DictReader(open(CSV_PATH, encoding='utf-8')))
    g = lambda r, k: (r.get(k) or '').strip()
    cache = json.load(open(A.PLACES_CACHE, encoding='utf-8')) if os.path.exists(A.PLACES_CACHE) else {}

    live = []
    for i, r in enumerate(rows):
        r['_row'] = i + 2
        if g(r, 'slug') and g(r, 'status').lower() not in ('unverified', 'removed'):
            live.append(r)

    # rows that need an address and have a place_id to source it from
    todo = [(r, A.place_id_of(g(r, 'google_maps_url'))) for r in live
            if not g(r, 'address')]
    todo = [(r, p) for r, p in todo if p]
    missing = [(r, p) for r, p in todo if f'd:{p}' not in cache]
    print(f'{len(live)} live rows; {len(todo)} need address + have place_id; '
          f'{len(missing)} place_ids to fetch fresh', file=sys.stderr)
    for n, (r, p) in enumerate(missing, 1):
        try:
            cache[f'd:{p}'] = details(p)
        except Exception as e:
            cache[f'd:{p}'] = {'status': 'FETCH_ERROR', 'error': str(e)}
        time.sleep(0.1)
        if n % 25 == 0:
            json.dump(cache, open(A.PLACES_CACHE, 'w', encoding='utf-8'))
    json.dump(cache, open(A.PLACES_CACHE, 'w', encoding='utf-8'))

    writes, skipped = [], []
    for r, p in todo:
        d = cache.get(f'd:{p}', {})
        if d.get('status') != 'OK':
            skipped.append((r, p, d.get('status', '?')))
            continue
        res = d['result']
        gname, gaddr = res.get('name', ''), res.get('formatted_address', '')
        if not gaddr:
            skipped.append((r, p, 'no formatted_address'))
            continue
        if not A.names_match(g(r, 'title'), gname):
            skipped.append((r, p, f'name mismatch (google: {gname!r})'))
            continue
        writes.append((r['_row'], r['slug'], g(r, 'title'), gaddr))

    print(f"\n{'APPLY' if APPLY else 'DRY-RUN'} — {len(writes)} address cells to fill, "
          f"{len(skipped)} skipped\n")
    for rn, slug, title, addr in writes[:15]:
        print(f"  row {rn:>4}  {slug:<50} {addr}")
    if len(writes) > 15:
        print(f"  ... and {len(writes) - 15} more")
    if skipped:
        print(f"\n  skipped (no usable address): {len(skipped)} — e.g.")
        for r, p, why in skipped[:8]:
            print(f"    {r['slug']}: {why}")

    if not APPLY:
        print("\nDry run only. Re-run with --apply to write.")
        return

    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    svc = build('sheets', 'v4', credentials=Credentials.from_authorized_user_file(TOKEN_PATH))

    # one read of the whole identity range; assert no drift vs the refreshed CSV
    ab = svc.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=f"'{TAB}'!A2:B{len(rows) + 1}"
    ).execute().get('values', [])
    csv_ident = {i + 2: (g(r, 'title'), g(r, 'slug')) for i, r in enumerate(rows)}
    for rn, slug, title, addr in writes:
        live_pair = ab[rn - 2] if rn - 2 < len(ab) else ['', '']
        lt = (live_pair[0] if live_pair else '').strip()
        ls = (live_pair[1] if len(live_pair) > 1 else '').strip()
        if ls != slug or lt.lower() != title.lower():
            print(f"  !! DRIFT at row {rn}: expected ({title!r},{slug!r}) found ({lt!r},{ls!r}) — ABORT")
            return
    print("identity check passed — no drift; writing in one batch...")

    data = [{'range': f"'{TAB}'!{col_letter(ADDRESS_COL)}{rn}", 'values': [[addr]]}
            for rn, slug, title, addr in writes]
    svc.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={'valueInputOption': 'RAW', 'data': data}).execute()
    print(f"Wrote {len(data)} address cells in one batchUpdate.")

    # spot-check 3 rows
    for rn, slug, title, addr in (writes[:1] + writes[len(writes)//2:len(writes)//2+1] + writes[-1:]):
        chk = svc.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"'{TAB}'!B{rn}:B{rn}").execute().get('values', [['']])[0][0].strip()
        got = svc.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"'{TAB}'!{col_letter(ADDRESS_COL)}{rn}").execute().get('values', [['']])[0]
        print(f"  verify row {rn} slug={chk!r} address={ (got[0] if got else '')[:60]!r}")


if __name__ == '__main__':
    main()
