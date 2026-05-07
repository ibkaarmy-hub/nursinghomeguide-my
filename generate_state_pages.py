#!/usr/bin/env python3
"""
Generate state pages from the johor template for new Malaysian states.

Reads:
  nursing-homes/johor/index.html  (canonical template)

Writes:
  nursing-homes/<state-slug>/index.html  for each new state
  <state-slug>.html                       redirect stubs at root

States to generate determined by JKM data + existing state pages.
"""
import os
import re

REPO = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(REPO, 'nursing-homes', 'johor', 'index.html')

# Map state name → (slug, hero image filename, intro line)
NEW_STATES = {
    'Perak':            ('perak',           'Browse licensed nursing homes in Perak — including Ipoh, Teluk Intan, Sitiawan, and Taiping.'),
    'Penang':           ('penang',          'Browse licensed nursing homes in Penang — Georgetown, Butterworth, Bayan Lepas, and beyond.'),
    'Negeri Sembilan':  ('negeri-sembilan', 'Browse licensed nursing homes in Negeri Sembilan — Seremban, Mantin, and Port Dickson.'),
    'Pahang':           ('pahang',          'Browse licensed nursing homes in Pahang — Kuantan, Temerloh, Bentong, and Cameron Highlands.'),
    'Kedah':            ('kedah',           'Browse licensed nursing homes in Kedah — Alor Setar, Sungai Petani, and Langkawi.'),
    'Melaka':           ('melaka',          'Browse licensed nursing homes in Melaka — historic city, Klebang, Batu Berendam.'),
    'Sabah':            ('sabah',           'Browse licensed nursing homes in Sabah — Kota Kinabalu and surrounding areas.'),
    'Sarawak':          ('sarawak',         'Browse licensed nursing homes in Sarawak — Kuching, Miri, and Sibu.'),
    'Terengganu':       ('terengganu',      'Browse licensed nursing homes in Terengganu — Kuala Terengganu and Kemaman.'),
    'Kelantan':         ('kelantan',        'Browse licensed nursing homes in Kelantan — Kota Bharu and surrounding districts.'),
    'Perlis':           ('perlis',          'Browse licensed nursing homes in Perlis — Kangar and surrounding areas.'),
    'Putrajaya':        ('putrajaya',       'Browse licensed nursing homes in Putrajaya — federal administrative capital.'),
    'Labuan':           ('labuan',          'Browse licensed nursing homes in Labuan — federal territory.'),
}


def make_state_page(state_name, slug, intro):
    """Return a customised state page from the johor template."""
    with open(TEMPLATE, 'r', encoding='utf-8') as f:
        html = f.read()

    # Replace state-specific tokens. Order matters — replace longer/specific first.
    replacements = [
        # JSON-LD schema
        ('"name": "Nursing Homes in Johor, Malaysia"',
         f'"name": "Nursing Homes in {state_name}, Malaysia"'),
        ('"description": "Directory of licensed nursing homes in Johor with pricing and reviews."',
         f'"description": "Directory of licensed nursing homes in {state_name} with pricing and reviews."'),
        (f'"url": "https://nursinghomeguide.my/nursing-homes/johor/"',
         f'"url": "https://nursinghomeguide.my/nursing-homes/{slug}/"'),
        # Title + meta description
        ('<title>Nursing Homes in Johor | Compare Prices & Reviews</title>',
         f'<title>Nursing Homes in {state_name} | Compare Prices & Reviews</title>'),
        ('Browse licensed nursing homes in Johor, Malaysia. Compare monthly fees, care types, RN coverage, and reviews. Detailed profiles to help your family choose with confidence.',
         f'Browse licensed nursing homes in {state_name}, Malaysia. Compare monthly fees, care types, and reviews.'),
        # Canonical
        ('<link rel="canonical" href="https://nursinghomeguide.my/nursing-homes/johor/" />',
         f'<link rel="canonical" href="https://nursinghomeguide.my/nursing-homes/{slug}/" />'),
        # Hero background image
        ("url('/img/states/johor.jpg')",
         f"url('/img/states/{slug}.jpg')"),
        # Breadcrumb
        ('<span>Johor</span>',
         f'<span>{state_name}</span>'),
        # H1
        ('<h1>Nursing Homes in Johor</h1>',
         f'<h1>Nursing Homes in {state_name}</h1>'),
        # Intro paragraph (preserve case, just inject the state-specific text after heroCount)
        ('Browse <strong id="heroCount">—</strong> licensed nursing homes in Johor. Monthly fees, care types, and real reviews — all in one place.',
         f'Browse <strong id="heroCount">—</strong> {intro[len("Browse "):]} Monthly fees, care types, and real reviews — all in one place.'),
        # In-state phrase (results count)
        ("currentArea ? `in ${currentArea}` : 'in Johor'",
         f"currentArea ? `in ${{currentArea}}` : 'in {state_name}'"),
        # State filter (most important — controls which facilities show)
        ("data.filter(f => f.state === 'Johor'",
         f"data.filter(f => f.state === '{state_name}'"),
    ]

    for old, new in replacements:
        if old not in html:
            print(f"   ⚠️  Token not found in {state_name}: {old[:60]}...")
        html = html.replace(old, new)

    # Replace the AREA_NORMALIZE block with an empty one so areas auto-populate
    # from data without state-specific aliases initially.
    pattern = re.compile(r'const AREA_NORMALIZE = \{[\s\S]*?\};', re.MULTILINE)
    html = pattern.sub('const AREA_NORMALIZE = {};', html, count=1)

    return html


def make_redirect_stub(state_name, slug):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="0; url=/nursing-homes/{slug}/">
<link rel="canonical" href="https://nursinghomeguide.my/nursing-homes/{slug}/">
<meta name="robots" content="noindex,follow">
<title>Nursing Homes in {state_name} | Compare Prices & Reviews</title>
<meta name="description" content="Browse licensed nursing homes in {state_name}, Malaysia. Compare monthly fees, care types, and reviews.">
<script>window.location.replace("/nursing-homes/{slug}/");</script>
</head>
<body>
<p>This page has moved to <a href="/nursing-homes/{slug}/">/nursing-homes/{slug}/</a>.</p>
</body>
</html>
'''


def main():
    print(f"📥 Reading template: {TEMPLATE}")
    if not os.path.exists(TEMPLATE):
        print(f"❌ Template not found")
        return

    created = 0
    for state_name, (slug, intro) in NEW_STATES.items():
        # Skip if state page already exists
        page_dir = os.path.join(REPO, 'nursing-homes', slug)
        page_file = os.path.join(page_dir, 'index.html')

        os.makedirs(page_dir, exist_ok=True)

        print(f"\n🏙️  Generating {state_name} ({slug})...")
        html = make_state_page(state_name, slug, intro)
        with open(page_file, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"   ✅ {page_file}")

        # Redirect stub at /<slug>.html
        stub_file = os.path.join(REPO, f'{slug}.html')
        with open(stub_file, 'w', encoding='utf-8') as f:
            f.write(make_redirect_stub(state_name, slug))
        print(f"   ✅ {stub_file}")

        created += 1

    print(f"\n✅ Done — generated {created} state pages")
    print(f"\nNext:")
    print(f"  1. Add hero images at img/states/<slug>.jpg (or rely on CSS fallback)")
    print(f"  2. Push 388 new JKM facilities to sheet (status=unverified)")
    print(f"  3. Manually flip status to '' (blank=live) for verified entries")
    print(f"  4. Regenerate static facility pages: python3 generate_facility_pages.py")
    print(f"  5. Regenerate sitemap: python3 generate_sitemap.py")


if __name__ == '__main__':
    main()
