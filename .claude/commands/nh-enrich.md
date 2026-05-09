# /nh-enrich — Nursing Home Profile Enrichment

Given a facility slug, enrich its Google Sheets profile by pulling verified data from Google Maps, Instagram, and YouTube — then rewrite the editorial if new care/services information was found.

**Usage:** `/nh-enrich <slug>`
**Example:** `/nh-enrich pusat-jagaan-kindhara-sdn-bhd`

---

## Constants (always use these exact values)

```python
SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_PATH     = r'C:\Users\ibkaa\nursinghomeguide-my\Nursing Home Guide Malaysia\token_sheets.json'
CSV_PATH       = r'C:\Users\ibkaa\nursinghomeguide-my\Nursing Home Guide Malaysia\facilities_local.csv'
TAB            = 'google-sheets-facilities.csv'
APIFY_TOKEN    = 'YOUR_APIFY_TOKEN'  # set this from your Apify account → Settings → API tokens
```

---

## Column map — Facilities tab (1-based)

| Col | Letter | Field |
|-----|--------|-------|
| 1 | A | title |
| 2 | B | slug |
| 4 | D | area |
| 5 | E | phone |
| 6 | F | website |
| 10 | J | care_types |
| 13 | M | languages |
| 20 | T | google_maps_url |
| 25 | Y | whatsapp |
| 26 | Z | facebook (also Instagram) |
| 27 | AA | care_nursing |
| 28 | AB | care_dementia |
| 29 | AC | care_palliative |
| 30 | AD | care_rehab |
| 31 | AE | care_respite |
| 32 | AF | care_assisted |
| 51 | AY | editorial_summary |
| 52 | AZ | hero_image |
| 53 | BA | photos (pipe-separated) |
| 54 | BB | photo_count |

**Details tab schema:** `slug | section | label | value`
Recognised sections: `services`, `policies`, `social`, `clinical`, `staffing`, `rooms`, `included`, `extras`

---

## Step 0 — Load facility from CSV

Read `facilities_local.csv` and find the row matching the slug. Extract:
- `title`, `latitude`, `longitude`, `google_maps_url`, `facebook`, `phone`, `area`, `care_types`, `languages`
- Also get the sheet row number (data row index + 2, since row 1 is header)

If slug not found, stop and report error.

Also read the Details tab from Google Sheets for this slug to find any existing `section=social` rows (e.g. YouTube URL already stored).

---

## Step 1 — Google Maps verification

**Goal:** Confirm or find the correct Maps listing with a stable place ID URL.

Only run this step if the current `google_maps_url` is a raw lat/lng URL (`maps.google.com/?q=`) or a name-only search URL without a `query_place_id`. If it already has `query_place_id=` or `!1s` in the URL, skip to Step 2.

Run Apify `compass/crawler-google-places` (sync, timeout=60s):
```python
payload = {
    'searchStringsArray': [title],  # facility title from CSV
    'lat': latitude,
    'lng': longitude,
    'zoom': 15,
    'maxCrawledPlacesPerSearch': 5,
    'language': 'en',
}
```

**Validate the result before writing:**
- The returned `title` must roughly match the facility name (fuzzy — allow for Malay/English variants, Sdn Bhd vs without, etc.)
- The `address` must be in the same state as the facility
- If the top result is clearly wrong (completely different business type, wrong city, permanently closed), flag it to the user and skip the Maps update

If valid, extract:
- `placeId` → build URL: `https://www.google.com/maps/search/?api=1&query=ENCODED_TITLE&query_place_id=PLACE_ID`
- `address` → use as verified address for Details tab policies row
- `totalScore`, `reviewsCount` → note for editorial context (do not blindly overwrite sheet rating if discrepancy is large)

Update sheet column T (google_maps_url) with the verified URL.

---

## Step 2 — Instagram scraping

Only run if the `facebook` column contains an `instagram.com` URL.

Extract the username from the URL (e.g. `kindhara_seniorcarehome` from `https://www.instagram.com/kindhara_seniorcarehome/`).

Run Apify `apify/instagram-profile-scraper` (sync):
```python
payload = {'usernames': [username]}
```

Extract from the result:
- `fullName` — the verified business name
- `biography` — any services or info mentioned
- `externalUrl` / `externalUrls` — look for WhatsApp links (`wa.me/...`); extract the phone number
- `latestPosts` — collect `displayUrl`, `caption`, `type`, `timestamp` for all posts
- `postsCount`

**WhatsApp number:** If found in externalUrl (format: `wa.me/60XXXXXXXXX`), extract the number and update column Y (whatsapp) if currently empty.

---

## Step 3 — Image analysis

For each Instagram post (up to 5, newest first), download the `displayUrl` thumbnail to a temp file and use the Read tool to visually analyse the image.

```python
import urllib.request, os, tempfile
# Download to temp dir, e.g. _temp_enrich/<slug>/post_N.jpg
# Use User-Agent header to avoid 403s
```

For each image, note:
- **Services or care types visible** (e.g. "Day Care", "Stroke Care", "Specialised Care")
- **Facility features** (e.g. outdoor garden, dining area, therapy room, beds)
- **Text on screen** (marketing flyers often list services, phone numbers, addresses, JKM status, emails)
- **Staff or activities** visible
- **Whether the image is useful** (facility photo vs job ad vs social graphic)

**Critical rule:** Instagram CDN URLs (`fbcdn.net`) have expiry tokens and become dead links within days. **Never write these URLs to the sheet** (not hero_image, not photos). Only use them for analysis during this session.

After analysis, delete all temp files:
```python
import shutil
shutil.rmtree('_temp_enrich', ignore_errors=True)
```

---

## Step 4 — YouTube

Check for a YouTube URL in two places:
1. The `$arguments` passed to this command (user may paste a URL directly)
2. Details tab rows for this slug where `section=social` and `label=YouTube`

If a YouTube URL is found, use WebFetch on it. YouTube pages usually only return the video title (not the description), so extract whatever is available:
- Video title — often reveals the video's purpose (e.g. "Virtual Tour", "Services Overview")
- Any description text if present

Store the YouTube URL in the Details tab if not already there:
```
slug | social | YouTube | https://youtu.be/XXXX
```

---

## Step 5 — Compile findings and update sheet

Gather everything found across Steps 1–4. For each piece of data, only write it if:
- It was explicitly seen/confirmed (not inferred from vibes)
- It does not conflict with data already in the sheet in a way you can't explain

### Facilities tab updates (batch where possible)

Only update fields that have new confirmed data:

| Finding | Column |
|---------|--------|
| Verified Maps URL with placeId | T (google_maps_url) |
| WhatsApp number from Instagram | Y (whatsapp) |
| Area/neighbourhood | D (area) — if currently empty |
| Languages (from multilingual mention) | M (languages) |
| care_nursing=yes | AA |
| care_rehab=yes | AD — if stroke/post-hospital/rehab confirmed |
| care_respite=yes | AE — if respite/short-term stay confirmed |
| care_assisted=yes | AF — if day care/assisted living confirmed |
| care_types (full text) | J — expand if new types confirmed |

### Details tab — append new rows

Check for duplicates before appending (don't double-add if rows already exist for this slug+section+label).

**From image/Instagram findings:**
- `services` section: one row per confirmed service (label=service name, value=`yes`)
- `policies` section: Address if confirmed, Email if found

**From YouTube:**
- `social` section: `YouTube | <url>` (if not already there)

**From Maps:**
- `policies` section: `Address | <verified address>` (if not already there)

---

## Step 6 — Rewrite editorial

Rewrite the `editorial_summary` (column AY) if **any** of the following are true:
- The current editorial is blank or under 100 words
- New care types or services were confirmed that aren't reflected in the current editorial
- A verified address was found that isn't mentioned

**Editorial rules (from project style guide):**
- Tone: knowledgeable friend — not a brochure, not a review site
- 3 paragraphs + "What to ask on visit" bullets — 250–400 words total
- **Only include verified facts.** Frame unknowns as questions to ask on visit
- Para 1: What kind of place, where, who it's for, positioning
- Para 2: Care specialisations and what makes it distinctive
- Para 3: Practical — licensing, contact, languages, virtual tour if exists
- End with `**What to ask on visit**` + 5–7 bullet questions focused on the specific claims made (not generic questions)
- Never use: "statistically unreliable", "warrants caution", "only/just N reviews", "absence of any digital presence"
- JKM-confirmed facilities: do not include "Is it registered with JKM?" in the ask bullets

Write the finished editorial to column AY.

---

## Step 7 — Summary report

Print a clean summary of everything found and written:

```
✅ ENRICHED: <slug>

MAPS
  google_maps_url → updated (placeId: XXXX) / unchanged / skipped (wrong result)
  address confirmed: <address>

INSTAGRAM (@username)
  posts analysed: N
  whatsapp: +60XXXXXXXXX (updated) / already set / not found
  services found: Day Care, Short-term Stay, ...

SHEET UPDATES
  Facilities tab row <N>:
    D (area): Taman Johor Jaya
    AD (care_rehab): yes
    AE (care_respite): yes
    ...
  Details tab: +N rows appended

EDITORIAL
  Rewritten (was: blank / <N> words → now: <M> words)
  / Unchanged (no new data warranted a rewrite)
```

---

## Apify helper pattern

For all Apify calls use `requests` with `run-sync-get-dataset-items`:

```python
import requests, sys
sys.stdout.reconfigure(encoding='utf-8')

r = requests.post(
    f'https://api.apify.com/v2/acts/{ACTOR}/run-sync-get-dataset-items'
    f'?token={APIFY_TOKEN}&timeout=60',
    json=payload,
    timeout=90
)
data = r.json()  # list of result items
```

## Google Sheets helper pattern

```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file(
    TOKEN_PATH,
    ['https://www.googleapis.com/auth/spreadsheets']
)
svc = build('sheets', 'v4', credentials=creds)

# Single cell update
svc.spreadsheets().values().update(
    spreadsheetId=SPREADSHEET_ID,
    range=f"'{TAB}'!T{row}",
    valueInputOption='RAW',
    body={'values': [[new_value]]}
).execute()

# Append rows to Details tab
svc.spreadsheets().values().append(
    spreadsheetId=SPREADSHEET_ID,
    range="'Details'!A:D",
    valueInputOption='RAW',
    insertDataOption='INSERT_ROWS',
    body={'values': rows}
).execute()
```

---

## Error handling

- **Apify timeout / non-200:** Log the error, skip that step, continue with the rest
- **Wrong Maps result:** Flag clearly in summary, do not update google_maps_url
- **Instagram private / not found:** Skip Step 2 and 3, note in summary
- **Image download fails:** Skip that image, continue with others
- **Sheet auth error:** Stop and report — the token may need refreshing (run `reauth_sheets.py`)
- **Slug not in CSV:** Stop immediately with a clear error message
