"""
Mass-fix the mechanical validator errors:

  (A) google_maps_url present but malformed (no `query_place_id=`)  -> 39 rows.
      The URL is either a /maps/search/?api=1&query=... or /maps/place/<encoded>
      form that doesn't pin a place. Without a verified place_id we can't
      attribute Google-derived assets to a real listing, so:
        * google_maps_url -> ''  (cleared; re-enrichment can refill it)
        * hero_image / photos / photo_count -> ''  if present (bleed-through risk)
  (B) photos / hero_image present but no place_id at all  -> subset of (A).

  rating / review_count are kept (the validator doesn't gate on them, and they
  may have been correct at one point).

Single batchUpdate after a one-shot A:B identity check vs the freshly-refreshed
CSV. Dry-run by default; --apply to write. Run from the repo root.
"""
import os, sys, csv, time

sys.path.insert(0, os.path.dirname(__file__))
from fix_audit_round import col_letter, TAB, SPREADSHEET_ID, TOKEN_PATH

sys.stdout = __import__('io').TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
CSV_PATH = 'facilities_local.csv'
APPLY = '--apply' in sys.argv
URL, HERO, PHOTOS, PCOUNT = 20, 52, 53, 54  # 1-based


def main():
    rows = list(csv.DictReader(open(CSV_PATH, encoding='utf-8')))
    g = lambda r, k: (r.get(k) or '').strip()
    live = [(i + 2, r) for i, r in enumerate(rows)
            if g(r, 'status') not in ('unverified', 'removed')]

    plan = []  # (rn, slug, title, updates dict col->'')
    for rn, r in live:
        u = g(r, 'google_maps_url')
        has_pid = 'query_place_id=' in u
        if u and not has_pid:
            upd = {URL: ''}
            if g(r, 'photos') or g(r, 'hero_image'):
                upd[HERO] = ''; upd[PHOTOS] = ''; upd[PCOUNT] = ''
            plan.append((rn, g(r, 'slug'), g(r, 'title'), upd))
        elif not u and (g(r, 'photos') or g(r, 'hero_image')):
            # photos without any URL — pure bleed
            plan.append((rn, g(r, 'slug'), g(r, 'title'),
                         {HERO: '', PHOTOS: '', PCOUNT: ''}))

    print(f"\n{'APPLY' if APPLY else 'DRY-RUN'} — {len(plan)} rows to clear\n")
    for rn, slug, title, upd in plan:
        cleared = ','.join({URL: 'maps_url', HERO: 'hero', PHOTOS: 'photos',
                            PCOUNT: 'photo_count'}[c] for c in upd)
        print(f'  row {rn:>4}  {slug:<55} clear: {cleared}')
    if not APPLY:
        print('\nDry run only. Re-run with --apply to write.')
        return

    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    svc = build('sheets', 'v4', credentials=Credentials.from_authorized_user_file(TOKEN_PATH))

    # one identity check vs the refreshed CSV — abort on any drift
    ab = svc.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=f"'{TAB}'!A2:B{len(rows) + 1}"
    ).execute().get('values', [])
    for rn, slug, title, _ in plan:
        live_pair = ab[rn - 2] if rn - 2 < len(ab) else ['', '']
        lt = (live_pair[0] if live_pair else '').strip()
        ls = (live_pair[1] if len(live_pair) > 1 else '').strip()
        if ls != slug or lt != title:
            print(f'  !! DRIFT row {rn}: expected ({title!r},{slug!r}) found ({lt!r},{ls!r}) — ABORT')
            return
    print('identity check passed — writing one batchUpdate...')

    data = [{'range': f"'{TAB}'!{col_letter(c)}{rn}", 'values': [['']]}
            for rn, _, _, upd in plan for c in upd]
    svc.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={'valueInputOption': 'RAW', 'data': data}).execute()
    print(f'wrote {len(data)} cells across {len(plan)} rows')


if __name__ == '__main__':
    main()
