"""Upload all Selangor batch editorials to Google Sheet column AY.

Reads sel_batch_N.json (slug -> row_idx) + sel_batch_N_results.json (editorials).
"""
import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE = 'token_sheets.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
TAB = 'google-sheets-facilities.csv'

BATCHES = range(1, 20)  # 1-19 (re-runs are idempotent)

def main():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    sheet = build('sheets', 'v4', credentials=creds).spreadsheets()

    all_updates = []
    skipped = []

    for n in BATCHES:
        input_file = f'sel_batch_{n}.json'
        results_file = f'sel_batch_{n}_results.json'

        if not os.path.exists(input_file):
            print(f'!! Missing: {input_file}')
            continue
        if not os.path.exists(results_file):
            print(f'!! Missing: {results_file}')
            continue

        with open(input_file, 'r', encoding='utf-8') as f:
            batch_input = json.load(f)
        with open(results_file, 'r', encoding='utf-8') as f:
            batch_results = json.load(f)

        row_map = {item['slug']: item['row_idx'] for item in batch_input}

        print(f'\n=== Batch {n} ({len(batch_results.get("results", []))} results) ===')
        for r in batch_results.get('results', []):
            slug = r.get('slug')
            editorial = (r.get('editorial') or '').strip()
            if not editorial:
                skipped.append(slug)
                print(f'  SKIP (empty): {slug}')
                continue
            row_idx = row_map.get(slug)
            if row_idx is None:
                print(f'  !! NO ROW: {slug}')
                continue
            rng = f"'{TAB}'!AY{row_idx}"
            all_updates.append({'range': rng, 'values': [[editorial]]})
            status = r.get('status', '?')
            try:
                print(f'  [{status}] AY{row_idx} {slug[:50]:50s} ({len(editorial.split())}w)')
            except UnicodeEncodeError:
                print(f'  [{status}] AY{row_idx} <unicode> ({len(editorial.split())}w)')

    print(f'\nTotal queued: {len(all_updates)} | Skipped: {len(skipped)}')

    if not all_updates:
        print('Nothing to upload.')
        return

    body = {'valueInputOption': 'RAW', 'data': all_updates}
    resp = sheet.values().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
    print(f'Updated {resp.get("totalUpdatedCells", 0)} cells across {len(all_updates)} ranges.')

if __name__ == '__main__':
    main()
