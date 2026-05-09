"""Upload all final batch editorials (batches 20-23) to column AY.
Handles JSON repair if results files have unescaped quotes."""
import json, os, sys, re
sys.stdout.reconfigure(encoding='utf-8')
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE = 'token_sheets.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
TAB = 'google-sheets-facilities.csv'
BATCHES = range(20, 24)

BS, QT = chr(92), chr(34)

def repair_json(text):
    """Try to repair JSON with unescaped quotes inside editorial fields."""
    pattern = re.compile(r'"editorial":\s*"(.*?)",\s*\n\s*"facts":', re.DOTALL)
    def escape_body(body):
        out = []; i = 0
        while i < len(body):
            c = body[i]
            if c == BS and i+1 < len(body): out.append(body[i:i+2]); i += 2; continue
            if c == QT: out.append(BS+QT); i += 1; continue
            if c == '\n': out.append(BS+'n'); i += 1; continue
            if c == '\r': i += 1; continue
            if c == '\t': out.append(BS+'t'); i += 1; continue
            out.append(c); i += 1
        return ''.join(out)
    return pattern.sub(lambda m: f'"editorial": "{escape_body(m.group(1))}",\n      "facts":', text)

def load_results(path):
    with open(path, encoding='utf-8') as f: text = f.read()
    try: return json.loads(text)
    except json.JSONDecodeError:
        fixed = repair_json(text)
        try:
            d = json.loads(fixed)
            with open(path, 'w', encoding='utf-8') as f: f.write(fixed)
            print(f'  (auto-repaired {path})')
            return d
        except json.JSONDecodeError as e:
            print(f'  !! Cannot repair {path}: {e}')
            return None

def main():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    sheet = build('sheets', 'v4', credentials=creds).spreadsheets()
    all_updates = []; skipped = []
    for n in BATCHES:
        input_file = f'final_batch_{n}.json'
        results_file = f'final_batch_{n}_results.json'
        if not os.path.exists(input_file): print(f'!! missing {input_file}'); continue
        if not os.path.exists(results_file): print(f'!! missing {results_file}'); continue
        with open(input_file, encoding='utf-8') as f: batch_input = json.load(f)
        results = load_results(results_file)
        if results is None: continue
        row_map = {item['slug']: item['row_idx'] for item in batch_input}
        print(f'\n=== Batch {n} ===')
        for r in results.get('results', []):
            slug = r.get('slug')
            ed = (r.get('editorial') or '').strip()
            if not ed:
                skipped.append(slug); print(f'  SKIP (empty): {slug[:50]}'); continue
            row = row_map.get(slug)
            if row is None: print(f'  !! no row: {slug}'); continue
            all_updates.append({'range': f"'{TAB}'!AY{row}", 'values': [[ed]]})
            try:
                print(f'  [{r.get("status","?")}] AY{row} {slug[:50]:50s}  ({len(ed.split())}w)')
            except UnicodeEncodeError:
                print(f'  [{r.get("status","?")}] AY{row} <unicode>  ({len(ed.split())}w)')
    print(f'\nQueued: {len(all_updates)}, skipped: {len(skipped)}')
    if all_updates:
        body = {'valueInputOption': 'RAW', 'data': all_updates}
        resp = sheet.values().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
        print(f"Updated {resp.get('totalUpdatedCells')} cells.")
    if skipped:
        print('\nEmpty editorials needing manual stub fills:')
        for s in skipped: print(f'  {s}')

if __name__ == '__main__':
    main()
