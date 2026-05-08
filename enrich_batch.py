"""
Batch enrichment: top-N facilities by review count.

For each facility:
  1. Apify website-content-crawler  → Markdown content from up to 6 pages
  2. Apify Google Places scraper    → reviews + Google CDN photos
  3. Claude API                     → new-format editorial + data gap fills + photo picks

Output:
  - Scraped content cached in  _enrich_cache/<slug>/
  - Pending editorials in      pending_editorials/<date>-enriched-batch.json
  - Photo updates logged in    _enrich_cache/photo_updates.json

Usage:
  export APIFY_TOKEN=apify_api_xxxxx
  export ANTHROPIC_API_KEY=sk-ant-xxxxx
  python enrich_batch.py             # top 30, dry run (no sheet push)
  python enrich_batch.py --n 10      # smaller batch
  python enrich_batch.py --resume    # skip slugs already in pending output
"""

import argparse, csv, io, json, os, sys, time
from datetime import date
from pathlib import Path

import anthropic
import urllib.request
from apify_client import ApifyClient
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# ─── Config ───────────────────────────────────────────────────────────────────

SPREADSHEET_ID = "1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk"
FAC_TAB        = "google-sheets-facilities.csv"
TOKEN_FILE     = "token_sheets.json"
SCOPES         = ["https://www.googleapis.com/auth/spreadsheets"]

CACHE_DIR      = Path("_enrich_cache")
PENDING_DIR    = Path("pending_editorials")
TODAY          = str(date.today())
OUTPUT_FILE    = PENDING_DIR / f"{TODAY}-enriched-batch.json"

APIFY_TOKEN     = os.environ.get("APIFY_TOKEN", "").strip()
ANTHROPIC_KEY   = os.environ.get("ANTHROPIC_API_KEY", "").strip()

ACTOR_WEBSITE   = "apify/website-content-crawler"
ACTOR_PLACES    = "compass/crawler-google-places"

SLEEP_BETWEEN   = 2   # seconds between Apify calls

# ─── Already done from manual sessions (skip these) ───────────────────────────
BLOCKERS_FILE = PENDING_DIR / "_blockers.json"

def load_blockers():
    if BLOCKERS_FILE.exists():
        return set(json.loads(BLOCKERS_FILE.read_text()).keys())
    return set()

# ─── Sheet helpers ────────────────────────────────────────────────────────────

def load_sheet():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    svc   = build("sheets", "v4", credentials=creds)
    data  = svc.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=f"'{FAC_TAB}'"
    ).execute().get("values", [])
    headers = data[0]
    def g(row, col):
        i = headers.index(col) if col in headers else None
        return (row[i] if i is not None and i < len(row) else "").strip()
    rows = []
    for row in data[1:]:
        rows.append({h: (row[i] if i < len(row) else "") for i, h in enumerate(headers)})
    return rows

def get_top_n(rows, n, blockers):
    """Return top-n live facilities with real websites, sorted by review count desc."""
    candidates = []
    for row in rows:
        slug    = row.get("slug", "").strip()
        status  = row.get("status", "").strip()
        website = row.get("website", "").strip()
        if not slug or status in ("unverified", "removed"):
            continue
        if not website or website.startswith("/facilities/") or website.startswith("/"):
            continue
        if "facebook.com" in website and "http" in website:
            # Facebook-only → limited content, deprioritise but don't skip
            pass
        if slug in blockers:
            continue
        try:
            review_count = int(row.get("review_count", 0) or 0)
        except ValueError:
            review_count = 0
        candidates.append({**row, "_review_count": review_count})
    candidates.sort(key=lambda x: -x["_review_count"])
    return candidates[:n]

# ─── Apify helpers ────────────────────────────────────────────────────────────

def apify_crawl_website(client, url, slug):
    """Crawl up to 6 pages of the facility website. Returns list of page dicts."""
    cache = CACHE_DIR / slug / "website.json"
    if cache.exists():
        print(f"    [cache] website content for {slug}")
        return json.loads(cache.read_text())

    print(f"    [apify] crawling website: {url}")
    try:
        run = client.actor(ACTOR_WEBSITE).call(run_input={
            "startUrls": [{"url": url}],
            "maxCrawlDepth": 2,
            "maxCrawlPages": 6,
            "outputFormats": ["markdown"],
            "htmlTransformer": "readableText",
            "removeCookieWarnings": True,
            "removeElementsCssSelector":
                "nav, footer, .cookie-banner, .nav, .menu, script, style",
        })
        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(items, ensure_ascii=False, indent=2))
        return items
    except Exception as e:
        print(f"    [warn] website crawl failed for {slug}: {e}")
        return []

def apify_scrape_maps(client, facility, slug):
    """Scrape Google Maps for reviews + photos. Returns dict or None."""
    cache = CACHE_DIR / slug / "maps.json"
    if cache.exists():
        print(f"    [cache] maps data for {slug}")
        return json.loads(cache.read_text())

    maps_url  = facility.get("google_maps_url", "").strip()
    title     = facility.get("title", "").strip()
    area      = facility.get("area", "").strip()
    latitude  = facility.get("latitude", "").strip()
    longitude = facility.get("longitude", "").strip()

    if not maps_url and not (latitude and longitude):
        print(f"    [skip] no Maps URL or coords for {slug}")
        return None

    print(f"    [apify] scraping Google Maps for {slug}")
    try:
        search_input = {}
        if maps_url:
            search_input["startUrls"] = [{"url": maps_url}]
        else:
            search_input["searchStringsArray"] = [f"{title} {area} nursing home Malaysia"]
            search_input["lat"]  = latitude
            search_input["lng"]  = longitude
            search_input["zoom"] = 14

        search_input.update({
            "maxCrawledPlacesPerSearch": 1,
            "language": "en",
            "countryCode": "my",
            "maxReviews": 50,
            "scrapePlaceDetailPage": True,
            "scrapeReviewsPersonalData": False,
        })

        run   = client.actor(ACTOR_PLACES).call(run_input=search_input)
        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
        result = items[0] if items else None
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(result, ensure_ascii=False, indent=2))
        return result
    except Exception as e:
        print(f"    [warn] Maps scrape failed for {slug}: {e}")
        return None

# ─── Photo helpers ────────────────────────────────────────────────────────────

def extract_photos_from_website(website_pages):
    """Pull image URLs from Markdown and metadata returned by website-content-crawler."""
    import re
    photos = []
    for page in website_pages:
        # og:image from metadata
        meta = page.get("metadata", {}) or {}
        og = meta.get("ogImage") or meta.get("og:image") or ""
        if og and og.startswith("http") and og not in photos:
            photos.append(og)

        # Images embedded in Markdown: ![alt](url)
        md = page.get("markdown", "") or ""
        for m in re.finditer(r'!\[.*?\]\((https?://[^)]+)\)', md):
            u = m.group(1)
            # Skip tiny icons, tracking pixels, logos
            if any(x in u.lower() for x in ["icon", "logo", "pixel", "tracking", "1x1", "badge", "avatar"]):
                continue
            if u not in photos:
                photos.append(u)

    return photos[:12]  # cap at 12

def extract_photos_from_maps(maps_data):
    """Pull photo URLs from Google Maps result."""
    if not maps_data:
        return []
    photos = []
    for p in (maps_data.get("photos") or []):
        url = p.get("imageUrl") or p.get("url") or ""
        if url and url not in photos:
            photos.append(url)
    # Also top-level imageUrl
    hero = maps_data.get("imageUrl") or ""
    if hero and hero not in photos:
        photos.insert(0, hero)
    return photos[:10]

def merge_photos(existing_pipe, website_photos, maps_photos, max_total=10):
    """
    Merge existing + new photos. Prepend operator website photos (higher quality),
    followed by Maps photos, then existing. Deduplicate. Cap at max_total.
    """
    existing = [p.strip() for p in existing_pipe.split("|") if p.strip()] if existing_pipe else []
    seen = set(existing)
    merged = existing[:]

    # Prepend website photos (operator-owned, higher quality)
    new_website = [p for p in website_photos if p not in seen]
    new_maps    = [p for p in maps_photos    if p not in seen and p not in set(new_website)]

    combined = new_website + new_maps + merged
    # Deduplicate preserving order
    seen2, result = set(), []
    for p in combined:
        if p not in seen2:
            seen2.add(p)
            result.append(p)

    return result[:max_total]

# ─── Claude editorial generation ──────────────────────────────────────────────

EDITORIAL_SYSTEM = """You are a medical social worker and senior care researcher writing facility profiles for NursingHomeGuide.my.

You write in a clean, structured, family-facing style. Your job is to extract verified facts from scraped content and produce two outputs:
1. A structured editorial in the exact format specified
2. A JSON block of data gaps and field updates found

EDITORIAL FORMAT (use exactly this structure):

**What it is**
[1-2 sentences: facility type, location, who runs it, primary care focus. Mention founding year or group size if confirmed.]

**Care services**
- [verified service 1]
- [verified service 2]
(3-7 bullets, verified only)

**Staffing & support**
- [e.g. Registered nurses on-site 24/7]
- [Language support: English, Malay, Mandarin]
- [Caregiver ratio if known]
(2-5 bullets, verified only — omit section if nothing confirmed)

**Capacity & pricing**
- [Bed count, e.g. "45 beds (mixed occupancy)"] OR omit if unknown
- [e.g. RM 2,500–3,500/month (shared to private)] OR "Pricing not published on operator website — request a written quote during your visit"
- [Pricing source note if published]
(2-4 bullets)

**License & verification**
- **JKM status:** [registered / unverified / no registration required]
- **JKM verified via:** [JKM call / cert photo / operator claim / unverified]
- **JKM expires:** [date if found / unknown]
- **MOH status:** [licensed / unverified / not applicable]
(Note: only mark registered/licensed if the website explicitly states it — otherwise unverified)

**Special programs** (include ONLY if confirmed)
- [e.g. Respite care: flexible 2-week to 3-month stays]
- [e.g. Post-stroke rehab: structured program with physio]

**What to ask on visit**
- [3-5 practical questions for unverified items or care-specific needs]

STRICT RULES:
- Never invent data. Only state what is confirmed from the scraped content.
- Never mention absence of data as a negative ("does not appear in...", "no mention of...").
- Frame unverified items as questions to ask, not red flags.
- No generic phrases: "warm and caring", "dedicated team", "holistic approach".
- Omit any section where nothing is verified (except What it is, Pricing, License, What to ask).
- Total length: 200-300 words.

After the editorial, output a JSON block (fenced with ```json) with:
{
  "care_types": "...",        // e.g. "Nursing Home + Dementia + Palliative" — only if found, else null
  "total_beds": "...",        // number as string — only if confirmed, else null
  "pricing_display": "...",   // e.g. "From RM 2,500/mo (shared)" — only if found, else null
  "shared_price": null,       // numeric RM or null
  "private_price": null,      // numeric RM or null
  "jkm_status": "...",        // registered / unverified / no_register
  "jkm_licence_number": "...", // if explicitly found on site
  "jkm_verified_by": "...",   // operator_claim if site mentions JKM; else unverified
  "moh_status": "...",        // licensed / unverified / not_applicable
  "doctor_visits": "...",     // e.g. "weekly" / "monthly" / "on_call" / null
  "rn_24_7": "...",           // "yes" / "no" / null
  "languages": "...",         // comma-separated, e.g. "English, Malay, Mandarin"
  "new_photos": ["url1", "url2"],  // operator website photos found (not Google Maps)
  "data_quality": "high/medium/low",  // high=many verified facts, low=little found
  "confidence_note": "..."    // 1-sentence note on data quality/gaps
}
"""

def generate_editorial(client_ai, facility, website_pages, maps_data, website_photos):
    """Call Claude to generate new-format editorial + gap fills."""

    # Build context string
    existing = {k: v for k, v in facility.items() if v and not k.startswith("_")}
    context_parts = [
        f"FACILITY: {facility.get('title')} ({facility.get('area')}, {facility.get('state')})",
        f"Website: {facility.get('website')}",
        f"Current care_types: {facility.get('care_types', 'unknown')}",
        f"Current rating: {facility.get('rating')} ({facility.get('review_count')} reviews)",
        f"Current pricing_display: {facility.get('pricing_display', 'unknown')}",
        f"Current editorial (OLD PARAGRAPH STYLE TO REPLACE): {facility.get('editorial_summary', '')[:500]}",
    ]

    # Add scraped website content (truncated to 8000 chars total)
    website_text = ""
    for page in website_pages[:6]:
        md = (page.get("markdown") or page.get("text") or "")[:1500]
        url = page.get("url", "")
        website_text += f"\n\n--- Page: {url} ---\n{md}"
    if website_text:
        context_parts.append(f"\nSCRAPED WEBSITE CONTENT:{website_text[:8000]}")

    # Add Maps reviews summary
    if maps_data:
        reviews = maps_data.get("reviews") or []
        review_text = "\n".join(
            f"- {r.get('stars', '?')}★: {(r.get('text') or '')[:200]}"
            for r in reviews[:15]
        )
        context_parts.append(
            f"\nGOOGLE MAPS DATA:\n"
            f"Rating: {maps_data.get('totalScore', '?')} ({maps_data.get('reviewsCount', 0)} reviews)\n"
            f"Address: {maps_data.get('address', '')}\n"
            f"Recent reviews:\n{review_text}"
        )

    # Add photo URLs found
    if website_photos:
        context_parts.append(
            f"\nOPERATOR WEBSITE PHOTOS FOUND:\n" + "\n".join(website_photos[:8])
        )

    prompt = "\n\n".join(context_parts)
    prompt += "\n\nWrite the editorial in the exact structured format, then the JSON block."

    msg = client_ai.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=EDITORIAL_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text

def parse_editorial_response(response_text):
    """Split response into editorial text and structured JSON."""
    import re
    # Extract JSON block
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
    json_data = {}
    if json_match:
        try:
            json_data = json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # Editorial is everything before the ```json block
    editorial = response_text
    if json_match:
        editorial = response_text[:json_match.start()].strip()

    return editorial, json_data

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n",      type=int, default=30, help="Number of facilities to process")
    ap.add_argument("--resume", action="store_true",  help="Skip slugs already in output file")
    ap.add_argument("--dry-run", action="store_true", help="Scrape + generate but don't save to pending_editorials")
    args = ap.parse_args()

    if not APIFY_TOKEN:
        sys.exit("❌ APIFY_TOKEN env var not set. Run: export APIFY_TOKEN=apify_api_xxxxx")
    if not ANTHROPIC_KEY:
        sys.exit("❌ ANTHROPIC_API_KEY env var not set.")
    if not Path(TOKEN_FILE).exists():
        sys.exit(f"❌ {TOKEN_FILE} not found. Run from the repo root.")

    apify_client = ApifyClient(APIFY_TOKEN)
    claude_client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

    # Load existing output for resume
    already_done = set()
    if args.resume and OUTPUT_FILE.exists():
        existing = json.loads(OUTPUT_FILE.read_text())
        already_done = {f["slug"] for f in existing.get("facilities", [])}
        print(f"Resuming — {len(already_done)} slugs already in output file")

    blockers = load_blockers()
    print(f"Loading sheet...")
    rows = load_sheet()
    facilities = get_top_n(rows, args.n + len(already_done), blockers)

    # Filter to those not already in output
    facilities = [f for f in facilities if f["slug"] not in already_done][:args.n]

    print(f"\nProcessing {len(facilities)} facilities (top {args.n} by review count)\n")

    results = []
    photo_updates = []

    for i, facility in enumerate(facilities, 1):
        slug    = facility["slug"]
        title   = facility.get("title", slug)
        website = facility.get("website", "").strip()

        print(f"\n[{i}/{len(facilities)}] {title}")
        print(f"  Slug:    {slug}")
        print(f"  Website: {website}")
        print(f"  Reviews: {facility.get('review_count', 0)} @ {facility.get('rating', '?')}★")

        # Step 1: Scrape website
        website_pages = []
        if website:
            website_pages = apify_crawl_website(apify_client, website, slug)
            time.sleep(SLEEP_BETWEEN)

        # Step 2: Scrape Google Maps
        maps_data = apify_scrape_maps(apify_client, facility, slug)
        if maps_data:
            time.sleep(SLEEP_BETWEEN)

        # Step 3: Extract photos
        website_photos = extract_photos_from_website(website_pages)
        maps_photos    = extract_photos_from_maps(maps_data)

        existing_photos = facility.get("photos", "").strip()
        existing_hero   = facility.get("hero_image", "").strip()
        merged_photos   = merge_photos(existing_photos, website_photos, maps_photos)

        print(f"  Photos:  {len(website_photos)} from website, {len(maps_photos)} from Maps → {len(merged_photos)} merged")

        # Step 4: Generate editorial via Claude
        print(f"  [claude] generating editorial...")
        try:
            response = generate_editorial(
                claude_client, facility, website_pages, maps_data, website_photos
            )
            editorial, json_data = parse_editorial_response(response)
        except Exception as e:
            print(f"  [error] Claude API failed for {slug}: {e}")
            continue

        # Step 5: Build result record
        new_hero = merged_photos[0] if merged_photos and not existing_hero else existing_hero
        new_photos_pipe = "|".join(merged_photos)

        result = {
            "slug": slug,
            "title": title,
            "editorial_summary": editorial,
            # Data gap fills from Claude
            "care_types":         json_data.get("care_types") or facility.get("care_types"),
            "total_beds":         json_data.get("total_beds") or facility.get("total_beds"),
            "pricing_display":    json_data.get("pricing_display") or facility.get("pricing_display"),
            "shared_price":       json_data.get("shared_price") or facility.get("shared_price"),
            "private_price":      json_data.get("private_price") or facility.get("private_price"),
            "jkm_status":         json_data.get("jkm_status", "unverified"),
            "jkm_licence_number": json_data.get("jkm_licence_number", ""),
            "jkm_verified_by":    json_data.get("jkm_verified_by", "unverified"),
            "moh_status":         json_data.get("moh_status", "unverified"),
            "doctor_visits":      json_data.get("doctor_visits") or facility.get("doctor_visits"),
            "rn_24_7":            json_data.get("rn_24_7") or facility.get("rn_24_7"),
            "languages":          json_data.get("languages") or facility.get("languages"),
            "hero_image":         new_hero,
            "photos":             new_photos_pipe,
            "photo_count":        str(len(merged_photos)),
            "last_updated":       TODAY,
            "data_quality":       json_data.get("data_quality", "?"),
            "confidence_note":    json_data.get("confidence_note", ""),
        }

        results.append(result)

        # Track photo updates separately for review
        if website_photos:
            photo_updates.append({
                "slug": slug,
                "title": title,
                "website_photos_found": website_photos,
                "maps_photos_found": maps_photos[:5],
                "merged_total": len(merged_photos),
                "new_hero": new_hero,
            })

        print(f"  ✓ Editorial generated ({json_data.get('data_quality','?')} quality)")
        print(f"    {json_data.get('confidence_note','')}")

    # ─── Save outputs ─────────────────────────────────────────────────────────

    if args.dry_run:
        print(f"\n[dry-run] Would save {len(results)} records to {OUTPUT_FILE}")
        for r in results:
            print(f"  {r['slug']} — quality:{r['data_quality']}")
            print(r["editorial_summary"][:300])
            print("---")
        return

    PENDING_DIR.mkdir(exist_ok=True)

    # Merge with existing output if resuming
    if args.resume and OUTPUT_FILE.exists():
        existing_data = json.loads(OUTPUT_FILE.read_text())
        existing_facilities = existing_data.get("facilities", [])
    else:
        existing_facilities = []

    all_facilities = existing_facilities + results
    OUTPUT_FILE.write_text(json.dumps({
        "batch_date": TODAY,
        "total": len(all_facilities),
        "facilities": all_facilities
    }, ensure_ascii=False, indent=2))

    # Save photo updates log
    photo_log = CACHE_DIR / "photo_updates.json"
    CACHE_DIR.mkdir(exist_ok=True)
    photo_log.write_text(json.dumps(photo_updates, ensure_ascii=False, indent=2))

    print(f"\n{'='*60}")
    print(f"✅ Batch complete: {len(results)} facilities processed")
    print(f"   Output:        {OUTPUT_FILE}")
    print(f"   Photo log:     {photo_log}")
    print(f"\nNext steps:")
    print(f"  1. Review {OUTPUT_FILE}")
    print(f"  2. python upload_pending_editorials.py --apply")
    print(f"  3. git add pending_editorials && git commit -m 'Enrich batch {TODAY}'")

if __name__ == "__main__":
    main()
