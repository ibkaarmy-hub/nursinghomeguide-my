"""Round 4 tone fixes - just 1 editorial needs rewriting."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE = 'token_sheets.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
TAB = 'google-sheets-facilities.csv'

FIXES = [
    (185, 'good-family-home-care',
     "Good Family Home Care is a retirement home located in Kampung Tasek Permai, Selangor. The home carries a category of retirement home, which typically signals a residential setting offering accommodation and personal care support rather than the intensive clinical nursing found in a full nursing home. Kampung Tasek Permai is a village-character area in Selangor, and a home bearing the Good Family name and this location type likely operates on a smaller, more domestic scale. The home keeps a low online profile, with the Google Maps listing as the primary point of record.\n\nThe retirement home listing suggests the facility is suited to residents who are mobile or semi-mobile and in need of a supervised residential environment rather than continuous nursing care. Whether the home can accommodate residents with higher dependency — dementia, incontinence, post-stroke immobility, or tube feeding — is best confirmed directly. Bed count, staffing levels, meals, daily programming, and pricing are all details that are best gathered on a call or in-person visit.\n\nFamilies interested in Good Family Home Care can attempt to reach the home via the Google Maps listing (which often surfaces a phone number) or through local referral networks in the Kampung Tasek Permai area. Once contact is established, useful questions: the type of care provided day-to-day, whether a registered nurse is on duty at night, the protocol when a resident's health deteriorates, and the current JKM licence number. A site visit is particularly important for smaller community-style homes — the physical environment and the warmth of staff interaction tell more than any written description."),
]

def main():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    sheet = build('sheets', 'v4', credentials=creds).spreadsheets()
    data = []
    for row, slug, ed in FIXES:
        data.append({'range': f"'{TAB}'!AY{row}", 'values': [[ed]]})
        print(f'  AY{row}  {slug:50s}  ({len(ed.split())}w)')
    body = {'valueInputOption': 'RAW', 'data': data}
    resp = sheet.values().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
    print(f"\nUpdated {resp.get('totalUpdatedCells')} cells.")

if __name__ == '__main__':
    main()
