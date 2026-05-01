# Stage 02 — Data Enrichment

## Status: 🟡 In progress — Johor done, KL/Selangor pending

## What's done

**Pass A — Apify Google Maps (324/324)**
Filled: `area, latitude, longitude, phone, rating, review_count, wheelchair, hero_image, photos, google_maps_url`

**Pass B — WebFetch website extraction (Johor: ~60 facilities)**
Filled where evidence found: `care_types, care_nursing, care_dementia, care_palliative, care_rehab, care_respite, care_assisted, doctor_visits, medical_physio, languages, halal, shared_price, private_price, editorial_summary`

**Pass C — Photo gallery**
Up to 10 photos per facility. 261 of 269 live facilities have hero images.

**Pass D — Details tab (26 Johor facilities)**
Rooms, clinical capabilities, policies, checklists, nearby landmarks uploaded via `upload_details_batch*.py` scripts.

**Pass E — KL/Selangor data upload**
198 new facilities scraped via Apify (kl_selangor_raw.json) and processed by `process_kl_selangor.py`. State column (`BC`, index 54) added to sheet. All 198 uploaded.

**Pass F — Status column + Johor verification**
`status` column added (BD). 55 Johor facilities marked `unverified` (no care_types, pending contact). 4 marked `removed`. 31 had care_types auto-filled and remain live.

## What's pending (priority order)

1. **Pricing outreach** — 254 of 269 live facilities have blank pricing. Call or email each facility. This is the #1 data gap.
2. **KL/Selangor editorials** — 198 facilities have zero editorial summaries. No Details tab content either.
3. **JKM licence lookup** — Only 1 licence number across all 269 facilities. Bulk lookup from JKM public register needed.
4. **Johor hidden-55 outreach** — Email/phone to confirm care types; restore or permanently remove.
5. **Jeta Care pricing** — 2020 data, needs reconfirmation.
6. **Haywood Senior Living Medini** — JKM licence number unresolved.
7. **Haywood Medini + EHA Parkview** — Halal status unconfirmed.

## Hard rules

- **Don't invent.** Empty cell beats fake data.
- If pricing can't be confirmed, leave `shared_price` blank — `pricing_display` shows "Call for pricing" as fallback.
- Update `last_updated` whenever a row is verified.
- Photos column always pipe-separated; first URL is the hero.
- `care_types` must be populated before a facility is set live (enforced by status filter).

## Working scripts (root of project)

| Script | Purpose |
|--------|---------|
| `process_kl_selangor.py` | Process Apify output → upload to sheet |
| `hide_unverified.py` | Add status column, mark unverified/removed |
| `upload_details_batch*.py` | Upload Details tab rows for specific facilities |
| `merge_photos_oauth.py` | Merge photo URLs into Facilities tab |
| `update_editorials.py` | Batch update editorial_summary column |
| `gen_state_pages.py` | Regenerate kuala-lumpur.html and selangor.html from johor.html template |
