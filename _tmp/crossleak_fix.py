"""
Apply cross-leak fixes after deep website verification.

Per-domain decisions in CROSSLEAK_REPORT.md. This script only does the
mechanical sheet writes; the report explains the why for each.

Wrong-website clears (5 rows):
  row 464  edelweiss-elderly-care-centre              eldershome.com.my doesn't mention "Edelweiss"
  row 509  house-of-megaways-care-centre              megaseniorcarecentre.com is Mega's only PJ site
  row 621  pusat-jagaan-mak-swee-cawangan-1           thedementiasocietyperak is Ipoh-only
  row 671  pusat-jagaan-rumah-sejahtera-gopeng        tbspinghe.org is Harmopeace's site

Duplicate deactivation (1 row):
  row 517  joyful-home-elderly-care-centre  -> removed
       (same place_id, same address as the canonical my-joyful-home-care-centre row 300)

All writes identity-checked before applying.
"""
import os, sys, csv, time

sys.path.insert(0, os.path.dirname(__file__))
from fix_audit_round import col_letter, TAB, SPREADSHEET_ID, TOKEN_PATH

sys.stdout = __import__('io').TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
CSV_PATH = 'facilities_local.csv'
APPLY = '--apply' in sys.argv

C = {'website': 6, 'status': 56, 'last_updated': 21}
TODAY = time.strftime('%Y-%m-%d')

OPS = [
    (464, 'edelweiss-elderly-care-centre', 'Edelweiss Elderly Care Centre',
     {'website': '', 'last_updated': TODAY},
     "edelweiss not mentioned on eldershome.com.my — wrong website cleared"),
    (509, 'house-of-megaways-care-centre', 'House of Megaways Care Centre',
     {'website': '', 'last_updated': TODAY},
     "megaseniorcarecentre.com is Mega's PJ-only site; this row is Seremban NS — wrong website cleared"),
    (621, 'pusat-jagaan-mak-swee-cawangan-1', 'Pusat Jagaan Mak Swee (Cawangan 1)',
     {'website': '', 'last_updated': TODAY},
     "thedementiasocietyperak is an Ipoh-only day centre; this row is Muar Johor — wrong website cleared"),
    (671, 'pusat-jagaan-rumah-sejahtera-gopeng', 'Pusat Jagaan Rumah Sejahtera Gopeng',
     {'website': '', 'last_updated': TODAY},
     "tbspinghe.org is the Harmopeace site (different facility); wrong website cleared"),
    (517, 'joyful-home-elderly-care-centre', 'Joyful Home Elderly Care Centre',
     {'status': 'removed', 'last_updated': TODAY},
     "duplicate of row 300 my-joyful-home-care-centre (same place_id, address, rating) -> removed"),
]


def main():
    rows = list(csv.reader(open(CSV_PATH, encoding='utf-8')))
    print(f"\n{'APPLY' if APPLY else 'DRY-RUN'} — {len(OPS)} ops\n")
    drift = False
    for rn, slug, title, upd, note in OPS:
        live = rows[rn - 1]
        ls, lt = live[1].strip(), live[0].strip()
        ok = ls == slug and lt == title
        if not ok: drift = True
        print(f"  [{'ok' if ok else '!!'}] row {rn:>4}  {note}")
        if not ok:
            print(f'         expected ({title!r},{slug!r}) found ({lt!r},{ls!r})')
        for k, v in upd.items():
            print(f'           {k} = ' + (repr(v) if v else '<clear>'))
    if drift and APPLY:
        print('drift detected — abort'); sys.exit(1)
    if not APPLY:
        print('\nDry run only. Re-run with --apply.')
        return

    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    svc = build('sheets', 'v4', credentials=Credentials.from_authorized_user_file(TOKEN_PATH))
    data = []
    for rn, _, _, upd, _ in OPS:
        for k, v in upd.items():
            data.append({'range': f"'{TAB}'!{col_letter(C[k])}{rn}", 'values': [[v]]})
    svc.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={'valueInputOption': 'RAW', 'data': data}).execute()
    print(f'\nwrote {len(data)} cells across {len(OPS)} rows.')


if __name__ == '__main__':
    main()
