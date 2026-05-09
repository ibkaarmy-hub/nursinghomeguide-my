"""
Update script for: sunrise-care-centre-sdn-bhd
Sheet row: 58
Generated: 2026-05-10
"""

import sys
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout.reconfigure(encoding='utf-8')

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_PATH = r'C:\Users\ibkaa\nursinghomeguide-my\Nursing Home Guide Malaysia\token_sheets.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
FACILITIES_TAB = 'google-sheets-facilities.csv'
DETAILS_TAB = 'Details'

SLUG = 'sunrise-care-centre-sdn-bhd'
SHEET_ROW = 58  # 1-based, row 1 = header

# ── Editorial ──────────────────────────────────────────────────────────────────

EDITORIAL = """Sunrise Care Centre Sdn Bhd (Co. 567396-U) is one of two residential care centres operated by the Rebina Sunrise Elderly Care group, a family-owned operator that has been running nursing care in Johor Bahru since 2003. The facility sits at No. 48 Jalan Keranji in Taman Kebun Teh — a quiet residential neighbourhood — directly across from the group's founding home, Rebina House, at Nos. 15 & 17 on the same road. The group's stated origin story is practical: at founding, fewer than 30 care centres served a Johor Bahru population of nearly half a million, and the founders set out to fill that gap with reliable, no-frills care.

The clinical list documented on the group's website is unusually detailed for a residential home of this size. Confirmed services include Continuous Ambulatory Peritoneal Dialysis (CAPD), Ryle's tube feeding and replacement, phlegm suction, nebuliser therapy, oxygen supply, balloon catheter management, post-operative wound dressing, acupuncture, physiotherapy, and daily monitoring of blood pressure and glucose. Palliative and hospice care is also offered. Staff document individualised care plans with hourly schedules — a practice more commonly associated with step-down hospital wards than small community homes. The Instagram account shows Klinik Kesihatan Larkin doctors and nurses visiting the centres to conduct routine dental check-ups for residents, indicating an active public health partnership.

Pricing is not published on the rebinasunrise.com website; families should call +60 7-333 7715 or email care@rebinasunrise.com to request a quote. Gallery photos and social media posts show a busy activities programme — games sessions, seasonal celebrations spanning Chinese New Year, Deepavali, Eid, and Christmas — and regular community visits, giving the home a well-used, lived-in character. The facility accepts residents of all religions and backgrounds.

**What to ask on visit:**
- What is the monthly fee for the level of care needed, and what is included?
- Is the JKM or MOH registration certificate available to view?
- Which specific clinical services (CAPD, PEG feeding) are available at this branch versus Rebina House?
- What is the nursing staff ratio during day and night shifts?
- Are beds currently available, and what is the typical waiting time?"""

# Pre-flight check
assert '"' not in EDITORIAL, "Straight double-quote found in editorial — aborting"

# ── Photo fields ────────────────────────────────────────────────────────────────

WIX_PHOTOS = [
    'https://static.wixstatic.com/media/3f4314_15cc1d57ce24466a944b476aa7d502dd~mv2.jpeg',
    'https://static.wixstatic.com/media/3f4314_41d0f86fbcdf4986b2f787104f453d05~mv2.jpeg',
    'https://static.wixstatic.com/media/3f4314_536ebef4c67e4ffa8d755e05e2825cea~mv2.jpg',
    'https://static.wixstatic.com/media/3f4314_ae68941ab62c4ba6bc42208437fd86e5~mv2.jpg',
    'https://static.wixstatic.com/media/3f4314_7ad328f7189f42edb2524e24c335814d~mv2.jpg',
    'https://static.wixstatic.com/media/3f4314_003128c49023499a8b2421374e7841a3~mv2.jpg',
    'https://static.wixstatic.com/media/3f4314_07e8bc2c19754d3c8bcfee340b84d72e~mv2.jpg',
    'https://static.wixstatic.com/media/3f4314_ad2516df503948948403737568ef64fa~mv2.jpg',
]

GOOGLE_PHOTOS = [
    'https://lh3.googleusercontent.com/p/AF1QipOcfPmt3gwKXxeiTV9DRwCVtfy7OYCAhRUgx355=w1920-h1080-k-no',
    'https://lh3.googleusercontent.com/p/AF1QipM7-Cj2WqVP196sb-9dV9mGfQwrUCM1gZ_mXL2G=w1920-h1080-k-no',
    'https://lh3.googleusercontent.com/p/AF1QipNaVG5VXk_kMLrB5ppCupIzIdbnADCo_Qv1pNyQ=w1920-h1080-k-no',
    'https://lh3.googleusercontent.com/p/AF1QipP6958I6-_QwKemQMbzFNthDB3G-_6gKEQAr_w-=w1920-h1080-k-no',
    'https://lh3.googleusercontent.com/p/AF1QipPd6av0hFzWdgwWqTXLposAmapkOcax2B_xR1f0=w1920-h1080-k-no',
    'https://lh3.googleusercontent.com/p/AF1QipPYPkmRYJjbBsQVPjH04hbftw2UYUEksawaRWhy=w1920-h1080-k-no',
    'https://lh3.googleusercontent.com/p/AF1QipMIwvBSS7jC0UTpr5L4oF-EFoejdks9rD55QnnX=w1920-h1080-k-no',
]

ALL_PHOTOS = WIX_PHOTOS + GOOGLE_PHOTOS
NEW_HERO = WIX_PHOTOS[0]
PHOTOS_STR = '|'.join(ALL_PHOTOS)
PHOTO_COUNT = str(len(ALL_PHOTOS))

# ── Details rows ────────────────────────────────────────────────────────────────

DETAILS_ROWS = [
    # Address
    [SLUG, 'policies', 'Address', '48 Jalan Keranji, Taman Kebun Teh, 80250 Johor Bahru, Johor'],
    [SLUG, 'policies', 'Company registration', 'Sunrise Care Centre Sdn Bhd (Co. 567396-U)'],
    [SLUG, 'policies', 'Visiting hours', 'Monday to Sunday, 9:00 AM – 5:00 PM'],
    # Clinical services
    [SLUG, 'clinical', 'CAPD peritoneal dialysis', 'yes'],
    [SLUG, 'clinical', 'Ryle\'s tube feeding', 'yes'],
    [SLUG, 'clinical', 'Phlegm suction', 'yes'],
    [SLUG, 'clinical', 'Nebuliser therapy', 'yes'],
    [SLUG, 'clinical', 'Oxygen supply', 'yes'],
    [SLUG, 'clinical', 'Balloon catheter management', 'yes'],
    [SLUG, 'clinical', 'Post-operative wound dressing', 'yes'],
    [SLUG, 'clinical', 'Acupuncture', 'yes'],
    [SLUG, 'clinical', 'Physiotherapy', 'yes'],
    [SLUG, 'clinical', 'BP & glucose monitoring', 'Daily'],
    [SLUG, 'clinical', 'Palliative / hospice care', 'yes'],
    # Staffing
    [SLUG, 'staffing', 'Individualised care plans', 'Yes — hourly schedule documented'],
    # Rooms / pricing
    [SLUG, 'rooms', 'Pricing source', 'Not published on operator site (rebinasunrise.com) — call +60 7-333 7715 or email care@rebinasunrise.com'],
    # Activities
    [SLUG, 'activities', 'Seasonal celebrations', 'Chinese New Year, Deepavali, Eid, Christmas'],
    [SLUG, 'activities', 'Group games sessions', 'yes'],
    [SLUG, 'activities', 'Community / volunteer visits', 'yes'],
    # Nearby
    [SLUG, 'nearby', 'Klinik Kesihatan Larkin', 'Routine dental checks conducted at facility'],
    [SLUG, 'nearby', 'Rebina House Care Centre (sister facility)', '15 & 17 Jalan Keranji — same road'],
    # Photo credits
    [SLUG, 'policies', 'Photo credits', 'Facility photos courtesy of rebinasunrise.com (Wix CDN)'],
]


def get_service():
    with open(TOKEN_PATH) as f:
        creds_data = json.load(f)
    creds = Credentials(
        token=creds_data.get('token'),
        refresh_token=creds_data.get('refresh_token'),
        token_uri=creds_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
        client_id=creds_data.get('client_id'),
        client_secret=creds_data.get('client_secret'),
        scopes=SCOPES,
    )
    return build('sheets', 'v4', credentials=creds)


def col_letter(headers, name):
    """Return A1 column letter for a header name (1-based index)."""
    idx = headers.index(name)
    # Convert 0-based index to column letter(s)
    n = idx + 1
    result = ''
    while n:
        n, rem = divmod(n - 1, 26)
        result = chr(65 + rem) + result
    return result


def main():
    service = get_service()
    sheet = service.spreadsheets()

    # 1. Read headers row
    header_range = f"'{FACILITIES_TAB}'!1:1"
    headers_resp = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=header_range,
    ).execute()
    headers = headers_resp['values'][0]

    print(f"Headers loaded: {len(headers)} columns")

    # 2. Build column updates for row 58
    def cell_range(col_name):
        col = col_letter(headers, col_name)
        return f"'{FACILITIES_TAB}'!{col}{SHEET_ROW}"

    updates = [
        (cell_range('editorial_summary'), [[EDITORIAL]]),
        (cell_range('hero_image'), [[NEW_HERO]]),
        (cell_range('photos'), [[PHOTOS_STR]]),
        (cell_range('photo_count'), [[PHOTO_COUNT]]),
        (cell_range('last_updated'), [['2026-05-10']]),
        # Address from website
        (cell_range('address'), [['48 Jalan Keranji, Taman Kebun Teh, 80250 Johor Bahru, Johor']]),
        # Email from website
        (cell_range('email'), [['care@rebinasunrise.com']]),
        # care_dementia: not confirmed — leave unchanged
        # care_respite: not confirmed on website — leave unchanged
        # care_assisted: not confirmed — leave unchanged
    ]

    # Check if address and email columns exist
    optional_cols = ['address', 'email']
    for col_name, value in [('address', '48 Jalan Keranji, Taman Kebun Teh, 80250 Johor Bahru, Johor'), ('email', 'care@rebinasunrise.com')]:
        if col_name in headers:
            updates.append((cell_range(col_name), [[value]]))
        else:
            print(f"Warning: column '{col_name}' not found in headers — skipping")

    # Remove duplicates (address/email added twice above)
    seen_ranges = set()
    deduped = []
    for rng, val in updates:
        if rng not in seen_ranges:
            seen_ranges.add(rng)
            deduped.append((rng, val))
    updates = deduped

    print(f"\nApplying {len(updates)} cell updates to row {SHEET_ROW}...")
    for rng, val in updates:
        sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=rng,
            valueInputOption='RAW',
            body={'values': val},
        ).execute()
        col_display = rng.split('!')[-1]
        preview = str(val[0][0])[:80].replace('\n', ' ')
        print(f"  Updated {col_display}: {preview}")

    # 3. Append Details rows
    print(f"\nAppending {len(DETAILS_ROWS)} Details rows...")

    # First, check existing Details rows for this slug to avoid duplicates
    details_resp = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{DETAILS_TAB}'!A:D",
    ).execute()
    existing_rows = details_resp.get('values', [])

    existing_keys = set()
    for row in existing_rows[1:]:  # skip header
        if len(row) >= 3 and row[0] == SLUG:
            existing_keys.add((row[0], row[1] if len(row) > 1 else '', row[2] if len(row) > 2 else ''))

    new_rows = []
    for r in DETAILS_ROWS:
        key = (r[0], r[1], r[2])
        if key not in existing_keys:
            new_rows.append(r)
        else:
            print(f"  Skipping duplicate: {r[1]}/{r[2]}")

    if new_rows:
        sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=f"'{DETAILS_TAB}'!A:D",
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body={'values': new_rows},
        ).execute()
        print(f"  Appended {len(new_rows)} new Details rows")
    else:
        print("  No new Details rows to append (all already exist)")

    print("\nDone! All updates applied successfully.")


if __name__ == '__main__':
    main()
