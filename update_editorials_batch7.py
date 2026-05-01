"""
Batch update editorial_summary + key fields for 9 remaining facilities:
AX Nursing Home, Elim Batu Pahat, Healthlife, Parit Bilal, Impian Syimah Kemaman,
Ren Ai Senai, Yeo JB, Hang Gelang Patah, Yang Xin
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

'ax-nursing-home-plt': {
    'editorial_summary': (
        "AX Nursing Home PLT is a small, privately-owned nursing care facility in Johor "
        "Bahru, registered under Malaysia's Limited Liability Partnership (PLT) structure — "
        "a commercially oriented entity used by small-to-medium businesses. Its online "
        "presence is confined to a Facebook page (axnursinghome) and a Google Business "
        "listing, with no independent website, and it does not appear in any published "
        "'top nursing homes in JB' roundup or major directory.\n\n"
        "A Google rating of 3 stars from only 2 reviews signals a facility in an early "
        "or underpublicised stage: it is neither well-rated nor widely reviewed, and "
        "families researching online will find little to go on. No verified address, "
        "pricing, bed count, or clinical capability has been found in any public source. "
        "For-profit PLT registration indicates commercial intent; families should confirm "
        "whether nursing care or basic residential care is the primary offer.\n\n"
        "Prospective families should call +60 11-5999 9905 directly and ask for the "
        "JKM licence number to confirm the home's regulatory standing. Given the below-"
        "average rating on very thin review data, a site visit and verification of "
        "current residents' families' experiences is strongly recommended before any "
        "placement decision."
    ),
    'phone': '+60 11-5999 9905',
    'facebook': 'https://www.facebook.com/axnursinghome',
    'area': 'Johor Bahru',
    'pricing_display': 'Contact for rates',
    'ownership_type': 'Private (PLT)',
    'last_updated': TODAY,
},

'elim-nursing-home-batu-pahat': {
    'editorial_summary': (
        "Elim Nursing Home Batu Pahat operates under the Chinese name 冠冕疗养院 — "
        "'Crown Nursing Home' — with 冠冕 (guānmiǎn) being a distinctly Biblical Chinese "
        "term meaning 'crown of glory,' strongly suggesting Christian faith-based "
        "governance. 'Elim' itself is a Biblical place name (Exodus 15:27), further "
        "reinforcing a likely church-ministry or Christian NGO origin. Batu Pahat, roughly "
        "100 km northwest of Johor Bahru, is a mid-sized town with a smaller pool of "
        "specialist nursing homes; the local market is served by a handful of private "
        "facilities and KPJ Batu Pahat Specialist Hospital for acute care.\n\n"
        "The home's Google rating of 3 stars from 2 reviews yields no meaningful quality "
        "signal. No verified street address, bed count, pricing, or detailed care capability "
        "has been confirmed through any public directory or website. Families considering "
        "this home — particularly Chinese-Christian families in Batu Pahat — should "
        "call +60 11-1079 1685 for the address, visiting hours, and pricing.\n\n"
        "Before placement, families should ask about the home's church affiliation, "
        "JKM or MOH licence status, staffing ratios, and whether dietary requirements "
        "can be accommodated for non-Christian residents. A site visit is essential "
        "given the very limited available data on this facility."
    ),
    'phone': '+60 11-1079 1685',
    'facebook': 'https://www.facebook.com/elimnursinghomebp',
    'area': 'Batu Pahat, Johor',
    'pricing_display': 'Contact for rates',
    'ownership_type': 'Private (likely Christian NGO or sole proprietorship)',
    'religion': 'Christian (indicated by name; unverified)',
    'last_updated': TODAY,
},

'healthlife-old-folks-home': {
    'editorial_summary': (
        "Healthlife Old Folks Home operates from a shophouse unit on Jalan Haji Basir "
        "in Taman Limpoon, along the Jalan Kluang corridor in Batu Pahat, Johor. The "
        "facility's online presence links to a Yolasite website and Facebook page under "
        "the Chinese name 爱心疗养中心 (Ai Xin Liao Yang Zhong Xin — Love Heart Care "
        "Centre), strongly suggesting it is run by and for Batu Pahat's Chinese-speaking "
        "community. The name pairing of 'Healthlife' (English) with 爱心疗养中心 (Chinese) "
        "is a common pattern among Chinese-community care homes in Johor that serve a "
        "Mandarin- or dialect-speaking clientele.\n\n"
        "Online footprint is very thin: one Google review (5 star), a basic directory "
        "entry at No. 85-4, Jalan Haji Basir, and a Waze pin. No pricing, bed count, "
        "or clinical capability data is publicly available. The likely care model is "
        "basic custodial and assisted-living care rather than high-dependency nursing, "
        "consistent with small Chinese-community care homes in Johor's secondary towns.\n\n"
        "Families considering this home should contact directly by phone or WhatsApp "
        "(+60 19-769 9129) to verify current capacity, fees, and care capabilities. "
        "Ask about nursing qualifications of staff, JKM registration status, and "
        "whether Mandarin-speaking staff are on duty 24 hours. A site visit is the "
        "essential next step given the minimal available data."
    ),
    'phone': '+60 19-769 9129',
    'website': 'http://www.aixinliauyang.yolasite.com/',
    'facebook': 'https://www.facebook.com/AiXinLiaoYangZhongXin',
    'area': 'Batu Pahat, Johor',
    'pricing_display': 'Contact for rates',
    'ownership_type': 'Private',
    'last_updated': TODAY,
},

'pusat-jagaan-wargatua-parit-bilal': {
    'editorial_summary': (
        "Pusat Jagaan Wargatua Parit Bilal is a small elderly care centre situated in "
        "Parit Bilal, a rural township roughly 15 km north of Batu Pahat town in Johor. "
        "The postal address is POS 8A, Jalan Batu 3, Parit Bilal — a rural road address "
        "typical of Batu Pahat district's agricultural-belt villages. The name uses "
        "'Wargatua' (elderly citizens) rather than the more common 'Warga Emas' (golden "
        "citizens), suggesting a community-oriented, likely Malay-Muslim home consistent "
        "with the demographic character of Parit Bilal's rural population.\n\n"
        "The Facebook page (ID 100063647223251) has approximately 356 likes and 46 "
        "check-ins, indicating modest but active local engagement — a sign the facility "
        "is genuinely operational and known in its community. No pricing, bed count, "
        "clinical data, or formal ownership structure has been confirmed online. Given "
        "its welfare-style naming convention and rural location, this home may operate "
        "as a private welfare facility or community pertubuhan (society) rather than a "
        "commercial nursing home, and may accept JKM-referred or subsidised residents.\n\n"
        "Families should call +60 11-1682 6865 directly. Parit Bilal is served by "
        "Klinik Kesihatan Parit Bilal for basic primary healthcare referrals. Ask about "
        "JKM registration status, gender policy, visiting hours, and monthly fees before "
        "committing to placement."
    ),
    'phone': '+60 11-1682 6865',
    'facebook': 'https://www.facebook.com/profile.php?id=100063647223251',
    'area': 'Batu Pahat, Johor',
    'pricing_display': 'Contact for rates',
    'ownership_type': 'Private / welfare (unconfirmed)',
    'religion': 'Islam (inferred from rural Malay-Muslim community)',
    'last_updated': TODAY,
},

'pusat-jagaan-impian-syimah-jalan-kemaman': {
    'editorial_summary': (
        "Pusat Jagaan Impian Syimah (Jalan Kemaman) is the second residential branch of "
        "the Impian Syimah operator in Johor Bahru, running alongside the established "
        "Jalan Kemuncak branch in Kampung Nong Chik. The Jalan Kemaman branch is located "
        "at Lot 1818, No. 7, Jalan Kemaman, Kampung Tarom, 80100 JB — a kampung-belt "
        "address in the older residential fabric of JB, about 3 km west of the city "
        "centre. Both branches share a single phone number, email address, and Facebook "
        "page (PusatJagaanImpianSyimah), indicating a single-operator model.\n\n"
        "The Impian Syimah operator (SSM reg. JM0635898-M, incorporated 2012) has been "
        "documented housing up to 75 residents and caretakers across its locations, "
        "including 23 bedridden residents. It has attracted CSR visits from Sunway Group "
        "(Ramadan 2026) and Lalamove's 'Deliver Care' programme, pointing to community-"
        "welfare orientation. This is primarily a Malay-Muslim care home serving "
        "moderate-dependency elderly residents in the kampung JB catchment.\n\n"
        "No published pricing has been found. The care model focuses on residential "
        "custodial and basic nursing care. Families should call the shared line "
        "(+60 13-750 7134) and ask specifically about the Jalan Kemaman branch's current "
        "capacity, as the operator runs two sites. Verify the JKM licence number for "
        "this branch separately from the Kemuncak location."
    ),
    'phone': '+60 13-750 7134',
    'facebook': 'https://www.facebook.com/PusatJagaanImpianSyimah',
    'area': 'Johor Bahru',
    'pricing_display': 'Contact for rates',
    'care_assisted': 'yes',
    'care_nursing': 'yes',
    'ownership_type': 'Private',
    'religion': 'Islam',
    'halal': 'yes',
    'last_updated': TODAY,
},

'pusat-perjagaan-orang-tua-ren-ai': {
    'editorial_summary': (
        "Pusat Perjagaan Orang Tua Ren Ai operates in the Senai township within Kulai "
        "District, Johor — an area near Senai International Airport, midway between Kulai "
        "town and central Johor Bahru. The name 'Ren Ai' (仁爱, benevolence and love) and "
        "its Facebook handle RenAiSenai indicate a Chinese-community welfare orientation, "
        "likely Buddhist or non-denominational Chinese charitable in character, consistent "
        "with the tradition of self-help elderly care associations common to Johor's "
        "Chinese townships.\n\n"
        "Online presence is extremely limited: the Facebook page confirms the Senai "
        "location, but the facility does not appear in any major Malaysian nursing home "
        "directories including AGECOPE, ielder.asia, nursinghome.my, or Homage. No "
        "address, bed count, pricing, or JKM licence number could be confirmed. This "
        "is a zero-review, minimal-web-presence facility — indicating either a new "
        "operation, a primarily word-of-mouth referral base within the Chinese community, "
        "or a very small facility that has not engaged with digital platforms.\n\n"
        "Prospective families should call +60 7-599 1944 directly and verify JKM "
        "registration before committing to a visit. Confirm the exact address in Senai, "
        "the care model offered (nursing vs residential), language capabilities of staff "
        "(likely Mandarin/Cantonese), and current bed availability."
    ),
    'phone': '+60 7-599 1944',
    'facebook': 'https://www.facebook.com/RenAiSenai/',
    'area': 'Senai, Kulai, Johor',
    'pricing_display': 'Contact for rates',
    'ownership_type': 'Unknown — likely NGO/welfare association',
    'last_updated': TODAY,
},

'pusat-jagaan-orang-tua-yeo-jb': {
    'editorial_summary': (
        "Pusat Jagaan Orang Tua Yeo JB is a family-operated care home in Johor Bahru, "
        "identifiable by the Facebook page at gracehome.yeo and associated with a "
        "proprietor surnamed Yeo. The 'Grace Home' Facebook brand suggests either a "
        "Christian-leaning ethos or simply a name chosen by the Yeo family. Two different "
        "addresses surface in public data — Stulang Darat (80300 JB) and Taman Bukit "
        "Kempas (81200 JB) — suggesting the facility may have relocated or that one "
        "source holds stale data.\n\n"
        "The facility carries zero Google reviews and is absent from all major nursing "
        "home directories. No service details, pricing, bed count, or JKM registration "
        "status could be confirmed from available online sources. Family-operated care "
        "homes in JB can offer warm, personalised care in a home-like setting, but the "
        "complete absence of digital presence and verifiable regulatory information means "
        "families cannot conduct any meaningful remote assessment.\n\n"
        "A phone call to +60 16-717 3127 and a site visit are the only reliable ways to "
        "verify the current address, services, and licensing status. Ask specifically "
        "which address is current, request sight of the JKM licence on arrival, "
        "and speak with the proprietor Mr/Ms Yeo about staffing model and care levels."
    ),
    'phone': '+60 16-717 3127',
    'facebook': 'https://www.facebook.com/gracehome.yeo',
    'area': 'Johor Bahru',
    'pricing_display': 'Contact for rates',
    'ownership_type': 'Private (family-operated)',
    'last_updated': TODAY,
},

'hang-nursing-home-gelang-patah-branch': {
    'editorial_summary': (
        "Hang Nursing Home operates at least one branch in the Gelang Patah area of "
        "western Johor Bahru, near the Second Link causeway — a district that has expanded "
        "rapidly with Iskandar Malaysia development and carries a substantial Chinese-"
        "Malaysian residential population. The Facebook page at pusatjagaanhang confirms "
        "the facility exists; the 'branch' designation in available data implies at least "
        "one other location exists, though no other branch could be identified online. "
        "The contact number is +60 12-766 0927.\n\n"
        "No address, services breakdown, bed count, pricing, or JKM licence number was "
        "retrievable from online sources. The name 'Hang' is most plausibly a Chinese "
        "family surname, and the operator is likely a small family business serving "
        "the local Gelang Patah community. Hang Nursing Home does not appear in AGECOPE, "
        "ielder.asia, nursinghome.my, or any directory article reviewed, and carries "
        "zero Google reviews.\n\n"
        "Families should call ahead for directions, confirm which branch they are "
        "visiting, and request sight of the JKM licence certificate on arrival. Gelang "
        "Patah's rapid development means there may be limited competing care options "
        "in the immediate area, making this a local-community option worth investigating "
        "for families resident in the western JB corridor."
    ),
    'phone': '+60 12-766 0927',
    'facebook': 'https://m.facebook.com/pusatjagaanhang/',
    'area': 'Gelang Patah, Johor Bahru',
    'pricing_display': 'Contact for rates',
    'ownership_type': 'Private (likely family-operated)',
    'last_updated': TODAY,
},

'yang-xin-nursing-home': {
    'editorial_summary': (
        "Yang Xin Nursing Home is a Chinese-operated elderly care facility in Johor Bahru, "
        "identified on Facebook under the Chinese name 养心托管安老院 (Yǎng Xīn Tuōguǎn "
        "Ān Lǎo Yuàn). The full name translates as 'Yang Xin Full-Care Elderly Home' — "
        "'养心' means 'nourishing the heart and mind,' while '托管' (tuoguan) specifically "
        "denotes full-custody residential care rather than day care, indicating the "
        "facility provides 24-hour residential placement. The Chinese locale setting on "
        "the Facebook profile and the full Chinese name confirm this is a Chinese-medium "
        "environment, likely serving Mandarin or Cantonese-speaking families in JB.\n\n"
        "The high Facebook profile ID range suggests the page was created after mid-2022, "
        "consistent with a newer or recently registered facility. No street address, "
        "Google reviews, pricing, or JKM registration details have been confirmed from "
        "online sources. The facility is absent from all major Malaysian nursing home "
        "directories reviewed.\n\n"
        "Given the recency and minimal web footprint, families should call "
        "+60 16-768 6682 to confirm operating status, pricing, and care capabilities. "
        "Request JKM registration details and ask for a site visit before any placement "
        "decision. Ask specifically whether Mandarin-speaking nursing staff are available "
        "24 hours, and what clinical services are provided beyond basic residential care."
    ),
    'phone': '+60 16-768 6682',
    'facebook': 'https://www.facebook.com/profile.php?id=100084633097437',
    'area': 'Johor Bahru',
    'pricing_display': 'Contact for rates',
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
