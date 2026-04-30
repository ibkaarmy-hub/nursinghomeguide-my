# CONTEXT.md — Stage Router

## Where to go for each task

| Task | Stage |
|------|-------|
| Add a new facility, re-scrape JKM, dedupe | 01-data |
| Fill missing fields (pricing, beds, halal, care types, photos) | 02-enrich |
| Write copy: editorial summaries, state hub pages, FAQs (EN/BM) | 03-content |
| UI changes to facility/index pages, new components | 04-design |
| Static-site refactor or eventual migration off GitHub Pages | 05-build |

## Current focus

**Stage 02-enrich, pricing pass.** ~113 of 124 facilities still have no published pricing. Twilio voice/WhatsApp outreach is the next major task.

## Stage status

| Stage | Status |
|-------|--------|
| 01-data | ✅ Done — 124 facilities |
| 02-enrich | 🟡 In progress — see notes below |
| 03-content | ⬜ Not started |
| 04-design | 🟡 Facility profile + photo gallery shipped; homepage and state pages pending |
| 05-build | — Skipped while on static HTML |

## 02-enrich progress (snapshot)

- Apify Google Maps scrape (124/124): area, lat/lng, phone, ratings, hours, wheelchair, hero photo
- WebFetch website extraction (37/56 sites usable): care types, languages, RN 24/7, halal, summaries
- Photo gallery scrape (119/124 with photos), privacy-filtered → 547 kept, 139 removed
- **Still missing for ~113 rows:** monthly pricing, total_beds, availability, halal status, RN ratios, dialysis/oxygen, subsidy
- 18 facilities are Facebook-only — need a different scraper or manual call

## Rule

The Google Sheet is the source of truth. Stage `output/` folders are scratch space — final data always lands in the sheet.
