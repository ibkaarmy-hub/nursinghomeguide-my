# JKM Elderly Care Centre Scraper — Deployment Guide

## Step 1: Deploy to Apify

1. Create a new Actor in Apify Console: https://console.apify.com/actors
2. Name it: `jkm-elderly-care-scraper`
3. Paste the code from `apify-jkm-scraper.js` into the code editor
4. **Important:** In Actor Settings → Compute → Proxy configuration:
   - Select **"Use Apify Proxy"**
   - Enable **"Residential"**
   - Set country to **"Malaysia (MY)"**

## Step 2: Test & Refine Selectors

Before running the full 529-centre scrape, we need to verify the CSS selectors match the actual JKM page HTML.

1. Run the actor on **1 page only** (manually set `maxPages: 1` in code)
2. Check the results dataset
3. If rows are empty, I'll need you to:
   - Inspect the JKM page (F12 → Elements)
   - Find the table selector (e.g., `#results_table`, `.centre-list`)
   - Count the `<td>` columns to verify field order
   - Report back with actual selectors

## Step 3: Run Full Scrape

Once selectors are verified:

```bash
# Via Apify CLI (if installed)
apify run

# OR via API
curl -X POST https://api.apify.com/v2/actor-tasks \
  -H "Authorization: Bearer YOUR_APIFY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "actorId": "YOUR_ACTOR_ID",
    "build": "latest"
  }'
```

Results will be saved to the `JKM_CENTRES` dataset in Apify.

## Step 4: Download & Process Results

1. Go to your Actor's Runs → latest run → Results dataset
2. Export as JSON
3. Run the post-processor (see next section)

---

## Post-Processing: Map to Your Sheet Schema

Once you have the raw JKM data, use `process-jkm-results.js` to:
- Map JKM fields to your 56-column sheet schema
- Identify duplicates (address matching against existing 406 rows)
- Generate a comparison report

Run:
```bash
node process-jkm-results.js <jkm_raw_results.json>
```

Output:
- `jkm_mapped_to_sheet.csv` — ready to append to Google Sheet
- `jkm_duplicates_report.json` — potential matches with existing facilities
- `jkm_new_facilities.json` — 100% new centres (low address match confidence)

---

## Field Mapping

| JKM Field | Your Sheet Column |
|-----------|------------------|
| name | title |
| address | [parse address] |
| phone | phone |
| email | [new? or contact field] |
| fax | [store in Details?] |
| licence_number | licence_number |
| validity_date | [new? for admin use] |
| gps | latitude, longitude |
| ownership | ownership_type |

---

## Next Steps

1. Deploy actor to Apify ✓
2. Test on 1 page (verify selectors)
3. Run full scrape (53 pages, ~2–5 hours with residential proxy)
4. Post-process + deduplicate
5. Append new centres to sheet (via Google Sheets API or manual)
6. Regenerate static pages (`generate_facility_pages.py`)

Ready?
