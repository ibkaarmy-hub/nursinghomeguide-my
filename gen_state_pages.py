"""Generate kuala-lumpur.html and selangor.html from johor.html."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('johor.html', encoding='utf-8') as f:
    johor = f.read()

STATES = [
    {
        'file': 'kuala-lumpur.html',
        'state_val': 'Kuala Lumpur',
        'title_seo': 'Nursing Homes in Kuala Lumpur | Compare Prices & Reviews',
        'desc_seo': 'Browse licensed nursing homes in Kuala Lumpur, Malaysia. Compare monthly fees, care types, and reviews. Cheras, Kepong, Bangsar, Setapak and more.',
        'canonical': 'https://nursinghomeguide.my/kuala-lumpur.html',
        'h1': 'Nursing Homes in Kuala Lumpur',
        'filter_note': 'in Kuala Lumpur',
        'ld_name': 'Nursing Homes in Kuala Lumpur, Malaysia',
    },
    {
        'file': 'selangor.html',
        'state_val': 'Selangor',
        'title_seo': 'Nursing Homes in Selangor | Compare Prices & Reviews',
        'desc_seo': 'Browse licensed nursing homes in Selangor, Malaysia. Compare monthly fees, care types, and reviews across PJ, Shah Alam, Klang, Kajang, Subang and more.',
        'canonical': 'https://nursinghomeguide.my/selangor.html',
        'h1': 'Nursing Homes in Selangor',
        'filter_note': 'in Selangor',
        'ld_name': 'Nursing Homes in Selangor, Malaysia',
    },
]

def make_page(s, base):
    html = base

    # --- Title / meta ---
    html = html.replace(
        'Nursing Homes in Johor, Malaysia | Compare Prices &amp; Reviews',
        s['title_seo'].replace('&', '&amp;')
    )
    html = html.replace(
        'Nursing Homes in Johor, Malaysia | Compare Prices & Reviews',
        s['title_seo']
    )
    html = html.replace(
        'Browse 126 licensed facilities across Johor. Monthly fees, care types, and reviews — all in one place.',
        s['desc_seo']
    )
    html = html.replace(
        'https://nursinghomeguide.my/johor.html',
        s['canonical']
    )

    # --- Nav: deactivate johor link ---
    html = html.replace(
        '<a href="johor.html" style="color:var(--primary);font-weight:600">Johor</a>',
        '<a href="johor.html">Johor</a>'
    )

    # --- Hero h1 ---
    html = html.replace('<h1>Nursing Homes in Johor</h1>', '<h1>' + s['h1'] + '</h1>')

    # --- Hero paragraph ---
    html = html.replace(
        'Browse <strong id="heroCount">126</strong> licensed facilities across Johor. Monthly fees, care types, and real reviews — all in one place.',
        'Browse <strong id="heroCount">—</strong> licensed facilities ' + s['filter_note'] + '. Monthly fees, care types, and real reviews — all in one place.'
    )

    # --- Breadcrumb ---
    html = html.replace(
        '<span>Johor</span>\n    </nav>',
        '<span>' + s['state_val'] + '</span>\n    </nav>'
    )

    # --- JS: state filter ---
    html = html.replace(
        "allFacilities = data.filter(f => !f.state || f.state === 'Johor');",
        "allFacilities = data.filter(f => f.state === '" + s['state_val'] + "');"
    )

    # --- JS: result label ---
    html = html.replace(
        "currentArea ? `in ${currentArea}` : 'in Johor'",
        "currentArea ? `in ${currentArea}` : '" + s['filter_note'] + "'"
    )

    # --- JSON-LD ---
    html = html.replace(
        '"name": "Nursing Homes in Johor, Malaysia"',
        '"name": "' + s['ld_name'] + '"'
    )
    html = html.replace(
        '"description": "Directory of licensed nursing homes in Johor with pricing and reviews"',
        '"description": "' + s['desc_seo'].replace('"', '\\"') + '"'
    )
    html = html.replace(
        '"url": "https://nursinghomeguide.my/johor.html"',
        '"url": "' + s['canonical'] + '"'
    )

    return html

for s in STATES:
    page = make_page(s, johor)
    with open(s['file'], 'w', encoding='utf-8') as f:
        f.write(page)
    print(f"✅ {s['file']} written")
