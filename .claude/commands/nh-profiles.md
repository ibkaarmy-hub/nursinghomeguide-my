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

**Step 2 — External research**
- Search Google Maps URL (from sheet) for reviews — read **all** reviews, not just the first page. Note recurring themes (positive and negative), staff mentions, specific care events described
- Search `site:[website-domain]` for additional indexed content
- Check if mentioned in any news, JKM lists, or directories

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

**Step 4 — Write the editorial (3 paragraphs)**
- **Paragraph 1**: What the home is, where it is, who runs it, and what type of care it primarily provides. Include founding year or operator background if known.
- **Paragraph 2**: Specific care capabilities, capacity, notable facilities or programmes. Only state what is confirmed from website or reviews.
- **Paragraph 3**: What families should know — practical considerations, who this home suits best, any gaps to ask about when calling.

Rules:
- No fabrication. If unsure, don't say it.
- Write like a knowledgeable friend, not a brochure or a bot.
- No generic phrases: "warm and caring environment", "dedicated team", "holistic approach"
- Max 120 words per paragraph. Total editorial: 250–400 words.
- Write in English.

**Tone — DO NOT undermine the facility:**
- Never frame thin review counts as "statistically unreliable", "warrants caution", or "a perfect score on very few reviews is suspicious". A small number of reviews is normal for many small homes — just describe it neutrally if at all ("a small but consistently positive reviewer base" is fine).
- Never list absences as evidence ("does not appear in the top-10 roundups", "not in the AGECOPE directory", "not mentioned in any news"). Don't catalogue what's missing — focus on what's verified.
- Don't use language that reads as accusatory or sceptical. Families are stressed enough; the editorial's job is to describe what's verified and tell them what to ask, not to cast doubt on the facility.
- If something is unverified, frame it as something to ask about on a call ("worth confirming the JKM licence number when you visit"), not as a red flag in the prose. Red flags belong in the `facts.red_flags` field, not the editorial body.
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
- Update `editorial_summary` column for each facility using their `row_idx`
- Also update any other columns where new verified data was found (care_types, total_beds, etc.)

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
- Drop the standard EHA-style "ask for the JKM licence" line for established multi-branch chains with real websites; keep it for low-presence facilities.

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
