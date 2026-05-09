"""Fix 4 editorials with critical/undermining tone. Upload corrected versions."""
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE = 'token_sheets.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
TAB = 'google-sheets-facilities.csv'

# (row_idx, slug, new_editorial)
FIXES = [
    (
        283, 'pusat-jagaan-dan-rawatan-orang-tua-al-ikhlas',
        "Pusat Jagaan dan Rawatan Orang Tua Al-Ikhlas is set inside a converted endowed mosque (masjid lama diwakafkan) at Lot 3530, Jalan Batu 18, Kampung Pulau Meranti, Puchong — a kampung enclave tucked between Puchong's commercial sprawl and the Putrajaya wetlands. The centre was founded in 1999 by Muji binti Hj Sulaiman, a former Chief Nurse at Hospital Serdang who brought home elderly patients discharged without family to receive them and has been running the home ever since. That clinical background — two decades of geriatric ward nursing before founding the home — is the most substantive credential in the public record. The facility currently cares for around 50 residents and employs approximately 12 staff.\n\nThe centre is Islamic in character, accepting donations of zakat and fitting its care philosophy within an Islamic welfare framework, though available sources do not state that admission is exclusively restricted to Muslims. Care provision includes daily personal assistance (bathing, dressing, feeding), basic medical monitoring, and social and recreational activities with a physical, mental, and spiritual dimension. Reviewer feedback on directory sites praises effective communication between staff and families and a holistic care approach.\n\nThe converted mosque setting is unconventional and worth seeing in person — for some families, the quiet kampung environment and community character will feel exactly right; others may want a more medically equipped facility. Pricing, bed availability, and the JKM licence number are best confirmed directly with the home. Given the 50-resident scale and 12-person staff, ask about the nursing cover arrangement — specifically whether trained nurses or caregivers manage clinical tasks overnight, and what the protocol is for medical emergencies given the rural access point."
    ),
    (
        274, 'sunstar-golden-care-centre',
        "Sunstar Golden Care Centre is listed as a nursing home in Bandar Sunway, one of Selangor's most densely served eldercare corridors given its proximity to Sunway Medical Centre and a large residential population. The facility holds a 5-star Google rating across 24 reviews — a strong signal of resident and family satisfaction — and operates from a Bandar Sunway address. Beyond the Google Maps listing, the home does not maintain a published website or active social media page, so most service detail is best gathered on a call or visit.\n\nBandar Sunway's eldercare landscape ranges from premium retirement living products (Sunway Sanctuary is the most visible) down to smaller community-scale homes. Sunstar appears to sit toward the smaller, neighbourhood end of that spectrum based on its current footprint. The phone number (+60 14-660 1127) and its Google presence confirm it is operational, and the rating suggests a positively regarded environment.\n\nWhen calling or visiting Sunstar Golden Care Centre, useful questions include the JKM registration and licence status, the range of dependency levels accepted (low, medium, high, bed-bound), nurse-to-resident ratios, visiting doctor arrangements, and current pricing. Bandar Sunway's hospital proximity is a real asset for high-acuity transfers — ask about the protocol for medical escalation and which hospital they typically liaise with."
    ),
    (
        356, 'pusat-jagaan-rumah-warga-tua-cahaya',
        "Pusat Jagaan Rumah Warga Tua Cahaya is a registered care home situated at No. 2, Jalan Merpati 8, Puchong Jaya, 47100 Puchong, Selangor. Directory sources indicate it has been in operation since 2010 and is classified as an associations-type care provider rather than a corporate nursing home chain. The Google listing attributes a 4.5-star rating from 15 reviews and lists a total bed count of 76, which would make it a mid-sized facility relative to the Puchong neighbourhood home market. The listed phone number is 03-8071 0232.\n\nThe facility is described in public directories as offering day-care on a daily basis and full residential care on a monthly arrangement. With 76 beds on record, the home likely accommodates a mix of dependency levels. Specific nursing capabilities, medical visit frequency, and clinical services are best confirmed directly with the home. The 'associations' classification suggests the home may carry a welfare or community-care mandate alongside its residential operation.\n\nFamilies considering this home should verify the 76-bed figure and current occupancy directly, and ask what proportion of residents are ambulant versus bed-bound. An in-person visit is the most reliable way to assess staffing ratios, hygiene standards, and the quality of the outdoor or communal areas. Useful questions to bring: whether trained nurses are on duty overnight, what the visiting-doctor frequency is, and the current JKM (Social Welfare Department) licence number."
    ),
    (
        191, 'gam-yam-senior-home-in-ampang-kuala-lumpur-malaysia',
        "Gam Yam Senior Home operates from 327, Jalan 16, Kampung Baru Ampang — a long-established Chinese residential neighbourhood in Ampang that sits on the Selangor-KL boundary. The facility's Google listing categorises it as a retirement home, assisted living facility, and home health care service, suggesting it spans both residential and outreach care. A directory listing places physiotherapy and residential care for the elderly and disabled among its stated activities. The address is also associated with an entity listed as AIM Healthcare at the same premises — worth clarifying with the home which licence and which operator currently runs the facility.\n\nThe Google rating sits at 3.3 from 11 reviews, which is a smaller and more mixed reviewer base than some neighbouring Ampang facilities. No website or Facebook presence was found during research, so most service detail is best gathered on a call. The Kampung Baru Ampang setting is a densely built residential area with limited outdoor space, though Hospital Ampang is within a few kilometres for medical escalation.\n\nFamilies considering this home will want to ask for the Care Centre Act licence number, clarify the relationship with AIM Healthcare at the same address, confirm which medical conditions are managed in-house versus referred out, and ask the home for current family references. A visit during a mealtime or activity period will give a clearer picture of day-to-day conditions than a formal tour, and is the most reliable way to assess fit."
    ),
]

def main():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    sheet = build('sheets', 'v4', credentials=creds).spreadsheets()
    data = []
    for row, slug, ed in FIXES:
        data.append({'range': f"'{TAB}'!AY{row}", 'values': [[ed]]})
        try:
            print(f'  AY{row}  {slug[:55]:55s}  ({len(ed.split())}w)')
        except UnicodeEncodeError:
            print(f'  AY{row}  <unicode>  ({len(ed.split())}w)')

    body = {'valueInputOption': 'RAW', 'data': data}
    resp = sheet.values().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
    print(f"\nUpdated {resp.get('totalUpdatedCells')} cells.")

if __name__ == '__main__':
    main()
