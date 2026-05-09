"""Generic batch editorial uploader. Usage: python upload_batch.py <batch_results.json> <batch_label>"""
import json, sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE = 'token_sheets.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
TAB = 'google-sheets-facilities.csv'

def main():
    results_file = sys.argv[1]
    batch_label = sys.argv[2]

    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    with open('profile_queue.json', 'r', encoding='utf-8') as f:
        queue = json.load(f)
    row_map = {q['slug']: q['row_idx'] for q in queue}

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
            print(f"SKIP {slug}: {r.get('skip_reason','')[:80]}")
            continue
        row = row_map.get(slug)
        if row is None:
            print(f"!! NO ROW for {slug}")
            continue
        text = r['editorial']
        rng = f"'{TAB}'!AY{row}"
        updates.append({'range': rng, 'values': [[text]]})
        done_slugs.append(slug)
        print(f"QUEUED {slug} -> AY{row} ({len(text.split())} words)")

    if updates:
        body = {'valueInputOption': 'RAW', 'data': updates}
        resp = sheet.values().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
        print(f"\nUpdated {resp.get('totalUpdatedCells', 0)} cells across {len(updates)} ranges.")

    with open('profile_progress.json', 'r', encoding='utf-8') as f:
        prog = json.load(f)
    prog['done'].extend(done_slugs)
    prog['skipped'].extend(skipped)
    prog['last_batch'] = batch_label
    prog['total_done'] = len(prog['done'])
    with open('profile_progress.json', 'w', encoding='utf-8') as f:
        json.dump(prog, f, indent=2, ensure_ascii=False)
    print(f"\nProgress: {prog['total_done']} done, {len(prog['skipped'])} skipped")

if __name__ == '__main__':
    main()
