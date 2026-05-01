"""
Batch update editorial_summary + key fields for 8 facilities researched in session 5:
- EHA Golfview, Lakeview, Sunview, Kluang (branch-specific editorials replacing generic ones)
- Alda Homes Eldercare
- Agape Care Centre
- Blissful Senior Care Centre (Kluang)
- Pusat Jagaan Kebajikan Manna Sinar Cahaya
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

# ---------------------------------------------------------------------------
# Data payload — {slug: {field: value, ...}}
# ---------------------------------------------------------------------------
TODAY = str(date.today())

UPDATES = {

'eha-golfview-eldercare-mansion-johor-jaya-1-nursing-home-joh': {
    'editorial_summary': (
        "EHA Golfview Eldercare Mansion occupies a distinctive position within Johor Jaya's "
        "residential landscape, set within the Daiman 18 Golf Club precinct where residents "
        "benefit from a low-density, green-and-open environment rare for urban nursing homes. "
        "The Golfview branch is EHA's most-reviewed Johor location with 70 Google reviews and "
        "a 4.9-star rating, reflecting a sustained track record rather than a newly-opened "
        "facility flush. Reviewers consistently highlight staff attentiveness and the "
        "facility's particular strength in post-surgery and post-stroke recovery care.\n\n"
        "Clinically, Golfview operates under EHA's group-wide Focused-Care model, combining "
        "standard nursing care with physiotherapy, special nursing procedures (NGT, catheter, "
        "stoma, tracheostomy), and Traditional Chinese Medicine (acupuncture, herbal). "
        "Pricing sits at RM 3,200/month for assisted living, with respite care at RM 120/day "
        "and day care at RM 1,500/month — mid-range for the JB private market. Inclusions "
        "cover meals, housekeeping, Wi-Fi, utilities, vital signs monitoring, and all ADL "
        "assistance.\n\n"
        "The primary gaps for prospective families are the absence of published JKM licence "
        "details, room-type breakdowns, and nurse-to-resident ratios. The golf-adjacent "
        "environment makes Golfview attractive for mobile or semi-mobile residents who benefit "
        "from landscaped walking space, but families of bed-bound residents should verify "
        "room configuration and whether specialist nursing is resident on-site overnight."
    ),
    'phone': '+60197283697',
    'website': 'https://ehaeldercare.com.my/our-locations/eha-golfview-eldercare-mansion-johor-jaya/',
    'facebook': 'https://www.facebook.com/ehaeldercarejb/',
    'pricing_display': 'From RM 3,200/mo',
    'care_assisted': 'yes',
    'care_dementia': 'yes',
    'care_rehab': 'yes',
    'care_respite': 'yes',
    'care_nursing': 'yes',
    'doctor_visits': 'yes',
    'medical_physio': 'yes',
    'ownership_type': 'Private',
    'last_updated': TODAY,
},

'eha-lakeview-eldercare-mansion-permas-branch-1-nursing-home': {
    'editorial_summary': (
        "EHA Lakeview Eldercare Mansion occupies a lakeside position in Taman Bayu Puteri, "
        "Permas Jaya, and has earned a 'Most Beautiful Elderly Care Mansion' award — an "
        "accolade that aligns with reviewer descriptions of an unusually attractive physical "
        "environment. The lake aspect and greenery appear to function as genuine therapeutic "
        "assets, with multiple reviewers citing the tranquil setting as meaningful to their "
        "family member's wellbeing. At 4.9-star across 40 Google reviews, Lakeview sits "
        "alongside EHA Golfview as the group's highest-rated Johor branches.\n\n"
        "The branch carries all group-wide clinical capabilities: 24/7 caregiver cover, "
        "special nursing procedures (NGT, catheter, stoma, tracheostomy), wound management, "
        "physiotherapy, Traditional Chinese Medicine, and dementia care. Pricing is consistent "
        "with the JB group rate of RM 3,200/month for assisted living, RM 120/day for respite, "
        "and RM 1,500/month for day care. All inclusions — meals, utilities, Wi-Fi, "
        "housekeeping, and ADL assistance — are covered in the monthly rate.\n\n"
        "Permas Jaya's more established infrastructure provides good access to private "
        "hospitals and commercial services, making Lakeview a reasonable choice for families "
        "visiting frequently from eastern JB. Families should request the JKM licence "
        "certificate on-site, confirm RN night coverage, and ask for room-type availability "
        "before committing to placement."
    ),
    'phone': '+60197281686',
    'website': 'https://ehaeldercare.com.my/our-locations/eha-lakeview-eldercare-mansion-permas-jaya/',
    'facebook': 'https://www.facebook.com/ehaeldercarejb/',
    'pricing_display': 'From RM 3,200/mo',
    'care_assisted': 'yes',
    'care_dementia': 'yes',
    'care_rehab': 'yes',
    'care_respite': 'yes',
    'care_nursing': 'yes',
    'doctor_visits': 'yes',
    'medical_physio': 'yes',
    'ownership_type': 'Private',
    'last_updated': TODAY,
},

'eha-sunview-eldercare-kempas-1-nursing-home-johor-bahru': {
    'editorial_summary': (
        "EHA Sunview ElderCare in Kempas is EHA's newest Johor Bahru branch and markets "
        "itself as Malaysia's first theme-styled therapeutic villa — a concept borrowed from "
        "Taiwanese eldercare design that uses environmental theming to reduce cognitive "
        "disorientation and support residents' sense of identity. With a 5.0-star rating "
        "from 24 Google reviews and fully automatic medical beds and on-site rehabilitation "
        "equipment highlighted at launch, Sunview represents EHA's most premium and "
        "intentional build to date in the JB market.\n\n"
        "The clinical and care service model is consistent with the EHA group standard — "
        "24/7 caregiver cover, special nursing procedures, physiotherapy, Traditional Chinese "
        "Medicine, and dementia care. Launch materials make stronger staffing claims, "
        "specifically that doctors, nurses, and physiotherapists are available 24/7, which "
        "families should verify against current rostering during a visit. Pricing is "
        "RM 3,200/month for assisted living, RM 120/day for respite, and RM 1,500/month "
        "for day care, with all standard inclusions.\n\n"
        "As EHA's newest branch, Sunview has the thinnest track record in the network — "
        "24 reviews is credible but modest compared to Golfview's 70. The Kempas location "
        "is less established than Johor Jaya or Permas Jaya. For families seeking a newer "
        "facility with modern equipment and the themed villa concept, Sunview is the most "
        "differentiated branch in the EHA network; families with high-dependency relatives "
        "may want to wait for a longer operational track record."
    ),
    'phone': '+60187881686',
    'website': 'https://ehaeldercare.com.my/eha-sunview-eldercare-kempas/',
    'facebook': 'https://www.facebook.com/ehasunview/',
    'pricing_display': 'From RM 3,200/mo',
    'care_assisted': 'yes',
    'care_dementia': 'yes',
    'care_rehab': 'yes',
    'care_respite': 'yes',
    'care_nursing': 'yes',
    'doctor_visits': 'yes',
    'medical_physio': 'yes',
    'ownership_type': 'Private',
    'last_updated': TODAY,
},

'eha-elder-care-home-kluang-licensed-and-certified-by-govern': {
    'editorial_summary': (
        "EHA Elder Care Home in Kluang occupies a distinct niche within the EHA network as "
        "the group's value-tier offering and its only non-JB Johor location. At RM 2,300/month "
        "for assisted living — 28% below the JB group rate — Kluang is the only EHA branch "
        "accessible to middle-income families in the Kluang-Batu Pahat-Yong Peng corridor. "
        "Reviewers specifically cite the cost advantage, with one noting it is 'more than 30% "
        "cheaper than Johor Bahru even though the service standard is higher than most nursing "
        "homes in JB.' The 5.0-star rating across 33 reviews reflects consistent family "
        "satisfaction.\n\n"
        "The branch carries all EHA group clinical capabilities: special nursing procedures "
        "(NGT, catheter, stoma, tracheostomy), wound care, physiotherapy, TCM, and dementia "
        "care. A distinctive feature in reviews is the owner-accountability pattern — "
        "multiple reviewers praise the 'responsible and passionate' management by name, "
        "suggesting a more hands-on owner-operated style than the JB corporate branches. "
        "Respite care is available at RM 80/day and day care at RM 1,300/month.\n\n"
        "The Kluang location does carry trade-offs: the nearest specialist private hospital "
        "(KPJ Kluang) is in-town but limited compared to JB's hospital cluster, and major "
        "specialist care requires ~100 km transfer to JB. For medically stable residents "
        "needing personal care and supervision, this is not a barrier. This branch is "
        "well-suited for Kluang-based families keeping relatives near home, and for JB "
        "families seeking more affordable placement where geography is secondary."
    ),
    'phone': '+60197133697',
    'website': 'https://ehaeldercare.com.my/our-locations/eha-eldercare-home-kluang-johor/',
    'facebook': 'https://www.facebook.com/ehakluang/',
    'pricing_display': 'From RM 2,300/mo',
    'area': 'Kluang, Johor',
    'care_assisted': 'yes',
    'care_dementia': 'yes',
    'care_rehab': 'yes',
    'care_respite': 'yes',
    'care_nursing': 'yes',
    'doctor_visits': 'yes',
    'medical_physio': 'yes',
    'ownership_type': 'Private',
    'last_updated': TODAY,
},

'alda-homes-eldercare': {
    'editorial_summary': (
        "Alda Homes Eldercare has been caring for elderly residents in the heart of Johor "
        "Bahru since 2016, operating from a converted residential property in Taman Abad — "
        "a central, accessible neighbourhood within easy reach of the city's hospitals and "
        "amenities. Positioning itself around personalised, home-like care rather than a "
        "clinical or institutional model, the facility suits lower-dependency residents who "
        "would thrive in a small-scale, family-run environment rather than a large "
        "purpose-built centre. Its active social media presence, featuring group exercise "
        "sessions and community events, suggests a genuine commitment to resident wellbeing "
        "beyond basic physical care.\n\n"
        "The facility's key limitation for families conducting online research is a near-total "
        "absence of digital transparency. Its website domain is unreachable, its three Facebook "
        "pages create confusion about the canonical contact channel, and no pricing, staffing "
        "ratios, clinical capabilities, or JKM licence number have been disclosed publicly. "
        "Alda Homes does not appear in the AGECOPE Johor member directory, and has accumulated "
        "only 11 Google reviews in nearly a decade of operation.\n\n"
        "For a low-to-moderate dependency resident who needs a warm, central JB placement "
        "rather than high-acuity nursing, Alda Homes is worth a site visit. Pricing is "
        "unconfirmed but expected to be broadly mid-market for JB central. Prospective "
        "families should verify the JKM licence on-site, confirm RN coverage for both day "
        "and night shifts, and establish a clear communication protocol with the operator "
        "before committing to placement."
    ),
    'phone': '+60127238157',
    'whatsapp': '+60107128260',
    'facebook': 'https://www.facebook.com/aldahomeseldercare',
    'area': 'Johor Bahru',
    'pricing_display': 'Contact for rates',
    'ownership_type': 'Private',
    'last_updated': TODAY,
},

'agape-care-centre': {
    'editorial_summary': (
        "Agape Care Centre sits quietly on Jalan Lurah 18 in Kempas Baru — a residential "
        "street that has become one of Johor Bahru's most recognisable care home clusters, "
        "home also to Woon Ho Family Care Centre and Spring Valley Homecare. At No. 62, this "
        "small facility operates as both a nursing home and a retirement home, catering to "
        "elderly who need daily assistance rather than intensive clinical intervention. With a "
        "4.6-star Google rating from five reviewers, it carries an excellent word-of-mouth "
        "reputation within what appears to be a tight-knit referral circle.\n\n"
        "The name 'Agape' — Greek for unconditional love, central to Christian theology — "
        "strongly suggests faith-inspired ownership or management, placing Agape Care Centre "
        "in the tradition of church-affiliated elderly care. For Christian residents or those "
        "whose families are embedded in a Christian community, this setting may offer "
        "something most commercial nursing homes do not: a genuine sense of belonging, "
        "pastoral companionship, and a value system that treats care as vocation. Whether "
        "this translates to organised chapel sessions, church volunteer visits, or informal "
        "devotional culture is something families should ask directly.\n\n"
        "Agape Care Centre has no confirmed website, no publicly available pricing, no JKM "
        "licence number in any accessible registry, and no detailed clinical services list. "
        "This level of opacity is not unusual for a small referral-based care home in "
        "Malaysia, but it means families cannot evaluate this facility without a phone call "
        "and a site visit. Before placement, the JKM licence must be verified, clinical "
        "capabilities assessed against the resident's medical needs, and the nature of any "
        "religious programming clarified for non-Christian families."
    ),
    'phone': '+60 7-238 6880',
    'area': 'Kempas Baru, Johor Bahru',
    'pricing_display': 'Contact for rates',
    'ownership_type': 'Private',
    'last_updated': TODAY,
},

'blissful-senior-care-centre-licensed-and-certified-by-gover': {
    'editorial_summary': (
        "Blissful Senior Care Centre is one of Kluang's licensed residential care options "
        "for older adults, operating in a town of 323,000 people in central Johor — roughly "
        "100 km north of Johor Bahru and positioned as a more affordable alternative to the "
        "saturated urban eldercare market. The facility's emphasis on government licensing "
        "and certification, carried prominently in its name and description, signals a "
        "deliberate positioning against the unlicensed care homes that continue to operate "
        "across peninsular Malaysia's smaller towns. With two well-equipped hospitals in "
        "Kluang itself — the government Hospital Enche' Besar Hajjah Khalsom (MSQH-accredited) "
        "and the private KPJ Kluang Specialist Hospital (JCI and MSQH accredited) — residents "
        "requiring acute care have reliable access without lengthy transfers.\n\n"
        "The 4.8-star rating drawn from 22 Google reviews is the facility's most telling "
        "public signal. For a care home in a secondary Malaysian town, 22 reviews represents "
        "genuine community engagement, and a 4.8 average at that sample size almost certainly "
        "reflects authentic positive family experiences. Malaysian eldercare review patterns "
        "consistently reward facilities where staff warmth, cleanliness, food quality, and "
        "responsive family communication converge — traits that small, owner-operated care "
        "homes in towns like Kluang sometimes deliver more consistently than larger "
        "corporatised urban facilities.\n\n"
        "What limits this profile is entirely a data gap, not a performance concern. Blissful "
        "operates without any public web presence beyond its Google Business listing — no "
        "website, no indexed Facebook page, no published pricing. Pricing, clinical "
        "capabilities, room configurations, and staffing levels all require a direct call "
        "to the facility. Once pricing and clinical scope are confirmed, this facility has "
        "the hallmarks of a credible, community-trusted home in an underserved market."
    ),
    'area': 'Kluang, Johor',
    'pricing_display': 'Contact for rates',
    'ownership_type': 'Private',
    'last_updated': TODAY,
},

'pusat-jagaan-kebajikan-manna-sinar-cahaya': {
    'editorial_summary': (
        "Pusat Jagaan Kebajikan Manna Sinar Cahaya sits in a distinct segment of Johor "
        "Bahru's elder-care landscape — the welfare home sector — that serves clients who "
        "cannot access or afford the city's growing private nursing home industry. The name "
        "itself signals its positioning: 'Manna' is a Biblical reference found almost "
        "exclusively in Christian charity branding in Malaysia, while 'Kebajikan' (welfare) "
        "signals a social-care rather than commercial orientation. Families considering this "
        "facility should understand they are not comparing it against private nursing homes "
        "charging RM 2,000–5,000 per month; they are comparing it against other welfare "
        "homes where care is donation-subsidised, JKM-referred, and focused on shelter and "
        "basic daily support rather than clinical nursing.\n\n"
        "The facility has a minimal digital footprint — no website, no social media presence, "
        "and no listing in the major NGO or JKM directories accessible online — which is not "
        "unusual for small Christian welfare homes in Malaysia but does mean families must "
        "make direct contact and conduct in-person visits to assess quality. Its Google "
        "rating of 3.9 stars from just 7 reviews provides a weak signal; with so few "
        "reviewers, the score could reflect one or two dissatisfied family members rather "
        "than a systemic pattern.\n\n"
        "For families seeking an affordable long-term placement for an elderly relative who "
        "is financially disadvantaged, ambulatory or minimally dependent, and comfortable "
        "in a Christian environment, this facility warrants investigation through JKM Johor "
        "Bahru's referral process. Families should request to see the facility's JKM "
        "registration certificate, visit in person, and ask specifically about the monthly "
        "fee, staff roster, and emergency medical arrangements before committing. For "
        "high-dependency care — ventilator, PEG, dementia unit, post-surgical recovery — "
        "this type of welfare home is not the right fit."
    ),
    'area': 'Johor Bahru',
    'pricing_display': 'Contact for rates (welfare/JKM subsidy likely)',
    'ownership_type': 'NGO / Welfare charity',
    'religion': 'Christian (probable)',
    'subsidy': 'yes',
    'last_updated': TODAY,
},

}

# ---------------------------------------------------------------------------
# Execute updates
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

# Report slugs not found in sheet
for slug in UPDATES:
    if slug not in found_slugs:
        print(f"  ⚠️  Slug NOT FOUND in sheet: {slug}")

if updates:
    # Execute in batches of 100
    for start in range(0, len(updates), 100):
        batch = updates[start:start+100]
        ss.values().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={'valueInputOption': 'RAW', 'data': batch}
        ).execute()
    print(f"\n✅ Done — {len(updates)} cell updates applied across {len(found_slugs)} facilities.")
else:
    print("No updates executed.")
