"""Generate category-prefixed state listing pages and the /assisted-living/ landing.

Outputs (relative to repo root):
  nursing-homes/index.html              redirect to /
  nursing-homes/johor/index.html        Johor NH listing
  nursing-homes/kuala-lumpur/index.html KL NH listing
  nursing-homes/selangor/index.html     Selangor NH listing
  assisted-living/index.html            AL landing (state picker + intro)
  assisted-living/johor/index.html      Johor AL listing
  assisted-living/kuala-lumpur/index.html KL AL listing
  assisted-living/selangor/index.html   Selangor AL listing

  johor.html, kuala-lumpur.html, selangor.html → overwritten with redirect stubs
  facilities.html                       → redirect to /

The generator reads johor.html as the master template (it must be in 'template'
state — a state listing page that filters to f.state === 'Johor'). After
generation it overwrites johor.html with a redirect stub.

Run: python gen_state_pages.py
"""
import sys
import io
import os
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ── 1. Read master template ──────────────────────────────────────────────
# _template_state.html is the canonical state-listing template (preserved
# committed to repo). It is NEVER overwritten by this script — johor.html /
# kuala-lumpur.html / selangor.html are written as redirect stubs, but the
# template itself lives at _template_state.html.
TEMPLATE_PATH = '_template_state.html'
if not os.path.exists(TEMPLATE_PATH):
    # Bootstrap fallback: if template doesn't exist yet but johor.html still
    # holds the listing page (pre-restructure state), use it.
    if os.path.exists('johor.html'):
        with open('johor.html', encoding='utf-8') as f:
            candidate = f.read()
        if 'allFacilities' in candidate and 'data.filter' in candidate:
            TEMPLATE = candidate
            with open(TEMPLATE_PATH, 'w', encoding='utf-8', newline='\n') as f:
                f.write(candidate)
            print(f"Bootstrapped {TEMPLATE_PATH} from johor.html.", file=sys.stderr)
        else:
            print(f"ERROR: {TEMPLATE_PATH} missing and johor.html is not a listing template.", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"ERROR: {TEMPLATE_PATH} not found.", file=sys.stderr)
        sys.exit(1)
else:
    with open(TEMPLATE_PATH, encoding='utf-8') as f:
        TEMPLATE = f.read()

# Sanity check
if 'allFacilities' not in TEMPLATE or 'data.filter' not in TEMPLATE:
    print(f"ERROR: {TEMPLATE_PATH} does not look like a state listing template.", file=sys.stderr)
    sys.exit(1)


# ── 2. Helpers ───────────────────────────────────────────────────────────
def write_file(path, content):
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)


def redirect_stub(canonical_path, page_title, desc):
    canonical = 'https://nursinghomeguide.my' + canonical_path
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="0; url={canonical_path}">
<link rel="canonical" href="{canonical}">
<meta name="robots" content="noindex,follow">
<title>{page_title}</title>
<meta name="description" content="{desc}">
<script>window.location.replace({repr(canonical_path).replace("'", '"')});</script>
</head>
<body>
<p>This page has moved to <a href="{canonical_path}">{canonical_path}</a>.</p>
</body>
</html>
"""


# ── 3. State listing page generator ──────────────────────────────────────
# Each entry: (category, state_val, slug, page_title, meta_desc, h1, intro,
#              ld_name, ld_desc, breadcrumb_html)
STATES = [
    {'state_val': 'Johor', 'slug': 'johor', 'h1_state': 'Johor', 'state_short': 'Johor'},
    {'state_val': 'Kuala Lumpur', 'slug': 'kuala-lumpur', 'h1_state': 'Kuala Lumpur', 'state_short': 'KL'},
    {'state_val': 'Selangor', 'slug': 'selangor', 'h1_state': 'Selangor', 'state_short': 'Selangor'},
]


def make_listing_page(category, state):
    """Generate a state listing page for the given category and state.

    If state is None, generates a national directory (no state filter) — used
    for /home-care/ and /day-care/ where most operators are multi-state."""
    html = TEMPLATE
    national = state is None
    state_val = '' if national else state['state_val']
    state_slug = '' if national else state['slug']
    h1_state = 'Malaysia' if national else state['h1_state']

    if category == 'nursing-homes':
        cat_label = 'Nursing Homes'
        page_title = f'Nursing Homes in {h1_state} | Compare Prices & Reviews'
        meta_desc = f'Browse licensed nursing homes in {h1_state}, Malaysia. Compare monthly fees, care types, RN coverage, and reviews. Detailed profiles to help your family choose with confidence.'
        h1 = f'Nursing Homes in {h1_state}'
        intro = f'Browse <strong id="heroCount">—</strong> licensed nursing homes in {h1_state}. Monthly fees, care types, and real reviews — all in one place.'
        ld_name = f'Nursing Homes in {h1_state}, Malaysia'
        ld_desc = f'Directory of licensed nursing homes in {h1_state} with pricing and reviews.'
        category_filter_js = "(f.care_category === 'Nursing Home' || f.care_category === 'Mixed' || !f.care_category)"
        section_label = f'in {h1_state}'
    elif category == 'assisted-living':
        cat_label = 'Assisted Living'
        page_title = f'Assisted Living in {h1_state} | Senior Living Communities'
        meta_desc = f'Assisted living communities and senior living residences in {h1_state}, Malaysia. Lifestyle-led profiles covering amenities, community character, dining, and care escalation. Helping families choose with confidence.'
        h1 = f'Assisted Living in {h1_state}'
        intro = f'Browse <strong id="heroCount">—</strong> assisted living and senior living communities in {h1_state}. Built environment, amenities, dining, and what happens if care needs change — all in one place.'
        ld_name = f'Assisted Living Communities in {h1_state}, Malaysia'
        ld_desc = f'Directory of assisted living and senior living communities in {h1_state} with amenities and pricing.'
        category_filter_js = "(f.care_category === 'Assisted Living' || f.care_category === 'Mixed')"
        section_label = f'in {h1_state}'
    elif category == 'home-care':
        cat_label = 'Home Care'
        page_title = 'Home Care Malaysia | Caregivers & Home Nursing Agencies'
        meta_desc = 'Home care services in Malaysia. Caregivers, home nursing agencies, and live-in care providers covering Klang Valley, Johor, Penang and beyond. Hourly, daily, and monthly packages compared.'
        h1 = 'Home Care in Malaysia'
        intro = 'Browse <strong id="heroCount">—</strong> home care providers serving Malaysian families. Caregivers and home nurses come to your home — for personal care, post-stroke recovery, dementia support, palliative care, and live-in arrangements. Most providers cover multiple states, so we list them as a single national directory.'
        ld_name = 'Home Care Providers in Malaysia'
        ld_desc = 'Directory of home care agencies and home nursing services in Malaysia.'
        category_filter_js = "(f.care_category === 'Home Care')"
        section_label = 'in Malaysia'
    elif category == 'day-care':
        cat_label = 'Day Care'
        page_title = 'Day Care Centres for Seniors in Malaysia | PAWE & Private'
        meta_desc = 'Adult day care centres in Malaysia. Daytime supervision, social programmes, and structured activities — residents return home in the evening. JKM-subsidised PAWE centres and private day care compared.'
        h1 = 'Day Care for Seniors in Malaysia'
        intro = 'Browse <strong id="heroCount">—</strong> day care centres for seniors. Daytime programmes only — residents return home each evening. Useful for working family carers and for socialisation when staying home alone is no longer safe.'
        ld_name = 'Senior Day Care Centres in Malaysia'
        ld_desc = 'Directory of adult day care centres and PAWE programmes in Malaysia.'
        category_filter_js = "(f.care_category === 'Day Care')"
        section_label = 'in Malaysia'
    else:
        raise ValueError(f"Unknown category: {category}")

    canonical = (f'https://nursinghomeguide.my/{category}/' if national
                 else f'https://nursinghomeguide.my/{category}/{state_slug}/')

    # ── Title ──
    html = re.sub(
        r'<title>[^<]*</title>',
        f'<title>{page_title}</title>',
        html, count=1)

    # ── Meta description ──
    html = re.sub(
        r'<meta name="description" content="[^"]*"',
        f'<meta name="description" content="{meta_desc}"',
        html, count=1)

    # ── Canonical ──
    html = re.sub(
        r'<link rel="canonical" href="[^"]*"',
        f'<link rel="canonical" href="{canonical}"',
        html, count=1)

    # ── Add <base href="/"> after <meta charset> so all relative paths resolve from root ──
    html = html.replace(
        '<meta charset="UTF-8" />',
        '<meta charset="UTF-8" />\n  <base href="/">',
        1)

    # ── JSON-LD ItemList ──
    html = re.sub(
        r'"name":\s*"Nursing Homes in Johor, Malaysia"',
        f'"name": "{ld_name}"',
        html, count=1)
    html = re.sub(
        r'"description":\s*"Malaysia\'s most comprehensive guide[^"]*"',
        f'"description": "{ld_desc}"',
        html, count=1)
    html = re.sub(
        r'"url":\s*"https://nursinghomeguide\.my/johor\.html"',
        f'"url": "{canonical}"',
        html, count=1)

    # ── Breadcrumb ──
    if national:
        new_breadcrumb = (
            f'<a href="/">Malaysia</a>\n      <span>›</span>\n'
            f'      <span>{cat_label}</span>'
        )
    else:
        new_breadcrumb = (
            f'<a href="/">Malaysia</a>\n      <span>›</span>\n'
            f'      <a href="/{category}/">{cat_label}</a>\n      <span>›</span>\n'
            f'      <span>{h1_state}</span>'
        )
    html = re.sub(
        r'<a href="index\.html">Malaysia</a>\s*<span>›</span>\s*<span>Johor</span>',
        new_breadcrumb,
        html, count=1)

    # ── H1 ──
    html = re.sub(
        r'<h1>Nursing Homes in Johor</h1>',
        f'<h1>{h1}</h1>',
        html, count=1)

    # ── Intro paragraph ──
    html = re.sub(
        r'<p>Browse <strong id="heroCount">[^<]*</strong>[^<]*</p>',
        f'<p>{intro}</p>',
        html, count=1)

    # ── Nav logo ──
    html = html.replace('href="index.html" class="logo"', 'href="/" class="logo"', 1)

    # ── Footer ──
    html = re.sub(
        r'<a href="index\.html">All States</a>',
        '<a href="/">All States</a>',
        html, count=1)

    # ── Card link path: route by category ──
    # Replace `/facility/${f.slug}/` with category-aware path. Used in makeCard
    # and makeMapPopup. Approach: compute path from f.care_category at call time.
    # Insert a small helper at top of <script> block.
    helper_js = """
// Category → URL path (must match generate_facility_pages.py CATEGORY_DIRS)
function facUrl(f) {
  const c = (f.care_category || '').trim();
  if (c === 'Assisted Living') return '/assisted-living/' + f.slug + '/';
  if (c === 'Home Care')       return '/home-care/'       + f.slug + '/';
  if (c === 'Day Care')        return '/day-care/'        + f.slug + '/';
  return '/nursing-homes/' + f.slug + '/';   // Nursing Home, Mixed, blank
}
"""
    # Insert helper after the opening <script> for the page logic
    html = html.replace(
        '// ─── Area normalisation ────────────────────────────────────',
        helper_js.strip() + '\n\n// ─── Area normalisation ────────────────────────────────────',
        1)

    # Replace card and popup hrefs
    html = html.replace('`<a href="/facility/${f.slug}/" class="fac-card">', '`<a href="${facUrl(f)}" class="fac-card">')
    html = html.replace('href="/facility/${f.slug}/"', 'href="${facUrl(f)}"')
    html = html.replace("`<a href=\"/facility/${f.slug}/\"", "`<a href=\"${facUrl(f)}\"")
    # Pattern for map popup ("View Profile →" link)
    html = html.replace(
        '<a href="/facility/${f.slug}/" style="display:inline-block;margin-top:10px;background:#2563eb;color:#fff;padding:6px 14px;border-radius:6px;font-size:.82rem;font-weight:600;text-decoration:none">View Profile →</a>',
        '<a href="${facUrl(f)}" style="display:inline-block;margin-top:10px;background:#2563eb;color:#fff;padding:6px 14px;border-radius:6px;font-size:.82rem;font-weight:600;text-decoration:none">View Profile →</a>'
    )
    # Map card — has data-slug too
    html = html.replace(
        '<a href="/facility/${f.slug}/" class="mc-card"',
        '<a href="${facUrl(f)}" class="mc-card"'
    )

    # ── State + category filter ──
    if national:
        filter_js = f"allFacilities = data.filter(f => {category_filter_js});"
    else:
        filter_js = f"allFacilities = data.filter(f => f.state === '{state_val}' && {category_filter_js});"
    html = re.sub(
        r"allFacilities = data\.filter\(f =>[^)]*\);",
        filter_js,
        html, count=1)

    # ── Result label ──
    html = html.replace(
        "currentArea ? `in ${currentArea}` : 'in Johor'",
        f"currentArea ? `in ${{currentArea}}` : '{section_label}'"
    )

    # ── Initial map view ── (johor.html sets [1.8, 103.5] for Johor; keep per-state)
    if state_val == 'Kuala Lumpur':
        html = html.replace('setView([1.8, 103.5], 9)', 'setView([3.139, 101.6869], 11)')
    elif state_val == 'Selangor':
        html = html.replace('setView([1.8, 103.5], 9)', 'setView([3.07, 101.5], 9)')

    # ── Footer state-page links → category-prefixed ──
    # The footer points to johor.html etc; rewire to /nursing-homes/<state>/
    # (only for NH listing pages; for AL pages, point to /assisted-living/<state>/)
    return html


# ── 4. AL landing page ───────────────────────────────────────────────────
def make_al_landing():
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <base href="/">
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Assisted Living Malaysia | Senior Living Communities &amp; Retirement Residences</title>
  <meta name="description" content="Assisted living and senior living communities across Malaysia. Lifestyle-first profiles covering community character, amenities, dining, and how care escalates if needs change. Built for families choosing while their parent is still well." />
  <link rel="canonical" href="https://nursinghomeguide.my/assisted-living/" />
  <link rel="stylesheet" href="style.css?v=6" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='8' fill='%232563eb'/><path d='M8 14h16v10a2 2 0 0 1-2 2H10a2 2 0 0 1-2-2V14z' fill='white'/><path d='M6 14l10-8 10 8' fill='none' stroke='white' stroke-width='2' stroke-linejoin='round'/><rect x='13' y='18' width='6' height='8' rx='1' fill='%232563eb'/></svg>" />
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    "name": "Assisted Living Malaysia",
    "url": "https://nursinghomeguide.my/assisted-living/",
    "description": "Directory of assisted living and senior living communities in Malaysia."
  }
  </script>
</head>
<body>

<nav>
  <div class="nav-inner">
    <a href="/" class="logo">NursingHome<span>Guide.my</span></a>
  </div>
</nav>

<section class="hero hero-home">
  <div class="hero-home-content">
    <div class="hero-eyebrow">🌿 Senior Living Communities in Malaysia</div>
    <h1>Assisted Living &amp; Senior<br/>Living Communities</h1>
    <p>For families choosing while their parent is still well. Lifestyle-first profiles covering community character, dining, social calendar, and how care escalates if needs change later.</p>
    <div class="hero-stats">
      <div class="hero-stat"><div class="num">3</div><div class="label">States Covered</div></div>
      <div class="hero-stat"><div class="num">Free</div><div class="label">No Sign-Up</div></div>
      <div class="hero-stat"><div class="num">Verified</div><div class="label">Operator-by-Operator</div></div>
    </div>
  </div>
</section>

<div class="section">
  <div class="section-title">Browse by State</div>
  <div class="section-sub">Select a state to compare assisted living communities, lifestyle programmes, and pricing models</div>

  <div class="state-grid">

    <a href="/assisted-living/johor/" class="state-card" style="--sc:linear-gradient(135deg,#1e3a5f 0%,#2563eb 100%)">
      <div class="state-card-pattern"><span class="state-flag">🏙️</span></div>
      <div class="state-card-body">
        <div class="state-card-name">Johor</div>
        <div class="state-card-count">Assisted living &amp; senior residences</div>
        <div class="state-card-cta">Browse Johor →</div>
      </div>
    </a>

    <a href="/assisted-living/kuala-lumpur/" class="state-card" style="--sc:linear-gradient(135deg,#1a1a2e 0%,#16213e 100%)">
      <div class="state-card-pattern"><span class="state-flag">🌆</span></div>
      <div class="state-card-body">
        <div class="state-card-name">Kuala Lumpur</div>
        <div class="state-card-count">Boutique &amp; premium AL</div>
        <div class="state-card-cta">Browse KL →</div>
      </div>
    </a>

    <a href="/assisted-living/selangor/" class="state-card" style="--sc:linear-gradient(135deg,#14532d 0%,#166534 100%)">
      <div class="state-card-pattern"><span class="state-flag">🏘️</span></div>
      <div class="state-card-body">
        <div class="state-card-name">Selangor</div>
        <div class="state-card-count">Resort-style &amp; community AL</div>
        <div class="state-card-cta">Browse Selangor →</div>
      </div>
    </a>

  </div>
</div>

<div class="section" style="max-width:880px">
  <div class="section-title">What is assisted living?</div>
  <div class="section-sub" style="margin-bottom:24px">It's a different decision from a nursing home — and the questions families ask are different too.</div>
  <div style="background:#fff;border-radius:var(--radius);box-shadow:var(--shadow);padding:24px 28px;line-height:1.7;color:#334155">
    <p style="margin-bottom:14px"><strong>Assisted living</strong> is for older adults who are largely independent but want the security of staff on-site, meals taken care of, social company, and someone to call if something goes wrong. The trigger is usually pre-emptive — downsizing, widowhood, "while still healthy" — rather than a hospital discharge.</p>
    <p style="margin-bottom:14px"><strong>Nursing homes</strong> are for higher-acuity residents who need 24-hour nursing — post-stroke, advanced dementia, immobility, or complex medical needs. The decision criteria are clinical: RN coverage, doctor frequency, capacity for procedures.</p>
    <p style="margin-bottom:0">If you're not sure which your parent needs, our <a href="/guides/which-care.html" style="color:var(--primary);font-weight:600">5-question care selector</a> will give you a starting point in under two minutes.</p>
  </div>
</div>

<div class="section" style="max-width:880px">
  <div class="section-title">What we look for in an AL profile</div>
  <div class="section-sub" style="margin-bottom:24px">Same verification rigour as our nursing home pages — different emphasis.</div>
  <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px">
    <div style="background:#fff;border-radius:var(--radius);box-shadow:var(--shadow);padding:20px;border-left:4px solid #2563eb"><div style="font-weight:700;margin-bottom:8px;font-size:.95rem">🏡 Community character</div><div style="font-size:.85rem;color:#64748b;line-height:1.6">Active vs. quiet, urban vs. garden, age range, social calendar.</div></div>
    <div style="background:#fff;border-radius:var(--radius);box-shadow:var(--shadow);padding:20px;border-left:4px solid #16a34a"><div style="font-weight:700;margin-bottom:8px;font-size:.95rem">🍽️ Dining &amp; daily life</div><div style="font-size:.85rem;color:#64748b;line-height:1.6">Meal model, dietary flexibility, dining-room culture, in-room kitchenettes.</div></div>
    <div style="background:#fff;border-radius:var(--radius);box-shadow:var(--shadow);padding:20px;border-left:4px solid #d97706"><div style="font-weight:700;margin-bottom:8px;font-size:.95rem">🏛️ Built environment</div><div style="font-size:.85rem;color:#64748b;line-height:1.6">Apartment vs. suite, private balcony, communal spaces, outdoor compound.</div></div>
    <div style="background:#fff;border-radius:var(--radius);box-shadow:var(--shadow);padding:20px;border-left:4px solid #7c3aed"><div style="font-weight:700;margin-bottom:8px;font-size:.95rem">💰 Financial model</div><div style="font-size:.85rem;color:#64748b;line-height:1.6">Monthly fee vs. membership vs. lease-for-life. Hidden costs surfaced.</div></div>
    <div style="background:#fff;border-radius:var(--radius);box-shadow:var(--shadow);padding:20px;border-left:4px solid #db2777"><div style="font-weight:700;margin-bottom:8px;font-size:.95rem">🩺 If care needs change</div><div style="font-size:.85rem;color:#64748b;line-height:1.6">What happens if mum has a fall? On-site care escalation, transfer paths, NH wing if any.</div></div>
    <div style="background:#fff;border-radius:var(--radius);box-shadow:var(--shadow);padding:20px;border-left:4px solid #0891b2"><div style="font-weight:700;margin-bottom:8px;font-size:.95rem">📜 Licensing &amp; ownership</div><div style="font-size:.85rem;color:#64748b;line-height:1.6">Act 506/802 status, operator background, ownership transparency.</div></div>
  </div>
</div>

<div class="ad-slot banner" data-ad-slot="al-landing-prefooter"></div>

<footer>
  <div class="footer-inner">
    <div>
      <div class="footer-logo">NursingHomeGuide.my</div>
      <div class="footer-tagline">A free resource for Malaysian families navigating eldercare</div>
    </div>
    <div class="footer-links">
      <a href="/">Nursing Homes</a>
      <a href="/assisted-living/">Assisted Living</a>
      <a href="/guides/which-care.html">Which Care?</a>
      <a href="/guides/government-assistance.html">Govt Assistance</a>
    </div>
    <div class="footer-copy">© 2026 NursingHomeGuide.my — Not affiliated with JKM or any facility</div>
  </div>
</footer>

</body>
</html>
"""


# ── 5. Generate everything ───────────────────────────────────────────────
written = []

# Category state listing pages (NH + AL)
for category in ('nursing-homes', 'assisted-living'):
    for s in STATES:
        page = make_listing_page(category, s)
        path = f"{category}/{s['slug']}/index.html"
        write_file(path, page)
        written.append(path)

# National directories: home care + day care
# Home care providers are typically multi-state (Homage, Care Concierge, Noble
# Care). Day care has too few entries (7) for state pages. Single national
# listing per category instead of state pages.
for category in ('home-care', 'day-care'):
    page = make_listing_page(category, None)
    path = f"{category}/index.html"
    write_file(path, page)
    written.append(path)

# AL landing
write_file('assisted-living/index.html', make_al_landing())
written.append('assisted-living/index.html')

# NH landing → just redirect to homepage (the existing / IS the NH landing)
write_file('nursing-homes/index.html', redirect_stub(
    '/',
    'Nursing Homes Malaysia | NursingHomeGuide.my',
    'Browse licensed nursing homes across Malaysia. Detailed profiles, pricing, and reviews.'
))
written.append('nursing-homes/index.html')

# Redirect stubs at old top-level state pages
write_file('johor.html', redirect_stub(
    '/nursing-homes/johor/',
    'Nursing Homes in Johor | Compare Prices & Reviews',
    'Browse licensed nursing homes in Johor, Malaysia. Compare monthly fees, care types, and reviews.'
))
written.append('johor.html')
write_file('kuala-lumpur.html', redirect_stub(
    '/nursing-homes/kuala-lumpur/',
    'Nursing Homes in Kuala Lumpur | Compare Prices & Reviews',
    'Browse licensed nursing homes in Kuala Lumpur, Malaysia. Compare monthly fees, care types, and reviews.'
))
written.append('kuala-lumpur.html')
write_file('selangor.html', redirect_stub(
    '/nursing-homes/selangor/',
    'Nursing Homes in Selangor | Compare Prices & Reviews',
    'Browse licensed nursing homes in Selangor, Malaysia. Compare monthly fees, care types, and reviews.'
))
written.append('selangor.html')

# Redirect stub at facilities.html (old all-facilities page)
if os.path.exists('facilities.html'):
    write_file('facilities.html', redirect_stub(
        '/',
        'NursingHomeGuide.my — All Facilities',
        'Browse all elder care facilities in Malaysia.'
    ))
    written.append('facilities.html')

print(f"✅ Wrote {len(written)} files:", file=sys.stderr)
for p in written:
    print(f"   {p}", file=sys.stderr)
