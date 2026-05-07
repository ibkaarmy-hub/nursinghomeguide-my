#!/usr/bin/env python3
"""
Headless OAuth flow for Google Sheets API.

Step 1: Run with no args → prints authorization URL
Step 2: User visits URL, authorizes, gets redirected to localhost (fails — that's OK)
Step 3: User copies the 'code=...' value from browser URL bar
Step 4: Run: python3 oauth-init.py "<auth_code>"
        (or paste full redirect URL — script extracts code automatically)

Saves token.json for use by apply-schema-to-sheet.py and apply-enrichments.py.
"""
import json
import os
import sys
from urllib.parse import urlparse, parse_qs

import requests

REPO = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRET = os.path.join(REPO, 'client_secret.json')
TOKEN_FILE = os.path.join(REPO, 'token.json')
SCOPE = "https://www.googleapis.com/auth/spreadsheets"

with open(CLIENT_SECRET) as f:
    creds = json.load(f)['installed']

CLIENT_ID = creds['client_id']
CLIENT_SECRET_VALUE = creds['client_secret']
REDIRECT_URI = "http://localhost"

if len(sys.argv) < 2:
    # Print auth URL
    auth_url = (
        f"https://accounts.google.com/o/oauth2/auth?"
        f"client_id={CLIENT_ID}&"
        f"redirect_uri={REDIRECT_URI}&"
        f"scope={SCOPE}&"
        f"response_type=code&"
        f"access_type=offline&"
        f"prompt=consent"
    )
    print("=" * 80)
    print("OAUTH FLOW — STEP 1")
    print("=" * 80)
    print(f"\n1. Visit this URL:\n\n{auth_url}\n")
    print("2. Authorize the app")
    print("3. Browser will redirect to localhost (ERR_CONNECTION_REFUSED is OK)")
    print("4. Copy the FULL URL from address bar (or just the 'code=...' value)")
    print("5. Run: python3 oauth-init.py '<the_code_or_url>'")
    print()
    sys.exit(0)

# Step 2: Exchange code for tokens
arg = sys.argv[1]

# Extract code from URL if full URL provided
if arg.startswith('http'):
    parsed = urlparse(arg)
    qs = parse_qs(parsed.query)
    if 'code' in qs:
        code = qs['code'][0]
    else:
        print(f"❌ No 'code' parameter in URL: {arg}")
        sys.exit(1)
else:
    code = arg

print(f"📥 Exchanging code for token...")
resp = requests.post('https://oauth2.googleapis.com/token', data={
    'code': code,
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET_VALUE,
    'redirect_uri': REDIRECT_URI,
    'grant_type': 'authorization_code',
})

if resp.status_code != 200:
    print(f"❌ Token exchange failed: {resp.status_code}")
    print(resp.text)
    sys.exit(1)

tokens = resp.json()
print(f"✅ Got tokens (expires in {tokens.get('expires_in', '?')}s)")

# Save in google-auth library format
token_data = {
    'token': tokens['access_token'],
    'refresh_token': tokens.get('refresh_token'),
    'token_uri': 'https://oauth2.googleapis.com/token',
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET_VALUE,
    'scopes': [SCOPE],
}

with open(TOKEN_FILE, 'w') as f:
    json.dump(token_data, f, indent=2)

print(f"✅ Token saved: {TOKEN_FILE}")
print(f"\nNow run: python3 apply-schema-to-sheet.py --preview")
