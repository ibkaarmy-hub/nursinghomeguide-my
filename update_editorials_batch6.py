"""
Batch update editorial_summary + key fields for 9 facilities researched:
ECON Medicare Taman Perling, Fu Ka, Nur Ehsan, Impian Syimah Kemuncak,
Lotus Ville, Golden Age Muar, Master Nursing Daya, Sunrise/Rebina, Lee Nursing
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

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
    spreadsheetId=SPREADSHEET_ID, range=f"'{FAC_TAB}'"
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
TODAY = str(date.today())

UPDATES = {

'econ-medicare-centre-nursing-home-taman-perling-branch': {
    'editorial_summary': (
        "ECON Medicare Centre & Nursing Home – Taman Perling Branch stands apart from other "
        "private nursing homes in Johor Bahru by virtue of its corporate pedigree and scale. "
        "Opened in April 2013, this purpose-built 199-bed, four-storey facility (57,000 sq ft) "
        "is operated by ECON Healthcare Group — the largest private nursing home operator in "
        "Singapore and Malaysia by revenue, with 36 years of eldercare experience. Located "
        "approximately 45 minutes from the Causeway, it is the primary cross-border option "
        "for Singaporean families seeking significantly lower-cost nursing home care without "
        "sacrificing institutional quality standards. In mid-2025, US private equity firm TPG "
        "completed an S$87.8 million acquisition and delisted ECON from SGX; institutional-"
        "grade governance continues under the ECON brand.\n\n"
        "ECON Taman Perling's clinical offering is broad for a Malaysian nursing home: skilled "
        "nursing care, post-stroke rehabilitation, dementia and memory care, palliative care, "
        "Parkinson's and cancer care, physiotherapy, occupational therapy, and wound dressing "
        "are all confirmed. The group's distinctive 'East-meets-West' model integrates "
        "Traditional Chinese Medicine (TCM) including acupuncture alongside Western nursing "
        "protocols. The facility operates 24 hours, 7 days a week with Registered Nurses, "
        "physiotherapists, occupational therapists, and paramedics confirmed on staff. A "
        "group-wide Malaysia fee range of RM 1,950–6,600/month was disclosed in the 2021 "
        "IPO prospectus; room-type-specific pricing requires direct inquiry.\n\n"
        "Visiting hours are 10am–7pm daily with a maximum of two visitors at a time; "
        "children under 12 are restricted from wards but may visit in the designated family "
        "area. The facility is not listed on AGECOPE or nursinghome.my directories; JKM "
        "licence details require direct verification. With 152 Google reviews averaging "
        "4.5 stars — the highest review count in this dataset — families consistently praise "
        "nursing attentiveness, cleanliness, staff professionalism, and activity programming."
    ),
    'phone': '+60 7-234 4680',
    'website': 'https://econhealthcare.my',
    'facebook': 'https://www.facebook.com/econperling/',
    'pricing_display': 'From RM 1,950/mo (contact for current rates)',
    'care_assisted': 'yes',
    'care_dementia': 'yes',
    'care_palliative': 'yes',
    'care_rehab': 'yes',
    'care_respite': 'yes',
    'care_nursing': 'yes',
    'rn_24_7': 'yes',
    'medical_physio': 'yes',
    'ownership_type': 'Private',
    'total_beds': '199',
    'last_updated': TODAY,
},

'fu-ka-care-center': {
    'editorial_summary': (
        "Fu Ka Care Center, operating under the registered entity Fu Ka Nursing Care Center "
        "Sdn. Bhd. (reg. 1512468W), is a private nursing home established in May 2023 and "
        "situated at PTD 14521, Jalan Persiaran Kempas Baru, Kempas Baru, Johor Bahru. The "
        "facility is located in the Kempas Baru corridor — a growing residential district in "
        "south-central JB well-served by Kempas Medical Centre nearby. Being a newer entrant, "
        "the centre has not yet appeared in major Malaysian elder-care directories such as "
        "AGECOPE Johor or nursinghome.my, though it has established a presence on Facebook "
        "and Instagram at @fukacarecenter.\n\n"
        "The facility promotes itself as a full-service nursing home offering 24-hour nursing "
        "care, medical supervision, physiotherapy, dementia care, and specialist care. Its "
        "5-star rating across 24 Google reviews is a positive early signal for a facility "
        "incorporated in 2023. The name 'Fu Ka' (福家) translates from Chinese as 'blessed "
        "family,' suggesting a Chinese-community orientation, though care for all ethnicities "
        "is not excluded. Pricing information has not been publicly disclosed on any platform "
        "and must be confirmed by direct inquiry.\n\n"
        "JKM licence details, halal certification status, nurse-to-resident ratios, and "
        "staffing structure remain unverified from open sources. Families considering this "
        "centre should call +60 19-381 4521 or email fukanursinghome14521@gmail.com for "
        "pricing and availability. A site visit is recommended before any placement commitment "
        "given the limited review history for a facility less than three years old."
    ),
    'phone': '+60 19-381 4521',
    'facebook': 'https://www.facebook.com/fukacarecenter',
    'area': 'Kempas Baru, Johor Bahru',
    'pricing_display': 'Contact for rates',
    'care_assisted': 'yes',
    'care_dementia': 'yes',
    'care_nursing': 'yes',
    'medical_physio': 'yes',
    'ownership_type': 'Private',
    'last_updated': TODAY,
},

'pusat-jagaan-warga-emas-nur-ehsan': {
    'editorial_summary': (
        "Pusat Jagaan Warga Emas Nur Ehsan is a Muslim welfare home for the elderly operated "
        "by Persatuan Kebajikan Nur Ehsan Negeri Johor (PKNENJ), a registered NGO that has "
        "been active since November 2008. This is not a commercial nursing home — it is a "
        "faith-based welfare facility that accepts destitute, abandoned, and family-less "
        "elderly Muslims, as well as individuals with physical and mental disabilities and "
        "converts (muallaf). Residents are referred by JKM officers, hospital social work "
        "units (including Hospital Permai JB), the Johor Islamic Council (MAIJ), and the "
        "Johor Islamic Affairs Department (JAIJ). Families who can contribute are asked to "
        "pay a modest amount toward costs, but the facility is donation-driven and does not "
        "publish a standard fee schedule.\n\n"
        "The Kempas Baru branch at Jalan Denai 1 serves primarily male elderly residents "
        "across five wards categorised by care dependency, with a stated capacity of 56. "
        "The wider organisation runs four branches across Johor (Ledang, Bukit Indah, and "
        "Simpang Renggam), housing roughly 167 residents in total. Physiotherapy, daily "
        "health monitoring by visiting medical professionals, social and recreational "
        "activities, and 24-hour CCTV security are documented. The facility has received "
        "donations from Yayasan JCorp and Boustead Properties, confirming legitimate NGO "
        "standing.\n\n"
        "For families considering placement, this facility is most appropriate for "
        "low-income elderly Muslims without a family support network, or as a JKM-referred "
        "placement for individuals whose families cannot be traced. Families seeking "
        "fee-for-service care should contact the manager (Encik Saiful, 013-794 0350) to "
        "discuss individual arrangements. No JKM licence number is publicly listed; "
        "prospective referrers should request it directly before placement."
    ),
    'phone': '+60 7-232 6415',
    'facebook': 'https://m.facebook.com/pages/category/Public-Service/Pusat-Jagaan-Warga-Emas-Nur-Ehsan-1051759248276730/',
    'area': 'Kempas Baru, Johor Bahru',
    'pricing_display': 'Welfare/donation-based; JKM subsidy accepted',
    'ownership_type': 'NGO / Welfare',
    'religion': 'Islam',
    'halal': 'yes',
    'subsidy': 'yes',
    'medical_physio': 'yes',
    'care_assisted': 'yes',
    'last_updated': TODAY,
},

'pusat-jagaan-impian-syimah-jalan-kemuncak': {
    'editorial_summary': (
        "Pusat Jagaan Impian Syimah (Jalan Kemuncak) is a small, privately run care home "
        "in Kampung Nong Chik, Johor Bahru. Operated by a husband-and-wife team — Rosmi "
        "and Hasyimah — who have managed the centre for over a decade, the facility caters "
        "primarily to Malay-Muslim elderly residents and has received CSR attention from "
        "corporate partners including Lalamove (2023), Holiday Inn JB City Centre (2024), "
        "and Sunway Group (Ramadan 2026). A Sunway-reported event noted 61 elderly residents "
        "and 23 bedridden among the population served, indicating the centre takes high-"
        "dependency residents. The faith-based environment and consistent community goodwill "
        "suggest a genuinely caring ethos at the management level.\n\n"
        "The 3.5-star Google Maps rating — below the JB average for licensed care homes — is "
        "a flag that warrants honest disclosure. The text of the 11 reviews driving that "
        "score could not be independently retrieved. What is known is that this is a small, "
        "home-based setup in a kampung residential address, relying heavily on donor support "
        "for basics such as diapers and cleaning supplies. These characteristics are "
        "consistent with care homes that sometimes attract criticism for under-resourcing, "
        "though no inspection violations or regulatory actions appeared in any source.\n\n"
        "Families considering this centre should treat the below-average rating seriously "
        "and ask direct questions on-site: staff-to-resident ratio, nursing qualifications, "
        "how bedridden residents are managed overnight, and whether a current JKM licence "
        "is displayed. For families needing a fully staffed clinical environment, a higher-"
        "rated licensed home with documented RN coverage is a safer choice. Families seeking "
        "a small, Muslim-run community environment at a modest cost may find this worth a "
        "personal visit with due diligence."
    ),
    'phone': '+60 13-750 7134',
    'facebook': 'https://www.facebook.com/PusatJagaanImpianSyimah',
    'area': 'Johor Bahru',
    'pricing_display': 'Contact for rates',
    'ownership_type': 'Private',
    'religion': 'Islam',
    'halal': 'yes',
    'last_updated': TODAY,
},

'lotus-ville-care-centre': {
    'editorial_summary': (
        "Lotus Ville Care Centre Sdn Bhd is a private nursing home registered under "
        "Malaysia's Private Healthcare Facilities and Services Act (Act 586), operating "
        "from Taman Johor Jaya in Johor Bahru. Incorporated in April 2022, it is a "
        "relatively young facility that has earned membership in AGECOPE — the Association "
        "for Residential Aged Care Operators of Malaysia — signalling commitment to industry "
        "standards in a sector where many operators remain unaffiliated. Despite the .org.my "
        "domain, the company is registered as a private limited company (Sdn Bhd). AGECOPE "
        "confirms services include assisted living, palliative care, and dementia care, with "
        "staff described as trained in geriatrics, physiotherapy, and nursing care.\n\n"
        "A Facebook presence notes a Dr Thurgadevi as a contact, suggesting at least periodic "
        "doctor involvement. The 4-star rating from 8 Google reviews reflects steady community "
        "satisfaction, reasonable for a facility less than three years old. Two addresses "
        "appear in aggregator data — 67, Jalan Anggerik 20, Taman Johor Jaya (the more "
        "frequently cited, likely main site) and No. 1, Jalan Camar 3, Taman Perling — "
        "which may indicate a second branch or a data discrepancy that families should verify "
        "directly before visiting.\n\n"
        "No pricing has been published publicly — quote-on-request model consistent with the "
        "broader Malaysian nursing home market. No religious affiliation has been identified; "
        "the lotus branding appears to be aesthetic rather than Buddhist or denominational. "
        "Families should call +60 17-737 1233 to confirm the current address, pricing, RN "
        "night coverage, and halal meal availability before making a placement decision."
    ),
    'phone': '+60 17-737 1233',
    'website': 'https://lotusville.org.my/',
    'facebook': 'https://www.facebook.com/p/Lotus-Ville-100080820686444/',
    'area': 'Johor Bahru',
    'pricing_display': 'Contact for rates',
    'care_assisted': 'yes',
    'care_dementia': 'yes',
    'care_palliative': 'yes',
    'care_nursing': 'yes',
    'medical_physio': 'yes',
    'ownership_type': 'Private',
    'last_updated': TODAY,
},

'golden-age-care-centre': {
    'editorial_summary': (
        "Golden Age Care Centre (GACC) is a multi-branch private nursing home chain "
        "headquartered in Muar, Johor — note that Muar is a distinct town roughly 90 km "
        "north-west of Johor Bahru, not part of the JB conurbation. The Muar branch, the "
        "chain's founding location (established 2004, incorporated 2014), sits at 28-10 "
        "Jalan Ria 2, Taman Ria — off Jalan Salleh in central Muar, the same arterial road "
        "as Hospital Pakar Sultanah Fatimah, placing it within easy reach of the town's "
        "main government specialist hospital. The chain also operates in Batu Pahat, "
        "Tangkak, and Melaka.\n\n"
        "The Muar branch holds a 4-Star JKM rating — the highest tier achievable under the "
        "national licensing framework. Services span residential care, on-site nursing and "
        "physiotherapy, a dedicated Memory Care programme, occupational and speech therapy, "
        "nutritional dining with dietary accommodations, hospital transport, and 24/7 CCTV "
        "monitoring. Private and semi-private rooms are available; exact room pricing is not "
        "publicly disclosed. Visiting hours are 9am–6pm daily.\n\n"
        "At 3.9 stars from 8 Google reviews, the Muar branch occupies a mid-range position — "
        "thin volume but a substantially better signal than the Batu Pahat branch (1.3★/3 "
        "reviews), which carries a poor reputation. Families choosing GACC should confirm "
        "they are placing a loved one specifically at the Muar location and ask directly "
        "about halal meal provision, language capabilities of care staff (Mandarin, Malay, "
        "English), and whether dedicated dementia-unit beds are currently available."
    ),
    'phone': '+60 6-952 7711',
    'website': 'https://gacc.com.my',
    'facebook': 'https://www.facebook.com/goldenagecc',
    'area': 'Muar, Johor',
    'pricing_display': 'Contact for rates',
    'care_dementia': 'yes',
    'care_rehab': 'yes',
    'care_nursing': 'yes',
    'medical_physio': 'yes',
    'ownership_type': 'Private',
    'visiting_hours': '9:00am – 6:00pm daily',
    'last_updated': TODAY,
},

'master-nursing-care-centre-daya': {
    'editorial_summary': (
        "Master Care Centre @Daya (MCC@Daya) is one of three branches operated by Master "
        "Care Centre (慈康护理中心), a private nursing home group with over a decade of "
        "presence in Johor Bahru. The Daya branch sits at 58–62, Jalan Nipah 14, in Taman "
        "Daya — a mature residential suburb in JB's Tebrau zone, roughly 10–12 km north of "
        "the city centre, served by Causeway Link bus T11. The group's website "
        "(masternursingcare.com) was offline during research, but third-party directory "
        "data confirms the group's core services: personalised elderly care, post-surgery "
        "recovery, stroke rehabilitation, physiotherapy, dementia care, and palliative care.\n\n"
        "The 5-star rating from only 4 reviews warrants caution. A perfect score on a very "
        "thin review base is statistically unreliable. MCC@Daya does not appear in the top-10 "
        "nursing home roundups circulating in JB, nor in the AGECOPE member directory. "
        "Contact for the Daya branch: Mr Kelvin (+60 11-1080 1805) or Ms Wawa "
        "(+60 11-1129 9791). The group also operates branches at HQ in Bandar JB and at "
        "Taman Abad — families should confirm which branch they are enquiring about.\n\n"
        "Pricing is not published on any platform; families must call for a quote. No JKM "
        "licence number has surfaced in public directories. Halal meal policy is unconfirmed "
        "despite Taman Daya being a multi-faith neighbourhood. A site visit remains the "
        "recommended first step, with particular attention to staffing levels, overnight "
        "nursing cover, and the condition of shared facilities given the limited review base."
    ),
    'phone': '+60 11-1080 1805',
    'website': 'https://www.masternursingcare.com',
    'facebook': 'https://www.facebook.com/carecentrejbmsia/',
    'area': 'Johor Bahru',
    'pricing_display': 'Contact for rates',
    'care_dementia': 'yes',
    'care_palliative': 'yes',
    'care_rehab': 'yes',
    'care_nursing': 'yes',
    'medical_physio': 'yes',
    'ownership_type': 'Private',
    'last_updated': TODAY,
},

'sunrise-care-centre-sdn-bhd': {
    'editorial_summary': (
        "Sunrise Care Centre Sdn Bhd (Co. 567396-U) is one of three facilities operated "
        "under the Rebina Sunrise Elderly Care group, a family-owned eldercare operator "
        "established in Johor Bahru in 2003. The group's founding mission was to address a "
        "critical shortage of reliable nursing care in the city, and it has since expanded to "
        "three locations clustered in and around Taman Kebun Teh. Sunrise Care Centre "
        "occupies No. 48 Jalan Keranji — directly adjacent to the original Rebina House "
        "Care Centre at Nos. 15 & 17 on the same road. The domain rebinasunrise.com serves "
        "all three entities under a shared group brand.\n\n"
        "Clinically, the group punches above its residential positioning. Confirmed services "
        "include CAPD peritoneal dialysis, Ryle's tube feeding and replacement, phlegm "
        "suction, nebuliser therapy, balloon catheter management, post-operative wound care, "
        "acupuncture, physiotherapy, blood pressure and glucose monitoring, and oxygen "
        "supply — a notably comprehensive list for a private nursing home. The group also "
        "offers palliative and hospice care, indicating acceptance of higher-dependency "
        "residents. Individualised nursing care plans with hourly schedules are a documented "
        "care standard.\n\n"
        "Pricing is not published on the group's website or third-party directories; families "
        "must call +60 7-333 7715 or email care@rebinasunrise.com for a quote. The facility "
        "has 3 Google reviews at 5 stars specifically for the Sunrise branch — the sister "
        "facility Rebina House has wider review coverage (4.8★). No JKM licence number is "
        "publicly visible. A home care arm (Rebina Sunrise Home Care Services Sdn Bhd) also "
        "operates from 112 Jalan Wijaya, Taman Abad."
    ),
    'phone': '+60 7-333 7715',
    'website': 'https://www.rebinasunrise.com/',
    'area': 'Johor Bahru',
    'pricing_display': 'Contact for rates',
    'care_palliative': 'yes',
    'care_rehab': 'yes',
    'care_nursing': 'yes',
    'medical_physio': 'yes',
    'medical_peg': 'yes',
    'medical_oxygen': 'yes',
    'medical_dialysis': 'yes',
    'medical_wound': 'yes',
    'ownership_type': 'Private',
    'last_updated': TODAY,
},

'lee-nursing': {
    'editorial_summary': (
        "Lee Nursing Home (李护理疗养院) is a small, Chinese family-run facility in Taman "
        "Nesa, Skudai, operating since 2011. Run by the How family — Mr Richard How handles "
        "administration while Mdm Lee (a nurse) leads clinical care — it positions itself as "
        "a round-the-clock nursing home rather than a simple old-folk shelter. Services are "
        "meaningfully clinical: Ryle's tube feeding, tracheal suctioning, catheter changes, "
        "wound care, vital-sign monitoring, and blood-glucose checks are all offered, "
        "alongside meals, personal hygiene, laundry, and transport to clinic or hospital "
        "appointments. The same management has since opened a second site — Hibiscus "
        "Serenity Care Centre in Larkin, JB — suggesting growing operational confidence.\n\n"
        "The facility's 3-star Google rating from just two reviews is a meaningful caution "
        "flag. Two reviews is too thin a sample to be statistically reliable, but a midpoint "
        "score indicates at least one reviewer had a poor or neutral experience. Neither the "
        "website (leenursinghome.com) nor any public directory publishes pricing; families "
        "must call or WhatsApp for a quote. No JKM licence number or Ministry of Health "
        "registration code has been publicly confirmed.\n\n"
        "Address inconsistencies across directories (No. 7, 11, and 26 appear against "
        "different street names in Taman Nesa) warrant direct verification before visiting. "
        "Visiting hours are 9am–12pm and 4pm–7pm daily. Families considering Lee Nursing "
        "Home should visit in person, ask for the JKM or MOH licence, confirm the current "
        "address, and weigh the below-average Google score against the clinical depth the "
        "home claims — including the same management team's track record at Hibiscus "
        "Serenity Care Centre."
    ),
    'phone': '+60 12-777 6673',
    'website': 'https://www.leenursinghome.com',
    'facebook': 'https://www.facebook.com/Lee-Nursing-Home-101030911675780',
    'area': 'Skudai, Johor Bahru',
    'pricing_display': 'Contact for rates',
    'care_nursing': 'yes',
    'care_rehab': 'yes',
    'care_respite': 'yes',
    'rn_24_7': 'yes',
    'doctor_visits': 'yes',
    'medical_physio': 'yes',
    'medical_wound': 'yes',
    'medical_peg': 'yes',
    'visiting_hours': '9am–12pm and 4pm–7pm daily',
    'ownership_type': 'Private',
    'last_updated': TODAY,
},

}

# ---------------------------------------------------------------------------
updates = []
found_slugs = set()

for i, row in enumerate(fac_data[1:], start=2):
    if not row or slug_i >= len(row):
        continue
    slug = row[slug_i].strip()
    if slug not in UPDATES:
        continue
    found_slugs.add(slug)
    fields = UPDATES[slug]
    print(f"  → Queuing updates for [{slug}] at row {i}")
    for field, value in fields.items():
        col_i = h(field)
        if col_i is not None:
            updates.append({
                'range': f"'{FAC_TAB}'!{col_letter(col_i+1)}{i}",
                'values': [[value]]
            })
        else:
            print(f"    WARNING: column '{field}' not found in headers")

for slug in UPDATES:
    if slug not in found_slugs:
        print(f"  ⚠️  Slug NOT FOUND in sheet: {slug}")

if updates:
    for start in range(0, len(updates), 100):
        batch = updates[start:start+100]
        ss.values().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={'valueInputOption': 'RAW', 'data': batch}
        ).execute()
    print(f"\n✅ Done — {len(updates)} cell updates applied across {len(found_slugs)} facilities.")
else:
    print("No updates executed.")
