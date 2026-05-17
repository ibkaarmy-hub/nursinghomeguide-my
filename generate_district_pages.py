#!/usr/bin/env python3
"""Generate per-district listing pages under /<category>/<state>/<district>/.

A district page lists facilities in one administrative district (e.g. Kajang
in Selangor) for one care category (e.g. nursing-homes). Built from the
state-page template at nursing-homes/<state-slug>/index.html, with title,
breadcrumb, hero, intro, and facility-filter logic substituted per district.

Threshold: a district page is generated only when >=3 facilities in that
(state, district, category) tuple exist. Smaller districts skip — their
facilities still appear on the state page.

Run:  python generate_district_pages.py
"""
import csv
import io
import json
import os
import re
import sys
import urllib.request
from collections import defaultdict

from district_taxonomy import area_to_district, _DISTRICT_LABELS
from district_intros import DISTRICT_INTROS

BASE = "https://nursinghomeguide.my"
THRESHOLD = 3

FACILITIES_CSV = (
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ4_BgHIjnlgmITzjyUuGDpgpNzPL7MfjOY2069i0PtbVbXSxIAJk1tmBejwNo8aBBeLuRi62szF2sh/pub"
    "?gid=292378871&single=true&output=csv"
)

# Map state name → state slug (used both for URLs and for finding the
# template state page to clone from).
STATE_SLUGS = {
    "Johor": "johor",
    "Kuala Lumpur": "kuala-lumpur",
    "Selangor": "selangor",
    "Negeri Sembilan": "negeri-sembilan",
    "Penang": "penang",
    "Perak": "perak",
}

# Map (category) → (canonical URL dir, JS care-type filter as a JS snippet
# that returns true when a facility belongs in this category).
CATEGORIES = {
    "nursing-homes": {
        "label": "Nursing Homes",
        "label_lower": "nursing homes",
        "filter_js": (
            "((ct => !ct.includes('assisted living') && !ct.includes('home care') "
            "&& !ct.includes('day care'))((f.care_types||'').toLowerCase()) "
            "|| !(f.care_types||'').trim())"
        ),
        "category_key": "nursing home",
    },
    "assisted-living": {
        "label": "Assisted Living",
        "label_lower": "assisted-living homes",
        "filter_js": "((f.care_types||'').toLowerCase().includes('assisted living'))",
        "category_key": "assisted living",
    },
    "day-care": {
        "label": "Day Care",
        "label_lower": "day-care centres",
        "filter_js": "((f.care_types||'').toLowerCase().includes('day care'))",
        "category_key": "day care",
    },
    "home-care": {
        "label": "Home Care",
        "label_lower": "home-care providers",
        "filter_js": "((f.care_types||'').toLowerCase().includes('home care'))",
        "category_key": "home care",
    },
}


def fetch_csv():
    req = urllib.request.Request(FACILITIES_CSV, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read().decode("utf-8", errors="replace")
    return list(csv.DictReader(io.StringIO(body)))


def category_of(f):
    ct = (f.get("care_types") or "").lower()
    if "nursing home" in ct:
        return "nursing home"
    if "assisted living" in ct:
        return "assisted living"
    if "day care" in ct:
        return "day care"
    if "home care" in ct:
        return "home care"
    return "nursing home"


def html_escape(s):
    return (str(s or "")
            .replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;").replace("'", "&#39;"))


def build_intro_html(district_slug, district_label, state_label, category_label, count):
    """Build the intro <section> for a district page.

    First paragraph = hand-written district context from district_intros.py.
    Final paragraph = data-driven directory count line.
    """
    intro_text = DISTRICT_INTROS.get(district_slug, "")
    if not intro_text:
        # Fallback: minimal placeholder. We expect every page-worthy district
        # to have an intro; this fires only if a new district passes threshold
        # before its intro is written.
        intro_text = f"{district_label} is part of {state_label}, Malaysia."

    paragraphs = [p.strip() for p in intro_text.split("\n\n") if p.strip()]
    p_html = "\n".join(f"      <p>{html_escape(p)}</p>" for p in paragraphs)
    coverage = (
        f"      <p class=\"district-coverage\"><strong>{count}</strong> "
        f"{category_label.lower()} in {html_escape(district_label)} are listed below, "
        f"with operator-published fees, care details, and visit notes verified by our team of researchers.</p>"
    )
    return (
        '<section class="district-intro">\n'
        '  <div class="district-intro-inner">\n'
        f'{p_html}\n'
        f'{coverage}\n'
        '  </div>\n'
        '</section>\n'
    )


def transform_state_page(template_html, *, state_slug, state_label,
                         district_slug, district_label, district_filter_slugs,
                         category, count):
    cat = CATEGORIES[category]
    canonical = f"{BASE}/{category}/{state_slug}/{district_slug}/"
    title = f"{cat['label']} in {district_label}, {state_label} — Reviews & Fees"
    desc = (
        f"{count} {cat['label_lower']} in {district_label}, {state_label}. "
        f"Compare fees, care types, and visit notes — neutral profiles by our research team."
    )

    out = template_html

    # --- Head meta tags ---
    out = re.sub(r"<title>[^<]*</title>",
                 f"<title>{html_escape(title)}</title>", out, count=1)
    out = re.sub(r'<meta name="description" content="[^"]*"',
                 f'<meta name="description" content="{html_escape(desc)}"', out, count=1)
    out = re.sub(r'<meta property="og:title" content="[^"]*"',
                 f'<meta property="og:title" content="{html_escape(title)}"', out, count=1)
    out = re.sub(r'<meta property="og:description" content="[^"]*"',
                 f'<meta property="og:description" content="{html_escape(desc)}"', out, count=1)
    out = re.sub(r'<meta property="og:url" content="[^"]*"',
                 f'<meta property="og:url" content="{canonical}"', out, count=1)
    out = re.sub(r'<meta name="twitter:title" content="[^"]*"',
                 f'<meta name="twitter:title" content="{html_escape(title)}"', out, count=1)
    out = re.sub(r'<meta name="twitter:description" content="[^"]*"',
                 f'<meta name="twitter:description" content="{html_escape(desc)}"', out, count=1)
    out = re.sub(r'<link rel="canonical" href="[^"]*"',
                 f'<link rel="canonical" href="{canonical}"', out, count=1)

    # --- ItemList JSON-LD: name, description, url ---
    out = re.sub(
        r'("name":\s*)"Nursing Homes in [^"]+"',
        lambda m: f'{m.group(1)}"{cat["label"]} in {district_label}, {state_label}"',
        out, count=1,
    )
    out = re.sub(
        r'("description":\s*)"[^"]+"',
        lambda m: f'{m.group(1)}"Directory of {cat["label_lower"]} in {district_label}, {state_label}, with fees and visit notes."',
        out, count=1,
    )
    out = re.sub(
        r'("url":\s*)"https://nursinghomeguide\.my/nursing-homes/[^"]*"',
        lambda m: f'{m.group(1)}"{canonical}"',
        out, count=1,
    )

    # --- Breadcrumb: add the district level after the state ---
    # State pages have: Malaysia › Nursing Homes › <state>
    # District pages: Malaysia › Nursing Homes › <state> › <district>
    # The state link becomes clickable; the district is the current page (span).
    breadcrumb_pattern = re.compile(
        r'(<nav class="breadcrumb"[^>]*>\s*<a href="/">Malaysia</a>\s*<span>›</span>\s*<a href="/[^"]+">[^<]+</a>\s*<span>›</span>\s*)<span>([^<]+)</span>',
        re.DOTALL,
    )

    def _breadcrumb_sub(m):
        prefix = m.group(1)
        state_name = m.group(2)
        return (
            f'{prefix}<a href="/{category}/{state_slug}/">{html_escape(state_name)}</a>\n'
            f'      <span>›</span>\n'
            f'      <span>{html_escape(district_label)}</span>'
        )

    out, n = breadcrumb_pattern.subn(_breadcrumb_sub, out, count=1)
    if n == 0:
        print(f"  WARNING: breadcrumb pattern did not match for {district_slug}", file=sys.stderr)

    # --- Hero eyebrow + H1 + descriptor paragraph ---
    out = re.sub(
        r'<div class="state-hero-eyebrow">[^<]*</div>',
        f'<div class="state-hero-eyebrow">{html_escape(district_label)} · {html_escape(state_label)} · Malaysia</div>',
        out, count=1,
    )
    out = re.sub(
        r'<h1>Nursing Homes in [^<]+</h1>',
        f'<h1>{cat["label"]} in {html_escape(district_label)}</h1>',
        out, count=1,
    )
    out = re.sub(
        r'<p>Browse <strong id="heroCount">[^<]*</strong>[^<]*</p>',
        (f'<p>Browse <strong id="heroCount">—</strong> {cat["label_lower"]} in '
         f'{html_escape(district_label)}, {html_escape(state_label)}. '
         f'Monthly fees, care types, and real reviews — all in one place.</p>'),
        out, count=1,
    )

    # --- Insert district intro section directly after the hero ---
    intro_html = build_intro_html(district_slug, district_label, state_label, cat["label"], count)
    # Insert after the closing </section> of state-hero
    hero_close_re = re.compile(r'(</section>\s*<!-- Filter \+ view bar -->)')
    out, n = hero_close_re.subn(intro_html + r"\1", out, count=1)
    if n == 0:
        # Fallback: insert before the filter bar wrap
        out = out.replace(
            '<div class="filter-bar-wrap"',
            intro_html + '<div class="filter-bar-wrap"',
            1,
        )

    # --- JS facility filter: swap state filter for district-slug filter ---
    slug_list = ",".join(f'"{html_escape(s)}"' for s in sorted(district_filter_slugs))
    district_set_js = (
        f"const __DISTRICT_SLUGS = new Set([{slug_list}]);"
    )
    # The state page has a line like:
    #   allFacilities = data.filter(f => f.state === 'Selangor' && (<cat-filter>));
    # We rewrite it to filter by membership in __DISTRICT_SLUGS instead of by state,
    # and we inject the const just before that filter call.
    filter_line_re = re.compile(
        r"allFacilities\s*=\s*data\.filter\(f\s*=>\s*f\.state\s*===\s*'[^']+'\s*&&\s*[^;]+\);",
        re.DOTALL,
    )
    new_filter = (
        f"  {district_set_js}\n"
        f"  allFacilities = data.filter(f => __DISTRICT_SLUGS.has(f.slug));"
    )
    out, n = filter_line_re.subn(new_filter, out, count=1)
    if n == 0:
        print(f"  WARNING: filter-line pattern did not match for {district_slug}", file=sys.stderr)

    return out


def build_breadcrumb_jsonld(category, state_slug, state_label, district_label):
    cat = CATEGORIES[category]
    items = [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{BASE}/"},
        {"@type": "ListItem", "position": 2, "name": cat["label"], "item": f"{BASE}/{category}/"},
        {"@type": "ListItem", "position": 3, "name": state_label,
         "item": f"{BASE}/{category}/{state_slug}/"},
        {"@type": "ListItem", "position": 4, "name": district_label},
    ]
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items,
    }


def inject_breadcrumb_jsonld(html, ld):
    ld_json = json.dumps(ld, ensure_ascii=False, separators=(",", ":"))
    tag = f'<script type="application/ld+json" id="ld-breadcrumb-district">{ld_json}</script>'
    # Place right before </head>
    return html.replace("</head>", f"  {tag}\n</head>", 1)


def main():
    rows = fetch_csv()
    live = [r for r in rows if r.get("status", "").strip().lower() not in ("unverified", "removed")]

    # Bucket: (state_label, district_slug, category_key) → list of facility slugs
    buckets = defaultdict(list)
    by_district_meta = {}  # (state, slug) → district_label

    for f in live:
        state = (f.get("state") or "").strip()
        area = (f.get("area") or "").strip()
        slug = (f.get("slug") or "").strip()
        if not state or not area or not slug:
            continue
        d = area_to_district(state, area)
        if not d:
            continue
        district_slug, district_label = d
        cat_key = category_of(f)
        buckets[(state, district_slug, cat_key)].append(slug)
        by_district_meta[(state, district_slug)] = district_label

    # Reverse-map category_key → URL dir
    cat_dir = {
        "nursing home": "nursing-homes",
        "assisted living": "assisted-living",
        "day care": "day-care",
        "home care": "home-care",
    }

    written = 0
    for (state, district_slug, cat_key), slugs in sorted(buckets.items()):
        if len(slugs) < THRESHOLD:
            continue
        if state not in STATE_SLUGS:
            print(f"  Skip: unmapped state {state!r}")
            continue
        state_slug = STATE_SLUGS[state]
        district_label = by_district_meta[(state, district_slug)]
        category = cat_dir[cat_key]
        # Source template: the existing state index for this category+state
        src = os.path.join(category, state_slug, "index.html")
        if not os.path.exists(src):
            print(f"  Skip: no source template at {src}")
            continue
        with open(src, "r", encoding="utf-8") as fh:
            tmpl = fh.read()

        out_html = transform_state_page(
            tmpl,
            state_slug=state_slug,
            state_label=state,
            district_slug=district_slug,
            district_label=district_label,
            district_filter_slugs=slugs,
            category=category,
            count=len(slugs),
        )
        bc_ld = build_breadcrumb_jsonld(category, state_slug, state, district_label)
        out_html = inject_breadcrumb_jsonld(out_html, bc_ld)

        out_dir = os.path.join(category, state_slug, district_slug)
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "index.html")
        with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(out_html)
        written += 1
        print(f"  {len(slugs):>3}  /{category}/{state_slug}/{district_slug}/  {district_label}")

    print(f"\nWrote {written} district pages.")


if __name__ == "__main__":
    main()
