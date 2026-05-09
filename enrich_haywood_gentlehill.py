"""
Enrich existing Haywood and Gentle Hill rows with researched data.
"""
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import date

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE = 'token_sheets.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
FAC_TAB = 'google-sheets-facilities.csv'
TODAY = str(date.today())

creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
service = build('sheets', 'v4', credentials=creds)
ss = service.spreadsheets()

fac_data = ss.values().get(
    spreadsheetId=SPREADSHEET_ID,
    range=f"'{FAC_TAB}'"
).execute().get('values', [])

headers = fac_data[0]

def col_letter(n):
    s = ''
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s

def h(name):
    return headers.index(name) if name in headers else None

slug_i = h('slug')

enrichments = {
    'haywood-senior-living-medini-johor-bahru': {
        'pricing_display': 'By enquiry (premium)',
        'area': 'Johor Bahru (Medini / Iskandar Puteri)',
        'website': 'https://haywoodliving.co',
        'whatsapp': '+60 11-5587 9788',
        'care_types': 'Independent, Assisted, Long-term, Short-term rehab, Day care, Palliative',
        'care_nursing': 'yes',
        'care_dementia': 'unknown',
        'care_palliative': 'yes',
        'care_rehab': 'yes',
        'care_respite': 'yes',
        'care_assisted': 'yes',
        'rn_24_7': 'yes',
        'doctor_visits': 'yes',
        'medical_physio': 'yes',
        'medical_wound': 'yes',
        'medical_meds': 'yes',
        'wheelchair': 'yes',
        'ownership_type': 'Private (Mintygreen Healthcare Group)',
        'last_updated': TODAY,
        'editorial_summary': "Malaysia's first hotel-concept senior living in the south, embedded inside Ramada by Wyndham Medini. Private 400 sqft studio apartments with balconies, aqua aerobics pool, in-house physio and TCM, and monthly Singapore outings. Three minutes from Gleneagles Hospital Medini. Pricing by enquiry — aimed at JB–Singapore cross-border families.",
    },
    'gentle-hill-elder-care': {
        'area': 'Kulai, Johor',
        'care_types': 'Assisted, Long-term nursing',
        'care_nursing': 'yes',
        'care_assisted': 'yes',
        'halal': 'yes',
        'wheelchair': 'yes',
        'visiting_hours': 'By appointment — 3 time slots daily',
        'ownership_type': 'Private',
        'last_updated': TODAY,
        'editorial_summary': 'Community nursing home in Kulai offering a 2-week refundable trial admission — rare confidence signal. Fall detection technology and VOC-free construction materials show investment in safety and environment. Muslim and vegetarian-friendly. Appointment-only visiting in 3 daily slots. Hospital Kulai is 5 minutes away.',
    },
}

updates = []
for i, row in enumerate(fac_data[1:], start=2):
    slug = row[slug_i] if slug_i < len(row) else ''
    if slug in enrichments:
        for field, value in enrichments[slug].items():
            col_i = h(field)
            if col_i is not None:
                updates.append({
                    'range': f"'{FAC_TAB}'!{col_letter(col_i + 1)}{i}",
                    'values': [[value]]
                })
        print(f'  Queued {len(enrichments[slug])} updates for {slug}')

if updates:
    ss.values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={'valueInputOption': 'RAW', 'data': updates}
    ).execute()
    print(f'Applied {len(updates)} cell updates across Haywood + Gentle Hill.')
else:
    print('No updates applied.')
