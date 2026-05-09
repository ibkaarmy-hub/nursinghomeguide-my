"""Fill missing KL editorial_summary stubs for 56 facilities.

Stub format: 2-3 sentences using title, care_types, area, phone.
"""
import urllib.request, csv, io, re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE = 'token_sheets.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
TAB = 'google-sheets-facilities.csv'
CSV_URL = 'https://docs.google.com/spreadsheets/d/1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk/export?format=csv&gid=292378871'

CARE_LABELS = {
    'nursing home': 'a nursing home',
    'assisted living facility': 'an assisted living facility',
    'retirement home': 'a retirement home',
    'home health care service': 'a home health care service',
    'home help service agency': 'a home help service agency',
    'rehabilitation center': 'a rehabilitation centre',
    'hospice': 'a hospice',
    'medical clinic': 'a medical clinic',
    'registered general nurse': 'a registered nurse provider',
    'service establishment': 'a care provider',
    'local medical services': 'a local medical service',
    'aged care': 'an aged care provider',
}

def clean_care_types(raw):
    """Pick the most relevant care label from a comma-separated raw string."""
    if not raw:
        return 'a senior care provider'
    parts = [p.strip().lower() for p in raw.split(',')]
    for p in parts:
        if p in CARE_LABELS:
            return CARE_LABELS[p]
    # fallback: first part lower-cased
    first = parts[0]
    article = 'an' if first[:1] in 'aeiou' else 'a'
    return f'{article} {first}'

def format_area(area, state):
    """Avoid 'Kuala Lumpur, Kuala Lumpur' redundancy."""
    a = (area or '').strip()
    if not a or a.lower() in ('kuala lumpur', state.lower(), 'wilayah persekutuan'):
        return state
    return f'{a}, {state}'

def make_stub(row):
    title = row.get('title', '').strip()
    care = clean_care_types(row.get('care_types', ''))
    area = format_area(row.get('area', ''), row.get('state', 'Kuala Lumpur'))
    phone = (row.get('phone', '') or '').strip()
    rating = (row.get('rating', '') or '').strip()
    review_count = (row.get('review_count', '') or '').strip()

    s1 = f"{title} is {care} based in {area}."
    s2 = "Specific clinical capabilities, staffing details, pricing, and admission criteria have not yet been verified — families should call directly to confirm services and current availability."
    bits = []
    if phone:
        bits.append(f"the facility on {phone}")
    s3_lead = "Contact " + " or ".join(bits) if bits else "Contact the facility"

    if rating and review_count:
        try:
            r = float(rating); rc = int(review_count)
            if rc >= 5:
                s4 = f" Google reviews currently average {r:.1f} stars across {rc} reviews — a useful starting reference, though we recommend reading the actual review content before deciding."
            else:
                s4 = f" Only {rc} Google review{'s' if rc != 1 else ''} are available so far, so the rating ({r:.1f} stars) is not yet a reliable signal."
        except Exception:
            s4 = ""
    else:
        s4 = " No Google reviews are available yet."

    return f"{s1} {s2} {s3_lead} for fees, room types, visiting hours, and JKM licence verification.{s4}"


def main():
    data = urllib.request.urlopen(CSV_URL).read().decode('utf-8')
    reader = list(csv.DictReader(io.StringIO(data)))

    # Find KL live rows with empty editorial_summary
    targets = []
    for idx, r in enumerate(reader, start=2):  # row 2 is first data row (sheet 1-indexed, header=row 1)
        if r.get('state','').strip() != 'Kuala Lumpur':
            continue
        if r.get('status','').strip() != '':
            continue
        if (r.get('editorial_summary','') or '').strip():
            continue
        targets.append((idx, r))

    print(f'Found {len(targets)} KL rows needing stub editorials')

    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    updates = []
    for row_idx, r in targets:
        stub = make_stub(r)
        rng = f"'{TAB}'!AY{row_idx}"
        updates.append({'range': rng, 'values': [[stub]]})
        try:
            print(f'  AY{row_idx} {r["slug"][:50]:50s} ({len(stub)} chars)')
        except UnicodeEncodeError:
            print(f'  AY{row_idx} <unicode-slug> ({len(stub)} chars)')

    if updates:
        body = {'valueInputOption': 'RAW', 'data': updates}
        resp = sheet.values().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
        print(f'\nUpdated {resp.get("totalUpdatedCells", 0)} cells.')

if __name__ == '__main__':
    main()
