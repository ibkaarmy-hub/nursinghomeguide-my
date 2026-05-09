from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE = 'token_sheets.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
FAC_TAB = 'google-sheets-facilities.csv'

creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
service = build('sheets', 'v4', credentials=creds)
ss = service.spreadsheets()

fac_data = ss.values().get(
    spreadsheetId=SPREADSHEET_ID,
    range=f"'{FAC_TAB}'"
).execute().get('values', [])

headers = fac_data[0]

def row_summary(row_num):
    row = fac_data[row_num - 1]  # -1 because fac_data includes header at index 0, row 1 = index 0... wait
    # Actually fac_data[0] = header, fac_data[1] = row 2, etc.
    row = fac_data[row_num - 1]  # row_num is 1-indexed including header
    filled = sum(1 for v in row if v.strip())
    slug = row[headers.index('slug')] if 'slug' in headers else ''
    title = row[headers.index('title')] if 'title' in headers else ''
    phone = row[headers.index('phone')] if 'phone' in headers and headers.index('phone') < len(row) else ''
    hero = row[headers.index('hero_image')] if 'hero_image' in headers and headers.index('hero_image') < len(row) else ''
    editorial = row[headers.index('editorial_summary')] if 'editorial_summary' in headers and headers.index('editorial_summary') < len(row) else ''
    return f'  slug="{slug}" | filled={filled} | phone="{phone}" | hero="{hero[:40]}" | editorial="{editorial[:50]}"'

check_rows = [56, 118, 78, 81, 123]
print('Roseville Villa:')
for r in [56, 118]:
    print(f'  Row {r}:', row_summary(r))

print('\nPusat Sri Kenangan:')
for r in [78, 81, 123]:
    print(f'  Row {r}:', row_summary(r))
