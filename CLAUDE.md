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

## Two-sheet data model

The Google Sheet has **two tabs**, both consumed by `data.js`:

**Tab 1 — `Facilities`** (the main one we already had)
One row per facility, ~50 columns. Used for tabular fields shared by every listing.

**Tab 2 — `Details`** (new, long-format)
Schema: `slug, section, label, value`. One row per per-facility custom fact. Lets us add per-facility extras (room types, daily schedule, included/extras, nearby landmarks, JKM details) without ever growing the main sheet's column count.

Recognized `section` values (page renders these into the right UI components):

| section | renders as | example label / value |
|---------|-----------|-----------------------|
| `policies` | info-row pairs (Overview tab) | `Visiting hours` / `2pm–6pm daily` |
| `rooms` | info-row pairs (Pricing tab) | `2-bed (RM/mo)` / `2,800` |
| `included` | green checklist (Pricing tab) | `Diapers` / `yes` |
| `extras` | amber list (Pricing tab) | `Physio session` / `RM 60/session` |
| `clinical` | yes/no/unknown grid (Care tab) | `Syringe driver` / `yes` |
| `staffing` | info-row pairs (Care tab) | `RN overnight` / `Yes, 1 on duty` |
| `dining` | amenity tags (Amenities) | `Halal certified` / `Yes` |
| `activities` | amenity tags (Amenities) | `Daily exercise` / `yes` |
| `services` | amenity tags (Amenities) | `Laundry` / `included` |
| `outdoor` | amenity tags (Amenities) | `Compound size` / `21,800 sqft` |
| `schedule` | timetable (Amenities) | `09:30` / `Group physio` |
| `nearby` | landmark list (Map tab) | `Hospital Sultanah Aminah` / `~12 km` |
| `checklist` | sidebar bullet list | `Ask for JKM cert` / *(value blank)* |

To add a new section type, add a renderer in `facility.html` and document the convention here. The main sheet column count never grows.

To wire up the Details tab in production:
1. In Google Sheets: Data → Add new sheet, name it `Details`, columns: `slug, section, label, value`
2. File → Share → Publish to web → choose the Details sheet → CSV → publish; copy the `gid` from the resulting URL
3. Replace `DETAILS_TAB_GID` in `data.js` with that gid

Until the gid is set, `loadDetails()` returns `{}` and pages render fine using only the main sheet.
