# Stage 02 — Data Enrichment

## Status: 🟡 In progress

Three passes complete. One major pass (pricing outreach) pending.

## What's done

**Pass A — Apify Google Maps (124/124)**
Filled: `area, latitude, longitude, phone, rating, review_count, wheelchair, visiting_hours, parking, hero_image, photos`.

**Pass B — WebFetch website extraction (37/56 sites usable)**
Filled where evidence found: `care_nursing, care_dementia, care_palliative, care_rehab, care_respite, care_assisted, rn_24_7, doctor_visits, medical_physio, languages, halal, shared_price, private_price, editorial_summary`.

**Pass C — Photo gallery scrape + privacy filter**
Up to 10 photos per facility, 547 kept after Claude vision classification removed images of identifiable elderly residents (139 removed). Streetview placeholders kept only as fallback.

## What's pending

**Pass D — Pricing & operational details (the moat)**
For ~113 facilities: monthly pricing, total beds, current availability, halal certification, RN ratios, dialysis/oxygen capability, JKM subsidy acceptance.

Outreach plan: Twilio voice + WhatsApp script. Phone numbers already in sheet. Use `phoneUnformatted`-style E.164 format. Record `last_updated` whenever a row is touched.

## Hard rules for this stage

- **Don't invent.** Empty cell beats fake data.
- If pricing can't be confirmed, leave `shared_price` etc. blank — `pricing_display` already has a fallback message.
- Update `last_updated` whenever a row is verified.
- Photos column always pipe-separated; first URL is the hero.

## Working files

`sheet.csv, sheet_merged.csv, sheet_final.csv, sheet_with_photos.csv, sheet_filtered_photos.csv` — historical merge stages
`apify_results.json, photos_results.json, firecrawl_results.json` — raw scrape outputs
`merge_*.py, filter_photos.py` — merge scripts (kept for re-runs)
`photo_classification.json` — vision classifier results, 664 photos labeled KEEP/REMOVE
