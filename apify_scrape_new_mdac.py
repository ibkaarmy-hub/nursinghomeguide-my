"""
apify_scrape_new_mdac.py
Start an Apify Google Maps scrape for the 82 newly added MDAC facilities.
Uses compass/crawler-google-places with 1 result per search (exact match mode).

Input:  mdac_confirmed_new.csv (has addresses for precise search queries)
        mdac_added_slugs.json  (slug lookup)
Output: run_new_mdac.json      (Apify run metadata, for polling)
        apify_new_mdac_input.json (the input sent to Apify, for reference)
"""

import csv, json, re, urllib.request, urllib.parse

APIFY_TOKEN = 'YOUR_APIFY_TOKEN'
ACTOR       = 'compass~crawler-google-places'
API_BASE    = f'https://api.apify.com/v2/acts/{ACTOR}/runs?token={APIFY_TOKEN}'

# ── Build search queries ───────────────────────────────────────────────────────

mdac_rows = list(csv.DictReader(open('mdac_confirmed_new.csv', encoding='utf-8')))
slug_data  = json.load(open('mdac_added_slugs.json', encoding='utf-8'))
slug_index = {d['title']: d for d in slug_data}

# Deduplicate (same as add script)
seen = set()
unique_rows = []
for r in mdac_rows:
    key = (r['name'].strip(), r['phone'].strip())
    if key not in seen:
        seen.add(key)
        unique_rows.append(r)

def clean_name(raw):
    return re.sub(r'\s*-\s*MYS\s*$', '', raw.strip()).strip()

def make_query(row):
    name  = clean_name(row['name'])
    addr  = row['address'].strip()
    state = row['state_detected']
    # Use address if it has a Taman/Jalan component (more specific)
    if re.search(r'(jalan|taman|lorong|persiaran|lebuh)', addr, re.I):
        return f"{name}, {addr}, Malaysia"
    # Fall back to name + state
    city_map = {'Johor': 'Johor Bahru', 'Selangor': 'Selangor', 'KL/Selangor': 'Kuala Lumpur'}
    city = city_map.get(state, 'Malaysia')
    return f"{name}, {city}, Malaysia"

searches = []
for row in unique_rows:
    q = make_query(row)
    searches.append(q)

print(f"Search queries: {len(searches)}")
for q in searches[:10]:
    print(f"  {q}")
print("  ...")

# ── Apify actor input ──────────────────────────────────────────────────────────

actor_input = {
    "searchStringsArray": searches,
    "language": "en",
    "maxCrawledPlacesPerSearch": 3,   # top 3 results; we pick the best match
    "maxImages": 15,
    "scrapeContacts": False,
    "includeHistogram": False,
    "includeOpeningHours": True,
    "includePeopleAlsoSearch": False,
    "additionalInfo": False,
    "exportPlaceUrls": False,
}

with open('apify_new_mdac_input.json', 'w') as f:
    json.dump(actor_input, f, indent=2)
print(f"\nInput saved to apify_new_mdac_input.json")

# ── Start run ─────────────────────────────────────────────────────────────────

body = json.dumps(actor_input).encode('utf-8')
req  = urllib.request.Request(
    API_BASE,
    data=body,
    headers={'Content-Type': 'application/json'},
    method='POST'
)

with urllib.request.urlopen(req) as resp:
    result = json.loads(resp.read())

run_id     = result['data']['id']
dataset_id = result['data']['defaultDatasetId']
status     = result['data']['status']

print(f"\nApify run started!")
print(f"  Run ID:     {run_id}")
print(f"  Dataset ID: {dataset_id}")
print(f"  Status:     {status}")
print(f"  Monitor:    https://console.apify.com/actors/runs/{run_id}")

with open('run_new_mdac.json', 'w') as f:
    json.dump({
        'run_id': run_id,
        'dataset_id': dataset_id,
        'status': status,
        'n_queries': len(searches),
    }, f, indent=2)
print(f"\nRun metadata saved to run_new_mdac.json")
print("Next: run process_new_mdac_results.py once the run completes (~10-20 min)")
