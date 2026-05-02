"""Hand-fix Genesis Life Care Centre Puchong — single-profile update.

Operator sources:
  https://genesiscare.com.my/
  https://genesiscare.com.my/nursing-home-in-puchong
  https://genesiscare.com.my/our-services

Rules (locked 2026-05-02 + new self-rating guard):
  - No contact info in editorial body (lives in structured columns).
  - Only operator's own factual claims about THEIR OWN facility.
  - No operator self-ratings ("best of" / listicles ranking themselves).
  - No fabricated pricing — operator publishes none, so editorial says so.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import date

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE     = 'token_sheets.json'
SCOPES         = ['https://www.googleapis.com/auth/spreadsheets']
FAC_TAB        = 'google-sheets-facilities.csv'
DETAILS_TAB    = 'Details'
SLUG           = 'genesis-life-care-centre-puchong'
TODAY          = str(date.today())

EDITORIAL = (
    "Genesis Life Care Centre Puchong sits in Taman Perindustrian Puchong, "
    "with highway access via the LDP and ELITE corridors. It is one of five "
    "Genesis Life Care branches in the Klang Valley and Johor — the others "
    "being Petaling Jaya, Klang, Kajang and Johor Bahru — operating under a "
    "chain that the operator describes as Ministry-approved and JKM-"
    "registered. The Puchong centre opened in 2022 and is the chain's "
    "largest single site, with the operator stating capacity for 120+ "
    "residents."
    "\n\n"
    "The published service mix covers six categories: Nursing Home Care, "
    "Dementia & Memory Care, Stroke Rehabilitation, Palliative Care, Post-"
    "Operative Recovery, and Senior Day Care. The dementia programme is "
    "described as psychologist-led, with structured cognitive stimulation "
    "activities. Stroke rehabilitation is delivered through dedicated "
    "physiotherapy and occupational therapy. Across all care levels the "
    "operator lists 24/7 nursing supervision, weekly doctor consultations, "
    "dietician-supervised meals, medication management and personalised "
    "care plans. Senior Day Care typically runs 8am–5pm on weekdays and is "
    "useful for families not yet ready for full residential placement."
    "\n\n"
    "Pricing is not posted on the Genesis Life Care website for any branch "
    "— final monthly fees depend on care level and room type, so request a "
    "written quote during your visit. Because the Puchong site is large "
    "and stroke rehab and dementia care are headline services, two "
    "questions are worth asking on viewing: what the night-shift nurse-to-"
    "resident ratio looks like at full occupancy, and whether residents "
    "with advanced dementia share common areas or are managed in a "
    "dedicated wing. Day care availability also makes the centre worth "
    "considering as a staged option before full admission."
)

WEBSITE_URL = 'https://genesiscare.com.my/nursing-home-in-puchong'

FAC_UPDATES = {
    'editorial_summary': EDITORIAL,
    'website':           WEBSITE_URL,
    'longitude':         '',         # clear stray editorial text
    'last_updated':      TODAY,
}

# Details rows to add (skip if already present)
NEW_DETAILS = [
    ('rooms',    'Operator-stated capacity', '120+ beds'),
    ('rooms',    'Pricing source',           'Not published on operator site (genesiscare.com.my) — request a written quote during your visit'),
    ('services', 'Nursing Home Care',                       'yes'),
    ('services', 'Dementia & Memory Care',                  'Psychologist-led, cognitive stimulation activities'),
    ('services', 'Stroke Rehabilitation',                   'Physiotherapy + occupational therapy'),
    ('services', 'Palliative Care',                         'yes'),
    ('services', 'Post-Operative Recovery',                 'Short-term, typically 2–8 weeks'),
    ('services', 'Senior Day Care',                         '8am–5pm weekdays'),
]

creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
service = build('sheets', 'v4', credentials=creds)
ss = service.spreadsheets()

# ─── Facilities tab ─────────────────────────────────────────────────────
fac = ss.values().get(spreadsheetId=SPREADSHEET_ID, range=f"'{FAC_TAB}'").execute().get('values', [])
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
row_n = None
for i, row in enumerate(fac[1:], start=2):
    if slug_i < len(row) and row[slug_i].strip() == SLUG:
        row_n = i
        break
if row_n is None:
    print(f"❌ Slug not found: {SLUG}"); sys.exit(1)
print(f"FAC row {row_n}: {SLUG}")

for field, value in FAC_UPDATES.items():
    ci = h(field)
    if ci is None:
        print(f"  WARN: missing col '{field}'"); continue
    batch.append({
        'range': f"'{FAC_TAB}'!{col_letter(ci+1)}{row_n}",
        'values': [[value]],
    })

ss.values().batchUpdate(
    spreadsheetId=SPREADSHEET_ID,
    body={'valueInputOption': 'RAW', 'data': batch},
).execute()
print(f"✅ Applied {len(batch)} facility-row updates")

# ─── Details tab ────────────────────────────────────────────────────────
det = ss.values().get(spreadsheetId=SPREADSHEET_ID, range=f"'{DETAILS_TAB}'").execute().get('values', [])
existing_keys = {(r[0], r[1], r[2]) for r in det[1:] if len(r) >= 3}

new_rows = []
for sec, lbl, val in NEW_DETAILS:
    if (SLUG, sec, lbl) in existing_keys:
        print(f"  skip duplicate: {sec}/{lbl}")
        continue
    new_rows.append([SLUG, sec, lbl, val])

if new_rows:
    ss.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{DETAILS_TAB}'!A:D",
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body={'values': new_rows},
    ).execute()
    print(f"✅ Appended {len(new_rows)} Details rows")
    for r in new_rows: print(f"   {r}")
else:
    print("(no new details rows)")

print("\n✨ Done.")
