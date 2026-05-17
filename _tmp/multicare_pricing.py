"""
Apply MultiCare Nursing Home pricing to the PJ row (row 395) from the scraped
operator website (multicarehomes.com/packages.html), plus updates the contact
phone to the operator's main +60 12-650 1805 number.

The packages page lists 7 room tiers from VIP RM 3,500 down to 6-bed sharing
RM 1,800, all 'with Personal Caregiver'. The Facilities sheet's flat pricing
columns capture the summary; the full per-room breakdown lands in the Details
tab under section='rooms' so the Pricing tab renders the complete table.
"""
import os, sys, csv, time

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.getcwd())  # for _enrich_lib in repo root
from fix_audit_round import col_letter, TAB, SPREADSHEET_ID, TOKEN_PATH
DETAILS_TAB_GID = 1104748854

sys.stdout = __import__('io').TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
CSV_PATH = 'facilities_local.csv'
APPLY = '--apply' in sys.argv
TODAY = time.strftime('%Y-%m-%d')

# 1-based Facilities columns
C = {'phone': 5, 'pricing_display': 7, 'shared_price': 8, 'private_price': 9,
     'four_bed_price': 47, 'dorm_price': 48, 'last_updated': 21}

# Per-room pricing (verbatim from multicarehomes.com/packages.html)
ROOMS = [
    ('VIP (RM/mo)',          '3,500'),
    ('Single (RM/mo)',       '3,000'),
    ('2-bed sharing (RM/mo)','2,800'),
    ('3-bed sharing (RM/mo)','2,500'),
    ('4-bed sharing (RM/mo)','2,300'),
    ('5-bed sharing (RM/mo)','2,000'),
    ('6-bed sharing (RM/mo)','1,800'),
]
INCLUDED = [
    ('Personal caregiver',    'yes'),
    ('Air-conditioned room',  'yes'),
    ('TV with WiFi',          'yes'),
    ('Attached bathroom',     'yes'),
    ('Meals in room',         'yes'),
    ('24-hour care assistant','yes'),
]

# Facilities row 395 updates
ROW395_UPDATES = {
    'phone':           '+60 12-650 1805',          # was 03-79321621; operator main
    'pricing_display': 'From RM 1,800/mo (6-bed sharing) — RM 3,500/mo (VIP)',
    'shared_price':    '2800',                     # 2-bed sharing
    'private_price':   '3000',                     # single room
    'four_bed_price':  '2300',
    'dorm_price':      '1800',                     # 6-bed sharing
    'last_updated':    TODAY,
}

SLUG = 'multicare-nursing-home'
TITLE = 'MultiCare Nursing Home'


def main():
    rows = list(csv.reader(open(CSV_PATH, encoding='utf-8')))
    live = rows[394]  # row 395 (1-based)
    print(f"\n{'APPLY' if APPLY else 'DRY-RUN'} — multicare pricing")
    print(f'  row 395 (PJ) sheet says: title={live[0]!r}  slug={live[1]!r}')
    assert live[1].strip() == SLUG and live[0].strip() == TITLE, \
        f'identity mismatch — expected {TITLE!r}/{SLUG!r}'
    print('  identity OK')
    print('  Facilities row updates:')
    for k, v in ROW395_UPDATES.items():
        print(f'    {k} = {v!r}')
    print(f'  Details rows to append (section=rooms, {len(ROOMS)}):')
    for lbl, val in ROOMS:
        print(f'    {lbl}: {val}')
    print(f'  Details rows to append (section=included, {len(INCLUDED)}):')
    for lbl, val in INCLUDED:
        print(f'    {lbl}: {val}')

    if not APPLY:
        print('\nDry run only. Re-run with --apply.')
        return

    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    svc = build('sheets', 'v4', credentials=Credentials.from_authorized_user_file(TOKEN_PATH))

    # Update Facilities row 395
    data = [{'range': f"'{TAB}'!{col_letter(C[k])}395", 'values': [[v]]}
            for k, v in ROW395_UPDATES.items()]
    svc.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={'valueInputOption': 'RAW', 'data': data}).execute()
    print(f'  wrote {len(data)} Facilities cells')

    # Append Details rows — resolve Details tab name from gid
    meta = svc.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    details_name = next(s['properties']['title'] for s in meta['sheets']
                        if s['properties']['sheetId'] == DETAILS_TAB_GID)
    details_rows = [[SLUG, 'rooms', lbl, val] for lbl, val in ROOMS] \
                 + [[SLUG, 'included', lbl, val] for lbl, val in INCLUDED]
    svc.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{details_name}'!A:D",
        valueInputOption='RAW',
        body={'values': details_rows}).execute()
    print(f'  appended {len(details_rows)} Details rows to {details_name!r}')


if __name__ == '__main__':
    main()
