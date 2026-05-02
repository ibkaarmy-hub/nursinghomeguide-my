"""
Apply 2026-05-02 editorial revision rules across remaining 7 EHA Eldercare branches:
  Lakeview, Parkview Perling (long+short slug), Sunview, Kluang,
  Grandview Titiwangsa, Grandview Kepong, Bayview.

Pricing source: https://ehaeldercare.com.my/our-packages/
  JB & KL bracket : Assisted from RM 3,200/mo | Respite from RM 120/day | Day Care from RM 1,500/mo
  Kluang         : Assisted from RM 2,300/mo | Respite from  RM 80/day | Day Care from RM 1,300/mo

Per-row work:
  - Rewrite editorial_summary (no contact info; operator-website services; real
    pricing with "starting from" caveat; no JKM push; no clinical jargon).
  - Clear shared_price; set private_price to bracket headline; set
    pricing_display to "From RM X/mo".
  - Update last_updated.

Details tab work:
  - Relabel existing `rooms` rows to "(from RM/...)" where they exist.
  - Append `rooms`/`policies` baseline rows for branches with 0 Details rows
    (Grandview Titiwangsa, Grandview Kepong, Bayview, Parkview-long).
  - Append `Pricing source` row everywhere (idempotent, skips dupes).

The duplicate short-slug 'eha-parkview-eldercare-perling' gets the same
editorial as the long slug; its broken Details rows are left untouched and
flagged in the final report.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import date

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE    = 'token_sheets.json'
SCOPES        = ['https://www.googleapis.com/auth/spreadsheets']
FAC_TAB       = 'google-sheets-facilities.csv'
DETAILS_TAB   = 'Details'

creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
service = build('sheets', 'v4', credentials=creds)
ss = service.spreadsheets()

TODAY = str(date.today())

# ─────────────────────────────────────────────────────────────────────────────
# Universal paragraph-2 templates (services + pricing) — pulled from operator site
# ─────────────────────────────────────────────────────────────────────────────
SERVICES_LINE = (
    "The group's website lists eight published service categories that apply "
    "across branches: medical support, nutrition and diet, rehabilitation by "
    "physiotherapy, social activities, caregiver training and support, skilled "
    "nurses, special nursing procedures, and a traditional Chinese medicine "
    "approach (acupuncture and herbal). Pricing is published on EHA's website "
    "(ehaeldercare.com.my/our-packages/) and is quoted as a starting point — "
    "actual fees vary with the resident's care needs."
)
JBKL_PRICING = (
    "For the Johor Bahru and Klang Valley branches (which include this one), "
    "assisted senior living starts at RM 3,200/month for 24-hour residential "
    "care across able-bodied, semi-able-bodied, and bed-bound residents; "
    "respite stays of one to six months start at RM 120/day; and day care, "
    "available 11 hours a day across five days a week with flexible timing, "
    "starts at RM 1,500/month. The Kluang branch is priced lower (assisted "
    "from RM 2,300/month, respite from RM 80/day, day care from RM 1,300/"
    "month) — useful context if the family can travel and cost is a major "
    "factor. Bed count and current room availability are not published online."
)
KLUANG_PRICING = (
    "Kluang is EHA's only value-tier branch and its only non-JB Johor "
    "location. Assisted senior living starts at RM 2,300/month — roughly 28% "
    "below the JB and Klang Valley group rate of RM 3,200/month — for "
    "24-hour residential care across able-bodied, semi-able-bodied, and "
    "bed-bound residents. Respite stays of one to six months start at "
    "RM 80/day, and day care, available 11 hours a day across five days a "
    "week with flexible timing, starts at RM 1,300/month. Bed count and "
    "current room availability are not published online."
)
JBKL_P2 = SERVICES_LINE + " " + JBKL_PRICING
KLU_P2  = SERVICES_LINE + " " + KLUANG_PRICING

GROUP_BLURB = (
    "The parent group, EHA Eldercare (1478860-U), evolved from the Justlife "
    "ElderCare Home brand founded in 2009 and now runs eight residential "
    "locations across Malaysia with a combined 100-plus caregivers and "
    "500-plus residents — making it one of the more established private "
    "eldercare chains across Johor and the Klang Valley."
)

# ─────────────────────────────────────────────────────────────────────────────
# Per-branch editorials
# ─────────────────────────────────────────────────────────────────────────────
LAKEVIEW = (
    "EHA Lakeview Eldercare Mansion is the Permas Jaya branch of EHA "
    "Eldercare Group, sitting lakeside in Taman Bayu Puteri on the eastern "
    "side of Johor Bahru. The branch has been promoted by EHA as a \"Most "
    "Beautiful Elderly Care Mansion\" — an internal label that aligns with "
    "reviewer comments about the lake-facing aspect and landscaped grounds. "
    "Rated 4.9 stars across 40 Google reviews, it sits alongside Golfview "
    "as one of the group's higher-reviewed Johor branches. " + GROUP_BLURB
    + "\n\n" + JBKL_P2 +
    "\n\nPermas Jaya gives Lakeview good access to private hospitals and "
    "commercial services on the eastern JB corridor, which makes it a "
    "convenient choice for families visiting frequently from Pasir Gudang, "
    "Permas, or Tebrau. The lakeside setting and gardens are clearly part of "
    "the marketing pitch; on a viewing it's worth checking how often "
    "residents actually use the lake-facing communal space versus their "
    "rooms, asking how many caregivers are on the overnight roster, and "
    "confirming whether the published \"starting from\" rate matches the "
    "level of care your family member needs. Hospital Sultan Ismail is the "
    "nearest tertiary centre."
)

PARKVIEW = (
    "EHA Parkview Eldercare is the Perling branch of EHA Eldercare Group, "
    "in western Johor Bahru on the Skudai corridor. With 85 Google reviews "
    "at a 4.9-star average, Parkview has the largest review base of any "
    "branch in the EHA network — a meaningful signal of sustained operating "
    "history rather than a newly-opened facility. " + GROUP_BLURB
    + "\n\n" + JBKL_P2 +
    "\n\nPerling sits well-connected to the JB-Skudai highway and the wider "
    "Iskandar Puteri area, which suits families visiting from Bukit Indah, "
    "Tampoi, or further west. With Parkview's longer track record, the "
    "useful viewing questions are less about whether the facility runs and "
    "more about fit: ask how many residents are in each room, whether RN "
    "cover is on-site overnight (versus on-call), how often a physiotherapist "
    "attends in person, and what specific clinical procedures the home "
    "performs in-house versus refers out (PEG feeds, suction, oxygen, wound "
    "dressings, urinary catheter changes). Confirm that the \"starting from\" "
    "rate matches the actual care plan since add-ons can shift the monthly "
    "figure. Hospital Sultanah Aminah is the nearest government tertiary "
    "centre; KPJ Puteri Specialist Hospital is the nearest private option."
)

SUNVIEW = (
    "EHA Sunview Eldercare is the Kempas branch of EHA Eldercare Group and "
    "the group's newest Johor Bahru opening. Sunview markets itself as "
    "Malaysia's first \"theme-styled therapeutic villa\" — a concept the "
    "group describes as borrowing from Taiwanese eldercare design that uses "
    "environmental theming to reduce cognitive disorientation and reinforce "
    "residents' sense of identity. Launch materials highlight fully "
    "automatic medical beds and on-site rehabilitation equipment. With a "
    "5.0-star rating across 24 Google reviews, the early signal is "
    "favourable, though the review base is the thinnest in the group. "
    + GROUP_BLURB
    + "\n\n" + JBKL_P2 +
    "\n\nLaunch marketing also claims doctor, nurse, and physiotherapist "
    "availability around the clock, which is stronger than the group "
    "baseline and worth verifying against the current roster on a visit. "
    "Useful questions: how many residents are currently in the home, how "
    "many caregivers are on duty per shift, what specific clinical "
    "procedures are handled in-house, and whether the themed villa concept "
    "translates to anything operationally meaningful day-to-day. As a newer "
    "branch, Sunview suits families drawn to modern equipment and a fresh "
    "build; families with high-dependency relatives may want a longer "
    "operational track record before committing. Hospital Sultan Ismail "
    "and KPJ Pasir Gudang are the closest acute-care options."
)

KLUANG = (
    "EHA Elder Care Home in Kluang is EHA Eldercare Group's only non-Johor-"
    "Bahru Johor branch, set in the Kluang–Batu Pahat–Yong Peng corridor. "
    "Reviewers specifically cite the cost advantage relative to JB, with one "
    "noting it is \"more than 30% cheaper than Johor Bahru even though the "
    "service standard is higher than most nursing homes in JB.\" The 5.0-"
    "star rating across 33 reviews reflects consistent family satisfaction "
    "and a more hands-on, owner-operated feel than the JB corporate "
    "branches — multiple reviewers praise management by name. " + GROUP_BLURB
    + "\n\n" + KLU_P2 +
    "\n\nKluang's trade-off is geography: KPJ Kluang Specialist Hospital "
    "is in-town and Hospital Enche' Besar Hajjah Khalsom (MSQH-accredited "
    "government) is also nearby, but the wider tertiary hospital cluster is "
    "in JB, roughly 100 km south. For medically stable residents who need "
    "personal care and supervision rather than complex acute support, this "
    "is not a barrier. The branch suits Kluang-based families keeping "
    "relatives near home, and JB families seeking a more affordable "
    "placement where geography is a secondary concern. On a visit, confirm "
    "how acute escalations are handled (which JB hospitals the home "
    "typically transfers to and how transfer is arranged), and check whether "
    "the \"starting from\" rate matches the actual care needs."
)

GRANDVIEW_TITI = (
    "EHA Grandview Titiwangsa is the Kuala Lumpur city-centre branch of EHA "
    "Eldercare Group, sited near Lake Titiwangsa. The branch is associated "
    "in third-party listings with post-surgery recovery and stroke "
    "rehabilitation, but EHA's own website does not publish stroke-specific "
    "protocols, therapist staffing levels, or rehab equipment lists for "
    "this branch — so any rehab specialism should be verified on visit "
    "rather than assumed from the listing title. With a 5.0-star rating "
    "across 10 Google reviews, the early signal is favourable but the "
    "review base is light. " + GROUP_BLURB
    + "\n\n" + JBKL_P2 +
    "\n\nA Titiwangsa location gives Grandview good access to Hospital "
    "Kuala Lumpur (HKL), Institut Jantung Negara, and the National Heart "
    "Institute corridor — useful for residents who need frequent specialist "
    "follow-up. Practical viewing questions: how often a physiotherapist "
    "attends in person, who supervises exercise programmes on non-therapist "
    "days, what specific clinical procedures are handled in-house versus "
    "referred out (PEG feeds, suction, oxygen, wound dressings, urinary "
    "catheter changes), and what the home's typical resident profile looks "
    "like (post-surgery short-stay vs long-term residential vs dementia "
    "care). Confirm the \"starting from\" rate matches the actual care needs."
)

GRANDVIEW_KEPONG = (
    "EHA Grandview Eldercare in Kepong is the north-Kuala Lumpur branch of "
    "EHA Eldercare Group, serving the Kepong, Desa Parkcity, and Jalan "
    "Ipoh corridor. With a 5.0-star rating across 27 Google reviews, it "
    "carries a stronger early track record than the Titiwangsa branch and "
    "is one of the better-reviewed KL eldercare options on Google. "
    + GROUP_BLURB
    + "\n\n" + JBKL_P2 +
    "\n\nKepong gives the branch good access to Hospital Sungai Buloh and "
    "the Damansara hospital cluster (Sunway, KPJ Damansara, ParkCity "
    "Medical Centre), and proximity to the relatively quiet residential "
    "neighbourhoods of Desa Parkcity and Bandar Menjalara. Practical "
    "viewing questions: how many residents are currently in the home, how "
    "many caregivers cover each shift, whether RN cover is on-site "
    "overnight or on-call, and what clinical procedures are handled in-"
    "house versus referred out. Confirm the \"starting from\" rate matches "
    "the actual care plan since add-ons can shift the monthly figure."
)

BAYVIEW = (
    "EHA Bayview Eldercare is the Klang Valley branch of EHA Eldercare "
    "Group, sited in Bandar Sungai Long on the Cheras–Kajang fringe — a "
    "light-industrial enclave on the eastern edge of greater Kuala Lumpur. "
    "The branch's listing title and marketing emphasise its catchment "
    "across Cheras, Sungai Long, and Kajang. With a 5.0-star rating across "
    "22 Google reviews, the early signal is favourable, though the review "
    "base remains modest. " + GROUP_BLURB
    + "\n\n" + JBKL_P2 +
    "\n\nThe Sungai Long location gives Bayview reasonable access to "
    "private hospitals on the Cheras–Kajang corridor (KPJ Kajang, "
    "Columbia Asia Cheras, Sunway Velocity), although the immediate "
    "neighbourhood is more industrial-fringe than residential. Practical "
    "viewing questions: how many caregivers are on each shift, whether RN "
    "cover is on-site overnight, what acute-escalation pathways the home "
    "typically uses (which hospital, how transfer is arranged), and what "
    "clinical procedures are handled in-house versus referred out. Confirm "
    "the \"starting from\" rate matches the actual care plan since add-ons "
    "can shift the monthly figure."
)

# ─────────────────────────────────────────────────────────────────────────────
# Per-row updates
# ─────────────────────────────────────────────────────────────────────────────
UPDATES = {
    'eha-lakeview-eldercare-mansion-permas-branch-1-nursing-home': {
        'editorial_summary': LAKEVIEW,
        'pricing_display': 'From RM 3,200/mo',
        'shared_price': '',
        'private_price': 'RM 3,200',
        'last_updated': TODAY,
    },
    'eha-parkview-eldercare-perling-1-nursing-home-johor-bahru': {
        'editorial_summary': PARKVIEW,
        'pricing_display': 'From RM 3,200/mo',
        'shared_price': '',
        'private_price': 'RM 3,200',
        'last_updated': TODAY,
    },
    'eha-parkview-eldercare-perling': {
        'editorial_summary': PARKVIEW,
        'pricing_display': 'From RM 3,200/mo',
        'shared_price': '',
        'private_price': 'RM 3,200',
        'last_updated': TODAY,
    },
    'eha-sunview-eldercare-kempas-1-nursing-home-johor-bahru': {
        'editorial_summary': SUNVIEW,
        'pricing_display': 'From RM 3,200/mo',
        'shared_price': '',
        'private_price': 'RM 3,200',
        'last_updated': TODAY,
    },
    'eha-elder-care-home-kluang-licensed-and-certified-by-govern': {
        'editorial_summary': KLUANG,
        'pricing_display': 'From RM 2,300/mo',
        'shared_price': '',
        'private_price': 'RM 2,300',
        'last_updated': TODAY,
    },
    'eha-grandview-titiwangsa-kl-elderly-care-post-surgery-recovery-stroke-rehabilita': {
        'editorial_summary': GRANDVIEW_TITI,
        'pricing_display': 'From RM 3,200/mo',
        'shared_price': '',
        'private_price': 'RM 3,200',
        'last_updated': TODAY,
    },
    'eha-grandview-eldercare-甲洞温馨疗养别墅-1-nursing-home-kl-kepong-desa-parkcity-jalan-ip': {
        'editorial_summary': GRANDVIEW_KEPONG,
        'pricing_display': 'From RM 3,200/mo',
        'shared_price': '',
        'private_price': 'RM 3,200',
        'last_updated': TODAY,
    },
    'eha-bayview-eldercare-cheras-sungai-long-kajang-温馨疗养别墅-1-nursing-home-kl': {
        'editorial_summary': BAYVIEW,
        'pricing_display': 'From RM 3,200/mo',
        'shared_price': '',
        'private_price': 'RM 3,200',
        'last_updated': TODAY,
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# Details rows: relabel existing + append baseline + Pricing source
# ─────────────────────────────────────────────────────────────────────────────
ROOMS_RELABEL = {
    # existing label (case-sensitive)              -> new label
    ('rooms', 'Assisted Living (RM/mo)')           : 'Assisted Living (from RM/mo)',
    ('rooms', 'Respite / Short-term (RM/day)')     : 'Respite / Short-term (from RM/day)',
    ('rooms', 'Day Care (RM/mo)')                  : 'Day Care (from RM/mo)',
}

# Baseline rooms+pricing-source rows for branches whose Details have 0 rooms data.
# (Keyed by slug → list of (section,label,value).)
def baseline_rooms(jbkl=True):
    if jbkl:
        return [
            ('rooms', 'Assisted Living (from RM/mo)',           '3,200'),
            ('rooms', 'Respite / Short-term (from RM/day)',     '120'),
            ('rooms', 'Day Care (from RM/mo)',                  '1,500'),
        ]
    return [
            ('rooms', 'Assisted Living (from RM/mo)',           '2,300'),
            ('rooms', 'Respite / Short-term (from RM/day)',     '80'),
            ('rooms', 'Day Care (from RM/mo)',                  '1,300'),
    ]

PRICING_SOURCE_VALUE = (
    'ehaeldercare.com.my/our-packages/ — starting rates; final fee depends '
    'on care needs'
)

NEEDS_BASELINE_ROOMS = {
    'eha-parkview-eldercare-perling-1-nursing-home-johor-bahru': True,   # 0 detail rows
    'eha-grandview-titiwangsa-kl-elderly-care-post-surgery-recovery-stroke-rehabilita': True,
    'eha-grandview-eldercare-甲洞温馨疗养别墅-1-nursing-home-kl-kepong-desa-parkcity-jalan-ip': True,
    'eha-bayview-eldercare-cheras-sungai-long-kajang-温馨疗养别墅-1-nursing-home-kl': True,
}

# ─────────────────────────────────────────────────────────────────────────────
# Read existing data
# ─────────────────────────────────────────────────────────────────────────────
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

def h(name): return headers.index(name) if name in headers else None
slug_i = h('slug')

details_data = ss.values().get(
    spreadsheetId=SPREADSHEET_ID, range=f"'{DETAILS_TAB}'"
).execute().get('values', [])

# ─────────────────────────────────────────────────────────────────────────────
# Build batch update list
# ─────────────────────────────────────────────────────────────────────────────
batch_data = []
found = set()

# 1) Facilities-tab updates
for i, row in enumerate(fac_data[1:], start=2):
    if slug_i >= len(row): continue
    slug = row[slug_i].strip()
    if slug not in UPDATES: continue
    found.add(slug)
    print(f"FAC row {i}: {slug}")
    for field, value in UPDATES[slug].items():
        col_i = h(field)
        if col_i is None:
            print(f"  WARN: missing column '{field}'"); continue
        batch_data.append({
            'range': f"'{FAC_TAB}'!{col_letter(col_i+1)}{i}",
            'values': [[value]]
        })

for slug in UPDATES:
    if slug not in found:
        print(f"  ⚠️  Slug NOT FOUND in facilities tab: {slug}")

# 2) Details-tab relabels (only for rows whose label matches the OLD form)
for i, row in enumerate(details_data[1:], start=2):
    if len(row) < 4: continue
    if row[0] not in UPDATES: continue
    key = (row[1], row[2])
    if key in ROOMS_RELABEL:
        new_label = ROOMS_RELABEL[key]
        batch_data.append({
            'range': f"'{DETAILS_TAB}'!C{i}",
            'values': [[new_label]]
        })
        print(f"DET row {i} relabel: {row[0][:30]}... '{row[2]}' → '{new_label}'")

# Apply in-place updates first
if batch_data:
    for start in range(0, len(batch_data), 100):
        ss.values().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={'valueInputOption': 'RAW', 'data': batch_data[start:start+100]}
        ).execute()
    print(f"\n✅ Applied {len(batch_data)} in-place updates")

# 3) Append new Details rows: baseline rooms (if needed) + Pricing source (always)
existing_keys = {(r[0], r[1], r[2]) for r in details_data[1:] if len(r) >= 3}

new_rows = []
for slug in UPDATES:
    # Baseline rooms for branches with no rooms data
    if NEEDS_BASELINE_ROOMS.get(slug):
        # JB & KL bracket = True; Kluang/short-parkview already covered above
        is_kluang = (slug == 'eha-elder-care-home-kluang-licensed-and-certified-by-govern')
        for sec, lbl, val in baseline_rooms(jbkl=not is_kluang):
            if (slug, sec, lbl) not in existing_keys:
                new_rows.append([slug, sec, lbl, val])
    # Pricing source — append for every branch we're updating
    if (slug, 'rooms', 'Pricing source') not in existing_keys:
        new_rows.append([slug, 'rooms', 'Pricing source', PRICING_SOURCE_VALUE])

if new_rows:
    ss.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{DETAILS_TAB}'!A:D",
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body={'values': new_rows}
    ).execute()
    print(f"\n✅ Appended {len(new_rows)} new Details rows")
    for r in new_rows:
        print(f"  + [{r[1]}] {r[2]} = {r[3][:60]}  ({r[0][:40]}...)")

print("\n🎉 EHA chain revision complete.")
