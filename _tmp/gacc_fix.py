"""
Reconcile the Golden Age Care Centre (GACC) chain — 4 branches per the
operator (Muar HQ, Melaka, Batu Pahat, Tangkak):

  Row 38  golden-age-care-centre-muar       FIX place_id (was wrong PJ Selangor),
                                            address, area, photos
  Row 44  golden-age-care-centre-tangkak    already correct — no change
  Row 86  golden-age-care-centre-batu-pahat phone -> office +60 7-430 0880
  Row 485 golden-age-care-centre-sdn-bhd    REMOVED (duplicate of Batu Pahat:
                                            same place_id, same address)
  NEW     golden-age-care-centre-melaka     APPEND (was missing from the sheet)

Branch addresses + phones provided by the operator directly. Place_ids
verified via Places API text search. Single batchUpdate after one
identity check vs the freshly-refreshed CSV.

Run from repo root. Dry-run by default; --apply to write.
"""
import os, sys, csv, json, time, urllib.parse

sys.path.insert(0, os.path.dirname(__file__))
from fix_audit_round import col_letter, TAB, SPREADSHEET_ID, TOKEN_PATH

sys.stdout = __import__('io').TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
CSV_PATH = 'facilities_local.csv'
APPLY = '--apply' in sys.argv
TODAY = time.strftime('%Y-%m-%d')
NCOLS = 74

C = {'title': 1, 'slug': 2, 'area': 4, 'phone': 5, 'website': 6,
     'pricing_display': 7, 'care_types': 10, 'rating': 16, 'review_count': 17,
     'latitude': 18, 'longitude': 19, 'google_maps_url': 20, 'last_updated': 21,
     'editorial_summary': 51, 'hero_image': 52, 'photos': 53, 'photo_count': 54,
     'state': 55, 'status': 56, 'address': 72}


def U(title, pid):
    return ('https://www.google.com/maps/search/?api=1&query='
            + urllib.parse.quote(title) + '&query_place_id=' + pid)


photos = json.load(open('_tmp/gacc_photos.json', encoding='utf-8'))
MUAR_PHOTOS, MELAKA_PHOTOS = photos['muar'], photos['melaka']

# ── per-row updates ─────────────────────────────────────────────────────────
UPDATES = [
    # Row 38 — Muar: fix place_id, address, area; refresh photos
    (38, 'golden-age-care-centre-muar', 'Golden Age Care Centre (Muar)', {
        'title': 'Golden Age Care Centre (Muar)',
        'area': 'Taman Ria, Muar',
        'phone': '+60 6-952 7711',
        'address': "28-10, Jalan Ria 2, Taman Ria, 84000 Muar, Johor Darul Ta'zim, Malaysia",
        'google_maps_url': U('Golden Age Care Centre (Muar)', 'ChIJ9ZGrE2u50TER2SScyJEir88'),
        'rating': '3.9', 'review_count': '8',
        'hero_image': MUAR_PHOTOS[0] if MUAR_PHOTOS else '',
        'photos': '|'.join(MUAR_PHOTOS),
        'photo_count': str(len(MUAR_PHOTOS)),
        'last_updated': TODAY,
    }, 'Muar: correct place_id + address + photos (was wrong PJ listing)'),

    # Row 86 — Batu Pahat: phone -> office number
    (86, 'golden-age-care-centre-batu-pahat', 'Golden Age Care Centre Batu Pahat', {
        'phone': '+60 7-430 0880',
        'last_updated': TODAY,
    }, 'Batu Pahat: phone -> office +60 7-430 0880 (operator-provided)'),

    # Row 485 — sdn-bhd duplicate -> removed
    (485, 'golden-age-care-centre-sdn-bhd', 'Golden Age Care Centre Sdn. Bhd', {
        'status': 'removed',
    }, '-sdn-bhd: removed (same place_id + address as the Batu Pahat row 86)'),
]

# ── new Melaka row (append) ─────────────────────────────────────────────────
MELAKA_TITLE = 'Golden Age Care Centre (Melaka)'
MELAKA_ROW_FIELDS = {
    'title': MELAKA_TITLE,
    'slug': 'golden-age-care-centre-melaka',
    'area': 'Taman Bukit Serindit',
    'phone': '+60 6-286 5566',
    'website': 'https://gacc.com.my',
    'pricing_display': 'Call for pricing',
    'care_types': 'Elderly Care',
    'rating': '4', 'review_count': '9',
    'google_maps_url': U(MELAKA_TITLE, 'ChIJ_3hCRSbv0TERmAoiCpkFEKE'),
    'last_updated': TODAY,
    'hero_image': MELAKA_PHOTOS[0] if MELAKA_PHOTOS else '',
    'photos': '|'.join(MELAKA_PHOTOS),
    'photo_count': str(len(MELAKA_PHOTOS)),
    'state': 'Melaka',
    'address': 'Lot 643, Jalan Bukit Serindit, Taman Bukit Serindit, 75400 Melaka, Malaysia',
}


def build_new_row():
    row = [''] * NCOLS
    for k, v in MELAKA_ROW_FIELDS.items():
        row[C[k] - 1] = v
    return row


def main():
    rows = list(csv.reader(open(CSV_PATH, encoding='utf-8')))
    print(f"\n{'APPLY' if APPLY else 'DRY-RUN'} — {len(UPDATES)} updates + 1 new row\n")
    drift = False
    for rn, exp_slug, exp_title, upd, note in UPDATES:
        live = rows[rn - 1]
        ls, lt = live[1].strip(), live[0].strip()
        ok = ls == exp_slug and lt == exp_title
        flag = 'ok' if ok else '!!'
        if not ok: drift = True
        print(f'  [{flag}] row {rn:>4}  {note}')
        if not ok:
            print(f'         expected ({exp_title!r},{exp_slug!r}) found ({lt!r},{ls!r})')
        for k, v in upd.items():
            s = repr(v[:60] + '…' if isinstance(v, str) and len(v) > 60 else v)
            print(f'           {k} = {s}')
    print(f'  [+]  APPEND  new row: {MELAKA_TITLE} (place_id ChIJ_3hCRSbv0TER…, {len(MELAKA_PHOTOS)} photos)')
    if drift and APPLY:
        print('\n!! drift — abort'); sys.exit(1)
    if not APPLY:
        print('\nDry run only. Re-run with --apply.')
        return

    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    svc = build('sheets', 'v4', credentials=Credentials.from_authorized_user_file(TOKEN_PATH))

    # apply per-row updates as a single batchUpdate
    data = []
    for rn, _, _, upd, _ in UPDATES:
        for k, v in upd.items():
            data.append({'range': f"'{TAB}'!{col_letter(C[k])}{rn}", 'values': [[v]]})
    svc.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={'valueInputOption': 'RAW', 'data': data}).execute()
    print(f'wrote {len(data)} cells across {len(UPDATES)} existing rows')

    # append Melaka
    svc.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{TAB}'!A:A",
        valueInputOption='RAW', insertDataOption='INSERT_ROWS',
        body={'values': [build_new_row()]}).execute()
    print('appended Melaka row')


if __name__ == '__main__':
    main()
