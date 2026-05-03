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
- Search Google Maps URL (from sheet) for reviews — read the top 10–20 reviews. Note recurring themes (positive and negative), staff mentions, specific care events described
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

### Read the rating timeline before judging it (locked 2026-05-03)
A low Google aggregate is not automatically a current red flag. Many Malaysian homes opened around 2017–2019 caught a cluster of harsh reviews in their shake-down period that still drag the average down years later, even when current operations are fine. Before letting a rating shape the editorial:

- **Filter Google reviews by "Newest" and check the dates.** If the 1-stars cluster in the opening years and recent reviews trend positive, the headline number is a stale snapshot, not a current signal.
- **Cross-check with the soft-launch / opening date** (operator website, FB page, "since YYYY" tagline). 1-stars from year 1–2 of operations are growing pains; 1-stars from the last 12 months are a current-state signal.
- If the pattern is old-negative / recent-positive: say so explicitly in the editorial and tell families to filter by "newest" before forming a view. Don't write the rating off, but don't let it steer the verdict either.
- If recent reviews are also negative: that's a current signal — still don't use banned framing ("warrants caution", "concerning rating", "leave off your shortlist"). Stick to verified facts and call-time questions per the editorial rules.

Never write off a facility with "for most families there are better options" framing based on aggregate alone. That phrasing is banned regardless of what the rating is.

### Don't call a website "sparse" without checking sub-pages
Before describing a website as thin / sparse / lacking specifics, actually fetch `/about`, `/services`, `/contact-us`, `/gallery`, `/packages` (or whatever the nav lists). The AustinLoyal site looked empty on the homepage but `/contact-us` had the registered company number, exact address, opening date, services list, and visiting policy — none of which made it into the original editorial. Sparse-website framing should describe what's actually missing after you've checked the sub-pages, not what you didn't see on the homepage.
