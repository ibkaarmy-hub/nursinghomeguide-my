"""
Fix wrong-facility photo bleed-through.

When fix_audit_round.py corrected/cleared the 42 wrong place_ids (Check 7a) and
the 5 dead ones (7b), and screen_closed.py hid the 11 permanently-closed rows,
each fix touched google_maps_url / rating / review_count but NOT hero_image /
photos / photo_count — which had been enriched from the *wrong* place_id in the
original pass. Those rows still show another facility's photos.

This script visits every affected row (by number — row numbers <= 815 are
stable; the only structural change since was appends at the end):
  * row still has a place_id  -> re-fetch photos from it (new Places API),
    overwrite hero_image / photos / photo_count;
  * row has no place_id       -> clear hero_image / photos / photo_count
    (no verifiable photo source).

Each write is identity-checked against the freshly-refreshed CSV. Dry-run by
default; pass --apply. Run from the repo root.
"""
import os, sys, csv, re, json, time, urllib.request

sys.path.insert(0, os.path.dirname(__file__))
from fix_audit_round import col_letter, TAB, SPREADSHEET_ID, TOKEN_PATH

sys.stdout = __import__('io').TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
CSV_PATH = 'facilities_local.csv'
APPLY = '--apply' in sys.argv
KEY = os.environ.get('GOOGLE_MAPS_KEY', '').strip()
HERO, PHOTOS, PCOUNT = 52, 53, 54  # 1-based columns

# Affected row numbers, from this session's audit (Check 7a + 7b) and the
# permanently-closed sweep. Row 619 (Bukit Baru) already re-fetched separately.
AFFECTED_ROWS = sorted(set([
    # 7a — wrong-facility place_id
    84, 98, 324, 330, 331, 390, 396, 409, 445, 456, 461, 462, 473, 475, 510,
    512, 555, 559, 580, 581, 592, 594, 598, 612, 613, 614, 629, 632, 665, 666,
    669, 671, 676, 681, 705, 710, 712, 714, 716, 743, 786, 803,
    # 7b — dead place_id
    127, 130, 150, 213, 216,
    # permanently-closed sweep
    185, 279, 296, 377, 389, 393, 654, 662, 721, 798,
]))


def place_id_of(u):
    m = re.search(r'query_place_id=([\w-]+)', u or '')
    return m.group(1) if m else ''


def fetch_photos(pid, limit=10):
    """New Places API: place photos -> resolved lh3 URLs. Returns [] on any error."""
    try:
        req = urllib.request.Request(
            'https://places.googleapis.com/v1/places/' + pid,
            headers={'X-Goog-Api-Key': KEY, 'X-Goog-FieldMask': 'photos'})
        photos = json.load(urllib.request.urlopen(req, timeout=25)).get('photos', [])
    except Exception as e:
        print(f'    photo list error: {e}')
        return []
    urls = []
    for ph in photos[:limit]:
        try:
            r = urllib.request.Request(
                'https://places.googleapis.com/v1/' + ph['name']
                + '/media?maxWidthPx=1200&skipHttpRedirect=true&key=' + KEY)
            u = json.load(urllib.request.urlopen(r, timeout=20)).get('photoUri', '')
            if u:
                urls.append(u)
        except Exception:
            pass
        time.sleep(0.1)
    return urls


def main():
    rows = list(csv.reader(open(CSV_PATH, encoding='utf-8')))
    hdr = rows[0]
    gm = hdr.index('google_maps_url')

    plan = []  # (rownum, slug, title, action, updates)
    for rn in AFFECTED_ROWS:
        r = rows[rn - 1]
        slug, title = r[1].strip(), r[0].strip()
        has_photos = bool(r[PHOTOS - 1].strip() or r[HERO - 1].strip())
        pid = place_id_of(r[gm])
        if pid:
            urls = fetch_photos(pid)
            if urls:
                plan.append((rn, slug, title, f'refetch {len(urls)} photos',
                             {HERO: urls[0], PHOTOS: '|'.join(urls), PCOUNT: str(len(urls))}))
            else:
                plan.append((rn, slug, title, 'place_id has no photos -> clear',
                             {HERO: '', PHOTOS: '', PCOUNT: ''}))
        elif has_photos:
            plan.append((rn, slug, title, 'no place_id -> clear wrong photos',
                         {HERO: '', PHOTOS: '', PCOUNT: ''}))
        # no place_id + no photos -> nothing to do

    print(f"\n{'APPLY' if APPLY else 'DRY-RUN'} — {len(plan)} rows to fix\n")
    for rn, slug, title, action, _ in plan:
        print(f'  row {rn:>4}  {slug:<52} {action}')
    if not APPLY:
        print('\nDry run only. Re-run with --apply to write.')
        return

    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    svc = build('sheets', 'v4', credentials=Credentials.from_authorized_user_file(TOKEN_PATH))

    def call(req):
        for attempt in range(6):
            try:
                return req.execute()
            except HttpError as e:
                if e.resp.status == 429:
                    w = 30 * (attempt + 1)
                    print(f'   ...429, sleeping {w}s', flush=True); time.sleep(w); continue
                raise
        raise RuntimeError('repeated 429s')

    ok = 0
    for rn, slug, title, action, updates in plan:
        cur = call(svc.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range=f"'{TAB}'!A{rn}:B{rn}")).get('values', [['', '']])[0]
        ct = (cur[0] if cur else '').strip()
        cs = (cur[1] if len(cur) > 1 else '').strip()
        if cs != slug or ct != title:
            print(f'  !! row {rn}: DRIFT expected ({title!r},{slug!r}) found ({ct!r},{cs!r}) — SKIPPED')
            continue
        data = [{'range': f"'{TAB}'!{col_letter(c)}{rn}", 'values': [[v]]}
                for c, v in updates.items()]
        call(svc.spreadsheets().values().batchUpdate(
            spreadsheetId=SPREADSHEET_ID, body={'valueInputOption': 'RAW', 'data': data}))
        ok += 1
        print(f'  ok  row {rn}  {slug}  ({action})', flush=True)
        time.sleep(3.2)
    print(f'\nFixed {ok}/{len(plan)} rows.')


if __name__ == '__main__':
    main()
