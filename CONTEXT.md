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

## Current focus (2026-05-10)

**02-enrich — Maps placeId batch complete; pricing + Details tab still pending**
**03-content — area guides + care-type guides**

- Maps placeId: 350/471 licensed facilities now have `query_place_id` URLs ✅
- Area pages: PJ done; JB / Cheras / Subang Jaya / Kajang next
- Pricing/subsidy guide pages — link magnets
- BM translations of Tier 1 content
- All grounded in `_research/` (market data, user questions, competitor gaps)

## Stage status

| Stage | Status | Summary |
|-------|--------|---------|
| 01-data | ✅ Done | 406 rows in sheet; ~350 live after status filtering |
| 02-enrich | 🟡 Mostly done | Editorials 100%; Maps placeId 350/471; pricing + Details tab partial |
| 03-content | 🟡 In progress | 6 guides shipped; area pages next |
| 04-design | ✅ Done | Landing page redesigned (care quiz + state dropdown); site-wide nav on all pages; sitemap.html |
| 05-build | ⬜ Deferred | Stay on static HTML/GitHub Pages |

## Live facility counts (2026-05-10)

| State | Live static pages | Notes |
|-------|-------------------|-------|
| All states | 786 canonical pages | 758 NH + 16 AL + 6 HC + 6 DC |
| Johor | ~74 | 55 hidden (unverified) |
| Kuala Lumpur | 66 | — |
| Selangor | 206 | 1 hidden |
| **Total live** | **~350** | **56 hidden** |

## Hard rules (also in CLAUDE.md)

- The Google Sheet is the single source of truth.
- Never invent facility data. Unknown values surface as "Not published" / "Call for pricing", not fabricated.
- All live facilities must have `care_types` populated (enforced via `status=unverified` filter).
- Push directly to `main` — no PR flow. GitHub Pages auto-deploys.
- Read `_research/` before writing new content.
