"""
Apply AustinLoyal Care Centre editorial revision.

Changes:
1. Rewrite editorial_summary to reflect verified info from austinloyal.com
   (services, registration, hours) and the temporal pattern of Google reviews
   (negatives cluster in 2018 launch period; recent reviews positive).
2. Update visiting_hours and last_updated.
3. Append Details rows: registration, services, outpatient physio hours,
   pricing source.
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
SLUG          = 'austinloyal-care-centre'

creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
service = build('sheets', 'v4', credentials=creds)
ss = service.spreadsheets()

NEW_EDITORIAL = (
    "AustinLoyal Care Centre operates from a corner lot at 1, Jalan Mutiara Emas "
    "3/4 in Taman Mount Austin, a busy urban pocket of JB with hospitals, clinics, "
    "schools, and shops within a few minutes' drive. The home is run by AUSTINLOYAL "
    "SDN BHD (1142053-H) and soft-launched in March 2018, positioning itself as an "
    "\"urban care retreat\" — a modern, non-institutional alternative to traditional "
    "nursing homes, with a stated emphasis on rehabilitation and dignity rather than "
    "custodial care. The published service mix is broader than most JB homes its "
    "size: long-term residential care, short-term and respite stays, post-hospital "
    "rehabilitative care, adult social day care, and an outpatient physiotherapy "
    "clinic that runs weekdays 10am–6pm and is open to non-residents.\n\n"
    "A quirk worth understanding before you read the Google rating: the aggregate "
    "score sits at 1.9 across 260+ reviews, but the negative reviews cluster around "
    "the 2018–2019 opening period, while recent reviews trend positive. The rating "
    "is a stale snapshot of the facility's growing pains, not its current state — "
    "which is why we encourage families to filter Google reviews by \"newest\" "
    "before forming a view, rather than reading the headline number. Visiting hours "
    "are weekends and public holidays 12:30–4:30pm; weekday visits are by "
    "appointment, which the operator frames as a resident-privacy policy.\n\n"
    "What is not published is room configurations, monthly fees, capacity, JKM "
    "licence number, doctor visit frequency, and overnight nurse-to-resident ratio — "
    "so these belong on a tour or call. Useful questions for the enquiry: which "
    "care levels are accepted today (skilled nursing, dementia, palliative, "
    "tube-feeding via NG/PEG); the ratio of trained nurses to residents in the day "
    "and overnight; whether the visiting doctor is in-house or on-call and how "
    "often they round; whether physiotherapy is included or charged per session "
    "for residents; and a written, itemised quote covering room rate, diapers, "
    "medications, and supplements before any deposit."
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
    'visiting_hours': 'Sat/Sun & public holidays 12:30pm–4:30pm; weekdays by appointment',
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
# 2. Apply Facilities updates
# ---------------------------------------------------------------------------
if batch_data:
    ss.values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={'valueInputOption': 'RAW', 'data': batch_data}
    ).execute()
    print(f"\n✅ Applied {len(batch_data)} in-place updates")

# ---------------------------------------------------------------------------
# 3. Append new Details rows
# ---------------------------------------------------------------------------
details_data = ss.values().get(
    spreadsheetId=SPREADSHEET_ID, range=f"'{DETAILS_TAB}'"
).execute().get('values', [])

NEW_ROWS = [
    [SLUG, 'policies', 'Address', '1, Jalan Mutiara Emas 3/4, Taman Mount Austin, 81100 Johor Bahru'],
    [SLUG, 'policies', 'Operator', 'AUSTINLOYAL SDN BHD (1142053-H)'],
    [SLUG, 'policies', 'Opened', 'March 2018 (soft launch)'],
    [SLUG, 'policies', 'Visiting hours', 'Sat/Sun & PH 12:30pm–4:30pm; weekdays by appointment'],
    [SLUG, 'policies', 'Outpatient physio hours', 'Mon–Fri 10:00am–6:00pm (open to non-residents)'],
    [SLUG, 'services', 'Long-term residential care', 'yes'],
    [SLUG, 'services', 'Short-term / respite stays', 'yes'],
    [SLUG, 'services', 'Post-hospital rehabilitative care', 'yes'],
    [SLUG, 'services', 'Adult social day care', 'yes'],
    [SLUG, 'services', 'Outpatient physiotherapy clinic', 'yes — open to non-residents'],
    [SLUG, 'checklist', 'Filter Google reviews by "newest" — most negatives are from 2018–2019 launch period', ''],
    [SLUG, 'checklist', 'Ask for JKM licence number and a copy of the most recent inspection result', ''],
    [SLUG, 'checklist', 'Ask whether physiotherapy is included or billed per session for residents', ''],
]

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
