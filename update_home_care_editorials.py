"""
Push editorials + care_type corrections for 21 home-care-named facilities.
Sources: Apify Google Maps scraper + operator website research (2026-05-03).
"""

import sys, io
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
SHEET_TAB = 'google-sheets-facilities.csv'
TOKEN_PATH = r'C:\Users\ibkaa\nursinghomeguide-my\Nursing Home Guide Malaysia\token_sheets.json'
TODAY = '2026-05-03'

# ---------------------------------------------------------------------------
# Editorials — keyed by slug
# Also includes care_type corrections where the scraper confirmed true type
# ---------------------------------------------------------------------------
UPDATES = [
    {
        "slug": "my-peaceful-home-care-centre",
        "fields": {
            "care_types": "Nursing Home + Dementia",
            "last_updated": TODAY,
            "editorial_summary": (
                "My Peaceful Home Care Centre occupies a 670-square-metre property at 14, Jalan SS 19/3 in the SS 19 neighbourhood of Subang Jaya, Selangor. The operator expanded with a second centre in 2022 and serves residents from the Subang Jaya, Petaling Jaya and Damansara corridor. The home offers residential elderly care, assisted living and dedicated dementia nursing care.\n\n"
                "Two in-house physicians conduct weekly medical examinations; 24/7 trained caretakers are on duty and all rooms are fitted with call buttons. Room configurations include multi-sharing, twin-sharing and single private options, all with outdoor garden access. Operating enquiry hours are 9am to 10pm; visiting hours run 9am to 6pm.\n\n"
                "Six Google Maps reviews average 4.8 stars, with reviewers noting well-maintained facilities and experienced, approachable staff. Pricing and bed count are not posted on the website at mypeacefulhome.com.my — request a written quote during your visit and confirm the JKM licence number at the same time."
            ),
        },
    },
    {
        "slug": "my-joyful-home-care-centre",
        "fields": {
            "care_types": "Nursing Home + Dementia + Palliative",
            "last_updated": TODAY,
            "editorial_summary": (
                "My Joyful Home Care Center operates from 12, Jalan SS 19/3 in the SS 19 neighbourhood of Subang Jaya, Selangor — immediately adjacent to a similarly-named home at number 14. The centre launched a professional website in early 2025 at myjoyfulhome.com.my and lists 24/7 nursing staff as a core feature.\n\n"
                "Services span nursing home care, assisted living, dementia care, palliative care, diabetes management, respite stays and general senior residential care. Reviewers specifically mention daily doctor visits and describe a clean, homelike environment. Two contact numbers are listed: 019-329 3855 and 011-1281 2292.\n\n"
                "Eight Google Maps reviews average 5.0 stars. Reviewers describe professional caregivers, a comfortable atmosphere and attentive day-to-day support. Pricing and bed count are not posted on the operator website — contact the centre directly for a written fee breakdown and ask to confirm the JKM licence number during your site visit."
            ),
        },
    },
    {
        "slug": "prowell-elderly-home-care-centre-hq",
        "fields": {
            "care_types": "Nursing Home + Dementia + Palliative + Rehab + Day Care",
            "last_updated": TODAY,
            "editorial_summary": (
                "Prowell Elderly Home Care Centre is a family-owned operator billing itself as a fifth-generation company in the senior living space. The HQ sits at 17-1, Jalan Dato Haji Harun, Taman Taynton View, Cheras, with a second branch at 2, Persiaran Titiwangsa 2, Titiwangsa, both in Kuala Lumpur. The website is pehcc.com.my.\n\n"
                "Clinical capability is a stated strength: the centre lists feeding tube management, urinary catheter care, wound and bedsore dressing, tracheostomy management, physiotherapy and 24/7 doctor on-call with ambulance service. Care programmes cover long-term, short-term, retirement, dementia, bedridden and day care. Operating hours are daily 9am to 7pm.\n\n"
                "Seven Google Maps reviews of the Cheras HQ average 4.1 stars. One reviewer expressed gratitude for compassionate end-of-life care provided to their brother. Pricing, bed count and JKM licence numbers are not listed on the operator website — ask for these when you call or visit the facility."
            ),
        },
    },
    {
        "slug": "bandar-damai-home-care",
        "fields": {
            "total_beds": "40",
            "care_types": "Nursing Home",
            "last_updated": TODAY,
            "editorial_summary": (
                "Bandar Damai Home Care is a small nursing home in the Bandar Damai Perdana neighbourhood of Cheras, Kuala Lumpur, at No. 24, Jalan Damai Perdana 2/6f. The facility is managed by a retired government hospital staff nurse and supported by trained nurses, with a website at bandardamaihomecare.wixsite.com.\n\n"
                "The operator runs two homes with a combined capacity of 40 beds and provides 24-hour nursing care. Monthly doctor visits from KKM-registered physicians are included as a standard feature. Operating hours are daily 9am to 7pm. Phone: +60 3-9101 7930.\n\n"
                "Two Google Maps reviews average 4.5 stars, with reviewers noting good service and attentive staff. Pricing is not published on the website. Request monthly fee details and ask to confirm the JKM licence number when you make contact."
            ),
        },
    },
    {
        "slug": "my-precious-home-care-elder-care",
        "fields": {
            "care_types": "Nursing Home + Dementia + Palliative + Rehab",
            "last_updated": TODAY,
            "editorial_summary": (
                "My Precious Home Care Elder Care is a residential nursing home at 27, Jalan USJ 1/3B, Grandville, Subang Jaya, founded by a doctor who continues to conduct regular facility visits and health monitoring. The operator runs at least two branches — this USJ location and a second home in Kampung Tunku, Petaling Jaya. The website is myprecioushomecare.com.\n\n"
                "Care covers long-term and short-term stays, 24-hour personal care, dementia care, palliative care, an in-house physiotherapist for rehabilitation, and monitoring visits by the founding physician. Rooms have attached bathrooms and wheelchair accessibility; four home-cooked meals are served daily. Pricing is not published on the operator website.\n\n"
                "With 122 Google Maps reviews averaging 4.7 stars, this is among the most-reviewed elder care homes in the Subang Jaya area. Reviewers consistently describe kind, attentive staff and dignified treatment of residents. Request a written fee breakdown during your visit, noting that fees vary by care level and room type."
            ),
        },
    },
    {
        "slug": "my-precious-home-care-retirement-home",
        "fields": {
            "care_types": "Nursing Home + Dementia + Palliative + Rehab",
            "last_updated": TODAY,
            "editorial_summary": (
                "My Precious Home Care Retirement Home is the Petaling Jaya branch of the My Precious Home Care operator, located at 38, Jalan SS1/39 in Kampung Tunku, a mature residential neighbourhood near the SS1 and Jalan Utama corridor in PJ. The operator was founded by a doctor who maintains active medical involvement in resident oversight.\n\n"
                "Care services mirror those at the sibling USJ branch: 24-hour personal care, dementia and palliative care, in-house physiotherapy, monitoring visits and four daily home-cooked meals. All rooms feature attached bathrooms and wheelchair access. Website: myprecioushomecare.com; contact: +60 11-7489 9115.\n\n"
                "Eleven Google Maps reviews average 5.0 stars. One reviewer described a tour of the PJ bungalow as markedly different from a typical nursing home experience, noting a genuinely comfortable, spacious environment and residents who appeared content. Pricing is not listed on the operator website — request a written quote when you visit."
            ),
        },
    },
    {
        "slug": "rs-global-home-care-only-for-muslim",
        "fields": {
            "religion": "Muslim",
            "halal": "Yes",
            "care_types": "Nursing Home",
            "last_updated": TODAY,
            "editorial_summary": (
                "RS Global Home Care in Kampung Cheras Baru, Kuala Lumpur, is a residential nursing home serving Muslim residents exclusively, at 1C, Jalan 2, 56100 KL. The home emphasises Islamic programming alongside standard residential care. Phone: +60 11-3586 0025.\n\n"
                "Google Maps reviewers consistently highlight Islamic care practices as a key differentiator: residents receive assistance with daily prayers, participate in Quran recitation sessions, and are served halal meals. The facility has over 200 photos documented on Google Maps, reflecting active engagement by staff and families. Specific capacity and pricing details are not published online.\n\n"
                "Eighteen reviews average 4.7 stars. Malay-language reviewers describe clean rooms, well-prepared halal meals and staff who are attentive to religious obligations. For Muslim families seeking a values-aligned care environment with structured religious programming, this is one of the few facilities in the Cheras area explicitly committed to this. Confirm bed availability, fees and JKM licence directly by phone."
            ),
        },
    },
    {
        "slug": "sree-sai-elder-home-care-mental-health-old-age-residential-home",
        "fields": {
            "care_types": "Nursing Home",
            "last_updated": TODAY,
            "editorial_summary": (
                "Sree Sai Elder Home Care is a residential care facility at No. 204B, off Jalan Ampang, Kuala Ampang, Kuala Lumpur — a compact property on a quiet side street in the Ampang residential belt. The full registered name indicates care coverage that extends to both elderly residential needs and mental health support, making it one of the few KL facilities that explicitly states this dual scope. Phone: +60 12-297 0597.\n\n"
                "No website is available; care details are drawn from Google Maps data. Three photos show the facility exterior. The mental health component is worth clarifying on your first call to confirm whether the home accepts residents with behavioural or psychiatric conditions alongside standard physical care.\n\n"
                "Six reviews average 5.0 stars. Reviewers describe a well-organised, clean home with attentive staff. Care type specifics, capacity, pricing and JKM licence number should all be confirmed directly during a site visit."
            ),
        },
    },
    {
        "slug": "comfort-home-care-centre",
        "fields": {
            "care_types": "Nursing Home",
            "last_updated": TODAY,
            "editorial_summary": (
                "Comfort Home Care Centre is a residential nursing home at 56, Jalan Kampung Tengah 1/2, Taman Kampung Tengah, 84000 Muar, Johor — a quiet residential neighbourhood in central Muar town. It is one of a small number of dedicated elder care facilities serving Muar, a town with limited nursing home supply relative to its aging population. Phone: +60 12-696 9403.\n\n"
                "The facility has 11 photos on Google Maps, more than most comparable homes in the district, suggesting active day-to-day operations. Care details, capacity and pricing are not published online.\n\n"
                "Five reviews average 5.0 stars. No detailed review text was available at the time of writing, so specific care observations cannot be confirmed. When calling, ask about current bed availability, care types accepted, JKM licence status and monthly fees."
            ),
        },
    },
    {
        "slug": "his-grace-home-care-centretaman-pramlee",
        "fields": {
            "care_types": "Nursing Home",
            "last_updated": TODAY,
            "editorial_summary": (
                "His Grace Home Care Centre operates a branch from 10, Jalan Cempaka in the Taman P. Ramlee neighbourhood of Kuala Lumpur, close to Taman Desa and the MRR2 corridor. The operator also runs a second branch in Setapak. Phone for this branch: +60 11-1162 5831.\n\n"
                "The facility has 18 photos documented on Google Maps — a high count for a home of this size, suggesting regular photo updates by staff or family members. Care specifics, capacity and pricing are not published online.\n\n"
                "Two reviews average 4.5 stars, describing excellent and attentive service. No website is currently available. Confirm care types, JKM licence number and monthly fees during a site visit."
            ),
        },
    },
    {
        "slug": "his-grace-home-care-centre",
        "fields": {
            "care_types": "Nursing Home",
            "last_updated": TODAY,
            "editorial_summary": (
                "His Grace Home Care Centre is a residential care facility at 4, Jalan Perusahaan 1, off Jalan Genting Kelang, Setapak, Kuala Lumpur — a light commercial street in the Setapak area, accessible from both Jalan Genting Kelang and the Kerinchi Link. The operator also runs a second branch in the Taman P. Ramlee neighbourhood. Phone: +60 16-671 5732.\n\n"
                "Two Google Maps photos show the facility interior. Care specifics, capacity and pricing are not published online.\n\n"
                "Two reviews average 5.0 stars. Confirm care types accepted, current bed availability, JKM licence number and monthly fees when you visit."
            ),
        },
    },
    {
        "slug": "home-sweet-home-care-centre-jalan-gasing",
        "fields": {
            "care_types": "Nursing Home",
            "last_updated": TODAY,
            "editorial_summary": (
                "Home Sweet Home Care Centre occupies a residential property at 43, Jalan Gasing in the Bukit Gasing area of Petaling Jaya, Selangor — a well-established hillside neighbourhood with easy access to PJ's commercial belt and the Klang Valley highway network. The home maintains a Facebook page at facebook.com/homesweethomecarecentre. Phone: +60 16-603 6821.\n\n"
                "Four Google Maps photos document the facility. Care details and capacity are not published beyond what is visible on the Facebook page.\n\n"
                "Three reviews average 5.0 stars. Reviewers describe friendly, accommodating staff and a reassuring atmosphere where families feel confident leaving their loved ones. Confirm care types offered, JKM licence and monthly fees during your first call or visit."
            ),
        },
    },
    {
        "slug": "aurora-home-care-centre",
        "fields": {
            "care_types": "Nursing Home",
            "last_updated": TODAY,
            "editorial_summary": (
                "Aurora Home Care Centre is a small residential care facility at 166E, Jalan Sireh, off Jalan Meru, Kawasan 17, 41050 Klang, Selangor — a mixed residential area roughly midway between Klang town centre and Port Klang. The home maintains a Facebook presence at facebook.com/Aurorahomecarecentre. Phone: +60 16-690 6333.\n\n"
                "Two Google Maps photos are available. Care details and capacity are not published beyond the Facebook page, which is the primary public-facing channel for the facility.\n\n"
                "One review rates it 5.0 stars, praising the caregivers and specifically naming a staff member for attentive, consistent care. For a Klang-based facility with an active social media presence, this is a reasonable starting point. Confirm JKM licence, care types, current availability and monthly fees when you call."
            ),
        },
    },
    {
        "slug": "ln-home-care-center",
        "fields": {
            "care_types": "Nursing Home",
            "last_updated": TODAY,
            "editorial_summary": (
                "LN Home Care Center is a small nursing home at Bunga Ros, Kawasan 6, Taman Teluk Pulai, 41100 Klang, Selangor — a residential pocket within the Teluk Pulai township, a predominantly Chinese-majority neighbourhood in western Klang. Phone: +60 19-888 8690.\n\n"
                "Two Google Maps photos show the facility. Care details, capacity and pricing are not published online.\n\n"
                "Three reviews average 5.0 stars. No detailed review text was available, so specific care observations cannot be confirmed at this time. When calling, ask about the JKM licence number, care types accepted, current bed availability and monthly fees."
            ),
        },
    },
    {
        "slug": "sunshine-nursing-home-care",
        "fields": {
            "care_types": "Nursing Home",
            "last_updated": TODAY,
            "editorial_summary": (
                "Sunshine Nursing Home Care is a residential nursing facility at No. 33, Jalan Teluki 2, Bukit Sentosa, 44300 Rawang, Selangor — a township on the northern fringe of the Klang Valley, approximately 35km from central KL. Phone: +60 12-474 6615.\n\n"
                "One photo is available on Google Maps. Care details, capacity and pricing are not published online. No website is available.\n\n"
                "Two reviews present contrasting experiences: one 5-star review and one 1-star review citing a dispute over deposit refund following a resident's passing. Before admission, families should clarify the deposit and refund policy in writing and ask to see the JKM licence."
            ),
        },
    },
    {
        "slug": "rebina-home-care-centre-sdn-bhd",
        "fields": {
            "care_types": "Nursing Home + Day Care",
            "last_updated": TODAY,
            "editorial_summary": (
                "Rebina Home Care Centre Sdn Bhd is a formally incorporated elder care operator in Taman Abad, Johor Bahru, Johor, at 112, Jalan Wijaya — one of the older residential neighbourhoods in JB, close to the city centre. The registered corporate name suggests formal legal incorporation, though no website is available for further detail.\n\n"
                "The facility appears to offer both residential and day care services based on its registered care types. No phone number is currently published on Google Maps; families should visit directly or contact the JKM Johor office to obtain current details.\n\n"
                "Two Google Maps reviews average 3.5 stars. One reviewer described the environment as clean and quiet; a second observed strict daily routines and noted that some staff could be short-tempered with residents. When visiting, observe staff interactions with residents first-hand and ask about staffing ratios, resident routines and the JKM licence number."
            ),
        },
    },
    {
        "slug": "pine-tree-home-care-centre-johor",
        "fields": {
            "care_types": "Nursing Home",
            "last_updated": TODAY,
            "editorial_summary": (
                "Pine Tree Home Care Centre is located at 277, Lorong Setia, Jalan Parit Mesjid, 82000 Pontian District, Johor — a semi-rural residential area in the southern part of Johor, approximately 45km south-west of Johor Bahru. Phone: +60 19-776 6666.\n\n"
                "Two photos are available on Google Maps. Care details, capacity and pricing are not published online. No website is available.\n\n"
                "One review rates it 3.0 stars but contains no written comments. Families in the Pontian area have limited nursing home options in the immediate district; confirm care types accepted, JKM licence status and monthly fees by phone before making the trip to visit."
            ),
        },
    },
    {
        "slug": "good-family-home-care",
        "fields": {
            "care_types": "Nursing Home",
            "last_updated": TODAY,
            "editorial_summary": (
                "Good Family Home Care is a small residential care facility at 799, Lorong Permai 14, Kampung Tasek Permai, 68000 Ampang, Selangor — a semi-rural neighbourhood on the eastern fringe of Kuala Lumpur near the Ampang border. Nine photos are visible on Google Maps, providing a visual sense of the property exterior.\n\n"
                "No phone number, website or published care details are currently available online. The facility appears to operate without a significant digital presence, meaning direct in-person contact is the most reliable way to assess suitability.\n\n"
                "No reviews have been recorded on Google Maps at this time. Families considering this facility should visit in person and confirm care types offered, JKM licence status, current bed availability and monthly fees before making any decision."
            ),
        },
    },
    {
        "slug": "sayang-nursing-home-care",
        "fields": {
            "last_updated": TODAY,
            "editorial_summary": (
                "Sayang Nursing Home Care lists its address as the second floor of Anggerik Mall, Seksyen 14, 40000 Shah Alam, Selangor — a commercial mall location rather than a residential care property. This suggests the business may operate as a home care placement or coordination service rather than a live-in residential nursing facility. Phone: +60 3-5519 7501.\n\n"
                "No website, reviews or published care details are currently available. The nature of the operation — residential care or home-based care services — is not confirmed through publicly available information.\n\n"
                "Families should contact the Shah Alam number directly to clarify whether the service dispatches caregivers to clients' homes, operates a residential facility at a separate address, or provides both. This will help determine whether it meets your specific care requirements."
            ),
        },
    },
    {
        "slug": "city-home-care-centre",
        "fields": {
            "care_types": "Nursing Home",
            "last_updated": TODAY,
            "editorial_summary": (
                "City Home Care Centre is a nursing home at 20, Lorong Kadok, Taman Chi Liung, 41200 Klang, Selangor, with a website at dannycarecentre.wixsite.com. Phone: +60 16-612 3368. The facility has 10 photos documented on Google Maps.\n\n"
                "Care details and bed capacity are not published on the website. No staffing qualifications or JKM licence number is listed online.\n\n"
                "Six Google Maps reviews average 1.7 stars. Families considering this facility are strongly encouraged to read the Google Maps reviews in full before proceeding, visit the facility in person, and clarify in writing: the deposit amount and refund policy, the JKM licence number, staffing qualifications, and the escalation procedure if a resident requires urgent hospital transfer."
            ),
        },
    },
]


# ---------------------------------------------------------------------------
# Google Sheets helpers
# ---------------------------------------------------------------------------

def col_letter(idx):
    s = ''
    idx += 1
    while idx:
        idx, rem = divmod(idx - 1, 26)
        s = chr(65 + rem) + s
    return s


def load_sheet():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, scopes=['https://www.googleapis.com/auth/spreadsheets'])
    svc = build('sheets', 'v4', credentials=creds)
    result = svc.spreadsheets().values().get(
        spreadsheetId=SHEET_ID, range=f'{SHEET_TAB}!1:1'
    ).execute()
    headers = result['values'][0]
    result2 = svc.spreadsheets().values().get(
        spreadsheetId=SHEET_ID, range=f'{SHEET_TAB}!B:B'
    ).execute()
    slugs = [row[0] if row else '' for row in result2.get('values', [])]
    return svc, headers, slugs


def find_row(slugs, slug):
    for i, s in enumerate(slugs):
        if s == slug:
            return i + 1
    return None


def preflight_check(updates):
    for u in updates:
        slug = u['slug']
        editorial = u['fields'].get('editorial_summary', '')
        if '"' in editorial:
            print(f'PREFLIGHT FAIL: straight double-quote in editorial for {slug}')
            return False
    print('Preflight: all editorials clean.')
    return True


if __name__ == '__main__':
    if not preflight_check(UPDATES):
        sys.exit(1)

    print('Loading sheet...')
    svc, headers, slugs = load_sheet()
    print(f'Sheet loaded. {len(slugs)} rows, {len(headers)} columns.')

    batch = []
    skipped = []

    for u in UPDATES:
        slug = u['slug']
        row = find_row(slugs, slug)
        if not row:
            print(f'SKIP (not found): {slug}')
            skipped.append(slug)
            continue

        for col_name, value in u['fields'].items():
            if col_name not in headers:
                print(f'  WARNING: column "{col_name}" not found — skipping for {slug}')
                continue
            col_idx = headers.index(col_name)
            batch.append({
                'range': f'{SHEET_TAB}!{col_letter(col_idx)}{row}',
                'values': [[value]]
            })

        print(f'  Queued {len(u["fields"])} fields for {slug} (row {row})')

    print(f'\nPushing {len(batch)} cell updates across {len(UPDATES) - len(skipped)} slugs...')
    body = {'valueInputOption': 'USER_ENTERED', 'data': batch}
    resp = svc.spreadsheets().values().batchUpdate(
        spreadsheetId=SHEET_ID, body=body
    ).execute()
    print(f'Done. Updated {resp.get("totalUpdatedCells", 0)} cells across {resp.get("totalUpdatedRows", 0)} rows.')
    if skipped:
        print(f'Skipped: {skipped}')
