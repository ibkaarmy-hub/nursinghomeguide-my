#!/usr/bin/env python3
"""Generate one static HTML page per live facility under category-prefixed paths.

URL scheme (post-restructure 2026-05-03):
  /nursing-homes/<slug>/    for care_category in {Nursing Home, Mixed}
  /assisted-living/<slug>/  for care_category in {Assisted Living}
                            and ALSO mirrored for Mixed (cross-listed; canonical is /nursing-homes/)
  /home-care/<slug>/        for care_category = Home Care
  /day-care/<slug>/         for care_category = Day Care
  /facility/<slug>/         legacy redirect stub (meta-refresh + canonical to new URL)

Each page bakes in per-facility <title>, meta description, canonical, Open Graph,
Twitter Card, and LocalBusiness JSON-LD. Static so social scrapers (WhatsApp,
Facebook, Twitter, LinkedIn) and SEO crawlers see them without executing JS.

Run:  python generate_facility_pages.py
"""
import csv
import io
import json
import os
import re
import shutil
import sys
import urllib.request

BASE = "https://nursinghomeguide.my"
FACILITIES_CSV = (
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ4_BgHIjnlgmITzjyUuGDpgpNzPL7MfjOY2069i0PtbVbXSxIAJk1tmBejwNo8aBBeLuRi62szF2sh/pub"
    "?gid=292378871&single=true&output=csv"
)
TEMPLATE_PATH = "facility.html"

# Maps care_category → (canonical_dir, also_mirror_dirs)
# canonical_dir is where the rich static page lives; mirror dirs get a small
# redirect-to-canonical stub so the URL resolves but Google sees one canonical.
CATEGORY_DIRS = {
    "Nursing Home":     ("nursing-homes",   []),
    "Assisted Living":  ("assisted-living", []),
    "Mixed":            ("nursing-homes",   ["assisted-living"]),
    "Home Care":        ("home-care",       []),
    "Day Care":         ("day-care",        []),
}
DEFAULT_CATEGORY = "Nursing Home"

UNKNOWN_TOKENS = ("not stated", "not published", "not declared", "not confirmed", "unknown", "tbd")


def fetch_csv(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read().decode("utf-8", errors="replace")
    return list(csv.DictReader(io.StringIO(body)))


def is_unknown(v):
    if not v:
        return True
    s = v.lower()
    return any(t in s for t in UNKNOWN_TOKENS)


def trim_desc(s, limit=155):
    s = re.sub(r"\s+", " ", s or "").strip()
    if len(s) <= limit:
        return s
    cut = s[:limit - 1]
    cut = re.sub(r"\s+\S*$", "", cut).rstrip(",.;:")
    return cut + "…"


def build_meta_description(f):
    title = f.get("title", "").strip()
    area = f.get("area", "").strip() or "Malaysia"
    shared = f.get("shared_price", "").strip()
    editorial = f.get("editorial_summary", "").strip()
    parts = [f"{title} in {area}."]
    if shared:
        parts.append(f"From RM {shared}/mo.")
    if editorial:
        parts.append(editorial)
    return trim_desc(" ".join(parts), 155)


def build_jsonld(f, canonical):
    title = f.get("title", "").strip()
    address = {"@type": "PostalAddress", "addressCountry": "MY"}
    if f.get("area", "").strip():
        address["addressLocality"] = f["area"].strip()
    if f.get("state", "").strip():
        address["addressRegion"] = f["state"].strip()

    ld = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "@id": canonical,
        "name": title,
        "url": canonical,
        "address": address,
    }
    if f.get("hero_image", "").strip():
        ld["image"] = f["hero_image"].strip()
    if f.get("phone", "").strip():
        ld["telephone"] = f["phone"].strip()
    editorial = (f.get("editorial_summary") or "").strip()
    if editorial:
        ld["description"] = editorial[:500]
    try:
        lat = float(f.get("latitude", ""))
        lng = float(f.get("longitude", ""))
        ld["geo"] = {"@type": "GeoCoordinates", "latitude": lat, "longitude": lng}
    except (TypeError, ValueError):
        pass
    try:
        rating = float(f.get("rating", ""))
        reviews = int(f.get("review_count", "") or 0)
        if reviews > 0:
            ld["aggregateRating"] = {
                "@type": "AggregateRating",
                "ratingValue": f"{rating:.1f}",
                "reviewCount": reviews,
                "bestRating": "5",
                "worstRating": "1",
            }
    except (TypeError, ValueError):
        pass
    pricing = f.get("pricing_display", "").strip()
    if not pricing and f.get("shared_price", "").strip():
        pricing = f"From RM {f['shared_price'].strip()}/mo"
    if pricing and not is_unknown(pricing):
        ld["priceRange"] = pricing
    return ld


def html_escape(s):
    return (str(s or "")
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;"))


def build_head_inserts(f, slug, canonical):
    title = f.get("title", "").strip()
    page_title = f"{title} — NursingHomeGuide.my"
    desc = build_meta_description(f)
    img = f.get("hero_image", "").strip()
    twitter_card = "summary_large_image" if img else "summary"
    ld = build_jsonld(f, canonical)
    ld_json = json.dumps(ld, ensure_ascii=False, separators=(",", ":"))

    parts = [
        '<base href="/">',
        f'<link rel="canonical" href="{html_escape(canonical)}">',
        '<meta property="og:type" content="website">',
        '<meta property="og:site_name" content="NursingHomeGuide.my">',
        f'<meta property="og:title" content="{html_escape(page_title)}">',
        f'<meta property="og:description" content="{html_escape(desc)}">',
        f'<meta property="og:url" content="{html_escape(canonical)}">',
    ]
    if img:
        parts.append(f'<meta property="og:image" content="{html_escape(img)}">')
    parts.append(f'<meta name="twitter:card" content="{twitter_card}">')
    parts.append(f'<meta name="twitter:title" content="{html_escape(page_title)}">')
    parts.append(f'<meta name="twitter:description" content="{html_escape(desc)}">')
    if img:
        parts.append(f'<meta name="twitter:image" content="{html_escape(img)}">')
    parts.append(f'<script type="application/ld+json" id="ld-localbusiness">{ld_json}</script>')
    parts.append(f'<script>window.__FACILITY_SLUG={json.dumps(slug)};</script>')
    return page_title, desc, "\n".join(parts)


def transform_template(template, page_title, desc, head_inserts):
    out = template
    out = re.sub(
        r'<title id="pageTitle">[^<]*</title>',
        f'<title id="pageTitle">{html_escape(page_title)}</title>',
        out, count=1)
    out = re.sub(
        r'(<meta name="description" id="pageDesc" content=)"[^"]*"(\s*/>)',
        lambda m: f'{m.group(1)}"{html_escape(desc)}"{m.group(2)}',
        out, count=1)
    out = out.replace(
        '<meta charset="UTF-8" />',
        '<meta charset="UTF-8" />\n' + head_inserts,
        1)
    return out


def build_redirect_stub(canonical, page_title, desc):
    """Tiny HTML page that meta-refreshes to canonical and points rel=canonical there.
    Google treats 0-second meta-refresh as equivalent to a 301 for indexing purposes.
    """
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="0; url={html_escape(canonical)}">
<link rel="canonical" href="{html_escape(canonical)}">
<meta name="robots" content="noindex,follow">
<title>{html_escape(page_title)}</title>
<meta name="description" content="{html_escape(desc)}">
<script>window.location.replace({json.dumps(canonical)});</script>
</head>
<body>
<p>This page has moved to <a href="{html_escape(canonical)}">{html_escape(canonical)}</a>.</p>
</body>
</html>
"""


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def main():
    rows = fetch_csv(FACILITIES_CSV)
    live = [r for r in rows
            if r.get("title") and r.get("status", "").strip() not in ("unverified", "removed")
            and (r.get("slug") or "").strip()]

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = f.read()

    # Wipe category dirs + legacy facility dir to avoid stale slugs
    for d in ("nursing-homes", "assisted-living", "home-care", "day-care", "facility"):
        # Preserve any handcrafted index.html at /nursing-homes/ etc — only wipe slug subdirs.
        if d == "facility":
            if os.path.isdir(d):
                shutil.rmtree(d)
            continue
        if os.path.isdir(d):
            for entry in os.listdir(d):
                p = os.path.join(d, entry)
                if os.path.isdir(p):
                    shutil.rmtree(p)

    counts = {"nursing-homes": 0, "assisted-living": 0, "home-care": 0, "day-care": 0, "redirects": 0, "mirrors": 0}
    skipped_invalid = 0

    for r in live:
        slug = r["slug"].strip()
        if re.search(r"[\s/?#&\\]", slug) or not slug:
            print(f"  skip invalid slug: {slug!r}", file=sys.stderr)
            skipped_invalid += 1
            continue

        category = (r.get("care_category") or "").strip() or DEFAULT_CATEGORY
        if category not in CATEGORY_DIRS:
            category = DEFAULT_CATEGORY

        canonical_dir, mirror_dirs = CATEGORY_DIRS[category]
        canonical = f"{BASE}/{canonical_dir}/{slug}/"

        page_title, desc, head_inserts = build_head_inserts(r, slug, canonical)
        page_html = transform_template(template, page_title, desc, head_inserts)

        # Canonical static page
        write_file(os.path.join(canonical_dir, slug, "index.html"), page_html)
        counts[canonical_dir] += 1

        # Mirror redirect stubs (e.g. Mixed: also at /assisted-living/<slug>/)
        for mdir in mirror_dirs:
            stub = build_redirect_stub(canonical, page_title, desc)
            write_file(os.path.join(mdir, slug, "index.html"), stub)
            counts["mirrors"] += 1

        # Legacy redirect stub at /facility/<slug>/
        legacy_stub = build_redirect_stub(canonical, page_title, desc)
        write_file(os.path.join("facility", slug, "index.html"), legacy_stub)
        counts["redirects"] += 1

    summary = (f"Wrote: {counts['nursing-homes']} NH + {counts['assisted-living']} AL + "
               f"{counts['home-care']} HC + {counts['day-care']} DC canonical pages, "
               f"{counts['mirrors']} mirror stubs, {counts['redirects']} legacy /facility/ redirects"
               + (f" (skipped {skipped_invalid} invalid slugs)" if skipped_invalid else ""))
    print(summary, file=sys.stderr)


if __name__ == "__main__":
    main()
