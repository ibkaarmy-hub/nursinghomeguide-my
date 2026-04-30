# PROJECT.md — Nursing Home Guide Malaysia

A pricing-transparent nursing home directory for Malaysia. Built by a doctor. Modelled after VaccinePrice.sg.

**Live:** https://ibkaarmy-hub.github.io/nursinghomeguide-my/
**Repo:** https://github.com/ibkaarmy-hub/nursinghomeguide-my
**Domain target:** nursinghomeguide.my (not yet pointed)
**Phase:** Malaysia first → Singapore (Phase 2)

---

## Why this exists

Families searching for elderly care in Malaysia have nowhere to compare facilities by price, location, and care level. JKM publishes a license list with no other detail. Google Maps has photos and reviews but no pricing or care info. Nursing homes themselves rarely publish rates online — only EHA ElderCare and Yong An do, out of the 124 we surveyed.

The product is a directory that pulls everything together: pricing where verified, care levels, photos, location, contact — in EN and BM.

---

## Stack (current)

Static HTML/CSS/JS on GitHub Pages, fetching a published Google Sheets CSV at page load. No backend yet. Originally planned for Next.js + Supabase + Vercel; deferred until the data side is mature enough to justify it.

---

## Stage progress

| Stage | Goal | Status |
|-------|------|--------|
| 01-data | Clean MY facility list | ✅ 124 facilities (JKM scrape) |
| 02-enrich | Pricing, services, photos | 🟡 Photos + Maps + websites done. Pricing outreach pending |
| 03-content | EN + BM pages, FAQs, state hubs | ⬜ Not started |
| 04-design | Index + state + facility templates | 🟡 Facility profile shipped |
| 05-build | Production stack migration | ⬜ Deferred |

---

## What's been built

- **Sheet** (`google-sheets-facilities`, 50 columns) — single source of truth
- **facility.html** — profile page with 4 tabs (Overview / Pricing / Care & Medical / Location), photo gallery, sticky sidebar
- **index.html** — landing page (basic; needs work)
- **photo-manager.html** — admin tool to manually drop photos per facility, copy cleaned cell back to sheet
- **data.js** — CSV fetcher + parser

---

## Competitive moat

1. **Only directory that publishes real pricing** when the facility shares it
2. **Bilingual** — serves the BM-speaking majority that English-only directories ignore
3. **Doctor-founded** — credibility signal for families
4. **State-by-state coverage** based on JKM's licensed list, augmented with Google Maps

---

## Known issues / debt

- **Photo URLs are Google CDN** (`lh3.googleusercontent.com`) — they work but Google can rotate them. Mirror to Supabase Storage or Vercel Blob before launch.
- **18 facilities are Facebook-only** — WebFetch can't read those pages; outreach needed.
- **Pricing for 113 of 124 facilities is unknown** — the next big push.
- **5 entries are mis-categorized** in the JKM source (Cozzi confinement, Amitabha foundation) — should be removed before launch.
- **EN-only currently** — BM translations not started.

---

## Next actions

1. Twilio voice/WhatsApp outreach for pricing (priority — defines the moat)
2. Filter out mis-categorized entries from the sheet
3. Write index page with state-by-state navigation
4. Mirror photos to durable storage
5. BM translation pass on editorial summaries

---

## Resources

- Google Sheet (source of truth): https://docs.google.com/spreadsheets/d/1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk/edit
- JKM directory: https://www.jkm.gov.my
- Apify account: Vaccineprices (used for Google Maps scrape)
