"""Upload batch 1 editorials (9 facilities) to Google Sheet."""
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import date

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE = 'token_sheets.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
TAB = 'google-sheets-facilities.csv'

EDITORIALS = {

'jb-care-centre': (327, (
    "JB Care Centre is a nursing home situated in Taman Sri Tebrau, Johor Bahru, operating from "
    "Jalan Rentaka. The home accepts elderly residents requiring general nursing care and daily "
    "assistance, and has a capacity of around 40 beds. It is one of several independent nursing homes "
    "in this part of JB, serving residents in the Tebrau and surrounding corridor.\n\n"
    "The home is reachable at 07-3331999 for administrative enquiries. Specific clinical capabilities, "
    "staffing details, and visiting hours are not published, and the facility's website is currently "
    "inaccessible, which limits what families can verify online before visiting.\n\n"
    "Anyone considering JB Care Centre should call directly to ask about current bed availability, "
    "the scope of nursing care offered, and overnight staffing arrangements. It is best suited for "
    "residents who need general daily support and supervision rather than intensive medical management."
)),

'green-acres-home-care': (328, (
    "Green Acres Home Care has been providing elderly residential care in Johor Bahru since the 1990s, "
    "operating from two bungalow-style homes: the main branch at Taman Bukit Kempas on a hilltop site, "
    "and a second location at Kim Teng Park off Jalan Intan. The bungalow format gives both homes a "
    "genuinely residential feel that sets them apart from the shophouse nursing homes common in JB, "
    "and visiting hours run daily from 11am to 6pm.\n\n"
    "The clinical offering is solid for a smaller private home. Confirmed services include oxygen "
    "therapy, wound dressing, physiotherapy, dietician-controlled meal planning, and ambulance "
    "transport. On-call doctors attend when needed, and a qualified Home Manager oversees daily "
    "operations. The team is contactable via WhatsApp and a direct mobile line (016-7150393).\n\n"
    "Green Acres suits families looking for care that balances clinical support with a homely, "
    "non-institutional setting. Doctors are on-call rather than in-house, so residents requiring "
    "continuous medical monitoring should be assessed carefully before placement. Pricing is "
    "competitive but not published online — call or WhatsApp for a quote based on the level of care needed."
)),

'procare-care-centre': (344, (
    "Procare Care Centre has been operating in Taman Yarl, Kuala Lumpur, since 1997 and is registered "
    "with the Ministry of Health (MOH) — a distinction held by relatively few private nursing homes in "
    "Malaysia. Based on Jalan Awan Dandan, it specialises in post-stroke rehabilitation and "
    "high-dependency nursing care, and draws a significant proportion of its admissions directly from "
    "hospital discharges and families managing complex medical conditions at home.\n\n"
    "The clinical depth here stands out. An in-house doctor conducts daily consultations, a resident "
    "physiotherapist runs daily sessions, and the team is equipped to manage patients with paralysis, "
    "coma states, PEG feeding tubes, and dialysis-compatible needs. With over 20 staff and 27 years "
    "of continuous operation, Procare offers a level of medical coverage that is rare outside of "
    "hospital-affiliated step-down facilities.\n\n"
    "Pricing is not published, so families should call 03-79818522 or reach out via Facebook "
    "(PCCSB05) to discuss fees based on dependency level and room type. The main website is "
    "currently down. Given its MOH registration and clinical profile, Procare should be one of the "
    "first calls for families needing a medically capable nursing home in the KL south area."
)),

'afh-elder-care': (336, (
    "AFH Elder Care is a residential nursing home in Kepong, Kuala Lumpur, operating from Jalan "
    "Api Api. The facility is managed by a trained Matron and has been described by visitors as "
    "one of the cleaner homes in the Klang Valley — a recurring observation in online mentions. "
    "The home caters to elderly residents who need daily care and supervision in a residential setting.\n\n"
    "Detailed clinical information including bed count, specific services, and staffing ratios is "
    "not publicly available, and the facility's website is currently inaccessible. Previous accounts "
    "describe a cosy and spacious environment with attentive staff, and pricing is understood to be "
    "competitive within the Kepong corridor. Enquiries are handled by phone at 03-6243 3824.\n\n"
    "AFH Elder Care is worth considering for families living in Kepong, Sri Damansara, or the "
    "Selayang area who want a well-maintained local option. A visit in person before deciding is "
    "advisable — call ahead to confirm current availability and to assess whether the home's care "
    "scope matches your relative's specific needs."
)),

'amazing-grace-caring-home': (338, (
    "Amazing Grace Caring Home operates multiple branches across Kuala Lumpur and Subang Jaya, "
    "providing residential nursing care to elderly residents since 2007. The network is guided by "
    "Christian values and accepts residents of all backgrounds. Branches include sites at Taman Tan "
    "Yew Lai, Taman Yarl (KL), Section 14 Petaling Jaya, and SS19 Subang Jaya. Indicative pricing "
    "runs from RM 2,001 to RM 4,000 per month depending on room type — shared twin, triple, or "
    "single with attached bathroom — making it one of the few homes in this category that publishes "
    "a real price range.\n\n"
    "Confirmed clinical services across the network include dementia management, post-stroke "
    "rehabilitation support, post-operative recovery, wound care, medication management, and "
    "ambulance transport. The Subang Jaya branch has a strong Google and Facebook rating and has "
    "been recognised by Trusted Malaysia as among the better-regarded nursing homes in the KL "
    "and Subang corridor. Weekly chapel services are held at some branches for interested residents.\n\n"
    "Each branch operates independently, so quality can vary. Families should visit the specific "
    "location they are considering and ask directly about staffing ratios, overnight nursing cover, "
    "and whether there is a visiting or in-house doctor arrangement. JKM or MOH licensing has not "
    "been publicly confirmed across branches — worth verifying before committing. WhatsApp is "
    "the easiest way to start an enquiry."
)),

'amitabha-malaysia-old-folks-home-kl': (339, (
    "Amitabha Malaysia Old Folks Home operates from Happy Garden, off Jalan Kuchai Lama in Kuala "
    "Lumpur, as part of the Amitabha Foundation established in 1998. The Foundation runs a range "
    "of welfare services including a dialysis centre and an orphanage. Despite its Buddhist name, "
    "the home explicitly serves elderly residents of all religions, ethnicities, and backgrounds. "
    "Current capacity is approximately 30 residents.\n\n"
    "The model here is welfare-based residential care: meals, shelter, daily supervision, and "
    "community activities including a weekly social programme on Thursday mornings. The organisation "
    "is registered as a charity and depends partly on public donations for operating costs. It is "
    "not a nursing home in the clinical sense — there are no confirmed nursing or rehabilitation "
    "capabilities, and the focus is on basic daily living support and social wellbeing.\n\n"
    "This home is most appropriate for elderly individuals who are ambulatory, socially engaged, "
    "and do not require medical management or nursing care. Families with a loved one who needs "
    "daily nursing, physiotherapy, or clinical monitoring should look elsewhere. For those seeking "
    "an affordable, community-oriented option in the Kuchai Lama area, call 03-7890 3700 to "
    "understand the admission criteria and whether fees apply or admission is donation-based."
)),

'dhaalia-elderly-care-centre': (341, (
    "Dhaalia Elderly Care Centre (DECC) has been providing residential care for elderly and disabled "
    "adults in the Old Klang Road area of Kuala Lumpur since 2006, operating from Taman Halimahton. "
    "With close to two decades of operation in the same location, it has become a known option for "
    "families in the Taman Yarl and Old Klang Road area looking for affordable, round-the-clock "
    "residential care. Dementia care has been listed among its services in multiple eldercare "
    "directories, alongside general nursing and personal care.\n\n"
    "Clinical details beyond general nursing and dementia support are not publicly documented. The "
    "centre's website (deccmy.com) is currently inaccessible, and the facility is understood to "
    "use manual rather than digital administrative systems. The Facebook page (DECCKL) and phone "
    "numbers 03-79814729 and 019-389-2155 are the active contact points.\n\n"
    "A visit in person before placement is strongly recommended, both to assess the physical "
    "environment and to understand how the home is run day-to-day. DECC is best suited for elderly "
    "residents with moderate daily care needs and a budget-conscious placement in the Old Klang "
    "Road corridor. Ask specifically about nursing qualifications on staff and how medical "
    "emergencies are handled overnight."
)),

'merry-care-centre-jln-antoi': (343, (
    "Merry Care has operated small residential elderly care homes in Kepong and Kuchai Lama since "
    "2001, with the Jalan Antoi branch being one of several Kepong Baru sites. The model is "
    "deliberately small-scale: each home houses 14 to 18 residents with a caregiver-to-resident "
    "ratio of approximately 1 to 4 or 5. The group operates over five branches across Kepong, "
    "Selayang, and Desa Jaya, all accessible through the elderlycare.my platform.\n\n"
    "Pricing starts from RM 2,500 per month and covers five meals daily, laundry, and housekeeping. "
    "Diapers, medications, and hospital accompaniment (RM 200 per visit) are billed separately. "
    "The care model is assisted living: bathing support, medication reminders, mobility help, daily "
    "exercise, and social activities. There is no in-house doctor or registered nurse — the team "
    "comprises trained caregivers. This makes Merry Care well-suited for semi-independent elderly "
    "residents but unsuitable for those with complex medical dependencies.\n\n"
    "The small-home format appeals to families who want a quieter, more residential atmosphere for "
    "their relative rather than a larger institutional setting. Free 30-minute visits can be arranged "
    "via the website. Confirm JKM licensing status directly when visiting, and ask clearly about "
    "what happens if a resident's medical needs escalate during their stay."
)),

'rumah-orang-tua-charis': (345, (
    "Rumah Orang Tua Charis is a Christian welfare home in Taman Lucky, Kuala Lumpur, founded in "
    "1988 by Reverend Teo How Ken and registered as a charitable organisation with the Registrar "
    "of Societies in 1993. The home accommodates 17 elderly residents and operates alongside a "
    "children's home under the same organisation. Weekly services are held at the affiliated "
    "Methodist Charis Community Care Center, and a social programme called the VSOP Club "
    "(Very Strong Old People) meets on Thursday mornings.\n\n"
    "Care provided is welfare-level residential support: shelter, meals, basic daily assistance, "
    "access to medical attention when needed, and pastoral and emotional care. The home also "
    "assists with family reunification and funeral arrangements where required. This is not a "
    "nursing facility — there is no rehabilitation programme, dementia unit, or intensive medical "
    "capability, and the very small size means admission is selective and a waiting list likely exists.\n\n"
    "Rumah Charis suits elderly individuals who are Christian or would welcome a Christian community "
    "setting, who are relatively mobile and independent, and whose families need welfare-level "
    "support rather than clinical nursing. Admission tends to prioritise those from lower-income "
    "backgrounds given the charity model. Call 03-7781 5977 to speak with the Operations Manager "
    "about the admission process, current availability, and whether any contribution is expected."
)),

}

creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
service = build('sheets', 'v4', credentials=creds)
ss = service.spreadsheets()

updates = []
for slug, (row_num, editorial) in EDITORIALS.items():
    col_letter = 'AY'  # editorial_summary = col 50 (0-indexed) = AY
    updates.append({'range': f"'{TAB}'!AY{row_num}", 'values': [[editorial]]})

body = {'valueInputOption': 'RAW', 'data': updates}
result = ss.values().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
print(f'Uploaded: {result.get("totalUpdatedCells",0)} editorials')

progress = {
    'done': list(EDITORIALS.keys()),
    'skipped': [{'slug': 'acg-care-sdn-bhd', 'reason': 'Corporate entity / developer group, not a residential nursing home. Needs re-verification of what this listing represents.'}],
    'last_batch': str(date.today()),
    'total_done': len(EDITORIALS)
}
with open('profile_progress.json', 'w', encoding='utf-8') as f:
    json.dump(progress, f, indent=2, ensure_ascii=False)
print(f'Progress saved: {len(EDITORIALS)} done, 1 skipped (ACG)')
