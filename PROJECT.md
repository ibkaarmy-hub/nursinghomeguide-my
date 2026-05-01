# PROJECT.md — Nursing Home Guide Malaysia

Malaysia's most comprehensive elder care and nursing home guide. Covers nursing homes, assisted living, day care, and home care. Built by a doctor to help families make the most important decision of their lives.

**Live:** https://ibkaarmy-hub.github.io/nursinghomeguide-my/
**Repo:** https://github.com/ibkaarmy-hub/nursinghomeguide-my
**Domain target:** nursinghomeguide.my
**Phase:** 3 states live (Johor, KL, Selangor) → Penang, Perak next

---

## Why this exists

Families searching for elderly care in Malaysia have nowhere to compare facilities. JKM publishes a licence list with no detail. Google Maps has reviews but no care info or pricing. This directory pulls everything together: care types, photos, location, contact, and pricing where available.

---

## Stack (current)

Static HTML/CSS/JS on GitHub Pages, fetching published Google Sheets CSV at page load. No backend. Google Sheets is the CMS — editors update the sheet, site reflects changes on next load.

Migration to Next.js + Supabase + Vercel is deferred until the data side justifies it (see Stage 05).

---

## Stage progress

| Stage | Goal | Status |
|-------|------|--------|
| 01-data | Clean MY facility list | ✅ 324 total rows (Johor 126, KL 56, Selangor 142) |
| 02-enrich | Pricing, care types, photos, editorials | 🟡 Photos done, 60 Johor editorials done, pricing & KL/Selangor editorials pending |
| 03-content | Guide pages, area pages, BM translations | ⬜ Not started — highest SEO priority |
| 04-design | All page templates | ✅ All pages shipped |
| 05-build | Production stack migration | ⬜ Deferred |

---

## What's been built

### Pages
- **`index.html`** — Malaysia state picker landing page; hero, why section, how it works
- **`johor.html`** — Johor state page: filter bar, area pills, sort, list/map toggle, Leaflet map
- **`kuala-lumpur.html`** — KL state page (same template)
- **`selangor.html`** — Selangor state page (same template)
- **`facility.html`** — 4-tab profile (Overview / Pricing / Care & Medical / Amenities + Map); carousel, sticky sidebar CTA, mobile fixed bar
- **`org.html`** — Organisation/chain profile page with all branch cards
- **`photo-manager.html`** — Admin tool for photo curation

### Data infrastructure
- **`data.js`** — CSV fetcher + parseCSV + loadFacilities() + loadDetails() + GROUPS registry + GROUPS_BY_SLUG index
- **`style.css`** — All shared styles; design tokens, card components, map, org, filter bar, skeleton loaders
- Two-tab Google Sheet model: Facilities (gid=292378871) + Details (gid=1866835625)
- `status` column: `unverified` / `removed` hides facilities from all pages without deleting data

### Data
- 324 total rows — 269 live, 55 hidden (status=unverified/removed pending verification)
- 28 organisation groups registered in data.js (13 Johor, 15 KL/Selangor)
- 60 editorial summaries written (all Johor)
- Details tab populated for ~26 Johor facilities (rooms, clinical, policies, checklists, nearby)
- Area normalisation map: 40+ raw Johor strings → 10 clean canonical areas (client-side, no sheet changes needed)

---

## Competitive positioning

1. **Most comprehensive** — nursing homes, assisted living, day care, home care all covered
2. **Detailed profiles** — editorial summaries, care type breakdown, clinical capabilities, photos
3. **Organisation pages** — chain/group pages no other directory has
4. **Map view** — Leaflet + OpenStreetMap, free, no API key
5. **Doctor-founded** — credibility signal for families and professionals
6. **Pricing where available** — honest "Call for pricing" when unknown, never fabricated

---

## Data quality gaps (as of 2026-05-01)

| Field | Live facilities with data | Gap |
|-------|--------------------------|-----|
| Pricing (shared_price) | 15 / 269 | 254 show "Call for pricing" |
| Editorial summary | 60 / 269 | 0 for KL/Selangor |
| JKM licence number | 1 / 269 | Critical pre-launch gap |
| Details tab content | ~26 / 269 | 0 for KL/Selangor |
| Johor hidden facilities | 55 | Need outreach to verify/restore |

---

## Known technical debt

- **Photo URLs are Google CDN** (`lh3.googleusercontent.com`) — not stable long-term; mirror to Supabase Storage or Vercel Blob before scaling
- **facility.html uses `?slug=` query params** — not ideal for SEO; clean URL paths (`/facilities/slug/`) are better but require a build step
- **No sitemap.xml or robots.txt** — blocks proper Google indexing
- **No structured data (schema.org)** — LocalBusiness, ItemList, BreadcrumbList all missing
- **No Google Search Console** — zero indexing visibility
- **BM translations** — not started; needed for Malay-speaking majority

---

## Next actions (prioritised)

### Immediate
1. Set up Google Search Console + submit sitemap.xml
2. Create robots.txt
3. Add LocalBusiness schema to facility profiles
4. Pricing outreach — call/email all 254 facilities with blank pricing
5. KL/Selangor editorials — 198 facilities with zero written content
6. JKM licence lookup — bulk lookup from JKM public register

### Content (SEO / backlinks)
7. Write "How Much Does a Nursing Home Cost in Malaysia?" — #1 link magnet
8. Write "How to Choose a Nursing Home in Malaysia" — referral from social workers
9. Write "How to Check JKM Licensing" — public service, linkable
10. District-level area pages (nursing home Petaling Jaya, nursing home JB, etc.)

### Data
11. Verify and restore 55 hidden Johor facilities via email/phone outreach
12. Confirm Jeta Care pricing (2020 data stale)
13. Resolve Haywood Senior Living Medini JKM licence
14. Confirm halal status: Haywood Medini, EHA Parkview

---

## Resources

- Google Sheet: https://docs.google.com/spreadsheets/d/1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk/edit
- JKM directory: https://www.jkm.gov.my
- Apify account: compass/crawler-google-places actor
- SEO backlink plan: see `social_work_audit_report.md` and the SEO agent report (completed 2026-05-01)
