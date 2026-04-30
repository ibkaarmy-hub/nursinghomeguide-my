# Stage 01 — Data Collection

## Status: ✅ Done

124 facilities scraped from JKM and merged with Google Maps via the Apify `compass/crawler-google-places` actor.

## What's in the sheet

For every facility:
- `title, slug, area, address` (postal info from Maps)
- `latitude, longitude, google_maps_url`
- `phone` (114/124)
- `rating, review_count` (98/124)

## Known issues to fix in this stage

- **5 mis-categorized entries** (Cozzi confinement, Amitabha foundation, etc.) — postpartum / dialysis / general care, not nursing homes. Should be deleted from the sheet.
- **18 Facebook-only listings** — these have no scrapable website. Either accept Facebook as the contact channel, or de-prioritize until manual call.

## Re-run instructions

If the JKM list updates or you need to re-scrape:

1. Pull the canonical URL list from the sheet's `google_maps_url` column → save as `apify_input.json`
2. POST to `https://api.apify.com/v2/acts/compass~crawler-google-places/runs` with `startUrls`, `maxImages: 10`, `scrapePlaceDetailPage: true`
3. Poll `/v2/actor-runs/<id>` until `SUCCEEDED`
4. Pull dataset from `/v2/datasets/<datasetId>/items?clean=true&format=json`
5. Merge into the sheet (see `merge_apify.py` for the column mapping)

## Outputs

The CSVs in this folder (`sheet.csv`, `apify_results.json`, etc.) are working files. The authoritative dataset is the Google Sheet.
