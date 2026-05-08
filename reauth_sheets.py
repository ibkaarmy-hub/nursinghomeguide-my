"""Re-authenticate Google Sheets OAuth token.
Run this when token_sheets.json refresh token has expired.
Opens a browser window for Google sign-in, then writes a fresh token_sheets.json.
"""
from google_auth_oauthlib.flow import InstalledAppFlow
import json

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

flow = InstalledAppFlow.from_client_secrets_file('credentials_temp.json', SCOPES)
creds = flow.run_local_server(port=0)

token_data = {
    'token': creds.token,
    'refresh_token': creds.refresh_token,
    'token_uri': creds.token_uri,
    'client_id': creds.client_id,
    'client_secret': creds.client_secret,
    'scopes': list(creds.scopes),
    'universe_domain': 'googleapis.com',
    'account': '',
    'expiry': creds.expiry.isoformat() if creds.expiry else None,
}
with open('token_sheets.json', 'w') as f:
    json.dump(token_data, f, indent=2)

print("✅ token_sheets.json refreshed successfully.")
