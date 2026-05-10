"""
update_perak_capabilities.py
Update care flags, medical capabilities, pricing, and Details tab services
for 10 Perak facilities based on data extracted from their own websites.
"""

import csv, io, sys, time, urllib.request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout.reconfigure(encoding='utf-8')

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_PATH     = r'C:\Users\ibkaa\nursinghomeguide-my\Nursing Home Guide Malaysia\token_sheets.json'
TAB            = 'google-sheets-facilities.csv'
TODAY          = '2026-05-10'

CSV_URL = (
    'https://docs.google.com/spreadsheets/d/e/'
    '2PACX-1vQ4_BgHIjnlgmITzjyUuGDpgpNzPL7MfjOY2069i0PtbVbXSxIAJk1tmBejwNo8aBBeLuRi62szF2sh'
    '/pub?gid=292378871&single=true&output=csv'
)

def col_letter(idx):
    """Convert 1-based column index to spreadsheet letter (1=A, 27=AA, etc.)"""
    result = ''
    while idx > 0:
        idx, r = divmod(idx - 1, 26)
        result = chr(65 + r) + result
    return result


# Per-facility data extracted from their websites.
# Keys match column names from the sheet schema.
FACILITY_UPDATES = {

    'my-place-convalescent-home-care-centre': {
        'tab': {
            'care_types':   'Nursing Home',
            'care_nursing': 'yes',
            'care_rehab':   'yes',
            'care_assisted':'yes',
            'rn_24_7':      'yes',
            'medical_physio': 'yes',
            'last_updated': TODAY,
        },
        'details': [
            # services
            ('services', 'Post-Surgery Recovery',   'Garden Terrace setting; daily support and recovery'),
            ('services', 'Assisted Living',          'Garden Tower; modern senior residence'),
            ('services', 'Physiotherapy',            'Available (additional charge)'),
            ('services', 'Medication Management',    'Available (additional charge)'),
            ('services', 'Morning Exercise',         'Daily programme'),
            ('services', 'Handcraft Sessions',       'Social activity'),
            ('services', 'Gardening Activities',     'Therapeutic gardening'),
            ('services', 'Hospital Transport',       'Available (additional charge)'),
            # rooms
            ('rooms', 'Single Room',      'Available'),
            ('rooms', 'Double-Bedded',    'Available'),
            ('rooms', 'Triple-Bedded',    'Available'),
            ('rooms', 'Four-Bed & Above', 'Available'),
            ('rooms', 'Pricing source',   'Not published — contact +6017-449 6008 for quote'),
            # included
            ('included', 'Meals',             'Nutritious, tailored to resident'),
            ('included', 'Daily Care Support','Personal hygiene and assistance'),
            ('included', 'Exercise Programme','Daily morning exercise'),
            # extras
            ('extras', 'Daily Care Supplies', 'Billed separately'),
            ('extras', 'Physiotherapy',        'Billed separately'),
            ('extras', 'Medication Management','Billed separately'),
            ('extras', 'Hospital Transport',   'Billed separately'),
        ],
    },

    'd-palace-care-centre': {
        'tab': {
            'care_types':     'Nursing Home',
            'care_nursing':   'yes',
            'care_dementia':  'yes',
            'care_palliative':'yes',
            'care_rehab':     'yes',
            'care_assisted':  'yes',
            'rn_24_7':        'yes',
            'medical_physio': 'yes',
            'medical_wound':  'yes',
            'medical_peg':    'yes',
            'medical_oxygen': 'yes',
            'last_updated':   TODAY,
        },
        'details': [
            ('services', '24-Hour Nursing Care',  'Fully qualified registered staff nurses'),
            ('services', 'Palliative Care',        'Cancer and non-cancer; terminal care; free NGT/catheter for palliative referrals from Hospital 1R'),
            ('services', 'Dementia Care',          'Specialist support'),
            ('services', "Parkinson's Disease",    'Management and care'),
            ('services', 'Stroke Care',            'Neurological care and rehabilitation'),
            ('services', 'Post-Surgery Care',      'yes'),
            ('services', 'Coma Nursing',           'yes'),
            ('services', 'Assisted Living',        'Indoor activities'),
            ('services', 'Day Care',               'yes'),
            ('services', 'Physiotherapy',          'yes'),
            # clinical
            ('clinical', 'Wound Management',       'Diabetic, bedsore, post-surgery wounds'),
            ('clinical', 'Ryles Tube (NGT)',        'Insertion, changing, and tube feeding'),
            ('clinical', 'Urinary Catheter',       'Insertion and changing'),
            ('clinical', 'Tracheostomy Care',      'Suction management'),
            ('clinical', 'Colostomy Care',         'yes'),
            ('clinical', 'Oxygen Concentrator',    'Available on-site'),
            # policies
            ('policies', 'Free NGT & Catheter',    'Free for palliative referrals from Hospital 1R with documentation'),
            ('policies', 'Teaching Centre',        'Accepts clinical practice students from local universities'),
        ],
    },

    'dr-thomas-care-centre': {
        'tab': {
            'care_types':     'Nursing Home',
            'care_nursing':   'yes',
            'care_palliative':'yes',
            'care_rehab':     'yes',
            'care_assisted':  'yes',
            'rn_24_7':        'yes',
            'medical_physio': 'yes',
            'medical_wound':  'yes',
            'last_updated':   TODAY,
        },
        'details': [
            ('services', 'Wound Care & Management',   'Major and minor wounds; latest technology'),
            ('services', 'Stroke Rehabilitation',      'Therapy and recovery programme'),
            ('services', 'Palliative Care',            'Early identification and comfort care'),
            ('services', 'Physiotherapy',              'Tailored individual treatment plans'),
            ('services', 'Post-Hospitalisation Care',  'Professional recovery environment'),
            ('services', 'Day Care',                   'Short-term stays with full care'),
            ('services', 'Medical Procedures',         'Surgical or physical rehabilitation care'),
            ('services', 'Specialised Care',           'Higher dependency nursing'),
            ('services', 'Elder Care',                 'Round-the-clock inclusive senior care'),
        ],
    },

    'ig-care-centre': {
        'tab': {
            'care_types':    'Nursing Home',
            'pricing_display': 'RM 1,500 – RM 3,000 per month',
            'care_nursing':  'yes',
            'care_dementia': 'yes',
            'care_rehab':    'yes',
            'care_respite':  'yes',
            'care_assisted': 'yes',
            'rn_24_7':       'yes',
            'doctor_visits': 'yes',
            'medical_physio':'yes',
            'medical_wound': 'yes',
            'medical_peg':   'yes',
            'last_updated':  TODAY,
        },
        'details': [
            # services
            ('services', 'Long Term Stay',           '24-hour residential nursing care'),
            ('services', 'Respite Care',              '1–3 months; post-operative recovery or caregiver relief'),
            ('services', 'Day Care',                  'Daytime supervision with rehabilitation programme'),
            ('services', 'Caregiver Training',        'Family caregiver skills programme'),
            ('services', 'Stroke Recovery',           'Active rehabilitation'),
            ('services', 'Fracture Rehabilitation',   'Active rehabilitation'),
            ("services", "Parkinson's Disease Care",  'Specialist support'),
            ('services', 'Dementia Care',             'Structured activity programme'),
            ('services', 'Post-operative Rehab',      'Active rehabilitation'),
            ('services', 'Spinal Cord Injury Care',   'Specialist support'),
            # rooms (pricing)
            ('rooms', 'Pricing range',     'RM 1,500 – RM 3,000 per month'),
            ('rooms', 'Payment deadline',  'First 7 days of each month'),
            ('rooms', 'Payment methods',   'Cash, cheque, or online transfer (preferred)'),
            ('rooms', 'Pricing source',    'https://igcare.com.my/fees/ — published rates'),
            # included
            ('included', 'Doctor Consultation',  'Regular; included in monthly fee'),
            ('included', '24-Hour Nursing',       'By certified nurses'),
            ('included', 'Physiotherapy',         'By qualified therapists'),
            ('included', 'Meals',                 '3 meals + 2 snacks daily'),
            ('included', 'Accommodation',         'yes'),
            # extras
            ('extras', 'Ripple Mattress',          'Billed separately'),
            ('extras', 'Oxygen Concentrator',      'Billed separately'),
            ('extras', 'Suction Equipment',        'Billed separately'),
            ('extras', 'Complex/Sterile Dressing', 'Billed separately'),
            ('extras', 'Blood Tests',              'Billed separately'),
            ('extras', 'Medication',               'Billed separately'),
            ('extras', 'Diapers & Wet Wipes',      'Billed separately'),
            ('extras', 'Tube Change',              'Billed separately'),
            ('extras', 'Other Medical Procedures', 'Billed separately'),
            # clinical
            ('clinical', 'Wound Care',            'yes'),
            ('clinical', 'Tube Feeding',          'yes'),
            ('clinical', 'Urinary Catheter Care', 'yes'),
            ('clinical', 'Pressure Sore Prevention','yes'),
        ],
    },

    'pusat-jagaan-mesra-intan': {
        'tab': {
            'care_types':    'Nursing Home',
            'care_nursing':  'yes',
            'care_dementia': 'yes',
            'care_rehab':    'yes',
            'care_assisted': 'yes',
            'rn_24_7':       'yes',
            'medical_physio':'yes',
            'medical_ot':    'yes',
            'medical_wound': 'yes',
            'medical_peg':   'yes',
            'last_updated':  TODAY,
        },
        'details': [
            ('services', 'Post-Stroke Care',       'Specialist recovery support'),
            ('services', 'Post-Surgery Care',       'yes'),
            ('services', 'Day Care',                'Personalized daytime care'),
            ('services', 'Dementia Care',           'yes'),
            ('services', 'Mobility Assistance',     'Bedridden and limited mobility residents'),
            ('services', 'Rehabilitative Therapy',  'Physiotherapy and occupational therapy'),
            ('services', '24-Hour Skilled Nursing', 'Professional registered nurses'),
            # clinical
            ('clinical', 'Ryle Tube (NGT)',          'Insertion and feeding management'),
            ('clinical', 'PEG Feeding',              'yes'),
            ('clinical', 'Urinary Catheter Care',    'Insertion and changing'),
            ('clinical', 'Wound & Pressure Sore',    'Dressing and management'),
            ('clinical', 'Physiotherapy',            'yes'),
            ('clinical', 'Occupational Therapy',     'yes'),
        ],
    },

    'pusat-jagaan-qaseh-murni': {
        'tab': {
            'care_types':    'Nursing Home',
            'care_nursing':  'yes',
            'rn_24_7':       'yes',
            'doctor_visits': 'yes',
            'last_updated':  TODAY,
        },
        'details': [
            ('services', '24-Hour Nursing Care',   'Licensed nurses'),
            ('services', 'Post-Treatment Care',    'Rehabilitation and recovery for elderly'),
            ('services', 'Flexible Stays',         'Hourly, daily, weekly, monthly, or permanent'),
            ('services', 'Specialist Doctor',      'On-site specialist doctor oversight'),
            ('services', 'Sahabat Senja Programme','Anak Angkat Warga Emas community adoption programme'),
        ],
    },

    'pusat-jagaan-rumah-orang-orang-tua-pkk-simee': {
        'tab': {
            'care_types':   'Nursing Home',
            'care_nursing': 'yes',
            'last_updated': TODAY,
        },
        'details': [
            ('services', 'Residential Care', 'Daily care, meals, and essential provisions'),
            ('services', 'Recreation',        'Activities and social programmes'),
            ('services', 'CSR & Group Visits','Birthday celebrations and corporate visits welcome'),
            ('services', 'Volunteer Programme','Individual and group volunteers welcome'),
            ('policies', 'Operating Hours',   'Monday – Sunday including public holidays, 8:30am – 5:30pm'),
            ('policies', 'Donation Recognition','RM 5,000+ on Donor Wall; RM 100,000+ on Honorary Donor Board'),
        ],
    },

    'pusat-jagaan-yayasan-teratai': {
        'tab': {
            'care_types':   'Nursing Home',
            'care_nursing': 'yes',
            'last_updated': TODAY,
        },
        'details': [
            ('services', 'Aged Care Home',   'Residential care for senior citizens'),
            ('services', 'Education Care',   'Education support programme'),
            ('policies', 'Founded',          '14 April 2001 — charitable limited liability company'),
            ('policies', 'Address',          '16 Jalan Raja Dihilir, 30350 Ipoh, Perak'),
        ],
    },

    'starshine-care-centre': {
        'tab': {
            'care_types':    'Nursing Home',
            'care_nursing':  'yes',
            'care_rehab':    'yes',
            'care_assisted': 'yes',
            'rn_24_7':       'yes',
            'doctor_visits': 'yes',
            'medical_physio':'yes',
            'last_updated':  TODAY,
        },
        'details': [
            ('services', '24-Hour Nursing',        'By qualified nurses'),
            ('services', 'Doctor Visits',          'Regular visiting doctor'),
            ('services', 'Physiotherapy',          'yes'),
            ('services', 'Day Care',               'yes'),
            ('services', 'Assisted Living',        'yes'),
            ('services', 'Rehabilitation',         'yes'),
            ('services', 'Post-Hospitalisation',   'yes'),
            ('services', 'Chronic Care',           'Long-term chronic condition management'),
            ('services', 'Retirement Care',        'yes'),
            ('services', 'Medical Nursing Care',   'yes'),
            # included
            ('included', 'Air-Conditioned Rooms',  'Fully furnished'),
            ('included', '24-Hour CCTV',           'Full facility monitoring'),
            ('included', 'Nurse Calling System',   'yes'),
            ('included', 'WiFi',                   'yes'),
            ('included', 'Astro TV',               'yes'),
            ('included', 'Meals',                  'With dietary consideration'),
            ('included', 'Personal Hygiene',       'yes'),
            ('included', 'Activities',             'Physical and mental health programming'),
            ('included', 'Garden Access',          'yes'),
        ],
    },

    'the-salvation-army-perak-home-for-the-aged-care-ce': {
        'tab': {
            'care_types':   'Nursing Home',
            'care_nursing': 'yes',
            'last_updated': TODAY,
        },
        'details': [
            ('services', 'Residential Aged Care', 'Safe, peaceful environment with meals and daily support'),
            ('services', 'Compassionate Care',    'Christian charitable care model'),
            ('policies', 'Operator',              'The Salvation Army Malaysia — 20+ facilities nationwide'),
        ],
    },
}


def fetch_csv():
    print('Fetching published CSV...')
    with urllib.request.urlopen(CSV_URL) as r:
        return r.read().decode('utf-8')


def main():
    data = fetch_csv()
    reader = csv.DictReader(io.StringIO(data))
    headers = list(reader.fieldnames)

    # Build column letter map
    col = {name: col_letter(i + 1) for i, name in enumerate(headers)}

    # Find all rows for target slugs
    slug_rows = {}
    for i, row in enumerate(reader, start=2):
        slug = row.get('slug', '').strip()
        if slug in FACILITY_UPDATES:
            slug_rows.setdefault(slug, []).append(i)

    print(f'Found {len(slug_rows)} slugs across {sum(len(v) for v in slug_rows.values())} rows\n')

    creds = Credentials.from_authorized_user_file(
        TOKEN_PATH, ['https://www.googleapis.com/auth/spreadsheets']
    )
    svc = build('sheets', 'v4', credentials=creds)

    # --- Read existing Details rows to avoid duplicates ---
    existing_details = svc.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="'Details'!A:D"
    ).execute().get('values', [])
    existing_keys = {(r[0], r[1], r[2]) for r in existing_details if len(r) >= 3}
    print(f'Existing Details rows: {len(existing_details)}')

    total_tab_updates = 0
    new_details_rows = []

    for slug, row_list in sorted(slug_rows.items()):
        update = FACILITY_UPDATES[slug]
        tab_fields = update.get('tab', {})
        details = update.get('details', [])

        print(f'\n{slug} ({len(row_list)} row(s)):')

        # Build batchUpdate data for Facilities tab
        batch_data = []
        for row_n in row_list:
            for field, value in tab_fields.items():
                if field not in col:
                    print(f'  WARNING: column {field!r} not in headers, skipping')
                    continue
                range_str = f"'{TAB}'!{col[field]}{row_n}"
                batch_data.append({'range': range_str, 'values': [[value]]})

        if batch_data:
            # Split into chunks of 50 to avoid quota issues
            for chunk_start in range(0, len(batch_data), 50):
                chunk = batch_data[chunk_start:chunk_start + 50]
                try:
                    svc.spreadsheets().values().batchUpdate(
                        spreadsheetId=SPREADSHEET_ID,
                        body={'valueInputOption': 'RAW', 'data': chunk}
                    ).execute()
                    total_tab_updates += len(chunk)
                    print(f'  Facilities tab: {len(chunk)} cells updated for rows {row_list}')
                except Exception as e:
                    print(f'  ERROR updating Facilities tab: {e}')
                time.sleep(0.5)

        # Collect new Details rows (use first row's slug — same for all)
        for section, label, value in details:
            key = (slug, section, label)
            if key not in existing_keys:
                new_details_rows.append([slug, section, label, value])
                existing_keys.add(key)  # prevent duplicates within this run
            else:
                pass  # already exists, skip

        detail_count = sum(1 for s, l, v in details if (slug, s, l) not in existing_keys or True)
        new_count = sum(1 for s, l, v in details if [slug, s, l, v] in new_details_rows)
        print(f'  Details: {new_count} new rows queued')

    # --- Batch append Details rows ---
    if new_details_rows:
        print(f'\nAppending {len(new_details_rows)} Details rows...')
        svc.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range="'Details'!A:D",
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body={'values': new_details_rows}
        ).execute()
        print('Details append OK')
    else:
        print('\nNo new Details rows to append')

    print(f'\n{"="*60}')
    print(f'CAPABILITIES UPDATE COMPLETE')
    print(f'  Facilities tab cells updated: {total_tab_updates}')
    print(f'  Details rows appended:        {len(new_details_rows)}')


if __name__ == '__main__':
    main()
