# CONTEXT.md — Stage Router

Quick lookup for "where do I work on X?". For working rules and conventions, see `CLAUDE.md`. For project mission, see `PROJECT.md`. For external research grounding, see `_research/`.

## Where to go for each task

| Task | Stage |
|------|-------|
| Add new facilities, re-scrape, dedupe | `stages/01-data/` |
| Fill missing fields (pricing, beds, halal, care types, photos, editorials) | `stages/02-enrich/` |
| Write guide pages, area pages, BM translations | `stages/03-content/` (read `_research/` first) |
| UI changes to any HTML/CSS/JS page | `stages/04-design/` |
| Static-site refactor or migration off GitHub Pages | `stages/05-build/` |

## Current focus (2026-05-03)

**03-content — area guides + care-type guides**

- Area pages: PJ first, then JB / Cheras / Subang Jaya / Kajang
- Pricing/subsidy guide pages — link magnets
- BM translations of Tier 1 content
- All grounded in `_research/` (market data, user questions, competitor gaps)

## Stage status

| Stage | Status | Summary |
|-------|--------|---------|
| 01-data | ✅ Done | 406 rows in sheet; ~346 live after status filtering |
| 02-enrich | ✅ Editorials done | 350/350 editorials; pricing + Details tab partial |
| 03-content | 🟡 In progress | 2 guides shipped (`which-care`, `government-assistance`); area pages next |
| 04-design | ✅ Done | All page templates shipped + per-facility static pages with OG/JSON-LD |
| 05-build | ⬜ Deferred | Stay on static HTML/GitHub Pages |

## Live facility counts (2026-05-03)

| State | Live | Hidden (`unverified`) |
|-------|------|------------------------|
| Johor | ~74 | 55 |
| Kuala Lumpur | 66 | 0 |
| Selangor | 206 | 1 |
| **Total** | **~346** | **56** |

## Hard rules (also in CLAUDE.md)

- The Google Sheet is the single source of truth.
- Never invent facility data. Unknown values surface as "Not published" / "Call for pricing", not fabricated.
- All live facilities must have `care_types` populated (enforced via `status=unverified` filter).
- Push directly to `main` — no PR flow. GitHub Pages auto-deploys.
- Read `_research/` before writing new content.
