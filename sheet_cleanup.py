"""Sheet cleanup based on flags raised during profile research batches 1-6.

Actions:
1. Set status='removed' for non-NH entries (3 rows)
2. Set status='unverified' for facility with dead website + no third-party content (1 row)
3. Fix state column for facilities tagged with wrong state (6 rows)

Columns:
- state: BC (index 54)
- status: BD (index 55)
"""
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE = 'token_sheets.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
TAB = 'google-sheets-facilities.csv'

# (row_idx, slug, status_value)
STATUS_UPDATES = [
    (337, 'acg-care-sdn-bhd', 'removed'),                       # corporate entity, not NH
    (401, 'rumah-ozanam', 'removed'),                           # children's home (St Vincent de Paul)
    (407, 'nurses-at-home', 'removed'),                         # home-nursing service, not residential
    (362, 'green-cottage-retirement-and-nursing-home', 'unverified'),  # website dead, no third-party content
]

# (row_idx, slug, new_state)
STATE_UPDATES = [
    (336, 'afh-elder-care',                          'Kuala Lumpur'),  # postcode 52100
    (339, 'amitabha-malaysia-old-folks-home-kl',     'Kuala Lumpur'),  # Happy Garden 58200
    (341, 'dhaalia-elderly-care-centre',             'Kuala Lumpur'),  # 58000
    (343, 'merry-care-centre-jln-antoi',             'Kuala Lumpur'),  # Kepong Baru is KL
    (345, 'rumah-orang-tua-charis',                  'Kuala Lumpur'),  # Taman Lucky 58200
    (12,  'multicare-nursing-home-johor',            'Selangor'),      # actually in PJ
]


def main():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    updates = []
    for row, slug, val in STATUS_UPDATES:
        rng = f"'{TAB}'!BD{row}"
        updates.append({'range': rng, 'values': [[val]]})
        print(f"STATUS BD{row} = '{val}'  ({slug})")

    for row, slug, val in STATE_UPDATES:
        rng = f"'{TAB}'!BC{row}"
        updates.append({'range': rng, 'values': [[val]]})
        print(f"STATE  BC{row} = '{val}'  ({slug})")

    body = {'valueInputOption': 'RAW', 'data': updates}
    resp = sheet.values().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
    print(f"\nUpdated {resp.get('totalUpdatedCells', 0)} cells across {len(updates)} ranges.")


if __name__ == '__main__':
    main()
