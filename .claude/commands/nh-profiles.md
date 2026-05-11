# /nh-profiles — Nursing Home Profile Research Batch

Research and write detailed 3-paragraph editorial profiles for the next 10 nursing homes in `profile_queue.json` that have websites and need proper editorials. Track progress in `profile_progress.json`.

## What to do

### Setup
1. Load `profile_queue.json` — sorted by editorial quality (shortest first = most needs work)
2. Load `profile_progress.json` if it exists (tracks completed slugs). If not, create it as `{"done": [], "skipped": []}`.
3. Select the next 10 facilities NOT in `done` or `skipped`, with a real website (not Facebook/JKM/blogspot).

### For each of the 10 facilities

**Step 1 — Website investigation**
- Fetch the homepage: look for About Us, Our Services, Care Types, Team, Facilities, Pricing, Gallery pages
- Check `/sitemap.xml` for additional pages
- Visit any pages that reveal: care specialisations, bed count, staff info, accreditations, founding story, religious affiliation, visiting hours, languages spoken, pricing range
- Note everything concrete — avoid marketing fluff

**Step 2 — Google reviews (MANDATORY — do not skip)**
- Run Apify `compass/crawler-google-places` for every facility before writing, even if the Maps URL is a raw lat/lng link with no place ID. Raw lat/lng URLs are NOT an excuse to skip this step — pass lat/lng + title to the actor; it resolves the place ID and returns reviews.
- Read **all** reviews, not just the first page. Note recurring themes (positive only — see review rules below), staff mentions, specific care events described.
- If the facility has **fewer than 5 reviews**: mention rating and count in prose only — "Google reviews stand at X★ across N reviews — too few to identify recurring trends" — do not write a bullet block.
- Also check: `site:[website-domain]` for additional indexed content; JKM lists or directories for licence info.

**Actor payload:**
```python
{
    'searchStringsArray': [facility_title],
    'lat': latitude,
    'lng': longitude,
    'zoom': 15,
    'maxCrawledPlacesPerSearch': 3,
    'language': 'en'
}
```

**Step 3 — Medical social worker + consumer analysis**
Evaluate from TWO lenses:

*Medical Social Worker lens:*
- What clinical capabilities are confirmed vs claimed?
- Is there a registered nurse on-site? Doctor visits?
- Are there any red flags: vague staffing claims, no licence info, unverified medical services?
- Suitability for: high-dependency residents, dementia, palliative

*Consumer/Family lens:*
- Is pricing mentioned or completely opaque?
- Can a family get key answers from the website alone?
- Photo quality and authenticity (real photos vs stock)
- Social proof: are Google reviews detailed and believable?
- Visiting hours, contact ease, WhatsApp availability

**Step 4 — Write the editorial (locked structure 2026-05-11)**

The editorial has a fixed five-part structure. Follow this exactly:

**Part 1 — Prose opening paragraph**
What the home is, where it is, who runs it, licence number (if known), capacity, founding year or operator background if known. No bullet lists here — prose only.

**Part 2 — Services block**
```
**Services (from [domain.com]):**
- [verbatim service name from operator website]
- [verbatim service name]
...
```
Quote the operator's own service categories verbatim. Do NOT rename, combine, or invent. If the operator website is unavailable, omit this block and note it in Key facts. Follow with 1–2 sentences of clinical context if relevant (e.g. visiting doctor frequency, RN on-site).

**Part 3 — What reviewers say block (MANDATORY)**
```
**What reviewers say (Google, N reviews, X★):**
- [positive/neutral theme]
- [positive/neutral theme]
...
```
- Only include **positive and neutral** themes. **Never include negative review content** — remove any complaints or criticisms entirely.
- If a concern from reviews is worth surfacing (e.g. deposit policy, supervision standards), reframe it as a neutral visit question in Part 5 only — never cite the review as a source.
- For <5 reviews: replace with prose — "Google reviews stand at X★ across N reviews — too few to identify recurring trends." No bullet block.

**Part 4 — Practical paragraph**
Pricing (published or "Call for pricing"), visiting hours (exact if known, "not published — confirm when booking" if not), bold-linked website and Facebook at end of paragraph:
```
Full details at **[domain.com](https://domain.com/)** and on Facebook at **[Page Name](https://facebook.com/...)**.
```
Links must be formatted as `**[text](url)**` — renders as bold hyperlink in static pages.

**Part 5 — What to ask on visit**
```
**What to ask on visit:**
- [practical question]
- [practical question]
...
```
5–7 bullets. Rules:
- Plain-answer questions only — a family can get a direct answer on a visit or phone call
- No process/operational speculation ("how does X work in practice")
- No clinical jargon (outcome measures, gait, ADL, etc.)
- If a concern was removed from Part 3 reviews, the neutralised version belongs here
- If JKM/MOH confirmed: do not ask "Is it registered with JKM?" — see **License status** section

**Writing rules (all parts):**
- No fabrication. Only write what is confirmed from website, reviews, or sheet data.
- Write like a knowledgeable friend, not a brochure or a bot.
- No generic phrases: "warm and caring environment", "dedicated team", "holistic approach"
- No phone/WhatsApp/email anywhere in editorial body — sidebar only.
- Total editorial: 250–400 words.
- Write in English.

**Tone — DO NOT undermine the facility:**
- Never frame thin review counts as "statistically unreliable", "warrants caution", or "a perfect score on very few reviews is suspicious". A small number of reviews is normal for many small homes — describe it neutrally if at all.
- Never list absences as evidence ("does not appear in the top-10 roundups", "not in the AGECOPE directory", "not mentioned in any news"). Focus on what's verified.
- Don't use language that reads as accusatory or sceptical. Families are stressed enough; the editorial describes what's verified and prompts practical enquiries — it does not cast doubt.
- Frame unverified items as call-time questions. Red flags belong in `facts.red_flags` only.
- Avoid "only", "merely", "just X reviews" — these read as belittling.

**Step 5 — Produce the report**
For each facility, output:

```
## [Facility Name] — [State]
Website: [url]
Slug: [slug]

### Key facts found
- [bullet list of verified facts extracted]

### Red flags / gaps
- [anything concerning or missing]

### Editorial (for sheet)
[3 paragraphs]

### Sheet updates recommended
- care_types: [if found]
- total_beds: [if found]
- religion: [if found]
- pricing_display: [if found]
- any other columns with new data]
```

### Step 6 — Update progress tracker
After completing each batch:
1. Append all 10 slugs to `done` in `profile_progress.json`
2. Append any skipped (Facebook-only, JKM links, broken sites) to `skipped` with reason
3. Print summary: how many done total, how many remain

### Step 7 — Upload editorials to Google Sheet
After writing all 10:
- Use the Google Sheets API (token_sheets.json, SCOPES=['https://www.googleapis.com/auth/spreadsheets'])
- Sheet ID: 1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk
- Tab: 'google-sheets-facilities.csv'
- Update `editorial_summary` column + any other changed columns for each facility

**MANDATORY: use `batchUpdate` per row, not individual `values().update()` calls.** Individual calls at scale hit HTTP 429 rate-limit errors (quota: 60 writes/minute). Group all cell updates for one row into a single `batchUpdate`:
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

## Progress tracking file format

`profile_progress.json`:
```json
{
  "done": ["slug-1", "slug-2", ...],
  "skipped": [{"slug": "slug-3", "reason": "Facebook only"}],
  "last_batch": "2026-05-01",
  "total_done": 10
}
```

## Important constraints
- Never invent data. Only write what is confirmed from website, reviews, or existing sheet data.
- If a website is broken/Facebook/JKM redirect: add to skipped, pick next facility to reach 10.
- If a Google Maps URL is present, always check it for reviews.
- The editorial goes in `editorial_summary` column in the sheet — this is the live public-facing text.
- Flag any JKM licence numbers found — these are critical gaps to fill.

---

## Hand-fix mode (single-profile, user-flagged)

When the user pastes a specific facility URL with feedback, switch from the bulk batch workflow above to a focused per-profile fix. Lessons from past sessions:

### Resolving location conflicts
- The sheet has `state`, `area`, `slug`, `latitude/longitude`, and `google_maps_url` — when they disagree, **decode the coordinates first** before assuming any one of them is wrong.
  - Lat 1.4–1.6, lng 103.5–104.0 = Johor Bahru metro (Skudai/Iskandar Puteri/Tampoi/Permas)
  - Lat 3.0–3.3, lng 101.4–101.8 = Klang Valley (KL/PJ/Selangor)
- A misleading slug is **not** automatic evidence of mis-classification. A multi-branch chain headquartered in PJ may have opened a real Johor branch — search Facebook + Google for "[chain] expanding to [city]" before flipping the data the wrong way.
- A previous editorial that confidently states the wrong location (e.g. "actually in PJ, not Johor") is a red flag that someone else made the same mistake. Verify independently.

### Editorial style — what NOT to write
- **No meta-commentary opening lines.** Anything like "Note the slug first…" or "Despite the listing title…" reads as AI talking about its own data. The reader doesn't care about our slug; lead with what the home is.
- **No "this is a stub" / "limited information available" disclaimers.** Either write a confident shorter editorial from verified facts, or don't publish.
- Drop the JKM registration ask from "What to ask on visit" for any facility where `jkm_data_source` confirms MOH or JKM status — see **License status in editorials** section below for the full rule.

### Operator photos
- Always check the operator website's `/gallery` page and homepage for usable images.
- Common URL patterns to probe with curl HEAD: `img/image1.jpg`–`image10.jpg`, `img/pf1.png`–`pf4.png`, `assets/img/...`, `images/...`. Stop at first 404 in a numeric sequence.
- Prepend operator photos to the existing `photos` field (pipe-separated), keep Google CDN photos after, and bump `photo_count`. Don't replace the hero unless the existing one is broken.
- **Attribution**: add a Details row with `section=policies`, `label=Photo credits`, `value=Facility photos courtesy of <domain>`. There's no per-photo attribution column; this single row is the canonical place.

### Operator self-promotion — guard rule (locked 2026-05-03)
- **Never cite, quote, paraphrase, or use as evidence ANY content where an operator rates themselves favourably against competitors.** This applies to operator blog listicles, "Top N" or "Best of" posts, internal awards, or any marketing piece that ranks the operator's own facility against others. Operator self-ratings are marketing, not evidence — citing them would compromise the site's editorial credibility.
- Stick to the operator's own factual claims about THEIR OWN facility: services, pricing, locations, capacity, branch dates, awards from independent bodies, JKM licence numbers.
- Skip blog/news pages entirely if their content is self-comparative. If the only material on the operator site is self-promotional, treat the facility as low-information and write a conservative stub instead — do not pad the editorial with marketing language.
- This applies across the entire site, not just one operator. First seen on Genesis Life Care's `/blog/best-nursing-homes-kl-selangor-2026` (operator ranking themselves as best).

### Operator-published services without pricing
- Common pattern: operator publishes a clean services list (e.g. "Nursing Home Care, Dementia & Memory Care, Stroke Rehabilitation, Palliative Care, Post-Operative Recovery, Senior Day Care") but no monthly fees anywhere on the site.
- Editorial should quote the operator's verbatim service categories — do not invent or rename them — and explicitly say pricing is not posted (e.g. "Pricing is not posted on the [chain] website for any branch — final monthly fees depend on care level and room type, so request a written quote during your visit").
- Encode the services list as Details `services` rows: `label = service name (verbatim)`, `value = short qualifier or "yes"` (e.g. `Dementia & Memory Care` / `Psychologist-led, cognitive stimulation activities`).
- Add a Details `rooms` row `Pricing source` / `Not published on operator site (<domain>) — request a written quote during your visit`.
- Add a Details `rooms` row `Operator-stated capacity` / `<N> beds` if the operator publishes a bed count.
- Do NOT invent "from RM X" pricing in the editorial just because past editorials had a number. Past editorials are not a source — verify against the live operator site every time. Genesis Puchong had an unsourced "from RM 2,500" claim that had to be removed.

### Pricing on operator websites
- If the operator publishes a tier list (rare and valuable), encode all tiers as Details `rooms` rows with labels like `2-bed shared (RM/mo)` → value `2,800`. Don't bury the range in the editorial only.
- Default assumption: published rates apply chain-wide. Don't caveat as "flagship only" unless the operator explicitly says branch pricing differs.
- Always add a Details row `rooms / Pricing source / <full-url> — chain rates; final fee depends on care needs`.
- Update `pricing_display` to show the full range, not just shared/private (e.g. `From RM 1,800 (6-bed shared) to RM 3,500 (VIP single) — published on operator website`).
- `four_bed_price` exists as a column — populate it when the tier list has a 4-bed rate.

### Workflow checklist
1. Pull row by slug from facilities CSV + Details rows by slug.
2. Check `pending_editorials/_blockers.json` and `_progress.json` to avoid colliding with the bulk agent. If the slug is in flight, ask user before overriding.
3. Decode coords; reconcile state/area/slug; flag any inconsistency to user.
4. Visit operator website (homepage, /packages, /gallery, /contact, /weare, /about). Search FB for branch announcements if multi-branch.
5. Present plan to user with: old vs new editorial (full new text), exact column diffs (old → new), Details rows to add. **Wait for confirmation.**
6. Push via a dedicated `update_<slug>.py` script modeled on `update_eha_chain.py`. Always update `last_updated` to today.
7. Append slug to `pending_editorials/_blockers.json` (it's an object: `{"slug": "reason"}`, NOT an array).
8. Commit with author `ibkaarmy-hub@users.noreply.github.com`, push to main.
9. Re-fetch the published CSV and verify the change is live before reporting done.

### Token + script location
- `token_sheets.json` lives only in the **main repo root** (gitignored). When working from a worktree, reference it via absolute path or `cd` to main repo to run the update script.
- Headers index changes occasionally — never hardcode column letters; always look up via `headers.index(name)`.

### Chain reconciliation (multi-branch operators)
- When existing sheet slugs are address-named (e.g. `jln-antoi`, `jln-belinggai`), **map them to operator branches by street address**, not by guessing from the name. Fetch each operator branch page and compare the address to the existing row's area/coords before deciding which slug maps to which branch.
- Present the full mapping table to the user before pushing: `existing slug → operator branch name → address`. The slug-to-branch mapping is the highest-risk part of a chain fix.
- For facilities that share a similar name with a chain but have a different phone number and aren't in the operator's branch directory: **do not group them**. Phone + operator directory are the two checkpoints.
- The operator's "branch count" is what they publish. Re-count from their live site before planning — the screenshot the user provides may be stale.

### Operator photos: Wix CDN
- Wix-hosted operator sites serve photos from `static.wixstatic.com/media/<id>~mv2.jpg`.
- WebFetch returns URLs with transformation suffixes like `/v1/fill/w_238,h_237,q_90,enc_avif,quality_auto/<id>~mv2.jpg` — strip everything after `/media/` except `<id>~mv2.jpg` to get the stable base URL.
- Hero = first image on the branch page; gallery = all subsequent `0807fc_*` images. Skip logo files (`d3104b_*`) and generic social-proof photos (e.g. `1cd9eba76...`).
- No WordPress `/wp-content/uploads/` pattern to expect from Wix sites; adjust URL probing accordingly.

### Static page regeneration after new rows
- `generate_facility_pages.py` fetches the **published CSV** (`/pub?output=csv`), not the export URL. There is typically a **5–10 minute publishing delay** after sheet edits before new rows appear in the pub CSV.
- After appending new facility rows to the sheet: **poll the pub CSV until the new slug count is correct** before running the generator; otherwise the new pages will be silently skipped.
  ```bash
  # Poll pattern (adjust slug prefix / expected count as needed)
  until python -c "
  import csv, urllib.request, sys
  rows = list(csv.DictReader(...))
  print(sum(1 for r in rows if 'merry' in r.get('slug','').lower()))
  " | grep -qx '6'; do sleep 60; done
  ```
- After the pub CSV reflects all new rows: run both `python generate_facility_pages.py` AND `python generate_sitemap.py`, then commit the `facility/` tree + `sitemap.xml` together. New facility URLs 404 until this is done.

### Worktree rebase collisions
- Automated agents (editorial bulk writer, WhatsApp fix, etc.) commit to `main` concurrently. When pushing from a worktree, `git push origin HEAD:main` may fail with "non-fast-forward". Pattern:
  ```bash
  git fetch origin main
  GIT_EDITOR=true git rebase origin/main
  git push origin HEAD:main
  ```
- If `_blockers.json` conflicts during rebase: merge both sets of keys manually (keep all existing entries + add new ones), then `git add` and `GIT_EDITOR=true git rebase --continue`.

### License status in editorials (locked 2026-05-09)

**Rule: MOH and JKM are mutually exclusive registries. Do not ask about JKM for MOH-licensed facilities.**

The `jkm_data_source` column in the sheet drives the editorial `**License & verification**` section and the "What to ask on visit" bullets.

**License & verification block — write exactly one bullet:**
| `jkm_data_source` value | Editorial text |
|------------------------|----------------|
| contains "moh" | `- MOH Licensed — confirmed in MOH nursing home registry.` |
| contains "jkm" AND `licence_number` filled | `- JKM Registered — licence number: <number>.` |
| contains "jkm" AND no licence number | `- JKM Registered — confirmed in JKM registry.` |
| neither | `- To be verified — confirm JKM or MOH registration on visit.` |

**"What to ask on visit" — JKM registration questions:**
- **MOH licensed**: remove ALL bullets that mention JKM. MOH-licensed facilities are regulated by the Ministry of Health and will not hold a JKM registration. Asking about JKM is incorrect and confusing.
- **JKM confirmed** (licence in sheet): remove "Is the facility registered with JKM?" style bullets — the answer is already known. Also remove "Can you show the JKM registration certificate?" if phrased as a registration check. It's fine to keep operational questions like admission eligibility or waiting lists.
- **Unverified**: keep the JKM registration ask — families should verify it on visit.

**Script:** `fix_jkm_ask.py` applies these rules across a batch. Re-run whenever editorials are regenerated in bulk.

**Hardcoded "What to ask on your tour" card in `facility.html`** (the reviews tab, separate from the editorial):
- The inspection question is rendered dynamically from `f.jkm_data_source`:
  - MOH → "When was the last MOH inspection, and can I see the result?"
  - JKM → "When was the last JKM inspection, and can I see the result?"
  - Unverified → "Is the facility registered with JKM or MOH, and can I see the licence and last inspection result?"
- After any change to this block, regenerate all static pages with `python generate_facility_pages.py`.

### Column-shift / corruption detection (locked 2026-05-03 from Jasper Lodge fix)
When pulling a row, **dump every column raw** — not just the ones you expect — and look for misplaced data. Past corruption patterns to scan for:
- `google_maps_url` that starts with `https://lh3.googleusercontent.com/` or `https://streetviewpixels-pa.googleapis.com/` → it's a Google CDN photo URL, not a place URL. Replace with a Maps search URL: `https://www.google.com/maps/search/?api=1&query=<urlencoded name + address>`.
- `last_updated` containing pipe-separated URLs → photos got dumped into the wrong column. Move to `photos`, set `last_updated` to today.
- `halal` containing a number like `10` → that's a misplaced `photo_count`. Clear it.
- `latitude` or `longitude` containing prose ("X is a care home located in Selangor...") → an editorial blurb landed in the coords column. Clear both lat/lng unless you can verify real numbers.
- `editorial_summary` containing literal `",\n\n      "` or other JSON fragments → broken upload from a previous batch. Rewrite from scratch.

**Pre-flight check in the update script:** before pushing, assert `'"' not in editorial_body` for every branch — any straight double-quote in a published editorial is suspicious (curly quotes are fine). The script should abort on failure, not push corrupted text.

### Chain-aware editorials with shared paragraph 2 (locked 2026-05-03)
When fixing multiple branches of one chain in one pass:
- Paragraph 1 = branch-specific (address, what's distinctive). Paragraph 3 = branch-specific (review trail, practical viewing notes). **Paragraph 2 is identical across all branches** — services list verbatim from operator + capacity + pricing line. Saves work and keeps the chain story consistent.
- If the operator only has individual pages for SOME branches (Jasper had pages for PJ2/PJ5 only, none for PJ1/PJ3), say so explicitly in paragraph 3 of the un-paged branches and flag any third-party-sourced address as third-party (don't pretend it's operator-confirmed).
- Phone normalisation: if the per-branch number on the sheet doesn't appear anywhere on the operator site, switch to the national careline (when the operator publishes one shared across branches) rather than keeping a number you can't verify.

### When the user supplies a pricing number
- Treat user-supplied pricing the same as any unverified claim: confirm against the operator site before locking it into `editorial_summary`, `pricing_display`, `private_price`, `shared_price`. Don't shortcut just because the user said it.
- If you can't find it on the operator site, ask the user once: "Operator site doesn't list a price — should I publish your number, or 'Call for pricing'?" The Jasper session burned a draft because the user gave a price ("from RM 2,500+") then retracted it as confused with another profile after the script was already written.
