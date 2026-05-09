"""
write_johor_editorials.py — standalone editorial writer for Johor facilities.
"""
import json, re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE     = 'token_sheets.json'
SCOPES         = ['https://www.googleapis.com/auth/spreadsheets']
TAB            = 'google-sheets-facilities.csv'

CARE_MAP = {
    'nursing home': 'nursing home', 'assisted living': 'assisted living centre',
    'old people': 'care home for elderly residents', 'retirement': 'retirement home',
    'rehabilitation': 'rehabilitation centre', 'home health': 'home care service',
    'home care': 'home care service', 'day care': 'senior day care centre',
    'hospice': 'hospice care centre', 'dementia': 'dementia care home',
    'palliative': 'palliative care centre', 'welfare': 'welfare home',
    'shelter': 'residential shelter', 'respite': 'respite care centre',
}

def care_label(ct):
    if not ct:
        return 'care home'
    ct_l = ct.lower()
    for k, v in CARE_MAP.items():
        if k in ct_l:
            return v
    return 'care home'

def location(area, state):
    skip = {state.lower(), 'wilayah persekutuan', 'wp', ''}
    if not area or area.lower() in skip:
        return state
    return f"{area}, {state}"

def write_editorial(r):
    cl   = care_label(r.get('care_types',''))
    loc  = location(r.get('area',''), r['state'])
    art  = 'an' if cl[0] in 'aeiou' else 'a'
    parts = [f"{r['title']} is {art} {cl} located in {loc}."]

    try:
        b = int(r.get('total_beds',''))
        if b > 0:
            parts.append(f"The home accommodates up to {b} residents.")
    except: pass

    try:
        rat = float(r.get('rating',''))
        rc  = int(r.get('review_count','') or 0)
        if rat > 0:
            if rc > 0:
                parts.append(f"It holds a {rat:.1f}/5 rating on Google Maps from {rc:,} reviews.")
            else:
                parts.append(f"It holds a {rat:.1f}/5 rating on Google Maps.")
    except: pass

    sub = (r.get('subsidy','') or '').lower()
    if any(w in sub for w in ['yes','available','jkm','government','subsidised','subsidized','oku']):
        parts.append('Subsidised placement may be available for eligible residents.')

    return ' '.join(parts)


facilities = json.load(open('johor_no_editorial.json', encoding='utf-8'))
print(f"Writing editorials for {len(facilities)} Johor facilities")
print()

creds   = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
service = build('sheets', 'v4', credentials=creds)
ss      = service.spreadsheets()

data    = ss.values().get(spreadsheetId=SPREADSHEET_ID, range=f"'{TAB}'").execute().get('values',[])
headers = data[0]
col     = {h:i for i,h in enumerate(headers)}
ed_col  = col['editorial_summary']
col_letter = chr(64 + ed_col + 1)

updates = []
for r in facilities:
    ed = write_editorial(r)
    print(f"  {r['title'][:50]}")
    print(f"  -> {ed}")
    print()
    updates.append({'range': f"'{TAB}'!{col_letter}{r['row_idx']}", 'values': [[ed]]})

body = {'valueInputOption': 'RAW', 'data': updates}
result = ss.values().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
print(f"Done. {result.get('totalUpdatedCells', 0)} editorials written.")
