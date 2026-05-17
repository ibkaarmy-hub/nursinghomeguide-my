#!/usr/bin/env python3
"""Generate sitemap.xml from the live Google Sheet.

Run:  python generate_sitemap.py
Writes sitemap.xml at repo root.
"""
import csv
import io
import os
import re
import sys
import urllib.request
from datetime import date, datetime
from xml.sax.saxutils import escape

BASE = "https://nursinghomeguide.my"
FACILITIES_CSV_LOCAL = "existing_facilities.csv"
FACILITIES_CSV = (
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ4_BgHIjnlgmITzjyUuGDpgpNzPL7MfjOY2069i0PtbVbXSxIAJk1tmBejwNo8aBBeLuRi62szF2sh/pub"
    "?gid=292378871&single=true&output=csv"
)
DATA_JS_PATH = "data.js"


def fetch_csv(url):
    # Try local CSV first
    if os.path.exists(FACILITIES_CSV_LOCAL):
        with open(FACILITIES_CSV_LOCAL, 'r', encoding='utf-8') as f:
            return list(csv.DictReader(f))
    # Fall back to remote
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read().decode("utf-8", errors="replace")
    return list(csv.DictReader(io.StringIO(body)))


def parse_lastmod(s):
    if not s:
        return None
    s = s.strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def extract_group_slugs(js_path):
    with open(js_path, "r", encoding="utf-8") as f:
        text = f.read()
    m = re.search(r"const GROUPS\s*=\s*\{(.+?)\n\};", text, re.S)
    if not m:
        return []
    body = m.group(1)
    slugs = []
    for line in body.splitlines():
        # Match top-level keys only: 2-space indent, then 'slug': {
        sm = re.match(r"^  '([a-z0-9][a-z0-9-]*)'\s*:\s*\{", line)
        if sm:
            slugs.append(sm.group(1))
    return slugs


def url_entry(loc, lastmod=None, changefreq="weekly", priority="0.5"):
    out = [f"  <url>", f"    <loc>{escape(loc)}</loc>"]
    if lastmod:
        out.append(f"    <lastmod>{lastmod}</lastmod>")
    out.append(f"    <changefreq>{changefreq}</changefreq>")
    out.append(f"    <priority>{priority}</priority>")
    out.append("  </url>")
    return "\n".join(out)


CATEGORY_DIRS = {
    "Nursing Home":     "nursing-homes",
    "Assisted Living":  "assisted-living",
    "Mixed":            "nursing-homes",   # canonical for cross-listed
    "Home Care":        "home-care",
    "Day Care":         "day-care",
}
DEFAULT_CATEGORY = "Nursing Home"


def main():
    today = date.today().isoformat()
    rows = fetch_csv(FACILITIES_CSV)
    live = [r for r in rows if r.get("title") and r.get("status", "").strip() not in ("unverified", "removed")]

    entries = []
    # Homepage (NH landing — state picker)
    entries.append(url_entry(f"{BASE}/", lastmod=today, changefreq="daily", priority="1.0"))
    # AL landing
    entries.append(url_entry(f"{BASE}/assisted-living/", lastmod=today, changefreq="daily", priority="0.9"))
    # Home care + day care national directories
    entries.append(url_entry(f"{BASE}/home-care/", lastmod=today, changefreq="weekly", priority="0.85"))
    entries.append(url_entry(f"{BASE}/day-care/", lastmod=today, changefreq="weekly", priority="0.8"))
    # NH state pages
    for state in ("johor", "kuala-lumpur", "selangor"):
        entries.append(url_entry(f"{BASE}/nursing-homes/{state}/", lastmod=today, changefreq="daily", priority="0.9"))
    # AL state pages
    for state in ("johor", "kuala-lumpur", "selangor"):
        entries.append(url_entry(f"{BASE}/assisted-living/{state}/", lastmod=today, changefreq="daily", priority="0.85"))
    # Guide pages
    for g in ("which-care", "government-assistance"):
        entries.append(url_entry(f"{BASE}/guides/{g}.html", lastmod=today, changefreq="monthly", priority="0.8"))

    # District pages — discovered from filesystem so we stay in sync with
    # generate_district_pages.py output without hardcoding a list.
    district_count = 0
    import os
    KNOWN_STATE_SLUGS = (
        "johor", "kuala-lumpur", "selangor", "negeri-sembilan",
        "penang", "perak", "kedah", "perlis", "kelantan", "terengganu",
        "pahang", "melaka", "sabah", "sarawak", "labuan", "putrajaya",
    )
    for category in ("nursing-homes", "assisted-living", "day-care", "home-care"):
        for state_slug in KNOWN_STATE_SLUGS:
            state_dir = os.path.join(category, state_slug)
            if not os.path.isdir(state_dir):
                continue
            for d in sorted(os.listdir(state_dir)):
                d_path = os.path.join(state_dir, d, "index.html")
                if os.path.isfile(d_path):
                    entries.append(url_entry(
                        f"{BASE}/{category}/{state_slug}/{d}/",
                        lastmod=today, changefreq="weekly", priority="0.85",
                    ))
                    district_count += 1

    # Facility pages — category-prefixed canonical URLs only
    # URL routing matches facUrl() in frontend state pages (uses care_types, not care_category)
    facility_count = 0
    seen_slugs = set()
    for r in live:
        slug = (r.get("slug") or "").strip()
        if not slug or slug in seen_slugs:
            continue
        seen_slugs.add(slug)
        ct = (r.get("care_types") or "").lower().strip()
        if "assisted living" in ct and "nursing home" not in ct:
            cat_dir = "assisted-living"
        elif "home care" in ct and "nursing home" not in ct:
            cat_dir = "home-care"
        elif "day care" in ct and "nursing home" not in ct:
            cat_dir = "day-care"
        else:
            cat_dir = "nursing-homes"
        lastmod = parse_lastmod(r.get("last_updated", "")) or today
        entries.append(url_entry(
            f"{BASE}/{cat_dir}/{slug}/",
            lastmod=lastmod, changefreq="weekly", priority="0.7"
        ))
        facility_count += 1

    # Org / chain pages
    org_count = 0
    for slug in extract_group_slugs(DATA_JS_PATH):
        entries.append(url_entry(
            f"{BASE}/org.html?slug={slug}",
            lastmod=today, changefreq="monthly", priority="0.6"
        ))
        org_count += 1

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(entries) + "\n"
        '</urlset>\n'
    )
    with open("sitemap.xml", "w", encoding="utf-8", newline="\n") as f:
        f.write(xml)

    print(f"Wrote sitemap.xml: {len(entries)} URLs total "
          f"(2 landings + 6 state pages + 2 guides + {facility_count} facilities + "
          f"{district_count} districts + {org_count} orgs)",
          file=sys.stderr)


if __name__ == "__main__":
    main()
