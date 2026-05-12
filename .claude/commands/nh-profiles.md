# /nh-profiles — Nursing Home Profile Research & Enrichment

Single skill for all facility profile work: writing new profiles, enriching existing ones, and batch processing.

## Usage

| Command | What happens |
|---------|-------------|
| `/nh-profiles` | **Batch mode** — research + write next 10 from queue |
| `/nh-profiles <slug>` | **Single mode** — new profile if editorial is blank/short; enrich-only if editorial already exists |

---

## Mode detection (single slug)

1. Load the row from `facilities_local.csv` by slug
2. Check `editorial_summary` (column AY):
   - **Blank or under 100 words** → **New profile mode**: full website research + Google reviews + write editorial from scratch
   - **100+ words already** → **Enrich mode**: check for new data (Maps placeId, Instagram, YouTube); rewrite editorial only if new care/services information was found

---

## Constants

```python
SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_PATH     = r'C:\Users\ibkaa\nursinghomeguide-my\Nursing Home Guide Malaysia\token_sheets.json'
CSV_PATH       = r'C:\Users\ibkaa\nursinghomeguide-my\Nursing Home Guide Malaysia\facilities_local.csv'
TAB            = 'google-sheets-facilities.csv'
APIFY_TOKEN    = open(r'C:\Users\ibkaa\nursinghomeguide-my\Nursing Home Guide Malaysia\.env').read().split('APIFY_TOKEN=')[1].split()[0].strip()
TODAY          = datetime.date.today().isoformat()
```

## Column map (1-based)

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
| 21 | U | last_updated |
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

Never hardcode column letters in scripts — always resolve via `headers.index(name)` from the live CSV header row.

---

## Step 1 — Load facility data

Extract from `facilities_local.csv`:
- `title`, `slug`, `latitude`, `longitude`, `google_maps_url`, `facebook`, `phone`, `website`, `area`, `care_types`, `languages`, `editorial_summary`
- Sheet row number = data row index + 2 (row 1 is header)

Also read the Details tab from Google Sheets for this slug to check existing `section=social` rows (YouTube, Instagram URLs already stored).

If slug not found: stop and report error.

---

## Step 2 — Website investigation *(new profile mode only)*

- Fetch the homepage: look for About Us, Services, Care Types, Team, Facilities, Pricing, Gallery pages
- Check `/sitemap.xml` for additional pages
- Visit any pages that reveal: care specialisations, bed count, staff info, accreditations, founding story, religious affiliation, visiting hours, languages, pricing range, JKM licence number
- Note everything concrete — avoid marketing fluff
- Check the operator website's `/gallery` page for usable photos (see **Operator photos** section)

---

## Step 3 — Google Maps + reviews (MANDATORY — never skip)

Run for **every facility** in every mode before writing or rewriting any editorial. Raw lat/lng URLs are NOT an excuse to skip — pass lat/lng + title to the actor; it resolves the place ID and returns reviews.

**Actor:** `compass/crawler-google-places`
```python
payload = {
    'searchStringsArray': [title],
    'lat': latitude,
    'lng': longitude,
    'zoom': 15,
    'maxCrawledPlacesPerSearch': 3,
    'language': 'en'
}
```

**Validate the result before writing:**
- Returned `title` must roughly match the facility name (fuzzy — allow Malay/English variants, Sdn Bhd vs without)
- Returned `address` must be in the same state as the facility
- If clearly wrong (different business, wrong city, permanently closed): flag to user, skip Maps update

**Extract if valid:**
- `placeId` → build URL: `https://www.google.com/maps/search/?api=1&query=ENCODED_TITLE&query_place_id=PLACE_ID` → update column T
- `address` → append to Details tab `policies | Address` if not already there
- `totalScore`, `reviewsCount` → update sheet columns P/Q (rating/review_count); note for editorial
- Reviews → extract **positive and neutral themes only** (see editorial rules on negatives)

**Review block rules:**
- **5+ reviews**: write `**What reviewers say (Google, N reviews, X★):**` bullet block
- **Fewer than 5 reviews**: prose only — "Google reviews stand at X★ across N reviews — too few to identify recurring trends." No bullet block.

---

## Step 4 — Social media enrichment *(enrich mode; also run in new profile mode if Instagram URL exists)*

### Instagram

Only run if the `facebook` column contains an `instagram.com` URL.

Extract username from URL. Run Apify `apify/instagram-profile-scraper`:
```python
payload = {'usernames': [username]}
```

Extract:
- `biography` — any services or info mentioned
- `externalUrl` / `externalUrls` — look for WhatsApp links (`wa.me/60XXXXXXXXX`); extract number → update column Y if currently empty
- `latestPosts` — collect `displayUrl`, `caption`, `timestamp` for up to 5 newest posts
- `postsCount`

**Image analysis** — for each post image (up to 5, newest first):
- Download `displayUrl` to `_temp_enrich/<slug>/post_N.jpg` with User-Agent header to avoid 403s
- Use Read tool to visually analyse: services/care types visible, facility features, text on screen (flyers often list services, JKM number, email), staff/activities visible
- **Never write Instagram CDN URLs (`fbcdn.net`) to the sheet** — expiry tokens make them dead links within days. Analysis only.
- Delete temp files after: `shutil.rmtree('_temp_enrich', ignore_errors=True)`

Also check Instagram captions for: activity programme mentions, languages, care types, pricing hints.

### YouTube

Check for a YouTube URL in:
1. Arguments passed to the command (user may paste a URL)
2. Details tab rows where `section=social` and `label=YouTube`

If found, use WebFetch. Extract: video title (often reveals purpose — "Virtual Tour", "Services Overview"), any description text. Store in Details tab `social | YouTube | <url>` if not already there.

---

## Step 5 — Write or rewrite editorial

**New profile mode**: always write editorial from scratch.
**Enrich mode**: rewrite editorial only if any of these are true:
- New care types or services were confirmed that aren't in the current editorial
- New verified address, pricing, or visiting hours found
- Current editorial is clearly outdated or wrong

### Fixed 5-part structure (follow exactly)

**Part 1 — Prose opening**
What the home is, where it is, who runs it, licence number if known, capacity, founding year or operator background if known. Prose only — no bullet lists.

**Part 2 — Services block**
```
**Services (from [domain.com]):**
- [verbatim service name from operator website]
- [verbatim service name]
```
Quote the operator's own service categories verbatim. Do NOT rename, combine, or invent. If operator website is unavailable, omit this block. Follow with 1–2 sentences of clinical context if relevant (visiting doctor frequency, RN on-site).

**Part 3 — What reviewers say (MANDATORY)**
```
**What reviewers say (Google, N reviews, X★):**
- [positive/neutral theme]
- [positive/neutral theme]
```
- Include **positive and neutral themes only**
- **Never include negative review content** — remove complaints/criticisms entirely from editorial
- If a concern is worth surfacing, reframe as a neutral visit question in Part 5 only — never cite the review as a source
- For <5 reviews: use prose line instead of bullet block (see Step 3)

**Part 4 — Practical paragraph**
Pricing (published with source, or "Pricing is not published — contact for a quote"), visiting hours (exact if known, or "Visiting hours are not published — confirm when booking a viewing"). End with bold-linked website and Facebook:
```
Full details at **[domain.com](https://domain.com/)** and on Facebook at **[Page Name](https://facebook.com/...)**.
```
Links formatted as `**[text](url)**` render as bold hyperlinks in static pages.

**Part 5 — What to ask on visit**
```
**What to ask on visit:**
- [practical question]
```
5–7 bullets. Rules:
- Plain-answer questions only — a family can get a direct answer on a visit or call
- No process/operational speculation ("how does X work in practice")
- No clinical jargon (outcome measures, gait, ADL, etc.)
- Concerns removed from Part 3 (negative reviews): neutralised version belongs here
- JKM/MOH confirmed: do not ask "Is it registered with JKM?" — see **License status** section

### Hard rules (all parts)
- No fabrication. Only write what is confirmed from website, reviews, or sheet data.
- Write like a knowledgeable friend, not a brochure or a bot.
- No generic phrases: "warm and caring environment", "dedicated team", "holistic approach"
- No phone/WhatsApp/email anywhere in editorial body — sidebar only
- Total editorial: 250–400 words
- Write in English

### Tone
- Never: "statistically unreliable", "warrants caution", "warrants scrutiny", "concerning rating"
- Never: "only/just/merely N reviews"
- Never: list absences as evidence ("not in directory X", "absence of any digital presence")
- Never: accusatory or sceptical framing
- Frame unverified items as call-time questions. Red flags in `facts.red_flags` only.

---

## Step 6 — Update Google Sheet

### 🚨 ALWAYS resolve target row by live slug lookup — NEVER by CSV index

**This is the highest-priority rule in this skill. Violating it has corrupted 52 editorials across 7 states (2026-05-11 incident).**

The local CSV (`facilities_local.csv` or any other snapshot) can drift from the live sheet at any time — rows get added, hidden, status-changed, or marked removed by other jobs while you're working. `data_row_index + 2` is **never safe**.

Canonical pattern — call this immediately before every write:

```python
def find_row_by_slug(svc, slug):
    """Return 1-based sheet row number for a given slug.
    Reads column B live every time. Raises if the slug is missing."""
    col_b = svc.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{TAB}'!B:B"
    ).execute().get('values', [])
    for i, row in enumerate(col_b, start=1):
        if row and row[0].strip() == slug:
            return i
    raise ValueError(f"Slug not found in sheet: {slug}")

# Every write must do this:
row = find_row_by_slug(svc, slug)
svc.spreadsheets().values().batchUpdate(
    spreadsheetId=SPREADSHEET_ID,
    body={'valueInputOption': 'RAW', 'data': [
        {'range': f"'{TAB}'!{col_letter(51)}{row}", 'values': [[editorial]]},
        # ...
    ]}
).execute()
```

**Forbidden patterns:**
```python
# WRONG — CSV index drifts from sheet row
row = data_row_index + 2

# WRONG — caching the row from one lookup and reusing it later in the batch
row_map = {slug: find_row_by_slug(svc, slug) for slug in batch}
for slug in batch: write(row_map[slug], ...)   # rows may shift between writes

# WRONG — trusting the row number returned by an earlier read in the same script
```

**Post-write verification (mandatory for batch jobs):**
After writing, read column B at that row back and assert it still equals the slug. If not, the row shifted — restore and re-resolve.

```python
verify = svc.spreadsheets().values().get(
    spreadsheetId=SPREADSHEET_ID,
    range=f"'{TAB}'!B{row}"
).execute().get('values', [['']])[0][0].strip()
assert verify == slug, f"Row {row} drifted: expected {slug}, found {verify}"
```

**Regression check:** Run `python verify_editorial_match.py` after any batch enrichment job. It flags rows where the editorial mentions a wrong state or shares no words with the title.

### Always use `batchUpdate` per row — never individual `values().update()` calls
Individual calls hit HTTP 429 rate-limit errors (quota: 60 writes/minute). Group all updates for one row:
```python
data = [
    {'range': f"'{TAB}'!{col_letter(51)}{row}", 'values': [[editorial]]},
    {'range': f"'{TAB}'!{col_letter(21)}{row}", 'values': [[TODAY]]},
    # add more cells as needed
]
svc.spreadsheets().values().batchUpdate(
    spreadsheetId=SPREADSHEET_ID,
    body={'valueInputOption': 'RAW', 'data': data}
).execute()
time.sleep(1)  # buffer between rows
```

### Facilities tab — update only confirmed new data

| Finding | Column |
|---------|--------|
| Verified Maps URL with placeId | T |
| WhatsApp from Instagram externalUrl | Y (if currently empty) |
| Area/neighbourhood | D (if currently empty) |
| Languages | M (if found) |
| care_nursing = yes | AA |
| care_dementia = yes | AB |
| care_palliative = yes | AC |
| care_rehab = yes | AD (stroke/post-hospital/rehab confirmed) |
| care_respite = yes | AE (respite/short-term stay confirmed) |
| care_assisted = yes | AF (day care/assisted living confirmed) |
| care_types full text | J (expand if new types confirmed) |
| editorial_summary | AY |
| last_updated | U (always set to TODAY) |

### Details tab — append new rows (check for duplicates first)

| Section | Label | Value | Source |
|---------|-------|-------|--------|
| `services` | service name (verbatim) | `yes` | Website / Instagram |
| `policies` | `Address` | verified address | Maps |
| `policies` | `Visiting hours` | hours string | Website |
| `policies` | `Email` | email address | Website / Instagram |
| `policies` | `Photo credits` | `Facility photos courtesy of <domain>` | Operator website photos |
| `rooms` | `Pricing source` | URL + caveat | Website |
| `rooms` | `Operator-stated capacity` | `N beds` | Website |
| `social` | `YouTube` | URL | YouTube |
| `clinical` | clinical capability | `yes` / `no` | Website / Instagram |

---

## Step 7 — Output report

```
## [Facility Name] — [State]
Slug: [slug]
Mode: New profile / Enrich

### Key facts found
- [verified facts from website/Maps/Instagram]

### Red flags / gaps
- [anything concerning or missing — internal only, not in editorial]

### Sheet updates
- [col]: [old value] → [new value]
- Details tab: +N rows appended

### Editorial (written to column AY)
[full editorial text]
```

---

## Batch mode (no slug argument)

1. Load `profile_queue.json` — sorted by editorial quality (shortest first = most needs work)
2. Load `profile_progress.json` if it exists. If not, create: `{"done": [], "skipped": []}`
3. Select next 10 facilities NOT in `done` or `skipped` with a real website (not Facebook/JKM/blogspot)
4. Run Steps 1–7 for each facility
5. If a website is broken/Facebook-only/JKM redirect: add to `skipped` with reason, pick next facility to reach 10

**Progress tracking file:**
```json
{
  "done": ["slug-1", "slug-2"],
  "skipped": [{"slug": "slug-3", "reason": "Facebook only"}],
  "last_batch": "2026-05-11",
  "total_done": 10
}
```

After each batch: append done slugs, append skipped with reasons, print summary (N done total, N remain).

---

## Reference: locked patterns

### Row resolution (locked 2026-05-12) — slug-by-slug live lookup
See **🚨 ALWAYS resolve target row by live slug lookup** in Step 6 above. This rule is non-negotiable. The 2026-05-11 multi-state batch corrupted 52 rows (mostly Perak, Selangor, Negeri Sembilan) when agents used CSV row indices that didn't match the live sheet. Pre-flight + post-flight slug verification is now mandatory for every write. Always run `verify_editorial_match.py` after any batch.

### License status in editorials (locked 2026-05-09)

MOH and JKM are mutually exclusive registries.

| `jkm_data_source` | Editorial license line |
|-------------------|----------------------|
| contains "moh" | `MOH Licensed — confirmed in MOH nursing home registry.` |
| contains "jkm" + licence_number filled | `JKM Registered — licence number: <number>.` |
| contains "jkm" + no licence number | `JKM Registered — confirmed in JKM registry.` |
| neither | `To be verified — confirm JKM or MOH registration on visit.` |

**"What to ask on visit" — JKM/MOH:**
- MOH licensed: remove ALL JKM bullets. MOH facilities do not hold JKM registration — asking is incorrect and confusing.
- JKM confirmed (licence in sheet): remove "Is it registered with JKM?" — answer already known.
- Unverified: keep the registration ask.

The `facility.html` "What to ask on your tour" card also renders dynamically from `jkm_data_source` — after any change, regenerate all static pages.

### Operator self-promotion guard (locked 2026-05-03)
Never cite, quote, or use as evidence any content where an operator rates themselves favourably against competitors: blog listicles, "Top N" posts, internal awards. Stick to the operator's own factual claims about their own facility. If the only material is self-promotional, write a conservative stub.

### Operator-published services without pricing
Quote the operator's verbatim service categories. Do not invent pricing because a past editorial had a number — verify against the live site every time. If pricing is not posted: "Pricing is not published — contact for a quote." Encode services as Details `services` rows.

### Pricing on operator websites
If a tier list is published, encode all tiers as Details `rooms` rows. Always add a Details `rooms | Pricing source` row with the URL. Update `pricing_display` to show the full range.

### Chain-aware editorials (locked 2026-05-03)
For multi-branch chains: Part 1 and Part 4 are branch-specific. The Services block (Part 2) is identical across all branches — same operator website, same published services. Saves work and keeps the chain story consistent.

### Operator photos
Always check `/gallery` and homepage for usable images. Common URL patterns to probe: `img/image1.jpg`–`image10.jpg`, `assets/img/...`, `images/...`. Stop at first 404 in a numeric sequence.
- Wix CDN: `static.wixstatic.com/media/<id>~mv2.jpg` — strip transformation suffixes, keep `<id>~mv2.jpg` as the stable URL.
- Prepend operator photos to `photos` field (pipe-separated), keep Google CDN photos after, bump `photo_count`.
- Add Details row: `policies | Photo credits | Facility photos courtesy of <domain>`.

### Resolving location conflicts
When `state`, `area`, `slug`, and `latitude/longitude` disagree — decode coordinates first:
- Lat 1.4–1.6, lng 103.5–104.0 = Johor Bahru metro
- Lat 3.0–3.3, lng 101.4–101.8 = Klang Valley (KL/PJ/Selangor)
A misleading slug is not automatic evidence of mis-classification. Verify independently.

### Column corruption detection (locked 2026-05-03)
When pulling a row, dump every column raw and check for misplaced data:
- `google_maps_url` starting with `lh3.googleusercontent.com` → photo URL in wrong column
- `last_updated` containing pipe-separated URLs → photos landed in wrong column
- `halal` containing a number → misplaced `photo_count`
- `latitude`/`longitude` containing prose → editorial blurb in coords column
- `editorial_summary` containing JSON fragments → broken batch upload, rewrite from scratch

Pre-flight check in update scripts: assert no straight double-quotes (`"`) in editorial body before pushing.

### Token + script location
`token_sheets.json` lives only in the main repo root (gitignored). When working from a worktree, reference via absolute path. Write update scripts to `.py` files — never inline `-c` heredocs.

### Static page regeneration
After sheet edits: run `python generate_facility_pages.py` AND `python generate_sitemap.py`, then commit together. The generator fetches the published CSV (`/pub?output=csv`) — there can be a 5–10 minute delay before new rows appear. Poll before running if new rows were added.

`transform_template()` targets `<main id="profileContent">` (not `<div>`). After any change to this function, verify a generated page contains `facility-static-data` before committing.

### Worktree rebase collisions
```bash
git fetch origin main
GIT_EDITOR=true git rebase origin/main
git push origin HEAD:main
```
If `_blockers.json` conflicts: merge both key sets manually, then `git add` and `GIT_EDITOR=true git rebase --continue`.

### User-supplied pricing
Treat as unverified. Confirm against the operator site before publishing. If not found: ask once — "Operator site doesn't list a price — should I publish your number, or 'Call for pricing'?"
