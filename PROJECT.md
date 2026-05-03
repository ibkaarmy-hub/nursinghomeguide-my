# PROJECT.md — Nursing Home Guide Malaysia

Malaysia's most comprehensive elder care directory. Covers nursing homes, assisted living, day care, and home care. Built to help Malaysian families make a high-stakes decision with verified information.

**Live:** https://nursinghomeguide.my
**Repo:** https://github.com/ibkaarmy-hub/nursinghomeguide-my
**Phase:** 3 states live (Johor, KL, Selangor) → Penang, Perak next

---

## Why this exists

Families searching for elderly care in Malaysia have nowhere to compare facilities neutrally. JKM publishes a licence list with no detail. Google Maps has reviews but no care info or pricing. Operator-run directories list themselves at #1. This directory pulls verified information together: care types, photos, location, contact, pricing where available — from a family's perspective, not an operator's.

See [`_research/competitors.md`](_research/competitors.md) for the competitive gap analysis.

---

## Stack

Static HTML/CSS/JS on GitHub Pages, fetching published Google Sheets CSV at page load. No backend. Google Sheets is the CMS — editors update the sheet, site reflects changes on next load. Per-facility static pages are pre-generated for SEO/social previews.

Migration to Next.js + Supabase + Vercel is deferred until data scale justifies it (see `stages/05-build/CONTEXT.md`).

---

## Stage progress (as of 2026-05-03)

| Stage | Goal | Status |
|-------|------|--------|
| 01-data | Clean MY facility list | ✅ 406 rows in sheet (~346 live after `status` filtering) |
| 02-enrich | Pricing, care types, photos, editorials | ✅ Editorials 100% (350/350); pricing + Details tab partial |
| 03-content | Guide pages, area pages, BM translations | 🟡 In progress: `guides/which-care.html` + `guides/government-assistance.html` shipped; area pages next |
| 04-design | All page templates | ✅ Shipped |
| 05-build | Production stack migration | ⬜ Deferred |

---

## What's been built

### Pages
- `index.html` — Malaysia state picker landing
- `johor.html`, `kuala-lumpur.html`, `selangor.html` — state pages with filter, sort, list/map toggle
- `facility.html` (template) + per-facility static pages at `/facility/<slug>/index.html`
- `org.html` — chain/group profile with all branch cards
- `guides/which-care.html`, `guides/government-assistance.html` — first guide pages
- `photo-manager.html` — admin tool

### Data infrastructure
- Two-tab Google Sheet: Facilities (gid=292378871) + Details (gid=1104748854)
- `status` column for visibility control (`unverified` / `removed` hidden automatically)
- `data.js` — CSV fetcher + GROUPS registry (28 chain groups indexed)

### SEO infrastructure (2026-05-03)
- Custom domain live (Namecheap → GitHub Pages, CNAME committed)
- `sitemap.xml` (~383 URLs) submitted to Google Search Console
- `robots.txt`
- 349 per-facility static pages with baked-in OG / Twitter / canonical / LocalBusiness JSON-LD
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
| Pricing (`shared_price`) | ~15 / 346 | Outreach needed |
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

### Data
6. Pricing outreach — call/email facilities with blank pricing.
7. JKM licence bulk lookup from public register.
8. Verify or remove the 56 hidden facilities.
9. Photo CDN migration — Google `lh3.googleusercontent.com` URLs are not stable long-term; mirror to Supabase Storage or Vercel Blob before scaling.

### Reach
10. Penang, Perak state expansion (data + pages).

---

## Resources

- Google Sheet: https://docs.google.com/spreadsheets/d/1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk/edit
- JKM directory: https://www.jkm.gov.my
- Backlink/outreach research: `_research/social-worker-outreach-audit.md`
