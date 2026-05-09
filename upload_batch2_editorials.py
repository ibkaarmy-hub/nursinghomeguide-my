"""Upload batch 2 editorials (9 facilities, 1 skipped) to Google Sheet."""
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE = 'token_sheets.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
TAB = 'google-sheets-facilities.csv'

# slug -> row_idx (from profile_queue.json)
ROW_MAP = {
    'seavoy-nursing-home-taman-setapak-indah': 346,
    'seavoy-nursing-home-desa-melawati': 347,
    'sri-seronok-retirement-village': 349,
    'klc-senior-care-center': 352,
    'lyc-senior-living-care-center': 353,
    'pj-mentalink-care-pj-old-folks': 355,
    'rumah-victory-elderly-home': 357,
    'berniece-care-service-centre': 361,
    'green-cottage-retirement-and-nursing-home': 362,
    'mintygreen-nursing-home-eldercare-center': 372,
}

def main():
    with open('batch2_results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    updates = []
    done_slugs = []
    skipped = []

    for r in data['results']:
        slug = r['slug']
        if r['status'] != 'done':
            skipped.append({'slug': slug, 'reason': r.get('skip_reason', '')})
            print(f"SKIP {slug}: {r.get('skip_reason','')}")
            continue
        row = ROW_MAP[slug]
        text = r['editorial']
        rng = f"'{TAB}'!AY{row}"
        updates.append({'range': rng, 'values': [[text]]})
        done_slugs.append(slug)
        print(f"QUEUED {slug} -> AY{row} ({len(text.split())} words)")

    if updates:
        body = {'valueInputOption': 'RAW', 'data': updates}
        resp = sheet.values().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
        print(f"\nUpdated {resp.get('totalUpdatedCells', 0)} cells across {len(updates)} ranges.")

    # Update progress tracker
    with open('profile_progress.json', 'r', encoding='utf-8') as f:
        prog = json.load(f)
    prog['done'].extend(done_slugs)
    for s in skipped:
        prog['skipped'].append(s)
    prog['last_batch'] = '2026-05-01-b2'
    prog['total_done'] = len(prog['done'])
    with open('profile_progress.json', 'w', encoding='utf-8') as f:
        json.dump(prog, f, indent=2, ensure_ascii=False)
    print(f"\nProgress updated: {prog['total_done']} done, {len(prog['skipped'])} skipped")

if __name__ == '__main__':
    main()
