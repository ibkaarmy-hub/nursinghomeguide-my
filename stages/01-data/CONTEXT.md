# Stage 01 — Data Collection

## Status: ✅ Done — 324 facilities across 3 states

## What's in the sheet

| State | Rows | Live | Hidden |
|-------|------|------|--------|
| Johor | 126 | 71 | 55 (status=unverified) |
| Kuala Lumpur | 56 | 56 | 0 |
| Selangor | 142 | 142 | 0 |
| **Total** | **324** | **269** | **55** |

For every facility: `title, slug, area, address, latitude, longitude, phone, rating, review_count, hero_image, photos, google_maps_url, state`

## Sources

**Johor:** JKM licensed list → Apify Google Maps scrape (`compass/crawler-google-places`)
**KL + Selangor:** Apify Google Maps scrape of Google Maps search results, filtered by `is_nh()` heuristic + state assignment logic. Raw data: `kl_selangor_raw.json`. Processing script: `process_kl_selangor.py`.

## Schema columns added since initial scrape

- `state` — "Johor" / "Kuala Lumpur" / "Selangor" (column BC, index 54)
- `status` — blank / "unverified" / "removed" (column BD, index 55)
- Both added via Google Sheets API (`appendDimension` + header write)

## Known issues

- **55 Johor facilities hidden** — no `care_types`, pending email/phone verification. Run `hide_unverified.py` output to see the list. Contact each, fill `care_types`, clear `status` to restore.
- **4 Johor rows permanently removed** — Magna Resort (hotel), Khazanah Nursery (children), Dion Confinement Center (postpartum), MediQas (medical supplier).
- **Facebook-only listings** — some KL/Selangor facilities have no website; Facebook only. Needs manual outreach.

## Re-run instructions (if needed)

If adding a new state or re-scraping:
1. Pull target search URLs / place IDs → save as `apify_input.json`
2. POST to `https://api.apify.com/v2/acts/compass~crawler-google-places/runs`
3. Poll until SUCCEEDED
4. Pull dataset items as JSON → save as `[state]_raw.json`
5. Run `process_kl_selangor.py` (or equivalent) to filter, dedupe, assign state, and upload
6. Run `hide_unverified.py` to apply status column to new unverified rows

## Apify credentials

- Actor: `compass/crawler-google-places`
- API token: stored in user_profile.md (memory) — do not commit to repo
- Slug list output: `kl_selangor_slugs.json`
