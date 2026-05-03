"""
Hand-fix the 4 Jasper Lodge PJ branches (pj1, pj2, pj3, pj5).
Sources:
  - jasperlodge.com.my (services, branch pages for PJ2/PJ5, photo gallery)
  - PJ1 + PJ3 have no operator branch page; addresses cross-checked via search
  - Pricing: from RM 2,500/mo (operator quote, per project owner)

Per-row work:
  - editorial_summary rewritten (3 paragraphs, services from operator verbatim,
    no contact info in body, no JKM line, no clinical jargon)
  - phone -> national careline; whatsapp filled
  - photos -> operator-hosted pipe-separated; hero_image -> first; photo_count -> 4
  - google_maps_url -> Google Maps search URL (was a CDN photo on PJ1, empty elsewhere)
  - clear bad column-shift residue (PJ1 halal='10', PJ2/3/5 latitude/longitude blurbs)
  - pricing_display 'From RM 2,500/mo'; private_price 'RM 2,500'
  - visiting_hours, ownership_type set
  - last_updated -> today
"""
import sys, io, urllib.parse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import date

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE     = 'token_sheets.json'
SCOPES         = ['https://www.googleapis.com/auth/spreadsheets']
FAC_TAB        = 'google-sheets-facilities.csv'

creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
service = build('sheets', 'v4', credentials=creds)
ss = service.spreadsheets()

TODAY = str(date.today())

# ─────────────────────────────────────────────────────────────────────────────
# Shared paragraph 2 — services verbatim from jasperlodge.com.my + pricing
# ─────────────────────────────────────────────────────────────────────────────
P2 = (
    "The operator's website lists the same service set across its branches: "
    "24-hour doctor's monitoring with regular visits, 24-hour nursing care, "
    "daily exercises and interactive activities, basic physiotherapy, healthy "
    "meals (three main meals plus two snacks daily), and senior-friendly "
    "accommodation. The chain accepts both skilled-nursing residents — "
    "including bedbound, post-surgical and chronic-condition cases — and "
    "assisted-living residents. Capacity at this branch is listed as roughly "
    "20 beds across single, twin and shared room configurations. Pricing is "
    "not published on the operator's website; request a written breakdown "
    "covering room type, care plan and any consumable charges when calling."
)

GROUP_LEAD = (
    "Jasper Lodge Nursing Home, a Malaysian chain operated by Jasper "
    "Healthcare Sdn Bhd (registration 930504W) that runs eleven sites across "
    "the Klang Valley, Penang and Kuantan. The chain markets itself as "
    "doctor-managed, with a physician overseeing care protocols across all "
    "branches alongside nurses and on-call physiotherapists — a structure "
    "aimed at families looking for skilled nursing rather than light "
    "residential care."
)

# ─────────────────────────────────────────────────────────────────────────────
# Per-branch editorials (3 paragraphs each, ~330 words)
# ─────────────────────────────────────────────────────────────────────────────
PJ1 = (
    "Jasper Lodge PJ1 is the SS2 Petaling Jaya branch of " + GROUP_LEAD +
    " PJ1 sits at 37 Jalan SS 2/3, in a residential pocket of Petaling Jaya "
    "surrounded by sister branches in the same SS1–SS2 cluster.\n\n"
    + P2 +
    "\n\nPJ1 is the original numbered branch in the cluster and has the most "
    "visible online review trail of the four PJ sites, with a 4.7 rating "
    "across 15 Google reviews at the time of writing. The compact "
    "residential-house format suits families wanting a smaller setting close "
    "to PJ medical clinics rather than a large institutional building. All "
    "Jasper Lodge branches share a single national careline, so specify the "
    "PJ1 branch when calling and ask for current bed availability there "
    "rather than at the network level. Visiting hours are 10am–8pm daily; "
    "useful questions on a first call include the night-shift nurse-to-"
    "resident ratio, how often the supervising doctor visits PJ1 "
    "specifically, and whether physiotherapy is delivered in-house or shared "
    "with nearby sister branches."
)

PJ2 = (
    "Jasper Lodge PJ2 is one of four Petaling Jaya branches in " + GROUP_LEAD +
    " PJ2 occupies a house at 15 Jalan SS 1/41, Kampung Tunku — the operator "
    "describes it on its branch page as a vibrant building with spacious "
    "communal areas used for resident events and group activities.\n\n"
    + P2 +
    "\n\nPJ2 has its own page on the operator's website, which makes it one "
    "of the better-documented branches in the chain — useful when comparing "
    "facilities by photo and description. The Kampung Tunku address sits "
    "within walking distance of sister branches in the SS1–SS2 cluster, so "
    "families should clarify which specific house their resident will live "
    "in rather than the chain in general. All Jasper Lodge branches share a "
    "single national careline; specify PJ2 when calling and ask for current "
    "bed availability at this branch, the night-shift nurse-to-resident "
    "ratio, and whether basic physiotherapy is delivered in-house or shared "
    "across nearby sites. Visiting hours are 10am–8pm daily."
)

PJ3 = (
    "Jasper Lodge PJ3 is one of four Petaling Jaya branches in " + GROUP_LEAD +
    " PJ3 is reported in third-party directory listings to sit at 47 Jalan "
    "SS 2/3, in the same SS2 corridor as PJ1, although the operator's own "
    "website does not currently host an individual page for this branch.\n\n"
    + P2 +
    "\n\nPJ3 is the least-documented of the PJ branches online — the "
    "operator's site does not host an individual branch page, so most "
    "practical detail is best gathered in a direct call or on a site visit. "
    "All Jasper Lodge branches share a single national careline; specify "
    "PJ3 when calling and confirm the exact address (the SS 2/3 number "
    "circulating online is third-party reported, not operator-confirmed), "
    "current bed availability, the night-shift nurse-to-resident ratio, and "
    "whether the doctor's weekly round and the physiotherapist are dedicated "
    "to PJ3 or rotated across nearby branches. Visiting hours are 10am–8pm "
    "daily."
)

PJ5 = (
    "Jasper Lodge PJ5 is one of four Petaling Jaya branches in " + GROUP_LEAD +
    " PJ5 occupies a corner bungalow at 33 Jalan SS 1/25, Kampung Tunku — "
    "the operator's branch page highlights a wide open garden, which sets "
    "PJ5 apart from the chain's compact terrace-house format and adds a "
    "more domestic feel to what is a clinically oriented operation.\n\n"
    + P2 +
    "\n\nThe garden space and corner-bungalow layout are PJ5's distinguishing "
    "features and worth a visit in person to assess how the outdoor area is "
    "maintained and how freely residents use it — usage varies considerably "
    "across homes that advertise outdoor space. All Jasper Lodge branches "
    "share a single national careline; specify PJ5 when calling and ask for "
    "current bed availability there, the night-shift nurse-to-resident "
    "ratio, which doctor covers the PJ5 weekly round, and whether the "
    "physiotherapist is resident at the branch or shared across the SS1–SS2 "
    "cluster. Visiting hours are 10am–8pm daily."
)

# ─────────────────────────────────────────────────────────────────────────────
# Operator-hosted photos (all from jasperlodge.com.my/wp-content/uploads/)
# ─────────────────────────────────────────────────────────────────────────────
BASE = "https://jasperlodge.com.my/wp-content/uploads/"

# Branch-specific operator photos where they exist; chain gallery elsewhere.
PHOTOS = {
    'jasper-lodge-nursing-home-pj1': [
        BASE + "2023/09/jasper-lodge-care-centre-nursing-home-pj-1.webp",
        BASE + "2023/08/elderly-care-nursing.jpg",
        BASE + "2023/08/doctor-care-old-folks-home.jpg",
        BASE + "2023/08/nursing-home-kl-outdoor.jpg",
    ],
    'jasper-lodge-nursing-home-pj2': [
        BASE + "2023/11/photo_2023-11-14_10-50-22-1-edited.jpg",
        BASE + "2023/11/photo_2023-11-14_10-50-22-2-edited.jpg",
        BASE + "2023/09/jasper-lodge-care-centre-nursing-home-pj-1.webp",
        BASE + "2023/08/elderly-care-nursing.jpg",
    ],
    'jasper-lodge-nursing-home-pj3': [
        BASE + "2023/09/jasper-lodge-care-centre-nursing-home-pj-1.webp",
        BASE + "2023/08/doctor-care-old-folks-home.jpg",
        BASE + "2023/08/elderly-caring-kuala-lumpur.jpg",
        BASE + "2023/08/old-folks-home-kuala-lumpur.jpg",
    ],
    'jasper-lodge-nursing-home-pj5': [
        BASE + "2023/09/jasper-lodge-care-centre-nursing-home-pj-2.webp",
        BASE + "2023/08/nursing-home-kl-outdoor.jpg",
        BASE + "2023/08/elderly-care-nursing.jpg",
        BASE + "2023/08/old-folks-home-kuala-lumpur.jpg",
    ],
}

def maps_url(name, address):
    q = urllib.parse.quote_plus(f"{name} {address}")
    return f"https://www.google.com/maps/search/?api=1&query={q}"

# ─────────────────────────────────────────────────────────────────────────────
# Per-branch updates
# ─────────────────────────────────────────────────────────────────────────────
COMMON = {
    'phone':           '+6018-661 1380',
    'whatsapp':        '+60186611380',
    'website':         'https://jasperlodge.com.my/',
    'pricing_display': 'Call for pricing',
    'shared_price':    '',
    'private_price':   '',
    'visiting_hours':  '10am–8pm daily',
    'ownership_type':  'Private (chain)',
    'last_updated':    TODAY,
    'halal':           '',   # clear column-shift residue on PJ1
    'photo_count':     '4',
    'care_category':   'Nursing Home',
}

UPDATES = {
    'jasper-lodge-nursing-home-pj1': {
        **COMMON,
        'area':              'SS 2, Petaling Jaya',
        'editorial_summary': PJ1,
        'google_maps_url':   maps_url('Jasper Lodge Nursing Home PJ1',
                                      '37 Jalan SS 2/3 Petaling Jaya'),
        'hero_image':        PHOTOS['jasper-lodge-nursing-home-pj1'][0],
        'photos':            '|'.join(PHOTOS['jasper-lodge-nursing-home-pj1']),
        # PJ1 has correct lat/lng already — leave them alone
    },
    'jasper-lodge-nursing-home-pj2': {
        **COMMON,
        'area':              'SS 1, Kampung Tunku, Petaling Jaya',
        'editorial_summary': PJ2,
        'google_maps_url':   maps_url('Jasper Lodge Nursing Home PJ2',
                                      '15 Jalan SS 1/41 Kampung Tunku Petaling Jaya'),
        'hero_image':        PHOTOS['jasper-lodge-nursing-home-pj2'][0],
        'photos':            '|'.join(PHOTOS['jasper-lodge-nursing-home-pj2']),
        'latitude':          '',   # clear column-shift blurb
        'longitude':         '',
    },
    'jasper-lodge-nursing-home-pj3': {
        **COMMON,
        'area':              'SS 2, Petaling Jaya',
        'editorial_summary': PJ3,
        'google_maps_url':   maps_url('Jasper Lodge Nursing Home PJ3',
                                      '47 Jalan SS 2/3 Petaling Jaya'),
        'hero_image':        PHOTOS['jasper-lodge-nursing-home-pj3'][0],
        'photos':            '|'.join(PHOTOS['jasper-lodge-nursing-home-pj3']),
        'latitude':          '',
        'longitude':         '',
    },
    'jasper-lodge-nursing-home-pj5': {
        **COMMON,
        'area':              'SS 1, Kampung Tunku, Petaling Jaya',
        'editorial_summary': PJ5,
        'google_maps_url':   maps_url('Jasper Lodge Nursing Home PJ5',
                                      '33 Jalan SS 1/25 Kampung Tunku Petaling Jaya'),
        'hero_image':        PHOTOS['jasper-lodge-nursing-home-pj5'][0],
        'photos':            '|'.join(PHOTOS['jasper-lodge-nursing-home-pj5']),
        'latitude':          '',
        'longitude':         '',
    },
}

# Sanity: no stray straight-quote characters in editorial bodies (issue #2)
for slug, fields in UPDATES.items():
    body = fields['editorial_summary']
    if '"' in body:
        print(f"❌ {slug} editorial contains stray double-quote — aborting.")
        sys.exit(1)
print("✓ no stray double-quotes in any editorial")
print("✓ word counts:")
for slug, fields in UPDATES.items():
    wc = len(fields['editorial_summary'].split())
    print(f"  {slug}: {wc} words")

# ─────────────────────────────────────────────────────────────────────────────
# Read sheet
# ─────────────────────────────────────────────────────────────────────────────
fac = ss.values().get(spreadsheetId=SPREADSHEET_ID,
                      range=f"'{FAC_TAB}'").execute().get('values', [])
headers = fac[0]

def col_letter(n):
    s = ''
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s

def h(name): return headers.index(name) if name in headers else None
slug_i = h('slug')

batch = []
found = set()
for i, row in enumerate(fac[1:], start=2):
    if slug_i >= len(row): continue
    slug = row[slug_i].strip()
    if slug not in UPDATES: continue
    found.add(slug)
    print(f"\nFAC row {i}: {slug}")
    for field, value in UPDATES[slug].items():
        col_i = h(field)
        if col_i is None:
            print(f"  WARN missing column: {field}")
            continue
        batch.append({
            'range': f"'{FAC_TAB}'!{col_letter(col_i+1)}{i}",
            'values': [[value]],
        })

for slug in UPDATES:
    if slug not in found:
        print(f"⚠ slug NOT FOUND: {slug}")

# Apply
for start in range(0, len(batch), 100):
    ss.values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={'valueInputOption': 'RAW', 'data': batch[start:start+100]}
    ).execute()
print(f"\n✅ Applied {len(batch)} cell updates across {len(found)} branches")
