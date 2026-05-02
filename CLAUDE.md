# CLAUDE.md — Nursing Home Guide Malaysia

Malaysia's most comprehensive elder care and nursing home guide. Covers nursing homes, assisted living, day care, and home care. Built by a doctor to help families make the most important decision of their lives.

**Live:** https://ibkaarmy-hub.github.io/nursinghomeguide-my/
**Repo:** https://github.com/ibkaarmy-hub/nursinghomeguide-my
**Domain target:** nursinghomeguide.my

---

## Stack (current)

- Static HTML/CSS/JS, hosted on **GitHub Pages**
- Data: single Google Sheet, published as CSV; site fetches at page load
- Sheet ID: `1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk`
- Facilities tab gid: `292378871` | Details tab gid: `1104748854`
- Note: sheet also has a legacy `details_seed` tab (gid=1866835625, 84 rows of placeholder data) — **not used by the site**, safe to delete
- Photos: Google CDN URLs (lh3.googleusercontent.com). Not stable long-term — mirror to Supabase Storage before scaling
- Vercel/Supabase/Next.js are not in use — possible future migration, not blocking

## Folder map

```
.
├── CLAUDE.md, CONTEXT.md, PROJECT.md     ← docs layer
├── facility.html                          ← facility profile (4-tab)
├── index.html                             ← Malaysia state picker landing page
├── johor.html                             ← Johor state listing page
├── kuala-lumpur.html                      ← KL state listing page
├── selangor.html                          ← Selangor state listing page
├── org.html                               ← Organisation/chain profile page
├── style.css                              ← all shared styles
├── photo-manager.html                     ← admin tool: trim photos per facility
├── data.js                                ← CSV fetcher, parser, GROUPS registry
├── _config/                               ← brand, voice, domain notes
└── stages/
    ├── 01-data/      — DONE (406 rows in sheet; ~350 live after status filtering)
    ├── 02-enrich/    — EDITORIALS DONE 100% (350/350 live facilities; pricing + Details tab still pending)
    ├── 03-content/   — NOT STARTED (guide pages, area pages, BM translations)
    ├── 04-design/    — DONE (all page templates shipped)
    └── 05-build/     — DEFERRED (stay on static HTML)
```

## Sheet schema (56 columns)

Identity: `title, slug, url, area, latitude, longitude, google_maps_url`
Contact: `phone, whatsapp, website, facebook`
Pricing: `pricing_display, shared_price, private_price, four_bed_price, dorm_price`
Care: `care_types, care_nursing, care_dementia, care_palliative, care_rehab, care_respite, care_assisted`
Medical: `doctor_visits, nurse_ratio_day/night, medical_physio, medical_ot, medical_wound, medical_peg, medical_dementia_unit, medical_dialysis, medical_oxygen, medical_meds`
Beds/access: `total_beds, availability, wheelchair, parking, visiting_hours`
Other: `religion, languages, halal, subsidy, ownership_type, licence_number, rating, review_count, last_updated, editorial_summary`
Photos: `hero_image, photos (pipe-separated), photo_count`
Admin: `state` (Johor / Kuala Lumpur / Selangor), `status` (blank=live, unverified=hidden, removed=permanent)

## Hard rules

- **Never invent facility data.** Only publish what is verified from a source.
- **Don't fabricate pricing.** Show "Call for pricing" when unknown — that's honest and acceptable.
- The Google Sheet is the single source of truth. Edits go there, not in code.
- All user-facing content must eventually exist in EN + BM.
- Don't mock the site against fake data — fetch the live CSV.
- Push directly to `main` — no PR flow. GitHub Pages auto-deploys.

## How updates flow

1. Data changes → edit the Google Sheet (or run a Python script via the Sheets API)
2. Site changes → edit HTML/CSS/JS → push to `main` → GitHub Pages auto-deploys
3. Photo curation → use `photo-manager.html` to drop bad photos, copy cleaned cell to sheet

## Two-sheet data model

**Tab 1 — `Facilities`** (gid=292378871)
One row per facility, ~56 columns. Main listing data.

**Tab 2 — `Details`** (gid=1104748854)
Schema: `slug, section, label, value`. Per-facility custom facts. Lets us add extras without growing column count.

Recognised `section` values:

| section | renders as | example |
|---------|-----------|---------|
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

## Status column (visibility control)

| value | meaning |
|-------|---------|
| *(blank)* | Live — shows on site |
| `unverified` | Hidden — care_types unknown, pending outreach |
| `removed` | Permanently hidden — confirmed non-NH (resort, nursery, etc.) |

`loadFacilities()` in data.js filters out `unverified` and `removed` automatically.

## GROUPS registry (data.js)

~36 organisation groups defined in `GROUPS` object. `GROUPS_BY_SLUG` is the reverse index (slug → group). Used to show group tags on facility cards and profiles, and to populate `org.html`.

To add a new group: add entry to `GROUPS` in data.js, list all branch slugs. The org page and branch tags populate automatically.

**Groups added in session 2026-05-02:** Genesis Life Care (5 branches), My Aged Care (5 PJ branches), Mintygreen (7 branches), Attia Nursing Care (3 branches), Woodrose Senior Residences (2 Shariah-compliant branches), Noble Care (3 branches), Mona Elder Care (4 branches), Harvestars (2 branches), Green Acres (3 branches). Cozzi-confinement removed. Duplicate/truncated slug entries cleaned up.

## Live facility counts (2026-05-02, post session 2)

| State | Live | Hidden (unverified) |
|-------|------|---------------------|
| Johor | ~74 | 55 |
| Kuala Lumpur | 66 | 0 |
| Selangor | 206 | 1 |
| **Total** | **~346** | **56** |

Notes:
- 82 MDAC facilities added (sheet now 406 rows); many Johor stubs
- 4 Cozzi confinement entries marked `removed` (Yong Peng, Muar, Sri Jaya, Tanah Merah)
- **100% editorial coverage** — every live facility has a 250+ word editorial in column AY
- Editorial coverage confirmed: Johor 78/78, KL 66/66, Selangor 206/206 = 350/350

## Editorial rules (locked 2026-05-02)

Tone: knowledgeable friend, 3 paragraphs, 250–400 words, verified facts only.

**Never use:**
- "statistically unreliable", "warrants caution", "warrants scrutiny", "concerning rating"
- "only/just/merely N reviews"
- "not in directory X", "absence of any digital presence" (absence ≠ evidence)
- Critical/undermining framing in the editorial body

Frame unverified items as call-time questions. Red flags belong in `facts.red_flags` only (not in the published editorial). Always write a complete editorial — never leave it empty.

Skill: `.claude/commands/nh-profiles.md`
