"""
Set up the three Pusat Jagaan Mahligai Kasih Juju branches as a proper chain.

The sheet currently has TWO duplicate rows (619, 620) for the same Bukit Baru
branch and nothing for the other two branches the operator runs.

This script:
  1. Merges the Bukit Baru duplicates -> keeps row 619 as the canonical
     Bukit Baru row (slug pusat-jagaan-mahligai-kasih-juju-bukit-baru), pulling
     in website/area/lat/lng from row 620; licence cleared (the two rows
     disagreed and neither is confidently correct); sets row 620 status=removed.
  2. Appends new rows for the Bachang (MKJ2) and Hulu Langat (MKJ3) branches,
     with editorials grounded in the scraped operator site + each branch's
     Google reviews.

Row-number writes are identity-checked (col A+B) before writing. Dry-run by
default; pass --apply. Run from the repo root.
"""
import os, sys, csv, time, urllib.parse

sys.path.insert(0, os.path.dirname(__file__))
from fix_audit_round import col_letter, TAB, SPREADSHEET_ID, TOKEN_PATH

sys.stdout = __import__('io').TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
CSV_PATH = 'facilities_local.csv'
APPLY = '--apply' in sys.argv
TODAY = time.strftime('%Y-%m-%d')

# ── column map (1-based) ────────────────────────────────────────────────────
C = {'title': 1, 'slug': 2, 'url': 3, 'area': 4, 'phone': 5, 'website': 6,
     'pricing_display': 7, 'care_types': 10, 'rating': 16, 'review_count': 17,
     'latitude': 18, 'longitude': 19, 'google_maps_url': 20, 'last_updated': 21,
     'licence_number': 24, 'editorial_summary': 51, 'state': 55, 'status': 56,
     'address': 72}
NCOLS = 74


def maps_url(title, pid):
    return ('https://www.google.com/maps/search/?api=1&query='
            + urllib.parse.quote(title) + '&query_place_id=' + pid)


BACHANG_EDITORIAL = """Pusat Jagaan Mahligai Kasih Juju operates its Bachang branch (MKJ2) at 25, Jalan Duku 2, Taman Rumpun Bahagia, 75250 Melaka. Bachang is an established residential and light-commercial district on the northern side of Melaka city, within reach of Melaka town and Hospital Melaka. This is the operator's second Melaka site, alongside the original Bukit Baru centre and a third branch in Hulu Langat, Selangor. The branch holds a 4.9-star Google rating across 13 reviews.

**Services (from mahligaikasihjuju.com):**
- Centre-based day care (balik hari)
- Short-term and respite residential care (24-hour)
- Long-term residential care (24-hour)
- Mobile home care by licensed nurses
- Mobile hospital care by licensed nurses

**What reviewers say (Google, 13 reviews, 4.9★):**
- Families describe staff as caring, friendly and welcoming
- Reviewers note attentive wound care for residents recovering from surgery
- The centre is described as clean, with a daily programme of activities
- Meals are described as nutritious and balanced

Pricing is not published — contact the operator on +60 18-371 4559 for a quote; the same number serves the wider Mahligai Kasih Juju group. JKM registration should be confirmed for this specific Bachang address before committing.

**What to ask on visit:**
- Is JKM registration current for the Bachang branch specifically — may we see the licence?
- What is the monthly fee for long-term residential care, and what does it cover?
- How many licensed nurses are on duty per shift?
- What does the daily activities programme involve?
- How is a resident's family kept updated when their condition changes?
- What is the deposit amount and the written refund policy?"""

HULU_LANGAT_EDITORIAL = """Pusat Jagaan Mahligai Kasih Juju operates its Hulu Langat branch (MKJ3) at No. 3 & 4, Jalan Lestari Mewah 3, Taman Lestari Mewah, 43100 Hulu Langat, Selangor. This is the operator's Selangor location, in the Hulu Langat district near the Cheras–Kajang corridor, alongside two Melaka branches in Bukit Baru and Bachang. The branch holds a 4.6-star Google rating across 19 reviews.

**Services (from mahligaikasihjuju.com):**
- Centre-based day care (balik hari)
- Short-term and respite residential care (24-hour)
- Long-term residential care (24-hour)
- Mobile home care by licensed nurses
- Mobile hospital care by licensed nurses

**What reviewers say (Google, 19 reviews, 4.6★):**
- Reviewers describe qualified, trusted staff and good care of residents
- Families describe the environment as comfortable, with attentive service to the elderly
- Several reviewers recommend the home to others

Pricing is not published — contact the branch on +60 12-373 2984 for a quote. JKM registration should be confirmed for the Hulu Langat address specifically before committing.

**What to ask on visit:**
- Is JKM registration current for the Hulu Langat branch — may we see the licence?
- What is the deposit amount, and what is the written refund policy if a placement ends early?
- What is the monthly fee for long-term residential care, and what does it cover?
- How many licensed nurses are on duty per shift?
- What does the daily activities programme involve?
- How are families kept updated when a resident's condition changes?"""

# ── new branch rows (col-name -> value) ─────────────────────────────────────
BACHANG = {
    'title': 'Pusat Jagaan Mahligai Kasih Juju (Bachang)',
    'slug': 'pusat-jagaan-mahligai-kasih-juju-bachang',
    'area': 'Bachang',
    'phone': '+60183714559',
    'website': 'https://www.mahligaikasihjuju.com/',
    'pricing_display': 'Call for pricing',
    'care_types': 'Elderly Care',
    'rating': '4.9', 'review_count': '13',
    'latitude': '2.2235142', 'longitude': '102.2468289',
    'google_maps_url': maps_url('Pusat Jagaan Mahligai Kasih Juju (Bachang)',
                                'ChIJqdKa2hLx0TER-Ob0LPxfAEI'),
    'last_updated': TODAY,
    'editorial_summary': BACHANG_EDITORIAL,
    'state': 'Melaka',
    'address': '25, Jalan Duku 2, Taman Rumpun Bahagia, 75250 Melaka, Malaysia',
}
HULU_LANGAT = {
    'title': 'Pusat Jagaan Mahligai Kasih Juju (Hulu Langat)',
    'slug': 'pusat-jagaan-mahligai-kasih-juju-hulu-langat',
    'area': 'Hulu Langat',
    'phone': '+60123732984',
    'website': 'https://www.mahligaikasihjuju.com/',
    'pricing_display': 'Call for pricing',
    'care_types': 'Elderly Care',
    'rating': '4.6', 'review_count': '19',
    'latitude': '3.1184432', 'longitude': '101.8162602',
    'google_maps_url': maps_url('Pusat Jagaan Mahligai Kasih Juju (Hulu Langat)',
                                'ChIJrYlA-FTPzTERN5sxg0uw59w'),
    'last_updated': TODAY,
    'editorial_summary': HULU_LANGAT_EDITORIAL,
    'state': 'Selangor',
    'address': 'No 3 & 4, Jalan Lestari Mewah 3, Taman Lestari Mewah, 43100 Hulu Langat, Selangor, Malaysia',
}

# ── Bukit Baru merge: updates applied to surviving row 619 ───────────────────
BUKIT_BARU_UPDATES = {
    'title': 'Pusat Jagaan Mahligai Kasih Juju (Bukit Baru)',
    'slug': 'pusat-jagaan-mahligai-kasih-juju-bukit-baru',
    'area': 'Taman Putra',
    'website': 'https://www.mahligaikasihjuju.com/',
    'latitude': '2.2233501', 'longitude': '102.2442206',
    'licence_number': '',          # the two dup rows disagreed; cleared per review
    'last_updated': TODAY,
}


def build_row(d):
    row = [''] * NCOLS
    for k, v in d.items():
        row[C[k] - 1] = v
    return row


def main():
    rows = list(csv.reader(open(CSV_PATH, encoding='utf-8')))
    r619, r620 = rows[618], rows[619]
    old_slug = 'pusat-jagaan-mahligai-kasih-juju-sdn-bhd'
    assert r619[1].strip() == old_slug and r620[1].strip() == old_slug, \
        f'rows 619/620 are not the expected MKJ dups: {r619[1]!r} {r620[1]!r}'

    print('PLAN')
    print(f'  row 619  MERGE -> Bukit Baru canonical row')
    for k, v in BUKIT_BARU_UPDATES.items():
        print(f'           {k} = ' + (repr(v) if v else '<clear>'))
    print(f'  row 620  status -> removed (duplicate of Bukit Baru)')
    print(f'  APPEND   {BACHANG["slug"]}  ({BACHANG["state"]})')
    print(f'  APPEND   {HULU_LANGAT["slug"]}  ({HULU_LANGAT["state"]})')
    print(f"\n{'APPLY' if APPLY else 'DRY-RUN'}\n")
    if not APPLY:
        print('Dry run only. Re-run with --apply to write.')
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

    def verify_identity(rownum, exp_title, exp_slug):
        cur = call(svc.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range=f"'{TAB}'!A{rownum}:B{rownum}")
        ).get('values', [['', '']])[0]
        ct = (cur[0] if cur else '').strip()
        cs = (cur[1] if len(cur) > 1 else '').strip()
        assert cs == exp_slug and ct == exp_title, \
            f'DRIFT row {rownum}: expected ({exp_title!r},{exp_slug!r}) found ({ct!r},{cs!r})'

    # 1. merge into row 619
    verify_identity(619, 'Pusat Jagaan Mahligai Kasih Juju Sdn. Bhd.', old_slug)
    data = [{'range': f"'{TAB}'!{col_letter(C[k])}619", 'values': [[v]]}
            for k, v in BUKIT_BARU_UPDATES.items()]
    call(svc.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body={'valueInputOption': 'RAW', 'data': data}))
    print('  ok  row 619 merged ->', BUKIT_BARU_UPDATES['slug'])

    # 2. row 620 -> removed
    verify_identity(620, 'Pusat Jagaan Mahligai Kasih Juju Sdn. Bhd.', old_slug)
    call(svc.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID, range=f"'{TAB}'!{col_letter(C['status'])}620",
        valueInputOption='RAW', body={'values': [['removed']]}))
    print('  ok  row 620 status=removed')

    # 3. append the two new branch rows
    call(svc.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID, range=f"'{TAB}'!A:A",
        valueInputOption='RAW', insertDataOption='INSERT_ROWS',
        body={'values': [build_row(BACHANG), build_row(HULU_LANGAT)]}))
    print('  ok  appended Bachang + Hulu Langat rows')

    # verify the appends landed
    colB = call(svc.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=f"'{TAB}'!B:B")).get('values', [])
    slugs = [r[0].strip() for r in colB if r]
    for s in (BACHANG['slug'], HULU_LANGAT['slug'], BUKIT_BARU_UPDATES['slug']):
        print(f"  verify  {s}: {'present' if s in slugs else 'MISSING'}")
    print(f"  verify  old dup slug {old_slug}: appears {slugs.count(old_slug)}x (expect 1, row 620 removed)")


if __name__ == '__main__':
    main()
