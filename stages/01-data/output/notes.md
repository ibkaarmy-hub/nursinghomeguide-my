# Stage 01 — Data Collection Notes

## Data Sources Identified

| Source | Type | Access | Quality |
|--------|------|--------|---------|
| wargaemas.jkm.gov.my | Official JKM licensed list | Searchable by state/district — no bulk download | ✅ Authoritative |
| malaysia.gov.my/elderly-care-institutions | Govt portal page | Links to JKM — not a direct list | ℹ️ Reference only |
| ielder.asia/blogs/directory/list-of-nursing-home-in-malaysia | Compiled list | Web scrape | ✅ Good coverage |
| chewmeiling.com/nursing-home-in-malaysia | Blog list | Web scrape | ⚠️ Partial |
| Google Maps / Outscraper | Crowdsourced | Paid export ($) | ✅ Good for gaps + photos |
| SmartScraper / Rentechdigital | Pre-scraped dataset | $299 CSV | ✅ Full dataset, fastest |

## Key Facts
- 494 nursing homes total in Malaysia (as of Jan 2025)
- Penang has the most: 110 facilities (22% of total)
- Top states: Selangor, KL, Penang, Johor, Perak
- JKM portal: search at wargaemas.jkm.gov.my → Perkhidmatan → Warga Emas → enter Negeri + Daerah

## Collection Plan

### Step 1 — JKM Portal (Chrome scrape, state by state)
Use Claude in Chrome to visit wargaemas.jkm.gov.my and extract listings for each state:
1. Selangor
2. Kuala Lumpur
3. Penang
4. Johor
5. Perak
6. Negeri Sembilan
7. Melaka
8. Pahang
9. Kelantan
10. Terengganu
11. Sabah
12. Sarawak
13. Kedah
14. Perlis

### Step 2 — iElder.Asia supplement
Scrape ielder.asia compiled list for any facilities missed by JKM portal.

### Step 3 — Deduplication + cleaning
Merge both sources, remove duplicates, flag closed facilities.

## Status
- [ ] JKM state-by-state extraction
- [ ] iElder.Asia supplement
- [ ] Deduplication
- [ ] Output clean CSV
