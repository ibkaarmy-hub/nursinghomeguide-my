# PROJECT.md — Nursing Home Guide Malaysia

Malaysia's most comprehensive elder care directory. Covers nursing homes, assisted living, day care, and home care. Built to help Malaysian families make a high-stakes decision with verified information.

**Live:** https://nursinghomeguide.my
**Repo:** https://github.com/ibkaarmy-hub/nursinghomeguide-my
**Phase:** All 15 states live; content + outreach next

---

## Why this exists

Families searching for elderly care in Malaysia have nowhere to compare facilities neutrally. JKM publishes a licence list with no detail. Google Maps has reviews but no care info or pricing. Operator-run directories list themselves at #1. This directory pulls verified information together: care types, photos, location, contact, pricing where available — from a family's perspective, not an operator's.

See [`_research/competitors.md`](_research/competitors.md) for the competitive gap analysis.

---

## Stack

Static HTML/CSS/JS on GitHub Pages, fetching published Google Sheets CSV at page load. No backend. Google Sheets is the CMS — editors update the sheet, site reflects changes on next load. Per-facility static pages are pre-generated for SEO/social previews.

Migration to Next.js + Supabase + Vercel is deferred until data scale justifies it (see `stages/05-build/CONTEXT.md`).

---

## Stage progress (as of 2026-05-10)

| Stage | Goal | Status |
|-------|------|--------|
| 01-data | Clean MY facility list | ✅ 406 rows in sheet (~350 live after `status` filtering) |
| 02-enrich | Pricing, care types, photos, editorials | 🟡 Editorials 100%; Maps placeId 350/471; pricing + Details tab partial |
| 03-content | Guide pages, area pages, BM translations | 🟡 In progress: 6 guides shipped; area pages next |
| 04-design | All page templates | ✅ Shipped + landing page redesigned (2026-05-10) |
| 05-build | Production stack migration | ⬜ Deferred |

---

## What's been built

### Pages
- `index.html` — landing page with embedded 2-question care-type quiz + state dropdown + care type cards
- `nursing-homes/<state>/index.html` — state listing pages (all 15 states)
- `assisted-living/`, `day-care/`, `home-care/` — care category pages
- `facility.html` (template) + per-facility static pages at `/facility/<slug>/index.html`
- `org.html` — chain/group profile with all branch cards
- `sitemap.html` — human-readable site map (added 2026-05-10)
- `guides/which-care.html` — rebuilt 2-question triage guide (English only)
- `guides/government-assistance.html`, `guides/how-to-choose-nursing-home.html`, `guides/nursing-home-cost-malaysia.html`, `guides/jkm-moh-licensing.html`, `guides/jkm-nursing-home-licence-malaysia.html`
- `area/petaling-jaya/`, `area/johor-bahru/`, `area/cheras/`, `area/subang-jaya/` — area guides
- `photo-manager.html` — admin tool

### Navigation
- Site-wide sticky nav on all 46 user-facing pages: logo + 6 links (Nursing Homes, Assisted Living, Day Care, Home Care, Guides, Site Map)
- Mobile hamburger menu (≤768px) — collapses to full-width dropdown

### Data infrastructure
- Two-tab Google Sheet: Facilities (gid=292378871) + Details (gid=1104748854)
- `status` column for visibility control (`unverified` / `removed` hidden automatically)
- `data.js` — CSV fetcher + GROUPS registry (28 chain groups indexed)

### SEO infrastructure (2026-05-03, updated 2026-05-10)
- Custom domain live (Namecheap → GitHub Pages, CNAME committed)
- `sitemap.xml` (~383 URLs) submitted to Google Search Console
- `robots.txt`
- **786 per-facility static pages** (758 NH + 16 AL + 6 HC + 6 DC) with baked-in OG / Twitter / canonical / LocalBusiness JSON-LD + hidden `display:none` data block for AI crawlers
- **350/471 licensed facilities** have Google Maps `query_place_id` URLs in col T (batch run 2026-05-10 via Apify, ~$0.21)
- **8 social accounts** discovered via free website scraping (`scrape_social_from_websites.py`)
- JS category classifier (`facility.html`) and Python generator now aligned — nursing home takes precedence over day-care/AL
- `generate_facility_pages.py` STATE_DIRS expanded to all 15 states (previously wiped state listing pages on regeneration)
- Weekly remote agent regenerates static pages + sitemap (Mondays 09:00 KL)
- Manage agent: https://claude.ai/code/routines

---

## Competitive positioning

1. **Most comprehensive coverage** — nursing homes, assisted living, day care, home care
2. **Neutral angle** — only directory not run by an operator
3. **Detailed profiles** — editorials, care breakdown, clinical capabilities, photos
4. **Organisation pages** — chain/group view no other directory has
5. **Map view** — Leaflet + OpenStreetMap, no API key required
6. **Honest pricing** — published when verified, "Call for pricing" when not — never fabricated

---

## Data quality gaps

| Field | Coverage | Gap |
|-------|----------|-----|
| Editorial summary | 350 / 350 live | ✅ done |
| Google Maps placeId URL | 350 / 471 licensed | 121 unmatched (wrong result or no listing) |
| Social media (Facebook/Instagram) | 8 new found 2026-05-10 | More via nh-enrich on demand |
| Pricing (`shared_price`) | ~15 / 350 | Outreach needed |
| JKM licence number | low | Bulk-lookup pending |
| Details tab content | partial | KL/Selangor pending |
| Hidden facilities (`status=unverified`) | 56 | Verify or remove |

---

## Next actions

### Content (highest leverage)
1. Area guide: Petaling Jaya — beat operator listicles with neutrality. Grounded in `_research/`.
2. Area guides: Johor Bahru, Cheras, Subang Jaya, Kajang/Sungai Long.
3. Care-type guides: dementia, assisted living, day care, palliative, home care.
4. Pricing & subsidy guides — link magnets for journalists / NGOs / social workers.
5. BM translations of Tier 1 content (`panduan-pilih-pusat-jagaan.html` etc.)

### Design / UX
6. Add nav to auto-generated per-facility static pages (`generate_facility_pages.py` already updated via `_template_state.html`; re-run weekly agent or trigger manually).

### Data
7. Pricing outreach — call/email facilities with blank pricing.
8. JKM licence bulk lookup from public register.
9. Verify or remove the 56 hidden facilities.
10. Photo CDN migration — Google `lh3.googleusercontent.com` URLs are not stable long-term; mirror to Supabase Storage or Vercel Blob before scaling.

### Reach
11. Penang, Perak state content expansion.

---

## Resources

- Google Sheet: https://docs.google.com/spreadsheets/d/1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk/edit
- JKM directory: https://www.jkm.gov.my
- Backlink/outreach research: `_research/social-worker-outreach-audit.md`
