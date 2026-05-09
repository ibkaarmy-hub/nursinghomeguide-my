"""
Update editorial_summary for all 5 new facilities with 3-paragraph rich descriptions.
"""
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

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

def col_letter(n):
    s = ''
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s

def h(name):
    return headers.index(name) if name in headers else None

slug_i = h('slug')
editorial_i = h('editorial_summary')

editorials = {
    'eha-parkview-eldercare-perling': (
        "EHA Parkview ElderCare is part of the EHA ElderCare Group, one of Johor's most established eldercare operators with over 14 years in the industry. The Perling branch is a full-service nursing home accepting residents across the care spectrum — from semi-ambulant seniors needing light support to bed-bound residents requiring 24/7 skilled nursing, post-hospitalisation rehabilitation, and complex clinical management including NGT tube feeding, catheter care, stoma care, and suctioning."

        "\n\nWhat sets EHA Parkview apart in the Malaysian market is its pricing transparency. Monthly rates start from RM 3,200 all-inclusive — covering accommodation, four daily meals, nursing care around the clock, and a notable allied health team: in-house physiotherapy, occupational therapy, and speech therapy. These services are typically charged separately at most nursing homes. For families managing a post-stroke or post-surgery discharge, this breadth of clinical support at a published, predictable rate is rare and genuinely valuable."

        "\n\nEHA Parkview holds a 4.9-star rating from 85 Google reviews — one of the strongest quality signals of any nursing home in Johor Bahru. Families consistently highlight the professionalism of the management and the attentiveness of the care team. The facility also offers respite care from RM 120/day and day care from RM 1,500/month, making it accessible for families exploring transitional care before committing to full residential placement."
    ),
    'fcc-family-care-centre': (
        "FCC Family Care Centre bills itself as Malaysia's first Integrated Senior Living and Wellness Village — and the description is not marketing overstatement. The campus in Ulu Tiram, Johor Bahru is built around a philosophy of natural living: an organic farm where residents plant and harvest, free-roaming animals throughout the grounds, healing gardens, and open gazebo spaces designed for community gathering rather than passive observation. This is a fundamentally different model from the clinical-ward nursing home, and it shows in the profile of residents who thrive here."

        "\n\nFor families navigating dementia, FCC operates a dedicated MemoryCare Home — a separate, purpose-designed unit with the structured routines, sensory-safe environments, and specialist staffing that memory care requires. The facility is also one of the first in Malaysia to deploy SmartPeep AI monitoring: a system that uses computer vision to detect falls, irregular movement, and distress without invasive physical checks, alerting staff in real time. For families who cannot visit frequently, this technology provides meaningful reassurance."

        "\n\nPricing tiers run from approximately RM 3,500 to RM 4,300 per month depending on room type — note that these figures are from third-party sources and should be confirmed directly with FCC, as rates may have been updated. Foreign residents (including those relocating from Singapore) are typically required to pay a three-month deposit. The MemoryCare Home pricing may differ from general nursing care rates; ask specifically when enquiring."
    ),
    'jeta-care': (
        "Jeta Care in Kulai, Johor holds the distinction of being Malaysia's first Australian-concept residential aged care facility — a term with real regulatory meaning. The facility was designed in partnership with Australian aged care consultants and operates under MOH CKAPS licensing (Ministry of Health's Quality Assurance Programme for Private Healthcare Facilities), a tier of oversight that goes significantly beyond the standard JKM registration. Its current CKAPS licence is valid through February 2028. A named medical director, Dr. Goh Yi Xiong, provides clinical governance accountability that is standard in Australian aged care but rare in Malaysia."

        "\n\nThe clinical capabilities at Jeta Care are among the most advanced in southern Malaysia. The team is equipped for PEG tube management, colostomy and ileostomy care, tracheostomy management, catheter care, and complex wound management — making the facility one of very few in the region able to accept complex hospital discharges that most nursing homes would turn away. All 62 beds are served by a 24/7 nurse call system throughout the three-storey building. Registered Nurses with Australian training form part of the core care staff."

        "\n\nBeyond clinical capability, Jeta Care invests in quality of life in ways that matter: a rooftop garden gives residents outdoor access and a sense of space; an on-site halal cafe and surau (prayer room) make it genuinely welcoming for Muslim residents and families; a dedicated physiotherapy and rehabilitation room supports recovery. Pricing data from 2020 placed rates between RM 3,001 and RM 6,000 per month depending on care level — these figures are likely outdated and should be confirmed directly with the facility."
    ),
    'gentle-hill-elder-care': (
        "Gentle Hill Elder Care is a community nursing home in Kulai, Johor, distinguished from most facilities by two policies that speak directly to what families worry about most: a 2-week fully refundable trial admission, and structured appointment-only visiting in three daily time slots. The trial period is extraordinary — very few nursing homes in Malaysia offer it — and signals genuine confidence in their standard of care. Families can move a parent in, observe the experience firsthand, and receive a full refund if it is not the right fit."

        "\n\nThe facility takes quality-of-life infrastructure seriously. Fall detection technology is deployed throughout, reducing response times and injury risk for residents. Construction and renovation used VOC-free materials, minimising chemical off-gassing in a population that often has respiratory sensitivities. The kitchen serves both halal and vegetarian menus, making it one of the more inclusively catered nursing homes in Kulai. Hospital Kulai is approximately five minutes away by car, providing solid emergency medical backup."

        "\n\nGentle Hill is best suited for residents with low-to-moderate care needs — assisted daily living, companionship, supervised mobility — rather than high-dependency medical cases. Rooms are available in 2-bed and 6-bed configurations; no private singles have been confirmed. Pricing is not published online and requires direct enquiry. Families with a parent needing tracheostomy, PEG tube, or intensive dementia management should confirm clinical capabilities with the facility before proceeding."
    ),
    'haywood-senior-living-medini-johor-bahru': (
        "Haywood Senior Living Medini is the first hotel-concept senior living facility in southern Malaysia, embedded inside the Ramada by Wyndham Medini hotel in Iskandar Puteri. Residents live in remodelled 400 sqft hotel studio apartments — complete with private balconies, CCTV, in-room call bells, and elderly-adapted bathrooms with grab bars and wall-mounted bath chairs — while receiving 24/7 caregiver support, on-site nursing, and standby doctors. The model is built for dignity of space: no shared wards, no institutional corridors. It is operated by Mintygreen Healthcare Group (Emerald Care Center Sdn Bhd), a Malaysian eldercare brand established in 2017."

        "\n\nThe location is a genuine differentiator. Gleneagles Hospital Medini Johor — the first tertiary private hospital in Iskandar Puteri — is three minutes away by car. For families whose primary concern is emergency medical access, no other nursing home reviewed in Johor Bahru can match this adjacency. The facility explicitly markets itself to JB-Singapore cross-border families: it sits 20 km from the Tuas Checkpoint, includes monthly resident outings to Singapore's Botanic Gardens, and positions the cost difference between Malaysian and Singaporean residential care as a key value proposition."

        "\n\nThe amenity programme goes beyond standard nursing home offerings: a senior-friendly heated swimming pool with aqua aerobics sessions, a fully equipped gym, reflexology pathways, in-house physiotherapy, and TCM services (acupuncture and Tui Na) available as add-ons. Four meals are included daily, with a complimentary hotel breakfast buffet once per week. Pricing is by enquiry only — consistent with premium positioning and likely in the upper tier of the Malaysian market. Families should confirm the JKM licence number directly with the facility, as it was not publicly listed at time of research."
    ),
}

updates = []
for i, row in enumerate(fac_data[1:], start=2):
    slug = row[slug_i] if slug_i < len(row) else ''
    if slug in editorials and editorial_i is not None:
        updates.append({
            'range': f"'{FAC_TAB}'!{col_letter(editorial_i + 1)}{i}",
            'values': [[editorials[slug]]]
        })
        print(f'  Queued editorial for {slug}')

if updates:
    ss.values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={'valueInputOption': 'RAW', 'data': updates}
    ).execute()
    print(f'Updated {len(updates)} editorial summaries.')
