# CLAUDE.md — Nursing Home Guide Malaysia

A pricing-transparency directory for Malaysian nursing homes. No competitor publishes pricing; that is the entire moat. English first, Bahasa Malaysia second.

**Live:** https://ibkaarmy-hub.github.io/nursinghomeguide-my/
**Repo:** https://github.com/ibkaarmy-hub/nursinghomeguide-my
**Domain target:** nursinghomeguide.my

---

## Stack (current)

- Static HTML/CSS/JS, hosted on **GitHub Pages**
- Data lives in a single Google Sheet, published as CSV; site fetches at page load
- Sheet ID: `1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk` (`google-sheets-facilities`)
- Photos: Google CDN URLs (lh3.googleusercontent.com). **Not stable long-term** — plan a Supabase Storage mirror before launch
- Vercel/Supabase/Next.js are not in use yet — possible future migration, not blocking

## Folder map

```
.
├── CLAUDE.md, CONTEXT.md, PROJECT.md     ← docs layer
├── facility.html, index.html, style.css  ← the live site
├── photo-manager.html                    ← admin tool: trim photos per facility
├── data.js                               ← CSV fetcher + parser
├── _config/                              ← brand, voice, domain notes
└── stages/
    ├── 01-data/      — DONE (124 facilities scraped from JKM)
    ├── 02-enrich/    — IN PROGRESS (Apify + WebFetch done; pricing outreach pending)
    ├── 03-content/   — not started
    ├── 04-design/    — facility profile shipped; index/state pages pending
    └── 05-build/     — N/A while we stay on static HTML
```

## Sheet schema (50 columns)

Identity: `title, slug, url, area, latitude, longitude, google_maps_url`
Contact: `phone, whatsapp, website, facebook`
Pricing: `pricing_display, shared_price, private_price, four_bed_price, dorm_price`
Care: `care_types, care_nursing, care_dementia, care_palliative, care_rehab, care_respite, care_assisted`
Medical: `rn_24_7, doctor_visits, nurse_ratio_day/night, medical_physio, medical_ot, medical_wound, medical_peg, medical_dementia_unit, medical_dialysis, medical_oxygen, medical_meds`
Beds/access: `total_beds, availability, wheelchair, parking, visiting_hours`
Other: `religion, languages, halal, subsidy, ownership_type, licence_number, rating, review_count, last_updated, editorial_summary`
Photos: `hero_image, photos (pipe-separated), photo_count`

## Hard rules

- **Never invent facility data.** Only publish what is verified from a source.
- **Always publish pricing when known** — that is the differentiator.
- The Google Sheet is the single source of truth. Edits go there, not in code.
- All user-facing content must eventually exist in EN + BM.
- Don't mock the site against fake data — fetch the live CSV.

## How updates flow

1. Data changes → edit the Google Sheet (or import a merged CSV via File → Import → Replace)
2. Site changes → edit HTML/CSS/JS → push to `main` → GitHub Pages auto-deploys
3. Photo curation → use `photo-manager.html` to drop bad photos per facility, copy the cleaned cell back to the sheet
