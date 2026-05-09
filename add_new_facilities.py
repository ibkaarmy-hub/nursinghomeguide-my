"""
Add EHA Parkview, FCC Family Care Centre, and Jeta Care to the Facilities sheet.
Also enrich Haywood and Gentle Hill with researched data.
"""
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import date

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE = 'token_sheets.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
FAC_TAB = 'google-sheets-facilities.csv'

creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
service = build('sheets', 'v4', credentials=creds)
ss = service.spreadsheets()

fac_data = ss.values().get(
    spreadsheetId=SPREADSHEET_ID,
    range=f"'{FAC_TAB}'"
).execute().get('values', [])

headers = fac_data[0]
today = str(date.today())

def h(name):
    return headers.index(name) if name in headers else None

def make_row(d):
    row = [''] * len(headers)
    for k, v in d.items():
        i = h(k)
        if i is not None:
            row[i] = str(v)
    return row

new_facilities = [
    {
        'title': 'EHA Parkview ElderCare',
        'slug': 'eha-parkview-eldercare-perling',
        'url': '',
        'area': 'Johor Bahru (Perling)',
        'phone': '',
        'website': '',
        'pricing_display': 'From RM 3,200/mo',
        'shared_price': '3200',
        'private_price': '',
        'four_bed_price': '',
        'dorm_price': '',
        'care_types': 'Assisted, Long-term, Respite, Day care, Post-hospitalisation',
        'care_nursing': 'yes',
        'care_dementia': 'unknown',
        'care_palliative': 'unknown',
        'care_rehab': 'yes',
        'care_respite': 'yes',
        'care_assisted': 'yes',
        'rn_24_7': 'yes',
        'doctor_visits': 'unknown',
        'medical_physio': 'yes',
        'medical_ot': 'yes',
        'medical_wound': 'yes',
        'medical_peg': 'unknown',
        'medical_dementia_unit': 'unknown',
        'medical_dialysis': 'unknown',
        'medical_oxygen': 'unknown',
        'medical_meds': 'yes',
        'rating': '4.9',
        'review_count': '85',
        'wheelchair': 'yes',
        'halal': 'unknown',
        'ownership_type': 'Private',
        'last_updated': today,
        'editorial_summary': 'One of the few nursing homes in Malaysia that publishes pricing openly. RM 3,200/mo all-in covers 4 meals and a strong allied health team — PT, OT, and Speech Therapy on-site. High-dependency clinical capabilities including NGT, catheter, stoma, and suction. Rated 4.9/5 from 85 Google reviews.',
    },
    {
        'title': 'FCC Family Care Centre',
        'slug': 'fcc-family-care-centre',
        'url': '',
        'area': 'Johor Bahru',
        'phone': '',
        'website': '',
        'pricing_display': 'From RM 3,500/mo',
        'shared_price': '3500',
        'private_price': '4300',
        'four_bed_price': '',
        'dorm_price': '',
        'care_types': 'Assisted, Dementia/Memory care, Long-term, Respite, Day care, Independent living',
        'care_nursing': 'yes',
        'care_dementia': 'yes',
        'care_palliative': 'unknown',
        'care_rehab': 'unknown',
        'care_respite': 'yes',
        'care_assisted': 'yes',
        'rn_24_7': 'yes',
        'doctor_visits': 'unknown',
        'medical_physio': 'unknown',
        'medical_ot': 'unknown',
        'medical_wound': 'unknown',
        'medical_peg': 'unknown',
        'medical_dementia_unit': 'yes',
        'medical_dialysis': 'unknown',
        'medical_oxygen': 'unknown',
        'medical_meds': 'yes',
        'wheelchair': 'yes',
        'halal': 'unknown',
        'ownership_type': 'Private',
        'last_updated': today,
        'editorial_summary': "Malaysia's 1st Integrated Senior Living and Wellness Village — a campus model with a dedicated MemoryCare Home for dementia, SmartPeep AI monitoring, organic farm, and resident animals. Pricing from RM 3,500/mo; 3-month deposit for foreign residents. Strong dementia care differentiator.",
    },
    {
        'title': 'Jeta Care',
        'slug': 'jeta-care',
        'url': '',
        'area': 'Johor Bahru',
        'phone': '',
        'website': '',
        'pricing_display': 'RM 3,001–6,000/mo (2020 — confirm)',
        'shared_price': '3001',
        'private_price': '6000',
        'four_bed_price': '',
        'dorm_price': '',
        'care_types': 'Assisted, Long-term, High-dependency, Palliative, Physiotherapy/Rehab',
        'care_nursing': 'yes',
        'care_dementia': 'unknown',
        'care_palliative': 'yes',
        'care_rehab': 'yes',
        'care_respite': 'unknown',
        'care_assisted': 'yes',
        'rn_24_7': 'yes',
        'doctor_visits': 'yes',
        'medical_physio': 'yes',
        'medical_ot': 'unknown',
        'medical_wound': 'yes',
        'medical_peg': 'yes',
        'medical_dementia_unit': 'unknown',
        'medical_dialysis': 'unknown',
        'medical_oxygen': 'unknown',
        'medical_meds': 'yes',
        'total_beds': '62',
        'wheelchair': 'yes',
        'halal': 'yes',
        'religion': 'Muslim-friendly (surau on-site)',
        'ownership_type': 'Private',
        'licence_number': 'MOH CKAPS (verify)',
        'last_updated': today,
        'editorial_summary': "Malaysia's first Australian-concept aged care facility, with MOH CKAPS licensing (higher than standard JKM) and a named medical director, Dr. Goh Yi Xiong. Clinical capabilities are exceptional: PEG, colostomy, tracheostomy, and catheter care. 62 beds, rooftop garden, halal café, and surau on-site.",
    },
]

# Build rows and append
new_rows = [make_row(f) for f in new_facilities]
next_row = len(fac_data) + 1

result = ss.values().append(
    spreadsheetId=SPREADSHEET_ID,
    range=f"'{FAC_TAB}'!A{next_row}",
    valueInputOption='RAW',
    insertDataOption='INSERT_ROWS',
    body={'values': new_rows}
).execute()

print(f'Appended {len(new_rows)} new facilities:')
for f in new_facilities:
    print(f"  - {f['title']} ({f['slug']})")
print(f'Sheet now has {len(fac_data) - 1 + len(new_rows)} facilities.')
