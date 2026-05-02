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
