"""Expand 2 short Selangor stubs into full editorials."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE = 'token_sheets.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
TAB = 'google-sheets-facilities.csv'

FIXES = [
    (409, 'care-concierge-malaysia',
     "Care Concierge Malaysia is a premium home-care provider headquartered in Petaling Jaya, with national coverage across KL, Selangor, Johor, Penang, Ipoh, and Melaka. The service is run by registered nurses and social workers and is structured around live-in care rather than residential beds — care teams are deployed to the client's home for 24-hour supervision. The contact line for enquiries is +60 3-7660 1803, and the operating site is mycareconcierge.com.\n\nThe service catalogue covers live-in 24-hour personal care, post-stroke rehabilitation packages, palliative home care, and hospital-to-home transition programmes. Pricing for live-in stroke care starts from RM 10,800 per month, which positions Care Concierge at the higher end of the Malaysian home-care market — consistent with the registered-nurse-led staffing and the multi-region operating footprint. The packages typically include nurse oversight, caregiver day-to-day support, and care-plan reviews.\n\nFamilies considering Care Concierge should expect a more clinical and structured arrangement than typical caregiver-only services, which is a fit for medically complex elders post-discharge. Useful questions to raise on a call: the LJM (Lembaga Jururawat Malaysia) registration of the assigned nurses, the supervising-nurse review cadence, the back-up arrangement when an assigned caregiver is on leave, the protocol for medical escalations, and what is included versus charged separately (medical equipment, transport, specialist consults). A trial week is sometimes available for live-in arrangements — worth asking about during the first call."),

    (411, 'pillar-care',
     "Pillar Care is a doctor-managed home-care service based in Petaling Jaya, operating across the Klang Valley and Johor under the website pillarcare.com.my. Rather than providing residential beds, Pillar Care assembles structured home-based care teams — caregivers, registered nurses, physiotherapists, and occupational therapists — and deploys them to the client's home under a supervising physician's care plan. The service positions itself between general home-help agencies and full clinical home-nursing providers.\n\nPackage pricing starts from RM 4,600 for a 20-day arrangement, which works out to approximately RM 230 per day for the basic structured package. The multi-disciplinary model means a single client can have caregivers, nursing visits, physiotherapy sessions, and OT input coordinated under one plan, which is useful for post-stroke recovery, post-surgical rehabilitation, and ongoing dementia management at home. The KL Valley + Johor coverage area means deployment is feasible across most of the central peninsula.\n\nFamilies considering Pillar Care should expect to engage with a structured care-plan process rather than a transactional caregiver booking. Useful questions on a first call: the qualifications of the supervising physician, the LJM registration of the nurses on the roster, how the multi-disciplinary plan is reviewed and adjusted, what's included in the RM 4,600 package versus charged extra, the back-up arrangement when staff are on leave, and the typical length of an initial assessment before deployment. A clear written care plan and pricing breakdown is sensible before committing."),
]

def main():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    sheet = build('sheets', 'v4', credentials=creds).spreadsheets()
    data = []
    for row, slug, ed in FIXES:
        data.append({'range': f"'{TAB}'!AY{row}", 'values': [[ed]]})
        print(f'  AY{row}  {slug:30s}  ({len(ed.split())}w)')
    body = {'valueInputOption': 'RAW', 'data': data}
    resp = sheet.values().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
    print(f"\nUpdated {resp.get('totalUpdatedCells')} cells.")

if __name__ == '__main__':
    main()
