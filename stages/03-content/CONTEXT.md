# Stage 03 — Content

## Status: 🟡 In progress

`guides/which-care.html` and `guides/government-assistance.html` are shipped. Area guides and care-type guides next.

## Hard rule: read `_research/` first

Before writing any new guide, area page, or content piece, read [`_research/`](../../_research/):

- `_research/market-demand.md` — DOSM demographics, supply growth, policy gap
- `_research/user-questions.md` — what Malaysian families actually ask (Lowyat-sourced)
- `_research/competitors.md` — operator-listicle landscape + the gap we own
- `_research/pricing-benchmarks.md` — verified Klang Valley fee tiers

This grounds content in evidence and protects our differentiator (neutral, family-side, fact-based vs operator-marketing listicles).

## What needs to be built (priority order)

### Tier 1 — Area guides (next up)

5 area pages at `/area/<slug>/index.html`, evidence-driven:

1. **Petaling Jaya** — heaviest commercial competition, strongest case for our angle
2. **Johor Bahru** — 46 facilities, light competitor coverage
3. **Cheras** — high KL search volume, light competitor coverage
4. **Subang Jaya / USJ** — moderate competition, 8 facilities
5. **Kajang / Sungai Long** — quieter cluster, 14 facilities

Each page covers (per evidence in `_research/user-questions.md`):
- Price reality in this area (real range from facility data)
- JKM vs MOH licensing distinction (under-explained elsewhere)
- What to ask staff to test specific medical capability (bed-bound, tube feeding, dementia)
- Transport access + nearest hospitals (addresses the "being forgotten" / "ED in time" concerns)
- Religious / dietary fit by area
- Waiting list reality
- Red flags after the polished tour

Word target: 600–900 words of editorial prose + auto-generated facility grid.

### Tier 1 — Link magnets / evergreen guides

1. **`nursing-home-cost-malaysia.html`** — "How Much Does a Nursing Home Cost in Malaysia? (2026 Guide)"
   - Real ranges from sheet + benchmarks from `_research/pricing-benchmarks.md`
   - #1 backlink magnet — journalists, NGOs, social workers cite this
   - Target keywords: "nursing home price Malaysia", "berapa harga pusat jagaan warga emas"

2. **`how-to-choose-nursing-home-malaysia.html`** — "How to Choose a Nursing Home in Malaysia"
   - Checklist format, JKM licensing angle, questions to ask on a visit (driven by `_research/user-questions.md`)
   - 800–1,000 words minimum

3. **`jkm-nursing-home-license-malaysia.html`** — "How to Check if a Nursing Home is JKM-Licensed"
   - Public service content; linkable from government-adjacent sites
   - Reference our `licence_number` data as a verification resource

### Tier 2 — Care-type guides (3-month horizon)

- `dementia-care-malaysia.html` — links from ADFM, neurologists
- `assisted-living-malaysia.html`
- `day-care-elderly-malaysia.html`
- `home-care-malaysia.html`
- `palliative-care-home-malaysia.html` — links from Hospis Malaysia

### Tier 3 — 6-month horizon

- `questions-to-ask-nursing-home.html` — printable checklist (high share value)
- `expat-guide-elderly-parents-malaysia.html` — for expat community
- BM versions of Tier 1 content (`panduan-pilih-pusat-jagaan.html` etc.)
- News/updates section

## Voice (from `_config/voice-rules.md`)

- Lead with care type and location
- No vague superlatives ("best", "top-rated")
- Sentences under 20 words
- Plain English, second-person ("you"), no marketing-speak
- State pricing honestly: "From RM X/month" when known, "Call for pricing" when not

## Output

- Final HTML files in repo root or `guides/` subfolder (existing pattern: `guides/which-care.html`)
- Area pages at `/area/<slug>/index.html` (consistent with `/facility/<slug>/`)
- Markdown drafts can live in `stages/03-content/output/` if useful before HTML conversion

## Facility-specific outreach notes

`facility-research-notes/` (5 files) — facility-by-facility outreach research from the 02-enrich era. Reference if writing about that specific facility's editorial.
