"""
Hand-fix Merry Care Centre chain (6 branches per operator screenshot):
  - Update existing rows: merry-care-centre-jln-antoi (Kepong Baru 1),
                          merry-care-centre-jln-belinggai (Kepong Baru 2)
  - Append new rows:      merry-care-kepong-baru-3, merry-care-kepong-baru-4,
                          merry-care-selayang-baru, merry-care-desa-jaya-kepong

Per-row work:
  - Title to operator's exact branch name
  - Area/state corrected from postcode
  - Phone, website, pricing, google_maps_url, hero_image, photos, photo_count
  - Editorial: 3 paragraphs, knowledgeable-friend tone, chain context + branch tail
  - last_updated 2026-05-03

Details tab:
  - Append rooms / Pricing source row per branch (idempotent)

Photos sourced from operator website (elderlycare.my, Wix CDN). Operator
publishes RM 2,500/mo starting rate for shared room incl. 5 meals.
"""
import sys, io, urllib.parse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import date

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE = r'C:\Users\ibkaa\nursinghomeguide-my\Nursing Home Guide Malaysia\token_sheets.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
FAC_TAB = 'google-sheets-facilities.csv'
DETAILS_TAB = 'Details'

creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
service = build('sheets', 'v4', credentials=creds)
ss = service.spreadsheets()
TODAY = str(date.today())

# ── Editorial building blocks ────────────────────────────────────────────────
GROUP_BLURB = (
    "Merry Care is a six-branch nursing home chain operating across Kepong "
    "Baru, Desa Jaya, and Selayang Baru in the Klang Valley. The group "
    "markets itself at elderlycare.my and positions on the affordable end of "
    "the residential care market — a deliberate point of difference against "
    "private retirement homes that typically start north of RM 4,000 per "
    "month. With multiple homes clustered within walking distance of each "
    "other in Kepong Baru, families touring the chain often visit two or "
    "three branches in a single afternoon."
)

SERVICES_LINE = (
    "The operator publishes the same service bundle across all branches: "
    "medication management, daily items purchasing, hospital visitation, "
    "daily fitness activities, a 24-hour assistant on duty, and five meals a "
    "day with unlimited servings on request. Pricing is published on the "
    "operator website (elderlycare.my) starting from RM 2,500 per month for "
    "a shared room — a starting figure that, in practice, varies with the "
    "resident's actual care needs and dependency level. Bed count and current "
    "room availability are not published online."
)

def editorial(branch_label, address, neighbourhood_tail):
    return (
        f"Merry Care {branch_label} is one of six branches in the Merry Care "
        f"chain, located at {address}. " + GROUP_BLURB
        + "\n\n" + SERVICES_LINE +
        "\n\n" + neighbourhood_tail
    )

# Per-branch tails — all anchor on practical viewing questions, no contact info,
# no JKM push, no clinical jargon checklists.
TAIL_KEPONG = (
    "Kepong Baru is a dense residential pocket in north-Kuala Lumpur with "
    "good access to Hospital Sungai Buloh and the Damansara hospital cluster "
    "(KPJ Damansara, Sunway, ParkCity Medical Centre). The neighbourhood is "
    "tightly built — terrace-house lots, narrow back lanes — so families "
    "should ask on a visit how natural light, communal space, and any "
    "outdoor compound are handled, how many residents share a room, how many "
    "caregivers cover each shift, whether a registered nurse is on-site "
    "overnight or on-call, and what specific clinical procedures the home "
    "performs in-house versus refers out (PEG feeds, oxygen, wound dressings, "
    "urinary catheter changes). Confirm the RM 2,500 starting rate matches "
    "the actual care plan since add-ons can shift the monthly figure."
)

TAIL_SELAYANG = (
    "Selayang Baru sits north of Kepong on the KL–Selangor border, with "
    "Hospital Selayang (a major MOH tertiary hospital) within a few "
    "kilometres — a practical advantage for residents who may need frequent "
    "specialist follow-up or acute escalation. The neighbourhood is "
    "lower-density than Kepong Baru, with more compound space typical of "
    "Selangor terrace lots. Useful viewing questions: how many residents are "
    "currently in the home, how many caregivers are on each shift, whether "
    "RN cover is on-site overnight, and what acute-escalation pathway the "
    "home typically uses. Confirm the RM 2,500 starting rate matches the "
    "actual care plan since add-ons can shift the monthly figure."
)

TAIL_DESA_JAYA = (
    "Taman Desa Jaya is on the Kepong–Desa Parkcity fringe, slightly "
    "quieter than the Kepong Baru cluster and closer to the Damansara "
    "hospital corridor (KPJ Damansara, Sunway, ParkCity Medical Centre). "
    "Useful viewing questions: how many residents share a room, how many "
    "caregivers cover each shift, whether RN cover is on-site overnight or "
    "on-call, what specific clinical procedures are handled in-house versus "
    "referred out, and whether the property has a usable outdoor compound. "
    "Confirm the RM 2,500 starting rate matches the actual care plan since "
    "add-ons can shift the monthly figure."
)

# ── Branch definitions ──────────────────────────────────────────────────────
def photo_url(media_id):
    return f"https://static.wixstatic.com/media/{media_id}~mv2.jpg"

def maps_url(address):
    return ("https://www.google.com/maps/search/?api=1&query="
            + urllib.parse.quote_plus(address))

CHAIN_PHONE = "+6014-636 6884"

KB1_ADDR = "42, Jalan Antoi 2, Kepong Baru, 52100 Kuala Lumpur"
KB2_ADDR = "53, Jalan Belinggai, Kepong Bahru, 52100 Kuala Lumpur"
KB3_ADDR = "No.1, Jalan 9, Taman Kepong, 52100 Kuala Lumpur"
KB4_ADDR = "39, Jalan Belibis 2, Kepong Baru, 52100 Kuala Lumpur"
SEL_ADDR = "12, Jalan 1D, Selayang Baru, 68100 Batu Caves, Selangor"
DJ_ADDR  = "No.27, Jalan 5, Taman Desa Jaya, Kepong, 52100 Kuala Lumpur"

KB1_PHOTOS = [photo_url(x) for x in [
    "0807fc_b2effad5978148a6afd9ed519079c2e3",
    "0807fc_d3bf1a6f39d245b9bb71a327df24f36d",
    "0807fc_70c686e2b3e446efb98191c73b57dbe9",
    "0807fc_bb7432dcb2c54328b26b4c8b1dc450c0",
    "0807fc_2df02c29d4de48b2b3d382dd5c53370a",
    "0807fc_56933de4d3c34e7ea1524ef4a3e631d7",
    "0807fc_64d84687ae0b4bbaad9b75b14944f320",
    "0807fc_dd7164fa70534ee69a73337d0c45581f",
    "0807fc_4f8e5dcdaba146a7bc89ea3194cbf072",
]]
KB2_PHOTOS = [photo_url(x) for x in [
    "0807fc_f112a86122a14e65b8dc9621db7fa834",
    "0807fc_ace0847425514bc4a8a971edd7032951",
    "0807fc_ecdbd3bf27b042088a50eb957ddcabb2",
    "0807fc_92c51f9fdfe744aeb6a42032255603cc",
    "0807fc_a4404794b10941209aebf1d7fe3fe25b",
    "0807fc_f848dda5a3f746e6ac47dcea6d94e0c0",
    "0807fc_47937203a2954dbd89ceeff28debd161",
    "0807fc_5b13d50ad8434158848ffe8a2070dbed",
    "0807fc_32293ddefa4e4715920f574e291cba14",
]]
KB3_PHOTOS = [photo_url(x) for x in [
    "0807fc_ad18278b2a684a46831e44edefe05ba8",
    "0807fc_a07186020aa445aabdf26ff54f9cb15e",
    "0807fc_893325fe68ab42dca8c06ade04872502",
    "0807fc_801e468165e54e7f8b77ebf0fb66d9db",
    "0807fc_d5674e229b214ce497ebdf50fb99d6c8",
    "0807fc_db2b71328a304f328dd6e070208127cc",
    "0807fc_deab199f525b40f7b9b594027682f50b",
    "0807fc_32989a99358e4f2c893f9d8112e58046",
    "0807fc_18ad5bed686845dfa19ec7e89c8c3ecf",
    "0807fc_41284ad2f77e4ff1a761acf5fe4f080b",
]]
KB4_PHOTOS = [photo_url(x) for x in [
    "0807fc_d4f3693d892f48dfb036a8fa77fb730a",
    "0807fc_7572f6998c19468787007f76a8f9532f",
    "0807fc_a419e59a984946db8a9c9ec8e4d3c2fc",
    "0807fc_10d7a95da4c348298f31bfc523344795",
    "0807fc_a60a9d66ac4346818831d23d3203cb1d",
    "0807fc_6a34e755070c4ccca39cc2c51808663a",
    "0807fc_53ea9573ba824b1f82fa4526902b2de6",
    "0807fc_f94f8cd4de174d18ac2c2c719baf3dc5",
    "0807fc_7a04d9554043405aa0802eb00f3cfc68",
]]
SEL_PHOTOS = [photo_url(x) for x in [
    "0807fc_0c45f1d1a7484677b45a1e1d4497f535",
    "0807fc_c578ca2a66524c798f9e3af0a36029db",
    "0807fc_fb124c7926e54e95beaa299a526171af",
    "0807fc_0ab0677b660f4e1e8a97b239805ffb98",
    "0807fc_dfd944b6e49c4987981291007ed85a8f",
    "0807fc_348637ffb70c4a0284a93cb6191995de",
    "0807fc_bf0f3c0b8c8644f2aea8e26836df0c12",
    "0807fc_6829b034188447b6a5175e69b60ccc57",
    "0807fc_a1f2c5e818af48d085fde9ca56cf9790",
    "0807fc_91d983ed34fb41d5957cc587996cf370",
    "0807fc_c5aebf1978764962b835a41491809f38",
    "0807fc_57f7f3278d5f4824b8368d50fcfbd6ef",
]]
DJ_PHOTOS = [photo_url(x) for x in [
    "0807fc_6defbed897024370b8326975e4160c75",
    "0807fc_3e9897115cc64fb9a8859637e8861338",
    "0807fc_57c9b09404e548b78d3c3fc25d4e6cfa",
    "0807fc_f3cb41313e814d7d9e49ddc7a305c17b",
    "0807fc_e0bb5cb87fea417e8206a80df7e475ef",
    "0807fc_1fcfa510eff447c2881626416096765d",
    "0807fc_3e21c672fd0942cc94e65f844466c54e",
    "0807fc_e2491f60013e41138031c752ca6cd325",
    "0807fc_ed092eaeec8840cc8cc8c7388dfe150d",
    "0807fc_ba726a936c9e4492946bca62199ac2bd",
    "0807fc_1f290654f72e445792020e523658df40",
    "0807fc_5ce3af92eb784b2bad294ac536397897",
]]

BRANCHES = {
    'merry-care-centre-jln-antoi': {
        'title': 'Merry Care Kepong Baru 1',
        'area': 'Kepong Baru',
        'state': 'Kuala Lumpur',
        'phone': CHAIN_PHONE,
        'website': 'https://www.elderlycare.my/merry-care/merry-care-kepong-baru-1',
        'pricing_display': 'From RM 2,500/mo',
        'shared_price': 'RM 2,500',
        'private_price': '',
        'google_maps_url': maps_url(KB1_ADDR),
        'hero_image': KB1_PHOTOS[0],
        'photos': '|'.join(KB1_PHOTOS),
        'photo_count': str(len(KB1_PHOTOS)),
        'editorial_summary': editorial("Kepong Baru 1", KB1_ADDR, TAIL_KEPONG),
        'last_updated': TODAY,
    },
    'merry-care-centre-jln-belinggai': {
        'title': 'Merry Care Kepong Baru 2',
        'area': 'Kepong Baru',
        'state': 'Kuala Lumpur',
        'phone': CHAIN_PHONE,
        'website': 'https://www.elderlycare.my/merry-care/merry-care-kepong-baru-2',
        'pricing_display': 'From RM 2,500/mo',
        'shared_price': 'RM 2,500',
        'private_price': '',
        'google_maps_url': maps_url(KB2_ADDR),
        'hero_image': KB2_PHOTOS[0],
        'photos': '|'.join(KB2_PHOTOS),
        'photo_count': str(len(KB2_PHOTOS)),
        'editorial_summary': editorial("Kepong Baru 2", KB2_ADDR, TAIL_KEPONG),
        'last_updated': TODAY,
    },
}

NEW_ROWS = {
    'merry-care-kepong-baru-3': {
        'title': 'Merry Care Kepong Baru 3',
        'area': 'Taman Kepong',
        'state': 'Kuala Lumpur',
        'phone': CHAIN_PHONE,
        'website': 'https://www.elderlycare.my/merry-care/merry-care-kepong-baru-3',
        'pricing_display': 'From RM 2,500/mo',
        'shared_price': 'RM 2,500',
        'google_maps_url': maps_url(KB3_ADDR),
        'hero_image': KB3_PHOTOS[0],
        'photos': '|'.join(KB3_PHOTOS),
        'photo_count': str(len(KB3_PHOTOS)),
        'editorial_summary': editorial("Kepong Baru 3", KB3_ADDR, TAIL_KEPONG),
        'last_updated': TODAY,
    },
    'merry-care-kepong-baru-4': {
        'title': 'Merry Care Kepong Baru 4',
        'area': 'Kepong Baru',
        'state': 'Kuala Lumpur',
        'phone': CHAIN_PHONE,
        'website': 'https://www.elderlycare.my/merry-care/merry-care-kepong-baru-4',
        'pricing_display': 'From RM 2,500/mo',
        'shared_price': 'RM 2,500',
        'google_maps_url': maps_url(KB4_ADDR),
        'hero_image': KB4_PHOTOS[0],
        'photos': '|'.join(KB4_PHOTOS),
        'photo_count': str(len(KB4_PHOTOS)),
        'editorial_summary': editorial("Kepong Baru 4", KB4_ADDR, TAIL_KEPONG),
        'last_updated': TODAY,
    },
    'merry-care-selayang-baru': {
        'title': 'Merry Care Selayang Baru',
        'area': 'Selayang Baru',
        'state': 'Selangor',
        'phone': CHAIN_PHONE,
        'website': 'https://www.elderlycare.my/merry-care/merry-care-selayang-baru',
        'pricing_display': 'From RM 2,500/mo',
        'shared_price': 'RM 2,500',
        'google_maps_url': maps_url(SEL_ADDR),
        'hero_image': SEL_PHOTOS[0],
        'photos': '|'.join(SEL_PHOTOS),
        'photo_count': str(len(SEL_PHOTOS)),
        'editorial_summary': editorial("Selayang Baru", SEL_ADDR, TAIL_SELAYANG),
        'last_updated': TODAY,
    },
    'merry-care-desa-jaya-kepong': {
        'title': 'Merry Care Desa Jaya Kepong',
        'area': 'Taman Desa Jaya',
        'state': 'Kuala Lumpur',
        'phone': CHAIN_PHONE,
        'website': 'https://www.elderlycare.my/merry-care/merry-care-desa-jaya-kepong',
        'pricing_display': 'From RM 2,500/mo',
        'shared_price': 'RM 2,500',
        'google_maps_url': maps_url(DJ_ADDR),
        'hero_image': DJ_PHOTOS[0],
        'photos': '|'.join(DJ_PHOTOS),
        'photo_count': str(len(DJ_PHOTOS)),
        'editorial_summary': editorial("Desa Jaya Kepong", DJ_ADDR, TAIL_DESA_JAYA),
        'last_updated': TODAY,
    },
}

PRICING_SOURCE_VALUE = (
    'elderlycare.my — starting rate RM 2,500/mo for shared room incl. 5 '
    'meals; final fee depends on care needs'
)

ALL_TOUCHED_SLUGS = list(BRANCHES.keys()) + list(NEW_ROWS.keys())

# ── Read sheet ──────────────────────────────────────────────────────────────
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

# ── In-place updates for existing 2 rows ────────────────────────────────────
batch_data = []
found = set()
for i, row in enumerate(fac_data[1:], start=2):
    if slug_i >= len(row): continue
    slug = row[slug_i].strip()
    if slug not in BRANCHES: continue
    found.add(slug)
    print(f"FAC row {i}: {slug}")
    for field, value in BRANCHES[slug].items():
        col_i = h(field)
        if col_i is None:
            print(f"  WARN: missing column '{field}'"); continue
        batch_data.append({
            'range': f"'{FAC_TAB}'!{col_letter(col_i+1)}{i}",
            'values': [[value]],
        })

for slug in BRANCHES:
    if slug not in found:
        print(f"  ⚠️  NOT FOUND: {slug}")
        sys.exit(1)

if batch_data:
    for start in range(0, len(batch_data), 100):
        ss.values().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={'valueInputOption': 'RAW', 'data': batch_data[start:start+100]}
        ).execute()
    print(f"\n✅ Applied {len(batch_data)} in-place updates")

# ── Append new rows ────────────────────────────────────────────────────────
existing_slugs = {row[slug_i].strip() for row in fac_data[1:] if len(row) > slug_i}
new_fac_rows = []
for slug, fields in NEW_ROWS.items():
    if slug in existing_slugs:
        print(f"  ⚠️  Slug already exists, skipping append: {slug}")
        continue
    full_row = [''] * len(headers)
    full_row[slug_i] = slug
    for field, value in fields.items():
        ci = h(field)
        if ci is None:
            print(f"  WARN: missing column '{field}' for {slug}"); continue
        full_row[ci] = value
    new_fac_rows.append(full_row)

if new_fac_rows:
    ss.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{FAC_TAB}'!A:A",
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body={'values': new_fac_rows},
    ).execute()
    print(f"\n✅ Appended {len(new_fac_rows)} new facility rows")

# ── Append Details: Pricing source row per branch ───────────────────────────
details_data = ss.values().get(
    spreadsheetId=SPREADSHEET_ID, range=f"'{DETAILS_TAB}'"
).execute().get('values', [])
existing_keys = {(r[0], r[1], r[2]) for r in details_data[1:] if len(r) >= 3}

new_detail_rows = []
for slug in ALL_TOUCHED_SLUGS:
    key = (slug, 'rooms', 'Pricing source')
    if key not in existing_keys:
        new_detail_rows.append([slug, 'rooms', 'Pricing source', PRICING_SOURCE_VALUE])

if new_detail_rows:
    ss.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{DETAILS_TAB}'!A:D",
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body={'values': new_detail_rows},
    ).execute()
    print(f"\n✅ Appended {len(new_detail_rows)} Details rows")

print("\n🎉 Merry Care chain update complete.")
print("Touched slugs:")
for s in ALL_TOUCHED_SLUGS:
    print(f"  - {s}")
