# Stage 03 — Content

## Status: ⬜ Not started

Editorial summaries for 37 facilities are auto-generated from website extraction (in `editorial_summary` column). Everything else is greenfield.

## What needs writing

1. **Index/homepage copy** — value prop, search-by-state, featured/popular listings
2. **State hub pages** — one per state with facilities listed (table or cards), price-range banner, intro paragraph, FAQs
3. **Facility editorial summaries** for the 87 rows that don't have one — write from the structured data we have rather than inventing
4. **FAQ pages** — pricing, JKM subsidy, how to choose, what's halal-certified, palliative vs nursing
5. **BM translations** — every public page needs a BM equivalent

## Voice

See `_config/voice-rules.md`. Key points:
- Lead with price when known
- No vague superlatives ("best", "top-rated")
- Sentences under 20 words
- Plain English, second-person ("you"), no marketing-speak

## Constraints

- Pricing is the first substantive section on every facility page (already enforced in `facility.html`)
- Don't fabricate — if a fact isn't in the sheet, omit it
- All public-facing strings must have a BM counterpart before launch

## Output

Final copy lives in the Google Sheet (`editorial_summary`, future `meta_title`, `meta_description`, `intro_bm`, etc.) or in Markdown files in this stage's `output/` for state hub / FAQ pages.
