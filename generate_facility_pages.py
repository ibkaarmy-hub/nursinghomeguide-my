#!/usr/bin/env python3
"""Generate one static HTML page per live facility under category-prefixed paths.

URL scheme (post-restructure 2026-05-03):
  /nursing-homes/<slug>/    for care_types containing 'Nursing Home' or blank (default)
  /assisted-living/<slug>/  for care_types = 'Assisted Living' (pure, no Nursing Home)
                            Mixed (Nursing Home + Assisted Living) → canonical /nursing-homes/, mirror /assisted-living/
  /home-care/<slug>/        for care_types containing 'Home Care' (pure)
  /day-care/<slug>/         for care_types containing 'Day Care' (pure)
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
FACILITIES_CSV_LOCAL = "existing_facilities.csv"
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
    # Try local CSV first
    if os.path.exists(FACILITIES_CSV_LOCAL):
        with open(FACILITIES_CSV_LOCAL, 'r', encoding='utf-8') as f:
            return list(csv.DictReader(f))
    # Fall back to remote
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


def yn_label(v):
    """Convert yes/no column value to human-readable text, or None if unknown."""
    if not v:
        return None
    s = v.strip().lower()
    if s in ('yes', 'y', 'true', '1'):
        return 'Yes'
    if s in ('no', 'n', 'false', '0'):
        return 'No'
    if is_unknown(s):
        return None
    return v.strip()


def build_static_content(f, category):
    """Return static HTML with all facility CSV fields for crawler visibility.

    Injected into <div id="profileContent"> so search engines and AI crawlers
    (GPTBot, ClaudeBot, PerplexityBot, Ahrefs, etc.) see every data field
    without executing JavaScript. The JS page renderer overwrites this block
    at runtime for interactive users.
    """
    e = html_escape
    title       = f.get('title', '').strip()
    area        = f.get('area', '').strip()
    state       = f.get('state', '').strip()
    location    = ', '.join(filter(None, [area, state, 'Malaysia']))
    care_types  = f.get('care_types', '').strip()
    editorial   = f.get('editorial_summary', '').strip()

    cat_dir = {
        'Nursing Home':  'nursing-homes',
        'Mixed':         'nursing-homes',
        'Assisted Living': 'assisted-living',
        'Home Care':     'home-care',
        'Day Care':      'day-care',
    }.get(category, 'nursing-homes')
    cat_label = 'Nursing Home' if category == 'Mixed' else category
    state_slug = re.sub(r'[^a-z0-9]+', '-', state.lower()).strip('-') if state else ''
    state_url  = f'/{cat_dir}/{state_slug}/' if state_slug else f'/{cat_dir}/'

    # ── Pricing ──────────────────────────────────────────────────────────
    pricing_rows = []
    pd = f.get('pricing_display', '').strip()
    if pd and not is_unknown(pd):
        pricing_rows.append(('Pricing', pd))
    for col, label in [
        ('shared_price',  'Shared room (RM/month)'),
        ('private_price', 'Private room (RM/month)'),
        ('four_bed_price','4-bed room (RM/month)'),
        ('dorm_price',    'Dormitory (RM/month)'),
    ]:
        v = f.get(col, '').strip()
        if v and not is_unknown(v):
            pricing_rows.append((label, v))

    # ── Care capabilities ─────────────────────────────────────────────────
    care_rows = []
    for col, label in [
        ('care_nursing',   'Nursing care'),
        ('care_dementia',  'Dementia care'),
        ('care_palliative','Palliative / end-of-life care'),
        ('care_rehab',     'Rehabilitation'),
        ('care_respite',   'Respite care'),
        ('care_assisted',  'Assisted daily living'),
    ]:
        v = yn_label(f.get(col, ''))
        if v is not None:
            care_rows.append((label, v))

    # ── Medical services ──────────────────────────────────────────────────
    medical_rows = []
    for col, label in [
        ('doctor_visits',        'Doctor visits'),
        ('medical_physio',       'Physiotherapy'),
        ('medical_ot',           'Occupational therapy'),
        ('medical_wound',        'Wound care'),
        ('medical_peg',          'PEG / tube feeding'),
        ('medical_dementia_unit','Dedicated dementia unit'),
        ('medical_dialysis',     'Dialysis'),
        ('medical_oxygen',       'Oxygen therapy'),
        ('medical_meds',         'Medication management'),
    ]:
        v = yn_label(f.get(col, ''))
        if v is not None:
            medical_rows.append((label, v))
    for col, label in [
        ('nurse_ratio_day',  'Nurse ratio (day shift)'),
        ('nurse_ratio_night','Nurse ratio (night shift)'),
    ]:
        v = f.get(col, '').strip()
        if v and not is_unknown(v):
            medical_rows.append((label, v))

    # ── Facility information ──────────────────────────────────────────────
    ops_rows = []
    for col, label in [
        ('total_beds',    'Total beds'),
        ('availability',  'Current availability'),
        ('visiting_hours','Visiting hours'),
        ('wheelchair',    'Wheelchair accessible'),
        ('parking',       'Parking'),
        ('religion',      'Religion / denomination'),
        ('languages',     'Languages spoken'),
        ('halal',         'Halal food'),
        ('subsidy',       'Government subsidy / JKM-funded'),
        ('ownership_type','Ownership type'),
        ('licence_number','JKM licence number'),
        ('last_updated',  'Last updated'),
    ]:
        v = f.get(col, '').strip()
        if v and not is_unknown(v):
            ops_rows.append((label, v))

    # ── Contact ───────────────────────────────────────────────────────────
    contact_rows = []
    for col, label in [
        ('phone',          'Phone'),
        ('whatsapp',       'WhatsApp'),
        ('website',        'Website'),
        ('facebook',       'Facebook'),
        ('google_maps_url','Google Maps'),
    ]:
        v = f.get(col, '').strip()
        if v and not is_unknown(v):
            contact_rows.append((label, v))

    # ── Rating ────────────────────────────────────────────────────────────
    rating_text = ''
    try:
        r = float(f.get('rating', '') or '')
        rc = int(f.get('review_count', '') or 0)
        rating_text = f'{r:.1f} / 5.0 ({rc} Google reviews)' if rc > 0 else f'{r:.1f} / 5.0'
    except (ValueError, TypeError):
        pass

    # ── Assemble HTML ─────────────────────────────────────────────────────
    s = []
    s.append('<div style="max-width:900px;margin:0 auto;padding:24px 20px;font-family:system-ui,sans-serif;color:#0f172a;line-height:1.65">')

    # breadcrumb
    s.append(
        f'<p style="font-size:.85rem;color:#64748b;margin:0 0 8px">'
        f'<a href="/" style="color:#2563eb">Home</a> &rsaquo; '
        f'<a href="/{cat_dir}/" style="color:#2563eb">{e(cat_label)}</a> &rsaquo; '
        f'<a href="{e(state_url)}" style="color:#2563eb">{e(state or "Malaysia")}</a>'
        f'</p>'
    )

    # H1
    s.append(f'<h1 style="font-size:1.85rem;font-weight:800;margin:0 0 4px">{e(title)}</h1>')
    s.append(f'<p style="color:#64748b;margin:0 0 12px">{e(location)}</p>')

    # meta row
    meta = []
    if rating_text:
        meta.append(f'<strong>Rating:</strong> {e(rating_text)}')
    if care_types:
        meta.append(f'<strong>Care type:</strong> {e(care_types)}')
    if meta:
        s.append(f'<p style="margin:0 0 20px">{"&ensp;&bull;&ensp;".join(meta)}</p>')

    # editorial
    if editorial:
        s.append('<section aria-label="About this facility" style="background:#f0f9ff;border-left:4px solid #2563eb;border-radius:8px;padding:20px 22px;margin:0 0 24px">')
        s.append('<p style="font-size:.72rem;font-weight:700;text-transform:uppercase;letter-spacing:.07em;color:#2563eb;margin:0 0 12px">About this facility</p>')
        for para in editorial.split('\n'):
            para = para.strip()
            if para:
                s.append(f'<p style="margin:0 0 10px">{e(para)}</p>')
        s.append('</section>')

    def dl_section(heading, rows):
        items = ''.join(
            f'<div style="display:flex;gap:16px;padding:7px 0;border-bottom:1px solid #f1f5f9">'
            f'<span style="min-width:220px;flex-shrink:0;color:#64748b;font-size:.88rem">{e(k)}</span>'
            f'<span style="font-size:.88rem;font-weight:500">{e(v)}</span>'
            f'</div>'
            for k, v in rows
        )
        return (
            f'<section aria-label="{e(heading)}" style="margin:0 0 24px">'
            f'<h2 style="font-size:1rem;font-weight:700;margin:0 0 10px;padding-bottom:6px;border-bottom:2px solid #e2e8f0">{e(heading)}</h2>'
            f'{items}'
            f'</section>'
        )

    if pricing_rows:
        s.append(dl_section('Pricing', pricing_rows))
    if care_rows:
        s.append(dl_section('Care capabilities', care_rows))
    if medical_rows:
        s.append(dl_section('Medical services', medical_rows))
    if ops_rows:
        s.append(dl_section('Facility information', ops_rows))
    if contact_rows:
        s.append(dl_section('Contact & location', contact_rows))

    s.append('</div>')
    return '\n'.join(s)


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


def transform_template(template, page_title, desc, head_inserts, static_content=''):
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
    if static_content:
        out = re.sub(
            r'(<div id="profileContent">).*?(</div>)',
            lambda m: m.group(1) + '\n' + static_content + '\n' + m.group(2),
            out, count=1, flags=re.DOTALL)
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

    # Wipe category dirs + legacy facility dir to avoid stale slugs.
    # Preserve state listing subdirs (e.g. nursing-homes/johor/) since those are
    # generated by gen_state_pages.py — only wipe directories that look like
    # facility slugs.
    STATE_DIRS = {
        "johor", "kuala-lumpur", "selangor",
        "perak", "penang", "negeri-sembilan", "pahang", "kedah",
        "melaka", "sabah", "sarawak", "terengganu", "kelantan",
        "perlis", "labuan", "putrajaya",
    }

    # Build a set of valid live slugs so we don't wipe a directory that we're
    # about to re-write anyway.
    valid_slugs = {(r.get("slug") or "").strip() for r in live}

    for d in ("nursing-homes", "assisted-living", "home-care", "day-care", "facility"):
        if d == "facility":
            if os.path.isdir(d):
                shutil.rmtree(d)
            continue
        if os.path.isdir(d):
            for entry in os.listdir(d):
                if entry in STATE_DIRS:
                    continue   # preserve state listing pages
                p = os.path.join(d, entry)
                if os.path.isdir(p) and entry not in valid_slugs:
                    shutil.rmtree(p)

    counts = {"nursing-homes": 0, "assisted-living": 0, "home-care": 0, "day-care": 0, "redirects": 0, "mirrors": 0}
    skipped_invalid = 0

    for r in live:
        slug = r["slug"].strip()
        if re.search(r"[\s/?#&\\]", slug) or not slug:
            print(f"  skip invalid slug: {slug!r}", file=sys.stderr)
            skipped_invalid += 1
            continue

        care_types_raw = (r.get("care_types") or "").strip().lower()
        if "assisted living" in care_types_raw and "nursing home" not in care_types_raw:
            category = "Assisted Living"
        elif "home care" in care_types_raw and "nursing home" not in care_types_raw:
            category = "Home Care"
        elif "day care" in care_types_raw and "nursing home" not in care_types_raw:
            category = "Day Care"
        else:
            category = DEFAULT_CATEGORY
        if category not in CATEGORY_DIRS:
            category = DEFAULT_CATEGORY

        canonical_dir, mirror_dirs = CATEGORY_DIRS[category]
        canonical = f"{BASE}/{canonical_dir}/{slug}/"

        page_title, desc, head_inserts = build_head_inserts(r, slug, canonical)
        static_content = build_static_content(r, category)
        page_html = transform_template(template, page_title, desc, head_inserts, static_content)

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
