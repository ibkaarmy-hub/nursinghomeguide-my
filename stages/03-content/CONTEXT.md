# Stage 03 — Content

## Status: ⬜ Not started — highest SEO priority

## What needs to be built (priority order)

### Tier 1 — Write first (link magnets + evergreen)

1. **`nursing-home-cost-malaysia.html`** — "How Much Does a Nursing Home Cost in Malaysia? (2026 Guide)"
   - Use real pricing data from the sheet (average, median, range by state)
   - This is the #1 backlink magnet — every journalist, NGO, and social worker needs this figure
   - Target keywords: "nursing home price Malaysia", "berapa harga pusat jagaan warga emas"

2. **`how-to-choose-nursing-home-malaysia.html`** — "How to Choose a Nursing Home in Malaysia"
   - Checklist format, JKM licensing angle, questions to ask on a visit
   - Target audience: families at decision point; social workers will link to this
   - 800–1,000 words minimum

3. **`jkm-nursing-home-license-malaysia.html`** — "How to Check if a Nursing Home is JKM-Licensed"
   - Public service content; linkable from government-adjacent sites
   - Reference our licence_number data as a verification resource

### Tier 2 — Within 3 months

4. **District area pages** (one per major area)
   - `nursing-home-petaling-jaya.html`, `nursing-home-johor-bahru.html`, `nursing-home-subang-jaya.html`, `nursing-home-klang.html`, `nursing-home-shah-alam.html`, `nursing-home-cheras.html`
   - Each: 300–500 words of area context + filtered facility list + nearby hospitals
   - Fast path to long-tail local keyword rankings

5. **Care type guides**
   - `dementia-care-malaysia.html` — links from ADFM, neurologists
   - `assisted-living-malaysia.html`
   - `day-care-elderly-malaysia.html`
   - `home-care-malaysia.html`
   - `palliative-care-home-malaysia.html` — links from Hospis Malaysia

6. **Government subsidy guide**
   - `government-subsidy-nursing-home-malaysia.html` — who qualifies, how to apply JKM subsidy

### Tier 3 — 6-month horizon

- `questions-to-ask-nursing-home.html` — printable checklist (high share value)
- `expat-guide-elderly-parents-malaysia.html` — for expat community
- Bahasa Malaysia versions of Tier 1 content (`panduan-pilih-pusat-jagaan.html` etc.)
- News/updates section

## KL/Selangor editorials (198 facilities)

These are the most pressing content gap. Each facility profile without an editorial summary is thin content. Approach:
- Write genuine editorial where website/data allows
- Auto-generate template summary from structured data fields as fallback: "X is a [care_types] facility in [area], [state]…"
- Progressively replace template with genuine copy as outreach confirms details

## Voice (from `_config/voice-rules.md`)

- Lead with care type and location
- No vague superlatives ("best", "top-rated")
- Sentences under 20 words
- Plain English, second-person ("you"), no marketing-speak
- State pricing honestly: "From RM X/month" when known, "pricing on request" when not

## Output

Final copy lives in:
- Google Sheet (`editorial_summary` column for facility summaries)
- New HTML files in the project root for guide/area pages
- Markdown drafts in `stages/03-content/output/` before final HTML conversion
