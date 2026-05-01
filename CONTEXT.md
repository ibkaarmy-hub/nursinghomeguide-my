# CONTEXT.md — Stage Router

## Where to go for each task

| Task | Stage |
|------|-------|
| Add new facilities, re-scrape, dedupe | 01-data |
| Fill missing fields (pricing, beds, halal, care types, photos, editorials) | 02-enrich |
| Write guide pages, area pages, BM translations | 03-content |
| UI changes to any HTML/CSS/JS page | 04-design |
| Static-site refactor or migration off GitHub Pages | 05-build |

## Current focus

**02-enrich (KL/Selangor) + 03-content (guide pages)**

- 198 KL/Selangor facilities need editorials and Details tab content
- 254 live facilities have blank pricing — outreach needed
- Guide pages (cost guide, how-to-choose, JKM licensing) are the #1 SEO priority

## Stage status

| Stage | Status | Summary |
|-------|--------|---------|
| 01-data | ✅ Done | 324 rows: Johor 126, KL 56, Selangor 142 |
| 02-enrich | 🟡 In progress | Photos done, 60 Johor editorials done, pricing + KL/SEL editorials pending |
| 03-content | ⬜ Not started | Guide pages, area pages, BM translations — highest SEO priority |
| 04-design | ✅ Done | All page templates shipped and live |
| 05-build | ⬜ Deferred | Stay on static HTML/GitHub Pages until constraints force migration |

## Live facility counts (2026-05-01)

| State | Live | Hidden (pending verification) |
|-------|------|-------------------------------|
| Johor | 71 | 55 |
| Kuala Lumpur | 56 | 0 |
| Selangor | 142 | 0 |
| **Total** | **269** | **55** |

## Hard rules

- The Google Sheet is the single source of truth. Edits go to the sheet, not to code.
- Never invent facility data. Unknown values surface as "Not published" / blank, not fabricated.
- All live facilities must have `care_types` populated (enforced via status=unverified filter).
- Push directly to `main` — no PR flow.
