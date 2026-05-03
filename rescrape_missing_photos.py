#!/usr/bin/env python3
"""Rescrape Google Places photos + metadata for facilities with no hero_image.

Targets the ~86 live facilities (mostly KL/Selangor MDAC import batch) that
came in without photos because mdac.my is text-only. Pulls them from Google
Places via Apify's `compass/crawler-google-places` actor.

## What this script fills

From Google Places (this script):
  - photos (pipe-separated URLs, up to N per facility)
  - hero_image (first photo)
  - photo_count
  - rating, review_count (cross-check / refresh)
  - phone (cross-check)
  - website (cross-check)
  - google_maps_url (refresh)

## What this script does NOT fill — use /nh-profiles skill for these

The Apify Places actor doesn't know:
  - care_types, care_nursing/dementia/palliative/etc.
  - total_beds, room types, pricing
  - religion, languages, halal status
  - JKM licence_number
  - editorial_summary

After this rescrape lands photos, run the `/nh-profiles` skill (defined in
`.claude/commands/nh-profiles.md`) on the same slugs to fill those deeper
fields from operator websites + Google reviews. The skill expects each
facility to have a website — many MDAC-imported facilities don't, so flag
those for outreach instead of running /nh-profiles.

## Two modes

### Mode A — direct Apify API (if APIFY_TOKEN env var is set)

    export APIFY_TOKEN=apify_api_xxxxx
    python rescrape_missing_photos.py

Calls the actor synchronously, slug by slug. Slow (~30 s per facility) but
no manual steps. Caches results in `.rescrape_cache/` so reruns skip done
slugs.

### Mode B — manual: run Apify in browser, then ingest

If APIFY_TOKEN is not set, the script writes `rescrape_queries.txt` (one
search query per line, e.g. `Loving Mansion Care Centre Johor Bahru
Malaysia`). Paste those into the Apify console for actor
`compass/crawler-google-places`, run it, download the resulting dataset JSON
to `rescrape_input.json`, then re-run:

    python rescrape_missing_photos.py --from-json rescrape_input.json

Either mode produces the same output: `rescrape_results.csv`.

## Output: rescrape_results.csv

Columns:
  slug, current_title, current_area, current_state,
  matched_title, matched_address, match_confidence,
  photos, hero_image, photo_count,
  rating_new, review_count_new, phone_new, website_new, google_maps_url_new,
  notes

Don't auto-write to the sheet. Review the CSV, run the photos through
`photo-manager.html` to drop any that contain residents' faces, then
bulk-paste the cleaned data into the sheet.

## Privacy: photo curation is mandatory before publishing

Google Places photos can include residents' faces. Always run new photos
through `photo-manager.html` and remove any that show identifiable people
before pasting into the sheet. This is the same flow used for the original
267 facilities — the privacy filter is non-negotiable.
"""

import argparse
import csv
import io
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

FACILITIES_CSV = (
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ4_BgHIjnlgmITzjyUuGDpgpNzPL7MfjOY2069i0PtbVbXSxIAJk1tmBejwNo8aBBeLuRi62szF2sh/pub"
    "?gid=292378871&single=true&output=csv"
)
APIFY_PLACES_ACTOR = "compass~crawler-google-places"  # Primary
APIFY_RAG_ACTOR = "apify~rag-web-browser"  # Fallback when Places times out
APIFY_RUN_SYNC = (
    "https://api.apify.com/v2/acts/{actor}/run-sync-get-dataset-items"
    "?token={token}&memory=2048&timeout=180"
)

CACHE_DIR = Path(".rescrape_cache")
QUERIES_PATH = Path("rescrape_queries.txt")
OUTPUT_CSV = Path("rescrape_results.csv")
MAX_PHOTOS_PER_FACILITY = 5
SLEEP_BETWEEN_CALLS = 1  # seconds — be polite to Apify


# ─── Helpers ──────────────────────────────────────────────────────────────────


def fetch_csv(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read().decode("utf-8", errors="replace")
    return list(csv.DictReader(io.StringIO(body)))


def get_missing_photo_facilities():
    """Return list of dicts for live facilities with no hero_image AND no photos."""
    rows = fetch_csv(FACILITIES_CSV)
    live = [
        r for r in rows
        if r.get("title") and r.get("status", "").strip() not in ("unverified", "removed")
    ]
    missing = [
        r for r in live
        if not (r.get("hero_image", "") or "").strip()
        and not (r.get("photos", "") or "").strip()
    ]
    return missing


def build_search_query(f):
    """Build a Google Places search query from facility row."""
    title = (f.get("title", "") or "").strip()
    area = (f.get("area", "") or "").strip()
    state = (f.get("state", "") or "").strip()
    bits = [title]
    if area and area.lower() != state.lower():
        bits.append(area)
    if state:
        bits.append(state)
    bits.append("Malaysia")
    # Strip duplicate whitespace
    return re.sub(r"\s+", " ", " ".join(bits)).strip()


def upgrade_lh3_resolution(url):
    """Replace e.g. =w408-h272 with =w1920-h1080-k-no on lh3 photo URLs."""
    if "lh3.googleusercontent.com" not in url:
        return url
    return re.sub(r"=w\d+-h\d+(-[a-z\-]+)?$", "=w1920-h1080-k-no", url)


def normalize_token(s):
    """Lowercase + strip non-alphanumerics for fuzzy title compare."""
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def title_similarity(a, b):
    """Crude token-overlap similarity between 0 and 1."""
    ta = set(re.findall(r"[a-z0-9]+", (a or "").lower()))
    tb = set(re.findall(r"[a-z0-9]+", (b or "").lower()))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / max(len(ta | tb), 1)


# ─── Apify direct API mode ────────────────────────────────────────────────────


def call_apify_places(token, query, max_results=3):
    """Call compass/crawler-google-places synchronously. Returns dataset items list."""
    payload = {
        "searchStringsArray": [query],
        "maxCrawledPlacesPerSearch": max_results,
        "language": "en",
        "countryCode": "my",
        "scrapePlaceDetailPage": False,
        "scrapeImageAuthors": False,
        "includeWebResults": False,
        "maxImages": MAX_PHOTOS_PER_FACILITY,
    }
    url = APIFY_RUN_SYNC.format(actor=APIFY_PLACES_ACTOR, token=token)
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=240) as r:
        return json.loads(r.read().decode("utf-8"))


def call_apify_rag(token, query):
    """Fallback: apify/rag-web-browser does generic web search + scrape.

    Returns list of search results, each typically containing:
      { searchResult: {url, title, description},
        metadata: {url, title, description, ogImage, ...},
        markdown: "...page text..." }

    We extract: og:image, image URLs from markdown, and the operator website URL.
    """
    payload = {
        "query": query + " nursing home",
        "maxResults": 3,
        "scrapingTool": "raw-http",
        "outputFormats": ["markdown"],
        "requestTimeoutSecs": 60,
    }
    url = APIFY_RUN_SYNC.format(actor=APIFY_RAG_ACTOR, token=token)
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read().decode("utf-8"))


def rag_to_places_shape(rag_items, query):
    """Convert RAG Web Browser output to the same shape pick_best_match() expects.

    Each RAG result has a website URL + scraped markdown that may contain image refs.
    We extract image URLs from <img> tags or markdown image syntax in the page content.
    """
    if not rag_items:
        return []
    shaped = []
    for item in rag_items:
        meta = item.get("metadata") or {}
        sr = item.get("searchResult") or {}
        title = meta.get("title") or sr.get("title") or ""
        desc = meta.get("description") or sr.get("description") or ""
        page_url = meta.get("url") or sr.get("url") or ""
        markdown = item.get("markdown") or item.get("text") or ""

        photos = []
        og = meta.get("ogImage") or meta.get("og:image")
        if og:
            photos.append(og)
        # Extract <img src="..."> and ![](url) from the markdown
        photos += re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', markdown)
        photos += re.findall(r'!\[[^\]]*\]\(([^)\s]+)', markdown)
        # Filter to plausible photo URLs (drop tracking pixels / icons)
        photos = [p for p in photos if re.search(r'\.(jpe?g|png|webp)(\?|$)', p, re.I)]
        # Absolute-URL only (skip data: and relative)
        photos = [p for p in photos if p.startswith("http")]
        # Dedupe, preserve order
        seen = set()
        photos = [p for p in photos if not (p in seen or seen.add(p))]
        photos = photos[:MAX_PHOTOS_PER_FACILITY]

        shaped.append({
            "title": title,
            "address": "",  # RAG doesn't reliably give addresses
            "imageUrls": photos,
            "website": page_url,
            "url": page_url,
            "_source": "rag",
            "_description": desc[:200],
        })
    return shaped


def collect_via_api(token, missing):
    """Fetch each facility via direct Apify API call.

    Strategy per slug:
      1. Try compass/crawler-google-places (rich Places data: photos, rating, etc.)
      2. If Places times out OR returns 0 results, fall back to apify/rag-web-browser
         (generic web search + scrape — gets photos from the operator's own site or
         any page that mentions the facility).
      3. Cache successful result. Failures are not cached (so reruns retry them).
    """
    CACHE_DIR.mkdir(exist_ok=True)
    results = {}
    for i, f in enumerate(missing, 1):
        slug = f["slug"]
        cache_path = CACHE_DIR / f"{slug}.json"
        if cache_path.exists():
            results[slug] = json.loads(cache_path.read_text(encoding="utf-8"))
            print(f"  [{i}/{len(missing)}] cached: {slug}", file=sys.stderr)
            continue
        query = build_search_query(f)
        print(f"  [{i}/{len(missing)}] places: {slug}  ←  {query}", file=sys.stderr)
        items = None
        try:
            items = call_apify_places(token, query)
            if items:
                print(f"    places-hit: {len(items)} result(s)", file=sys.stderr)
        except Exception as e:
            print(f"    places-fail: {e}", file=sys.stderr)
            items = None

        if not items:
            print(f"    rag-fallback: trying apify/rag-web-browser", file=sys.stderr)
            try:
                rag_items = call_apify_rag(token, query)
                items = rag_to_places_shape(rag_items, query)
                if items:
                    print(f"    rag-hit: {len(items)} page(s)", file=sys.stderr)
            except Exception as e:
                print(f"    rag-fail: {e}", file=sys.stderr)
                items = []

        if items:
            cache_path.write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")
        results[slug] = items or []
        time.sleep(SLEEP_BETWEEN_CALLS)
    return results


# ─── JSON ingest mode (fallback for manual Apify runs) ────────────────────────


def collect_via_json(json_path, missing):
    """Match facilities to entries in a single Apify dataset JSON file."""
    items = json.loads(Path(json_path).read_text(encoding="utf-8"))
    if not isinstance(items, list):
        items = items.get("items") or items.get("results") or []
    print(f"Loaded {len(items)} Apify items from {json_path}", file=sys.stderr)
    by_query = {}
    for it in items:
        q = (it.get("searchString") or "").strip()
        by_query.setdefault(q, []).append(it)
    results = {}
    for f in missing:
        q = build_search_query(f)
        results[f["slug"]] = by_query.get(q, [])
    return results


# ─── Match + extract ──────────────────────────────────────────────────────────


def pick_best_match(facility, candidates):
    """Pick the best Apify result for this facility. Returns (item, confidence, note)."""
    if not candidates:
        return None, "none", "no Apify results"
    title = facility.get("title", "")
    area = (facility.get("area", "") or "").lower()
    state = (facility.get("state", "") or "").lower()

    scored = []
    for it in candidates:
        sim = title_similarity(title, it.get("title", ""))
        addr = (it.get("address", "") or "").lower()
        loc_match = (area and area in addr) or (state and state in addr)
        scored.append((sim, loc_match, it))

    scored.sort(key=lambda x: (x[0] + (0.2 if x[1] else 0)), reverse=True)
    sim, loc_match, top = scored[0]
    if sim >= 0.6:
        conf = "high"
        note = f"title overlap {sim:.2f}; area-in-address={loc_match}"
    elif sim >= 0.4:
        conf = "medium"
        note = f"title overlap {sim:.2f}; review manually"
    else:
        conf = "low"
        note = f"title overlap {sim:.2f}; likely wrong match — review"
    return top, conf, note


def extract_fields(item):
    """Pull sheet-relevant fields from one Apify Places item."""
    if not item:
        return {}
    photos_raw = item.get("imageUrls") or item.get("images") or []
    if photos_raw and isinstance(photos_raw[0], dict):
        photos_raw = [p.get("imageUrl") or p.get("url") for p in photos_raw if p]
    photos = [upgrade_lh3_resolution(u) for u in photos_raw if u]
    photos = photos[:MAX_PHOTOS_PER_FACILITY]
    return {
        "matched_title": item.get("title", "") or "",
        "matched_address": item.get("address", "") or "",
        "photos": "|".join(photos),
        "hero_image": photos[0] if photos else "",
        "photo_count": len(photos),
        "rating_new": item.get("totalScore") or item.get("rating") or "",
        "review_count_new": item.get("reviewsCount") or item.get("reviewsTotal") or "",
        "phone_new": item.get("phone") or "",
        "website_new": item.get("website") or "",
        "google_maps_url_new": item.get("url") or item.get("placesUrl") or "",
    }


# ─── Main ─────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-json", help="Use a pre-downloaded Apify dataset JSON instead of calling the API")
    parser.add_argument("--queries-only", action="store_true",
                        help="Just write rescrape_queries.txt and exit (for manual Apify run)")
    args = parser.parse_args()

    print("Fetching live sheet to find missing-photo facilities...", file=sys.stderr)
    missing = get_missing_photo_facilities()
    print(f"  {len(missing)} live facilities have no photos.", file=sys.stderr)

    # Always write the queries file — useful even in API mode
    queries = [build_search_query(f) for f in missing]
    QUERIES_PATH.write_text("\n".join(queries) + "\n", encoding="utf-8")
    print(f"  Wrote {QUERIES_PATH} ({len(queries)} queries)", file=sys.stderr)

    if args.queries_only:
        return

    # Pick mode
    if args.from_json:
        print(f"\nMode B: ingesting from {args.from_json}", file=sys.stderr)
        results_by_slug = collect_via_json(args.from_json, missing)
    else:
        token = os.environ.get("APIFY_TOKEN", "").strip()
        if not token:
            print("\nNo APIFY_TOKEN env var found. Two options:", file=sys.stderr)
            print(f"  1. export APIFY_TOKEN=apify_api_xxxxx then rerun", file=sys.stderr)
            print(f"  2. Manual: paste {QUERIES_PATH} into Apify console for", file=sys.stderr)
            print(f"     compass/crawler-google-places, run it, download the dataset", file=sys.stderr)
            print(f"     to rescrape_input.json, then:", file=sys.stderr)
            print(f"       python rescrape_missing_photos.py --from-json rescrape_input.json", file=sys.stderr)
            return 1
        print("\nMode A: calling Apify API directly (slow, ~30s per facility)...", file=sys.stderr)
        results_by_slug = collect_via_api(token, missing)

    # Build review CSV
    print(f"\nWriting {OUTPUT_CSV}...", file=sys.stderr)
    fieldnames = [
        "slug", "current_title", "current_area", "current_state",
        "source", "matched_title", "matched_address", "match_confidence",
        "photos", "hero_image", "photo_count",
        "rating_new", "review_count_new", "phone_new", "website_new", "google_maps_url_new",
        "notes",
    ]
    high = medium = low = none = 0
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        for f in missing:
            slug = f["slug"]
            candidates = results_by_slug.get(slug, [])
            best, conf, note = pick_best_match(f, candidates)
            source = (best or {}).get("_source") or ("places" if best else "none")
            row = {
                "slug": slug,
                "current_title": f.get("title", ""),
                "current_area": f.get("area", ""),
                "current_state": f.get("state", ""),
                "source": source,
                "match_confidence": conf,
                "notes": note,
            }
            row.update(extract_fields(best))
            w.writerow(row)
            {"high": "high", "medium": "medium", "low": "low", "none": "none"}[conf]
            if conf == "high":
                high += 1
            elif conf == "medium":
                medium += 1
            elif conf == "low":
                low += 1
            else:
                none += 1

    print(f"  Done. {high} high / {medium} medium / {low} low / {none} no-match", file=sys.stderr)
    print(f"\nNext steps:", file=sys.stderr)
    print(f"  1. Open {OUTPUT_CSV}. Review medium/low/none rows manually.", file=sys.stderr)
    print(f"  2. Run new photo URLs through photo-manager.html — drop any with", file=sys.stderr)
    print(f"     residents' faces. (Privacy filter — same as original 267 facilities.)", file=sys.stderr)
    print(f"  3. Bulk-paste cleaned data into the Google Sheet:", file=sys.stderr)
    print(f"       hero_image, photos, photo_count are the priority columns.", file=sys.stderr)
    print(f"       rating, review_count, phone, website are cross-check refreshes.", file=sys.stderr)
    print(f"  4. To fill the deeper editorial fields (care_types, total_beds, religion,", file=sys.stderr)
    print(f"     pricing, JKM licence, editorial_summary), run /nh-profiles per facility.", file=sys.stderr)
    print(f"     See .claude/commands/nh-profiles.md for the workflow. The skill works", file=sys.stderr)
    print(f"     best on facilities with their own website — facilities that are MDAC-only", file=sys.stderr)
    print(f"     entries (no operator website) need direct outreach instead.", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main() or 0)
