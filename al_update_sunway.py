"""Update existing Sunway Sanctuary row (sheet_row=419, currently unverified).

Sets: care_category=Assisted Living, status=blank (live), phone, website, editorial.
Keeps existing title/area/care_types.
"""
import os, sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'token_sheets.json')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
TAB = 'google-sheets-facilities.csv'

SUNWAY_SANCTUARY_ED = (
    "Sunway Sanctuary is the senior-living arm of Sunway Group's integrated township "
    "in Bandar Sunway, Selangor - a purpose-built community offering hotel-grade "
    "apartments and suites for older adults who want to remain independent while "
    "having medical backup nearby. The community is annexed to Sunway Medical Centre, "
    "which is the practical reason most families consider it: residents have priority "
    "access to one of the country's largest private hospitals without leaving the "
    "compound. Suites are configured for ageing-in-place - wide doorways, level "
    "thresholds, grab rails as standard - and the campus shares amenities with the "
    "wider Sunway township, putting the pyramid mall, monorail, and parks within a "
    "covered walkway. "
    "\n\n"
    "Daily life leans active rather than clinical. Residents have a calendar of group "
    "exercise, art and music programmes, and outings; meals are served in a communal "
    "dining room with dietary options. The community is licensed and openly published "
    "as part of Sunway's healthcare arm, which is unusual transparency for the segment "
    "and helpful for families used to opaque smaller operators. "
    "\n\n"
    "Pricing sits at the premium end of the Klang Valley AL market - expect five-figure "
    "monthly fees with the model evolving (some suites have been offered as memberships "
    "rather than month-to-month rentals), so the financial model is the question to ask "
    "first on a tour. Other call-time questions: what happens if a resident's care "
    "needs escalate beyond AL (does the community have a nursing wing, or is the "
    "transfer path to Sunway Medical and then out), what is and isn't included in the "
    "fee (utilities, meal tiers, additional carer hours), and minimum tenancy."
)

ROW = 419   # Sunway Sanctuary
UPDATES = [
    {'range': f"'{TAB}'!E{ROW}",  'values': [['+60 3-7491 9191']]},                         # phone
    {'range': f"'{TAB}'!F{ROW}",  'values': [['https://www.sunwaymedical.com/sunway-sanctuary']]},  # website
    {'range': f"'{TAB}'!AY{ROW}", 'values': [[SUNWAY_SANCTUARY_ED]]},                       # editorial_summary (col 51)
    {'range': f"'{TAB}'!BD{ROW}", 'values': [['']]},                                        # status → live
    {'range': f"'{TAB}'!BE{ROW}", 'values': [['Assisted Living']]},                         # care_category
]

creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
sheet = build('sheets', 'v4', credentials=creds).spreadsheets()

# Verify the row before writing
res = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=f"'{TAB}'!A{ROW}:BE{ROW}").execute()
got = res.get('values', [[]])[0]
title = got[0] if got else ''
slug = got[1] if len(got) > 1 else ''
print(f"Updating row {ROW}: title={title!r}, slug={slug!r}")
assert slug == 'sunway-sanctuary', f"Slug mismatch at row {ROW}: got {slug!r}"

sheet.values().batchUpdate(
    spreadsheetId=SPREADSHEET_ID,
    body={'valueInputOption': 'RAW', 'data': UPDATES},
).execute()
print(f"  Updated {len(UPDATES)} cells.")
