"""
Apply EHA Golfview editorial revision per session 2026-05-02 feedback rules.

Changes:
1. Rewrite editorial_summary (remove contact info; add operator-website services + pricing).
2. Clear shared_price (RM 1,300 was a Kluang day-care rate, semantically wrong for JB).
3. Update last_updated.
4. Update 3 existing Details `rooms` rows: relabel to "(from RM/...)" to make
   "starting price" explicit.
5. Append 3 new Details rows: Alternative phone, Email, Pricing source.
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
SLUG          = 'eha-golfview-eldercare-mansion-johor-jaya-1-nursing-home-joh'

creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
service = build('sheets', 'v4', credentials=creds)
ss = service.spreadsheets()

NEW_EDITORIAL = (
    "EHA Golfview Eldercare Mansion is the Johor Jaya branch of EHA Eldercare Group, "
    "sited unusually within the grounds of Daiman 18 Golf Club at 85, Jalan Pesona, "
    "Taman Johor Jaya. The parent group, EHA Eldercare (1478860-U), evolved from the "
    "Justlife ElderCare Home brand founded in 2009 and now runs eight residential "
    "locations across Malaysia with a combined 100-plus caregivers and 500-plus "
    "residents — making it one of the more established private eldercare chains "
    "across Johor and the Klang Valley.\n\n"
    "The group's website lists eight published service categories that apply across "
    "branches: medical support, nutrition and diet, rehabilitation by physiotherapy, "
    "social activities, caregiver training and support, skilled nurses, special "
    "nursing procedures, and a traditional Chinese medicine approach (acupuncture and "
    "herbal). Pricing is published on EHA's website and is quoted as a starting "
    "point — actual fees vary with the resident's care needs. For the Johor Bahru "
    "branches (which include Golfview), assisted senior living starts at RM 3,200/"
    "month for 24-hour residential care across able-bodied, semi-able-bodied, and "
    "bed-bound residents; respite stays of one to six months start at RM 120/day; "
    "and day care, available 11 hours a day across five days a week with flexible "
    "timing, starts at RM 1,500/month. Kluang branch rates are noticeably lower "
    "(assisted living from RM 2,300/month, respite from RM 80/day, day care from "
    "RM 1,300/month) — useful context if cost is a major factor and the family can "
    "travel. Bed count and current room availability are not published online.\n\n"
    "Golfview's marketing emphasises landscaped grounds and lounge space inside the "
    "golf-club precinct, on-site meal preparation tailored to dietary needs, and a "
    "24/7 caregiving roster. The branch is associated with post-stroke rehabilitation "
    "in third-party listings, but EHA's own site does not publish stroke-specific "
    "protocols, therapist staffing, or rehab equipment lists. On a viewing it's "
    "worth asking how often a physiotherapist attends in person, who supervises "
    "exercise programmes on non-therapist days, and what specific clinical procedures "
    "the home performs in-house versus refers out (PEG feeds, suction, oxygen, wound "
    "dressings, urinary catheter changes). Confirm whether the published \"starting "
    "from\" rate matches the level of care your family member actually needs, since "
    "add-ons can shift the monthly figure significantly. Hospital Sultan Ismail is "
    "the nearest tertiary centre."
)

# ---------------------------------------------------------------------------
# 1. Facilities-tab updates
# ---------------------------------------------------------------------------
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

target_row = None
for i, row in enumerate(fac_data[1:], start=2):
    if slug_i < len(row) and row[slug_i].strip() == SLUG:
        target_row = i
        break

if target_row is None:
    print(f"ERROR: slug not found: {SLUG}")
    sys.exit(1)

print(f"Found facilities row at line {target_row}")

TODAY = str(date.today())
fac_updates = {
    'editorial_summary': NEW_EDITORIAL,
    'shared_price': '',
    'last_updated': TODAY,
}

batch_data = []
for field, value in fac_updates.items():
    col_i = h(field)
    if col_i is None:
        print(f"  WARN: column '{field}' not in headers")
        continue
    batch_data.append({
        'range': f"'{FAC_TAB}'!{col_letter(col_i+1)}{target_row}",
        'values': [[value]]
    })
    print(f"  → queue update {field} = {repr(value)[:80]}")

# ---------------------------------------------------------------------------
# 2. Details-tab updates: relabel 3 existing rooms rows
# ---------------------------------------------------------------------------
details_data = ss.values().get(
    spreadsheetId=SPREADSHEET_ID, range=f"'{DETAILS_TAB}'"
).execute().get('values', [])

# header is: slug, section, label, value
RELABEL_MAP = {
    ('rooms', 'Assisted Living (RM/mo)'):       'Assisted Living (from RM/mo)',
    ('rooms', 'Respite / Short-term (RM/day)'): 'Respite / Short-term (from RM/day)',
    ('rooms', 'Day Care (RM/mo)'):              'Day Care (from RM/mo)',
}

for i, row in enumerate(details_data[1:], start=2):
    if len(row) < 4: continue
    if row[0] != SLUG: continue
    key = (row[1], row[2])
    if key in RELABEL_MAP:
        new_label = RELABEL_MAP[key]
        batch_data.append({
            'range': f"'{DETAILS_TAB}'!C{i}",
            'values': [[new_label]]
        })
        print(f"  → relabel Details row {i}: '{row[2]}' → '{new_label}'")

# ---------------------------------------------------------------------------
# 3. Apply all in-place updates
# ---------------------------------------------------------------------------
if batch_data:
    ss.values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={'valueInputOption': 'RAW', 'data': batch_data}
    ).execute()
    print(f"\n✅ Applied {len(batch_data)} in-place updates")

# ---------------------------------------------------------------------------
# 4. Append new Details rows
# ---------------------------------------------------------------------------
NEW_ROWS = [
    [SLUG, 'policies', 'Alternative phone', '019-772 3697'],
    [SLUG, 'policies', 'Email', 'ask.ehagroup@gmail.com'],
    [SLUG, 'rooms', 'Pricing source',
        'ehaeldercare.com.my/our-packages/ — starting rates; final fee depends on care needs'],
]

# avoid duplicates
existing_keys = {(r[0], r[1], r[2]) for r in details_data[1:] if len(r) >= 3}
to_append = [r for r in NEW_ROWS if (r[0], r[1], r[2]) not in existing_keys]
skipped   = [r for r in NEW_ROWS if (r[0], r[1], r[2]) in existing_keys]

for r in skipped:
    print(f"  - skip duplicate: {r[1]}/{r[2]}")

if to_append:
    ss.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{DETAILS_TAB}'!A:D",
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body={'values': to_append}
    ).execute()
    print(f"\n✅ Appended {len(to_append)} new Details rows")

print("\n🎉 Done.")
