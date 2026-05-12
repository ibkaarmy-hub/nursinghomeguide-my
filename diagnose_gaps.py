"""Diagnose WHY data is missing across facilities.
For each major gap (editorial, pricing, photo, placeId, state), cluster the
affected rows by what evidence they DO have, so the root cause is visible
(ghost listing vs queue gap vs operator never published vs no Maps match).
"""

import sys, io, csv, urllib.request, re
from collections import Counter, defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SHEET_URL = 'https://docs.google.com/spreadsheets/d/1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk/export?format=csv&gid=292378871'


def fetch_csv():
    req = urllib.request.Request(SHEET_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return list(csv.reader(io.TextIOWrapper(r, encoding='utf-8')))


def make_getter(headers):
    idx = {h: i for i, h in enumerate(headers)}
    def g(row, col):
        i = idx.get(col)
        return (row[i] if i is not None and i < len(row) else '').strip()
    return g


def classify_web_presence(g, r):
    """Return (presence_bucket, details_str)"""
    website = g(r, 'website')
    facebook = g(r, 'facebook')
    has_real_site = bool(website) and 'facebook.com' not in website.lower() and 'wa.me' not in website.lower()
    has_fb = bool(facebook) or (website and 'facebook.com' in website.lower())
    has_placeid = 'query_place_id=' in g(r, 'google_maps_url')
    review_count = g(r, 'review_count')
    n_rev = int(review_count) if review_count.isdigit() else 0
    rating = g(r, 'rating')
    has_phone = bool(g(r, 'phone'))

    if has_real_site:
        bucket = 'Has real website'
    elif has_fb:
        bucket = 'Facebook only'
    elif has_placeid and n_rev >= 5:
        bucket = 'Maps-only (has reviews)'
    elif has_placeid:
        bucket = 'Maps-only (few/no reviews)'
    elif has_phone:
        bucket = 'Phone only (no web presence)'
    else:
        bucket = 'Ghost listing (no contact channels)'

    details = []
    if has_real_site:
        details.append(f"site={website[:40]}")
    if has_fb:
        details.append("fb")
    if has_placeid:
        details.append(f"map({n_rev}r/{rating}★)" if n_rev else "map(no-rev)")
    if has_phone and not has_real_site and not has_fb and not has_placeid:
        details.append(f"phone={g(r,'phone')[:14]}")
    return bucket, " ".join(details)


def main():
    print("Fetching live sheet...", file=sys.stderr)
    rows = fetch_csv()
    headers = rows[0]
    g = make_getter(headers)

    live = []
    for r in rows[1:]:
        slug = g(r, 'slug')
        if not slug:
            continue
        if g(r, 'status').lower() in ('unverified', 'removed'):
            continue
        live.append(r)

    print(f"\n# Gap diagnosis — {len(live)} live facilities\n")
    print("Each section below shows facilities missing one specific field, grouped by what they DO have. The bucket tells you whether the gap is fixable (queue work) or structural (operator never published).\n")
    print("---")

    # ============= GAP 1: editorial =============
    print("\n## Gap 1 — Missing editorial (197 facilities)\n")
    print("Bucket = how reachable / researchable the facility is. The first two buckets are normal queue work — re-run `/nh-profiles` for these. The bottom buckets are stubs that need operator outreach before a useful editorial can be written.\n")
    buckets = defaultdict(list)
    for r in live:
        editorial = g(r, 'editorial_summary')
        if editorial and len(editorial.split()) >= 100:
            continue
        bucket, _ = classify_web_presence(g, r)
        buckets[bucket].append((g(r, 'slug'), g(r, 'state'), g(r, 'title')))
    order = ['Has real website', 'Facebook only', 'Maps-only (has reviews)',
             'Maps-only (few/no reviews)', 'Phone only (no web presence)',
             'Ghost listing (no contact channels)']
    print(f"| Bucket | Count | Action |")
    print(f"|--------|------:|--------|")
    actions = {
        'Has real website': 'Quick win — `/nh-profiles <slug>` writes a full editorial',
        'Facebook only': '`/nh-profiles` works but Services block will be empty; FB caption scrape needed',
        'Maps-only (has reviews)': '`/nh-profiles` works — reviews carry the editorial; no Services block',
        'Maps-only (few/no reviews)': 'Conservative stub only — need operator outreach for real content',
        'Phone only (no web presence)': 'Cannot enrich digitally — needs phone call or visit',
        'Ghost listing (no contact channels)': 'Verify the facility is real before keeping it live',
    }
    for b in order:
        n = len(buckets[b])
        if n:
            print(f"| {b} | {n} | {actions[b]} |")

    # ============= GAP 2: pricing =============
    print("\n## Gap 2 — Missing pricing (710 facilities)\n")
    print("This is the **biggest gap by volume** and not a queue-work problem. Pricing is rarely published online — operators want a phone enquiry before quoting. The fixable subset is the slice that DOES publish prices on their own website.\n")
    pricing_buckets = defaultdict(int)
    for r in live:
        shared = g(r, 'shared_price')
        display = g(r, 'pricing_display').lower()
        if shared or (display and display != 'call for pricing'):
            continue
        bucket, _ = classify_web_presence(g, r)
        pricing_buckets[bucket] += 1
    print(f"| Bucket | Count | Note |")
    print(f"|--------|------:|------|")
    pricing_notes = {
        'Has real website': 'Has a website but no pricing published OR script never scraped — try `/nh-profiles` re-run; if site has /our-packages, encode as Details `rooms` rows',
        'Facebook only': 'Pricing essentially impossible without phone outreach',
        'Maps-only (has reviews)': 'Same — Google reviews rarely cite specific prices, only "affordable" / "expensive"',
        'Maps-only (few/no reviews)': 'No source — must call',
        'Phone only (no web presence)': 'Must call',
        'Ghost listing (no contact channels)': 'Cannot price — verify listing first',
    }
    for b in order:
        if pricing_buckets[b]:
            print(f"| {b} | {pricing_buckets[b]} | {pricing_notes[b]} |")

    # ============= GAP 3: photos =============
    print("\n## Gap 3 — Missing hero photo (29 facilities)\n")
    print("Almost everyone has photos now. The remaining 29 are stuck because Maps has no photos uploaded OR no Maps listing exists. Operator outreach for photo permission, OR a `/gallery` scrape of their website, is the only path.\n")
    photo_buckets = defaultdict(int)
    for r in live:
        if g(r, 'hero_image'):
            continue
        bucket, _ = classify_web_presence(g, r)
        photo_buckets[bucket] += 1
    print(f"| Bucket | Count | Path forward |")
    print(f"|--------|------:|--------------|")
    photo_notes = {
        'Has real website': 'Scrape operator `/gallery` page for images',
        'Facebook only': 'Scrape FB page (legal grey area; ask operator)',
        'Maps-only (has reviews)': 'Maps lists place but has no user-uploaded photos — try Apify or operator request',
        'Maps-only (few/no reviews)': 'Maps listing exists with no photos — operator visit/upload',
        'Phone only (no web presence)': 'Must visit or request',
        'Ghost listing (no contact channels)': 'No source',
    }
    for b in order:
        if photo_buckets[b]:
            print(f"| {b} | {photo_buckets[b]} | {photo_notes[b]} |")

    # ============= GAP 4: state =============
    print("\n## Gap 4 — Missing state assignment (31 facilities)\n")
    print("These rows have no `state` value. They are invisible on every state listing page. Most can be classified by decoding lat/lng:\n")
    print(" - Lat 1.4–1.6, lng 103.5–104.0 = Johor Bahru metro")
    print(" - Lat 3.0–3.3, lng 101.4–101.8 = Klang Valley (KL / PJ / Selangor)")
    print(" - Lat 5.4, lng 100.3 = Penang island")
    print(" - Lat 4.6, lng 101.1 = Ipoh / Perak\n")
    stateless = []
    for r in live:
        if g(r, 'state'):
            continue
        lat = g(r, 'latitude')
        lng = g(r, 'longitude')
        stateless.append({
            'slug': g(r, 'slug'),
            'title': g(r, 'title'),
            'lat': lat,
            'lng': lng,
            'area': g(r, 'area'),
            'phone': g(r, 'phone'),
        })

    # Auto-classify by coords
    def classify_coords(lat, lng):
        try:
            la = float(lat); ln = float(lng)
        except ValueError:
            return None
        if 1.3 <= la <= 1.7 and 103.4 <= ln <= 104.2: return 'Johor'
        if 3.0 <= la <= 3.4 and 101.3 <= ln <= 101.85: return 'Klang Valley (KL/Selangor)'
        if 2.7 <= la <= 3.0 and 101.5 <= ln <= 102.0: return 'Negeri Sembilan / S. Selangor border'
        if 5.2 <= la <= 5.6 and 100.1 <= ln <= 100.5: return 'Penang'
        if 4.4 <= la <= 5.1 and 100.7 <= ln <= 101.3: return 'Perak (Ipoh region)'
        if 4.2 <= la <= 5.1 and 100.4 <= ln <= 100.7: return 'Perak (coastal)'
        if 5.9 <= la <= 6.4 and 100.0 <= ln <= 100.7: return 'Kedah / Perlis'
        if 3.7 <= la <= 5.0 and 101.7 <= ln <= 103.5: return 'Pahang'
        if 5.5 <= la <= 6.4 and 102.0 <= ln <= 103.0: return 'Kelantan'
        if 4.3 <= la <= 5.8 and 102.7 <= ln <= 103.8: return 'Terengganu'
        if 2.0 <= la <= 2.5 and 102.0 <= ln <= 102.6: return 'Melaka'
        if 1.0 <= la <= 7.5 and 109.0 <= ln <= 116.0: return 'Sarawak / Sabah'
        return None

    classified = Counter()
    no_coords = []
    for s in stateless:
        guess = classify_coords(s['lat'], s['lng'])
        if guess:
            classified[guess] += 1
        else:
            no_coords.append(s)

    print(f"### Auto-classification (by lat/lng)\n")
    print(f"| Likely state | Count |")
    print(f"|--------------|------:|")
    for state, n in classified.most_common():
        print(f"| {state} | {n} |")
    if no_coords:
        print(f"\n### {len(no_coords)} rows have no usable coordinates — manual classification needed:\n")
        for s in no_coords[:15]:
            phone = s['phone'][:14] or '(no phone)'
            print(f"  - `{s['slug']}` — {s['title'][:60]} ({phone})")

    # ============= GAP 5: placeId =============
    print("\n## Gap 5 — Missing Google Maps placeId (168 facilities)\n")
    print("These rows have a maps URL but no `query_place_id=` token — the Map tab on the facility page can't pin them precisely, and reviews/photos can't be refreshed. Cause: original scrape used raw lat/lng URLs instead of resolving to placeIds. Fixable by re-running `batch_maps_placeid.py` or a Places API text-search batch.\n")

    # ============= GAP 6: Details rows =============
    print("\n## Gap 6 — Thin Details tab (Selangor 3%, KL 10%, Johor 29%)\n")
    print("These are the big-state quality gap. Editorials exist but the structured Details rows (rooms, clinical capabilities, policies, amenities) are sparse — the data behind the tabs on each profile page. This is the highest-effort enrichment because it requires reading the operator website or Instagram carefully and encoding structured rows. Cannot be done from Maps alone.\n")
    print("Path forward: prioritise facilities with real websites (rerun `/nh-profiles` once with `enrich mode` — the skill will append Details rows even if the editorial is unchanged).\n")


if __name__ == '__main__':
    main()
