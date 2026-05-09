"""
scrape_social_from_websites.py
Scrape facility websites for Facebook/Instagram links.
Free — no Apify calls. Updates column Z (facebook) in the sheet if empty.

Run: python scrape_social_from_websites.py
"""

import csv, io, re, sys, time, urllib.request
import requests
from bs4 import BeautifulSoup
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout.reconfigure(encoding='utf-8')

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_PATH     = r'C:\Users\ibkaa\nursinghomeguide-my\Nursing Home Guide Malaysia\token_sheets.json'
TAB            = 'google-sheets-facilities.csv'
CSV_URL        = (
    'https://docs.google.com/spreadsheets/d/e/'
    '2PACX-1vQ4_BgHIjnlgmITzjyUuGDpgpNzPL7MfjOY2069i0PtbVbXSxIAJk1tmBejwNo8aBBeLuRi62szF2sh'
    '/pub?gid=292378871&single=true&output=csv'
)

HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; NHGBot/1.0)'}
TIMEOUT = 10

FB_RE  = re.compile(r'https?://(?:www\.|m\.)?facebook\.com/[^\s"\'<>]{3,80}', re.I)
IG_RE  = re.compile(r'https?://(?:www\.)?instagram\.com/[^\s"\'<>]{3,50}', re.I)

SKIP_FB = {'facebook.com/sharer', 'facebook.com/share', 'facebook.com/dialog',
           'facebook.com/login', 'facebook.com/plugins', 'facebook.com/tr',
           'facebook.com/profile.php', 'facebook.com/profile'}


def clean_fb(url):
    url = url.rstrip('/?').split('?')[0]
    if any(s in url.lower() for s in SKIP_FB):
        return None
    # Must have a path segment beyond the domain
    path = url.split('facebook.com/', 1)[-1].strip('/')
    if not path or path in ('home', 'pages', 'groups', 'events'):
        return None
    return url


def clean_ig(url):
    url = url.rstrip('/?').split('?')[0]
    path = url.split('instagram.com/', 1)[-1].strip('/')
    if not path or '/' in path:
        return None
    return url


def scrape_social(website_url):
    try:
        r = requests.get(website_url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        if r.status_code != 200:
            return None, None
        html = r.text
    except Exception:
        return None, None

    fb_hits  = [clean_fb(u) for u in FB_RE.findall(html)]
    ig_hits  = [clean_ig(u) for u in IG_RE.findall(html)]
    fb_hits  = list(dict.fromkeys(u for u in fb_hits if u))
    ig_hits  = list(dict.fromkeys(u for u in ig_hits if u))
    return (fb_hits[0] if fb_hits else None), (ig_hits[0] if ig_hits else None)


def main():
    # Load sheet
    print('Fetching facilities CSV...')
    with urllib.request.urlopen(CSV_URL) as r:
        data = r.read().decode('utf-8')
    reader = csv.DictReader(io.StringIO(data))
    headers = reader.fieldnames
    col_fb      = headers.index('facebook') + 1        # col Z (1-based)
    col_website = headers.index('website')
    col_lic     = headers.index('licence_number')

    rows = list(reader)

    # Filter: licensed, live, has website, no social yet
    targets = []
    for i, row in enumerate(rows, start=2):
        if row.get('status','').strip() in ('unverified','removed'):
            continue
        if not row.get(headers[col_lic - 1],'').strip():
            continue
        fb = row.get('facebook','').strip()
        if fb:  # already has something
            continue
        website = row.get('website','').strip()
        if not website or 'facebook.com' in website:
            continue
        targets.append({
            'row': i,
            'slug': row.get('slug','').strip(),
            'title': row.get('title','').strip(),
            'website': website,
        })

    print(f'Licensed facilities with website but no social: {len(targets)}')

    creds = Credentials.from_authorized_user_file(TOKEN_PATH, ['https://www.googleapis.com/auth/spreadsheets'])
    svc   = build('sheets', 'v4', credentials=creds)

    found_fb = []
    found_ig = []
    not_found = []

    for idx, t in enumerate(targets, 1):
        print(f'[{idx}/{len(targets)}] {t["slug"]}', end=' ... ', flush=True)
        fb_url, ig_url = scrape_social(t['website'])
        social = ig_url or fb_url  # prefer Instagram if both found

        if social:
            label = 'IG' if ig_url else 'FB'
            print(f'{label}: {social}')
            col_letter = chr(ord('A') + col_fb - 1)  # Z
            svc.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=f"'{TAB}'!{col_letter}{t['row']}",
                valueInputOption='RAW',
                body={'values': [[social]]}
            ).execute()
            if ig_url:
                found_ig.append((t['slug'], social))
            else:
                found_fb.append((t['slug'], social))
        else:
            print('none')
            not_found.append(t['slug'])

        time.sleep(0.5)  # be polite

    print('\n' + '='*60)
    print(f'DONE. Scraped {len(targets)} facilities.')
    print(f'  Instagram found: {len(found_ig)}')
    for slug, url in found_ig:
        print(f'    {slug}: {url}')
    print(f'  Facebook found:  {len(found_fb)}')
    for slug, url in found_fb:
        print(f'    {slug}: {url}')
    print(f'  No social found: {len(not_found)}')


if __name__ == '__main__':
    main()
