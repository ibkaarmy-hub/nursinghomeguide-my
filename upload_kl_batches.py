"""Upload all KL deep-research editorials (batches 7-12) to the Google Sheet.

Row indices come from kl_batch_N.json (exported by export_kl_research_queue.py).
Editorials come from kl_batch_N_results.json (written by research agents).
Both thin and done statuses are uploaded — thin entries have a conservative editorial.
"""
import json, os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE = 'token_sheets.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
TAB = 'google-sheets-facilities.csv'

BATCHES = range(7, 13)  # batches 7 through 12 inclusive

def main():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    all_updates = []
    skipped = []

    for n in BATCHES:
        input_file = f'kl_batch_{n}.json'
        results_file = f'kl_batch_{n}_results.json'

        if not os.path.exists(input_file):
            print(f'!! Missing input: {input_file}')
            continue
        if not os.path.exists(results_file):
            print(f'!! Missing results: {results_file}')
            continue

        with open(input_file, 'r', encoding='utf-8') as f:
            batch_input = json.load(f)
        with open(results_file, 'r', encoding='utf-8') as f:
            batch_results = json.load(f)

        # Build slug -> row_idx map from input
        row_map = {item['slug']: item['row_idx'] for item in batch_input}

        print(f'\n=== Batch {n} ({len(batch_results["results"])} results) ===')
        for r in batch_results['results']:
            slug = r['slug']
            editorial = (r.get('editorial') or '').strip()

            if not editorial:
                skipped.append(slug)
                print(f'  SKIP (no editorial): {slug}')
                continue

            row_idx = row_map.get(slug)
            if row_idx is None:
                print(f'  !! NO ROW for: {slug}')
                continue

            rng = f"'{TAB}'!AY{row_idx}"
            all_updates.append({'range': rng, 'values': [[editorial]]})
            status = r.get('status', '?')
            try:
                print(f'  [{status}] AY{row_idx} {slug[:55]:55s} ({len(editorial.split())} words)')
            except UnicodeEncodeError:
                print(f'  [{status}] AY{row_idx} <unicode-slug> ({len(editorial.split())} words)')

    print(f'\nTotal queued: {len(all_updates)} updates, {len(skipped)} skipped (no editorial)')

    if not all_updates:
        print('Nothing to upload.')
        return

    body = {'valueInputOption': 'RAW', 'data': all_updates}
    resp = sheet.values().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
    print(f'Updated {resp.get("totalUpdatedCells", 0)} cells across {len(all_updates)} ranges.')

if __name__ == '__main__':
    main()
