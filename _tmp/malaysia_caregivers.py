"""
Append a Home Care profile for Malaysia Caregivers — the MCS Group's private-
nursing / caregiver-dispatch arm (same group as MultiCare Nursing Home). The
operator publishes its services and pricing on malaysiacaregivers.com.

Care category is Home Care (caregiver/nurse dispatch to home or hospital, not
a residential facility), so the page lands at /home-care/<slug>/.

All facts in the editorial are quoted/paraphrased from malaysiacaregivers.com
verified this session.
"""
import os, sys, csv, time

sys.path.insert(0, os.path.dirname(__file__))
from fix_audit_round import col_letter, TAB, SPREADSHEET_ID, TOKEN_PATH

sys.stdout = __import__('io').TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
CSV_PATH = 'facilities_local.csv'
APPLY = '--apply' in sys.argv
TODAY = time.strftime('%Y-%m-%d')
NCOLS = 74
DETAILS_TAB_GID = 1104748854

C = {'title': 1, 'slug': 2, 'area': 4, 'phone': 5, 'website': 6,
     'pricing_display': 7, 'care_types': 10, 'last_updated': 21,
     'editorial_summary': 51, 'state': 55, 'address': 72}

SLUG = 'malaysia-caregivers'
TITLE = 'Malaysia Caregivers (MultiCare Private Nursing)'

EDITORIAL = """Malaysia Caregivers is the private caregiver and home-nursing arm of MCS Group — the same operator behind MultiCare Nursing Home in Petaling Jaya. Rather than a residential facility, it is a dispatch service that places trained caregivers and nurses into clients' homes or into hospital wards, anywhere in Malaysia, from a Petaling Jaya base. The operator reports a roster of 560 registered caregivers, 350 clients served, and 30 years of group experience.

**Services (from malaysiacaregivers.com):**
- Long-term in-home caregiver (monthly contract)
- Monthly in-home caregiver plan
- Hospital sitter — hourly engagement
- All plans include bathing assistance, medication management, vital-sign monitoring, and light physiotherapy
- Affiliated services: MultiCare Nursing Home (residential) and MultiCare Mobility (wheelchair transport)

**Pricing (published on the operator site):**
- Long Term Plan — RM 4,500/month
- Monthly Plan — RM 5,000/month
- Hospital Sitter — RM 40/hour

Contact the operator on +60 12-650 1805 or info@malaysiacaregivers.com to book a caregiver. As this is a dispatch service rather than a fixed-location home, the right diligence is on the caregivers themselves and the engagement terms rather than on a physical building. There is no facility tour — the assessment moves to the matched caregiver's experience and references.

**What to ask on enquiry:**
- What training and prior experience does the assigned caregiver have for your loved one's specific condition (stroke, dementia, post-surgical, PEG/oxygen)?
- What is the minimum engagement period for the long-term and monthly plans?
- What happens if the caregiver is unwell or unavailable — is there a relief or replacement arrangement?
- Are caregivers locally hired or expatriate workers, and what background and document checks have they passed?
- What is the typical dispatch lead time from booking to first day?
- What hours are covered in the monthly plan, and how are extra hours billed?"""

ROW_FIELDS = {
    'title': TITLE,
    'slug': SLUG,
    'area': 'Petaling Jaya',
    'phone': '+60 12-650 1805',
    'website': 'https://malaysiacaregivers.com',
    'pricing_display': 'From RM 4,500/mo · RM 40/hr hospital sitter',
    'care_types': 'Home Care',
    'last_updated': TODAY,
    'editorial_summary': EDITORIAL,
    'state': 'Selangor',
    'address': 'Petaling Jaya, Selangor, Malaysia',
}

# Details tab rows — appendix detail not in the flat schema
DETAILS_ROOMS = [
    ('Long Term Plan (RM/mo)', '4,500'),
    ('Monthly Plan (RM/mo)', '5,000'),
    ('Hospital Sitter (RM/hour)', '40'),
    ('Pricing source', 'https://malaysiacaregivers.com — chain rates'),
]
DETAILS_INCLUDED = [
    ('Bathing assistance', 'yes'),
    ('Medication management', 'yes'),
    ('Vital-sign monitoring', 'yes'),
    ('Light physiotherapy', 'yes'),
    ('Trained registered caregivers', 'yes (560 on roster)'),
]
DETAILS_SERVICES = [
    ('Service type', 'Home Care / private nursing dispatch'),
    ('Coverage', 'All Malaysia (HQ Petaling Jaya)'),
    ('Affiliated operator', 'MCS Group — also MultiCare Nursing Home + MultiCare Mobility'),
]


def build_row():
    row = [''] * NCOLS
    for k, v in ROW_FIELDS.items():
        row[C[k] - 1] = v
    return row


def main():
    print(f"\n{'APPLY' if APPLY else 'DRY-RUN'} — append Home Care row for {SLUG}\n")
    for k, v in ROW_FIELDS.items():
        shown = v[:60] + ('…' if len(v) > 60 else '') if isinstance(v, str) and len(v) > 60 else v
        print(f'  {k}: {shown!r}')
    print(f'\n  Details rows: {len(DETAILS_ROOMS)} rooms + {len(DETAILS_INCLUDED)} included + {len(DETAILS_SERVICES)} services')

    if not APPLY:
        print('\nDry run only. Re-run with --apply.')
        return

    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    svc = build('sheets', 'v4', credentials=Credentials.from_authorized_user_file(TOKEN_PATH))

    # check slug not already present
    colB = svc.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=f"'{TAB}'!B:B").execute().get('values', [])
    existing = [r[0].strip() for r in colB if r]
    if SLUG in existing:
        print(f'!! slug {SLUG} already exists — abort'); return

    # append the facility row
    svc.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID, range=f"'{TAB}'!A:A",
        valueInputOption='RAW', insertDataOption='INSERT_ROWS',
        body={'values': [build_row()]}).execute()
    print(f'appended row for {SLUG}')

    # append Details rows
    meta = svc.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    details_name = next(s['properties']['title'] for s in meta['sheets']
                        if s['properties']['sheetId'] == DETAILS_TAB_GID)
    details_rows = ([[SLUG, 'rooms', l, v] for l, v in DETAILS_ROOMS]
                    + [[SLUG, 'included', l, v] for l, v in DETAILS_INCLUDED]
                    + [[SLUG, 'services', l, v] for l, v in DETAILS_SERVICES])
    svc.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID, range=f"'{details_name}'!A:D",
        valueInputOption='RAW',
        body={'values': details_rows}).execute()
    print(f'appended {len(details_rows)} Details rows')


if __name__ == '__main__':
    main()
