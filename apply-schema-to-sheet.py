#!/usr/bin/env python3
"""
Apply schema refactor directly to live Google Sheet:
1. Delete 10 placeholder columns (right-to-left to avoid index shifting)
2. Rename 2 license_* → licence_*
3. Add 3 new columns

Run with --preview first to see what will happen.
Run with --apply to execute changes.
"""
import argparse
import os
import sys

SHEET_ID = "1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk"
TAB_NAME = "Facilities"
TAB_ID = 292378871

DROP = {
    'license_number',
    'license_category',
    'license_expiry_warning',
    'pricing_model',
    'nurse_in_charge',
    'acuity_level',
    'evidence_ref',
    'outreach_last_attempt',
    'outreach_notes',
    'hidden_costs',
}

RENAME = {
    'license_expiry': 'licence_expiry',
    'license_verification_date': 'licence_last_checked',
}

ADD = ['address', 'email', 'jkm_data_source']

def get_service(creds_path, token_path):
    """Build Sheets service."""
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
    except ImportError:
        print("❌ Missing google libs. Run: pip3 install google-auth google-auth-oauthlib google-api-python-client")
        sys.exit(1)

    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, ["https://www.googleapis.com/auth/spreadsheets"])

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(creds_path):
                print(f"❌ Client secret not found: {creds_path}")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(
                creds_path, ["https://www.googleapis.com/auth/spreadsheets"]
            )
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as f:
            f.write(creds.to_json())

    return build('sheets', 'v4', credentials=creds)

def col_letter(idx):
    """0-based index to column letter."""
    s = ''
    n = idx
    while True:
        s = chr(ord('A') + n % 26) + s
        n = n // 26 - 1
        if n < 0:
            break
    return s

def get_headers(service):
    """Get header row from sheet."""
    result = service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range=f"{TAB_NAME}!A1:ZZ1"
    ).execute()
    return result.get('values', [[]])[0]

def find_col(headers, col_name):
    """Return (0-based index, column letter) or (None, None)."""
    try:
        idx = headers.index(col_name)
        return idx, col_letter(idx)
    except ValueError:
        return None, None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--preview', action='store_true', help='Show what will change (default)')
    ap.add_argument('--apply', action='store_true', help='Actually apply changes')
    ap.add_argument('--creds', default='client_secret.json')
    ap.add_argument('--token', default='token.json')
    args = ap.parse_args()

    print(f"🔗 Sheet: {SHEET_ID}")
    print(f"📄 Tab: {TAB_NAME}\n")

    service = get_service(args.creds, args.token)
    print(f"✅ Authenticated\n")

    headers = get_headers(service)
    print(f"📊 Current: {len(headers)} columns\n")

    # Preview changes
    print("🔍 Changes to apply:\n")

    # 1. Deletions
    print(f"🗑️  DELETE {len(DROP)} columns:")
    to_delete = []
    for col_name in sorted(DROP):
        idx, col_letter_str = find_col(headers, col_name)
        if idx is not None:
            to_delete.append((idx, col_name, col_letter_str))
            print(f"   {col_letter_str}  {col_name}")
        else:
            print(f"   ✗  {col_name} (not found)")

    # 2. Renames
    print(f"\n✏️  RENAME {len(RENAME)} columns:")
    for old, new in sorted(RENAME.items()):
        idx, col_letter_str = find_col(headers, old)
        if idx is not None:
            print(f"   {col_letter_str}  {old} → {new}")
        else:
            print(f"   ✗  {old} (not found)")

    # 3. Additions
    print(f"\n➕ ADD {len(ADD)} columns:")
    for col_name in ADD:
        if find_col(headers, col_name)[0] is None:
            print(f"   {col_name}")
        else:
            print(f"   ✓ {col_name} (already exists)")

    print(f"\n📊 Result: {len(headers)} - {len(to_delete)} + {len(ADD)} = {len(headers) - len(to_delete) + len(ADD)} columns")

    if not args.apply:
        print("\n💡 Run with --apply to execute these changes")
        return

    print(f"\n⚙️  Applying changes...\n")

    # Execute deletions (right-to-left to avoid index shifting)
    to_delete.sort(reverse=True, key=lambda x: x[0])
    for idx, col_name, col_letter_str in to_delete:
        print(f"   Deleting {col_letter_str} ({col_name})...", end=' ', flush=True)
        try:
            service.spreadsheets().batchUpdate(
                spreadsheetId=SHEET_ID,
                body={
                    'requests': [{
                        'deleteRange': {
                            'range': {
                                'sheetId': TAB_ID,
                                'dimension': 'COLUMNS',
                                'startIndex': idx,
                                'endIndex': idx + 1
                            },
                            'shiftDimension': 'COLUMNS'
                        }
                    }]
                }
            ).execute()
            print("✅")
        except Exception as e:
            print(f"❌ {e}")

    # Re-fetch headers after deletions
    headers = get_headers(service)
    print(f"\n   Headers after deletions: {len(headers)} columns")

    # Execute renames
    print(f"\n   Renaming columns...")
    for old, new in RENAME.items():
        idx, col_letter_str = find_col(headers, old)
        if idx is not None:
            print(f"      {col_letter_str} {old} → {new}...", end=' ', flush=True)
            try:
                cell = f"{col_letter_str}1"
                service.spreadsheets().values().update(
                    spreadsheetId=SHEET_ID,
                    range=f"{TAB_NAME}!{cell}",
                    valueInputOption='RAW',
                    body={'values': [[new]]}
                ).execute()
                print("✅")
            except Exception as e:
                print(f"❌ {e}")

    # Execute additions
    print(f"\n   Adding columns...", end=' ')
    try:
        requests = []
        for col_name in ADD:
            if find_col(headers, col_name)[0] is None:
                # Insert at end (or you could insert at a specific position)
                requests.append({
                    'appendCells': {
                        'sheetId': TAB_ID,
                        'rows': [{
                            'values': [{
                                'userEnteredValue': {'stringValue': col_name}
                            }]
                        }],
                        'fields': 'userEnteredValue'
                    }
                })
        if requests:
            service.spreadsheets().batchUpdate(
                spreadsheetId=SHEET_ID,
                body={'requests': requests}
            ).execute()
            print("✅")
        else:
            print("(all already exist)")
    except Exception as e:
        print(f"❌ {e}")

    # Final summary
    headers = get_headers(service)
    print(f"\n✅ Done! Sheet now has {len(headers)} columns")
    print(f"\nNext: python3 apply-enrichments.py --apply")

if __name__ == '__main__':
    main()
