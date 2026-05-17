"""
Build a single audit_triage.html — a manual-review interface for the open
data-quality items surfaced by the deep audit + validator.

Each row in the report carries direct action links:
  📋 Sheet row  - opens the live Google Sheet at that exact row
  👁 Profile    - opens the live facility page
  🗺 Maps       - opens the Google Maps listing (or a name search)

The page has client-side category tabs + free-text search so the user can
triage in one place without leaving the browser.

Run from the repo root:  python _tmp/build_triage_html.py
"""
import csv, re, json, os, sys, urllib.parse, html
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))
import audit_profile_data as A

CSV_PATH = 'facilities_local.csv'
PCACHE = '_tmp/audit_places_cache.json'
OUT = 'audit_triage.html'
SHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TAB_GID = '292378871'
SITE = 'https://nursinghomeguide.my'

e = html.escape


def sheet_url(rn):
    return f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit#gid={TAB_GID}&range=A{rn}'


def profile_url(slug):
    return f'{SITE}/facility.html?slug={urllib.parse.quote(slug)}'


def maps_url_for(row, fallback_title=''):
    u = (row.get('google_maps_url') or '').strip()
    if u:
        return u
    return ('https://www.google.com/maps/search/?api=1&query='
            + urllib.parse.quote(fallback_title or row.get('title') or ''))


def actions_html(rn, slug, title, row):
    return (f'<span class="actions">'
            f'<a class="btn" href="{sheet_url(rn)}" target="_blank" title="Open sheet row {rn}">📋 Sheet</a>'
            f'<a class="btn" href="{profile_url(slug)}" target="_blank" title="Open live profile">👁 Profile</a>'
            f'<a class="btn" href="{e(maps_url_for(row, title))}" target="_blank" title="Open on Google Maps">🗺 Maps</a>'
            f'</span>')


def main():
    rows = list(csv.DictReader(open(CSV_PATH, encoding='utf-8')))
    g = lambda r, k: (r.get(k) or '').strip()
    live = []
    for i, r in enumerate(rows):
        r['_row'] = i + 2
        if g(r, 'slug') and g(r, 'status').lower() not in ('unverified', 'removed'):
            live.append(r)
    pcache = json.load(open(PCACHE, encoding='utf-8')) if os.path.exists(PCACHE) else {}
    groups = A.load_groups()

    def detail(pid):
        d = pcache.get(f'd:{pid}') or {}
        return d.get('result') if d.get('status') == 'OK' else None

    # ── compute issue sets ─────────────────────────────────────────────────
    cats = {}

    # P1 — 7c sheet state wrong (currently 1 row)
    c7c = []
    for r in live:
        pid = A.place_id_of(g(r, 'google_maps_url'))
        d = detail(pid) if pid else None
        if not d:
            continue
        gname = d.get('name', '')
        if not A.names_match(g(r, 'title'), gname):
            continue
        gstate = A.state_in_address(d.get('formatted_address', ''))
        sstate = g(r, 'state')
        if (gstate and sstate not in ('', '(unknown)') and gstate != sstate
                and {gstate, sstate} != {'Selangor', 'Kuala Lumpur'}):
            c7c.append((r, pid, gname, gstate, d.get('formatted_address', '')))
    cats['p1_state'] = c7c

    # Check 3 — website cross-leak (shared domains across non-chain slugs)
    dom_map = defaultdict(list)
    for r in live:
        d = A.domain_of(g(r, 'website'))
        if d and 'facebook' not in d:
            dom_map[d].append(r)
    cross_domain = []
    seen = set()
    for d, rs in dom_map.items():
        if len(rs) <= 1:
            continue
        for a in rs:
            for b in rs:
                if a['slug'] < b['slug'] and not A.same_chain(a['slug'], b['slug'], groups):
                    k = (d, a['slug'], b['slug'])
                    if k not in seen:
                        seen.add(k); cross_domain.append((d, a, b))
    cats['c3_websites'] = cross_domain

    # Check 4 — shared assets (phone / place_id / hero / website domain)
    c4 = {}
    for field, key in [('phone', lambda r: A.phone_digits(g(r, 'phone'))),
                       ('place_id', lambda r: A.place_id_of(g(r, 'google_maps_url'))),
                       ('hero_image', lambda r: g(r, 'hero_image')),
                       ('website_domain', lambda r: A.domain_of(g(r, 'website'))
                        if 'facebook' not in (A.domain_of(g(r, 'website')) or '') else '')]:
        m = defaultdict(list)
        for r in live:
            v = key(r)
            if v:
                m[v].append(r)
        flagged = []
        for v, rs in m.items():
            if len(rs) < 2:
                continue
            slugs = [r['slug'] for r in rs]
            in_chain = (groups.get(slugs[0]) is not None
                        and all(A.same_chain(slugs[0], s, groups) for s in slugs[1:]))
            if not in_chain:
                flagged.append((v, rs))
        c4[field] = flagged
    cats['c4_shared'] = c4

    # Check 2 — address proxy (live row missing place_id / area / state)
    proxy = []
    for r in live:
        reasons = []
        if not A.place_id_of(g(r, 'google_maps_url')):
            reasons.append('no place_id')
        if not g(r, 'area'):
            reasons.append('no area')
        if g(r, 'state') in ('', '(unknown)'):
            reasons.append('no/unknown state')
        if reasons:
            proxy.append((r, reasons))
    cats['c2_address'] = proxy

    # Check 7d — phone/website drift (place_id correct, contact differs)
    drift = []
    for r in live:
        pid = A.place_id_of(g(r, 'google_maps_url'))
        d = detail(pid) if pid else None
        if not d:
            continue
        if not A.names_match(g(r, 'title'), d.get('name', '')):
            continue
        gstate = A.state_in_address(d.get('formatted_address', ''))
        sstate = g(r, 'state')
        if gstate and sstate not in ('', '(unknown)') and gstate != sstate \
                and {gstate, sstate} != {'Selangor', 'Kuala Lumpur'}:
            continue
        flags = []
        sd, gd = A.domain_of(g(r, 'website')), A.domain_of(d.get('website', ''))
        if sd and gd and sd != gd:
            flags.append(f'website: sheet {sd!r} → google {gd!r}')
        sp, gp = A.phone_digits(g(r, 'phone')), A.phone_digits(
            d.get('international_phone_number', '') or d.get('formatted_phone_number', ''))
        if sp and gp and sp[-8:] != gp[-8:]:
            flags.append(f'phone: sheet ‘{g(r,"phone")}’ → google ‘{d.get("international_phone_number","")}’')
        if flags:
            drift.append((r, pid, d, flags))
    cats['c7d_drift'] = drift

    # Check 6 — title/slug incoherence
    title_slug = []
    for r in live:
        tw = set(A.significant_words(g(r, 'title')))
        sw = set(t for t in re.split(r'[^a-z0-9]+', g(r, 'slug').lower())
                 if len(t) >= 3 and t not in A.TITLE_STOPWORDS)
        if tw and len(tw & sw) < 2:
            title_slug.append((r, sorted(tw), sorted(sw)))
    cats['c6_titleslug'] = title_slug

    # Validator soft warnings — re-derive from live rows
    warns = []
    for r in live:
        for k, lab in [('state', 'state'), ('area', 'area'),
                       ('phone', 'phone'), ('editorial_summary', 'editorial')]:
            if not g(r, k):
                warns.append((r, f'missing {lab}'))
    cats['warns'] = warns

    # ── render HTML ────────────────────────────────────────────────────────
    cat_counts = {
        'p1_state':    len(cats['p1_state']),
        'c3_websites': len(cats['c3_websites']),
        'c4_shared':   sum(len(v) for v in cats['c4_shared'].values()),
        'c2_address':  len(cats['c2_address']),
        'c7d_drift':   len(cats['c7d_drift']),
        'c6_titleslug': len(cats['c6_titleslug']),
        'warns':       len(cats['warns']),
    }

    parts = ['''<!doctype html><html lang="en"><meta charset="utf-8">
<title>Audit triage — nursinghomeguide.my</title>
<style>
  :root { --bd:#e5e7eb; --mu:#64748b; --tx:#0f172a; --bl:#2563eb; --rd:#dc2626; --am:#d97706; --gr:#059669; }
  *{box-sizing:border-box} body{font:14px/1.55 -apple-system,Segoe UI,sans-serif;color:var(--tx);margin:0;background:#f8fafc}
  header{position:sticky;top:0;background:#fff;border-bottom:1px solid var(--bd);padding:12px 20px;z-index:50}
  header h1{margin:0 0 8px;font-size:1.1rem}
  .tabs{display:flex;gap:6px;flex-wrap:wrap}
  .tabs button{background:#fff;border:1px solid var(--bd);border-radius:6px;padding:6px 11px;font:inherit;cursor:pointer;color:var(--mu)}
  .tabs button.active{background:var(--tx);color:#fff;border-color:var(--tx)}
  .tabs button .n{margin-left:6px;font-weight:600}
  .tabs button.zero{opacity:.45}
  #search{margin-left:auto;padding:6px 9px;border:1px solid var(--bd);border-radius:6px;font:inherit;width:240px}
  main{padding:18px 20px;max-width:1400px;margin:0 auto}
  section{display:none;margin-bottom:24px}
  section.active{display:block}
  section>h2{font-size:1rem;margin:8px 0 12px}
  section>p.note{color:var(--mu);font-size:.88rem;margin:0 0 14px}
  .item{background:#fff;border:1px solid var(--bd);border-radius:8px;padding:12px 14px;margin-bottom:8px}
  .item .head{display:flex;justify-content:space-between;gap:14px;align-items:flex-start}
  .item .lhs{flex:1;min-width:0}
  .item .slug{font-family:ui-monospace,Menlo,monospace;font-size:.82rem;color:var(--mu)}
  .item .row{font-size:.78rem;color:var(--mu)}
  .item .title{font-weight:600;margin:0 0 2px}
  .item .why{margin:8px 0 0;color:var(--rd);font-size:.88rem}
  .item .why.am{color:var(--am)}
  .item .data{margin:8px 0 0;font-size:.85rem;color:#334155}
  .item .data dt{color:var(--mu);display:inline-block;min-width:130px}
  .item .data dd{display:inline;margin:0}
  .actions{display:flex;gap:6px;flex-shrink:0}
  .btn{display:inline-block;background:#fff;border:1px solid var(--bd);border-radius:5px;padding:4px 9px;font-size:.78rem;color:var(--tx);text-decoration:none;white-space:nowrap}
  .btn:hover{background:#f1f5f9}
  .pair{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:8px}
  .pair > div{background:#f8fafc;border:1px solid var(--bd);border-radius:6px;padding:10px}
  .pair .nm{font-weight:600;margin-bottom:4px}
  details{background:#fff;border:1px solid var(--bd);border-radius:8px;padding:8px 14px;margin-bottom:6px}
  details summary{cursor:pointer;font-weight:500;display:flex;justify-content:space-between;align-items:center}
  details[open] summary{margin-bottom:8px;border-bottom:1px solid var(--bd);padding-bottom:6px}
  .pill{display:inline-block;background:#e0e7ff;color:#3730a3;padding:1px 7px;border-radius:9px;font-size:.74rem;font-weight:600;margin-left:6px}
  .pill.rd{background:#fee2e2;color:#991b1b}
  .pill.am{background:#fef3c7;color:#92400e}
  .pill.gr{background:#d1fae5;color:#065f46}
  .hidden{display:none !important}
</style>
<header>
  <h1>Audit triage — nursinghomeguide.my <span class="pill gr">0 errors</span> <span style="color:var(--mu);font-size:.85rem;margin-left:6px"></span></h1>
  <div class="tabs">
''']

    tabs = [
        ('p1_state',    f'P1: Wrong state',          'rd'),
        ('c3_websites', 'Website cross-leaks',       'am'),
        ('c4_shared',   'Shared assets',             'am'),
        ('c2_address',  'Missing data',              ''),
        ('c7d_drift',   'Phone/website drift',       ''),
        ('c6_titleslug', 'Title/slug mismatch',      ''),
        ('warns',       'Soft warnings',             ''),
    ]
    for key, label, pill in tabs:
        n = cat_counts[key]
        zero = ' zero' if n == 0 else ''
        active = ' active' if key == 'p1_state' and n > 0 or (key == 'c3_websites' and cat_counts['p1_state'] == 0) else ''
        parts.append(f'    <button class="tab{zero}{active}" data-tab="{key}">{label}<span class="n">{n}</span></button>\n')
    parts.append('    <input id="search" type="search" placeholder="search slug / title…">\n')
    parts.append('  </div></header><main>\n')

    # --- P1 wrong state ---
    parts.append('<section id="sec-p1_state"><h2>P1 — sheet state disagrees with Google</h2>\n')
    parts.append('<p class="note">place_id is correct (Google\'s name matches the sheet title), but the address says a different Malaysian state. Either update the sheet\'s state column, or re-verify the place_id is the right facility.</p>\n')
    for r, pid, gname, gstate, addr in cats['p1_state']:
        parts.append(f'''<div class="item searchable" data-text="{e(r["slug"]+" "+r["title"])}">
  <div class="head"><div class="lhs">
    <div class="title">{e(g(r,"title"))}</div>
    <div class="slug">{e(r["slug"])} <span class="row">· row {r["_row"]}</span></div>
    <p class="why">sheet state: <strong>{e(g(r,"state"))}</strong> · Google says: <strong>{e(gstate)}</strong></p>
    <p class="data">Google address: {e(addr)}</p>
    <p class="data">Google name: {e(gname)}</p>
  </div>{actions_html(r["_row"], r["slug"], g(r,"title"), r)}</div></div>\n''')
    parts.append('</section>\n')

    # --- Check 3 website cross-leaks ---
    parts.append('<section id="sec-c3_websites"><h2>Website cross-leaks — same domain on unrelated facilities</h2>\n')
    parts.append('<p class="note">Two slugs share a website domain but are <em>not</em> in the same GROUPS chain. Either they\'re a real chain (add them to data.js GROUPS), or one row has the wrong website.</p>\n')
    for dom, a, b in cats['c3_websites']:
        parts.append(f'''<div class="item searchable" data-text="{e(dom+" "+a["slug"]+" "+b["slug"]+" "+a["title"]+" "+b["title"])}">
  <div class="head"><div class="lhs">
    <p class="why am">shared domain: <code>{e(dom)}</code></p>
    <div class="pair">
      <div><div class="nm">{e(g(a,"title"))}</div><div class="slug">{e(a["slug"])} · row {a["_row"]} · {e(g(a,"state"))}</div>{actions_html(a["_row"], a["slug"], g(a,"title"), a)}</div>
      <div><div class="nm">{e(g(b,"title"))}</div><div class="slug">{e(b["slug"])} · row {b["_row"]} · {e(g(b,"state"))}</div>{actions_html(b["_row"], b["slug"], g(b,"title"), b)}</div>
    </div>
  </div></div></div>\n''')
    parts.append('</section>\n')

    # --- Check 4 shared assets ---
    parts.append('<section id="sec-c4_shared"><h2>Shared assets across non-chain slugs</h2>\n')
    parts.append('<p class="note">Same phone / place_id / hero / website on slugs that aren\'t in the same GROUPS chain. <strong>Shared place_id or hero almost always = a cross-write.</strong> Shared phone can be a real shared operator.</p>\n')
    field_label = {'phone': 'Phone', 'place_id': 'place_id', 'hero_image': 'hero_image', 'website_domain': 'Website domain'}
    field_severity = {'place_id': 'rd', 'hero_image': 'rd', 'phone': 'am', 'website_domain': 'am'}
    for field, items in cats['c4_shared'].items():
        if not items:
            continue
        parts.append(f'<details><summary>{field_label[field]} <span class="pill {field_severity[field]}">{len(items)}</span></summary>\n')
        for v, rs in sorted(items, key=lambda x: -len(x[1])):
            sample_text = (v + ' ' + ' '.join(r['slug'] for r in rs) + ' ' + ' '.join(r['title'] for r in rs))
            display_v = v if field != 'hero_image' else (v[:60] + '…')
            parts.append(f'<div class="item searchable" data-text="{e(sample_text)}"><div class="head"><div class="lhs">\n')
            parts.append(f'<p class="why am">{field_label[field]}: <code>{e(display_v)}</code></p>\n')
            parts.append('<ul style="margin:6px 0 0;padding-left:18px">\n')
            for r in rs:
                parts.append(f'  <li><strong>{e(g(r,"title"))}</strong> · <span class="slug">{e(r["slug"])}</span> · row {r["_row"]} · {e(g(r,"state"))} {actions_html(r["_row"], r["slug"], g(r,"title"), r)}</li>\n')
            parts.append('</ul></div></div></div>\n')
        parts.append('</details>\n')
    parts.append('</section>\n')

    # --- Check 2 missing data ---
    parts.append('<section id="sec-c2_address"><h2>Missing data on live rows</h2>\n')
    parts.append('<p class="note">Rows live on the site but missing one or more of: place_id, area, state. Easiest to enrich via <code>enrich_places_free.py</code> for the relevant state.</p>\n')
    for r, reasons in cats['c2_address']:
        parts.append(f'''<div class="item searchable" data-text="{e(r["slug"]+" "+r["title"])}">
  <div class="head"><div class="lhs">
    <div class="title">{e(g(r,"title"))}</div>
    <div class="slug">{e(r["slug"])} <span class="row">· row {r["_row"]} · {e(g(r,"state") or "(no state)")}</span></div>
    <p class="why am">missing: {e(", ".join(reasons))}</p>
  </div>{actions_html(r["_row"], r["slug"], g(r,"title"), r)}</div></div>\n''')
    parts.append('</section>\n')

    # --- Check 7d drift ---
    parts.append('<section id="sec-c7d_drift"><h2>Phone / website drift (informational)</h2>\n')
    parts.append('<p class="note">Place_id and name match, but Google has a different phone or website domain — usually Google is more current. Low priority; update on next enrichment pass.</p>\n')
    for r, pid, d, flags in cats['c7d_drift'][:300]:
        parts.append(f'''<div class="item searchable" data-text="{e(r["slug"]+" "+r["title"])}">
  <div class="head"><div class="lhs">
    <div class="title">{e(g(r,"title"))}</div>
    <div class="slug">{e(r["slug"])} <span class="row">· row {r["_row"]} · {e(g(r,"state"))}</span></div>
    {''.join(f'<p class="why am">{e(f)}</p>' for f in flags)}
  </div>{actions_html(r["_row"], r["slug"], g(r,"title"), r)}</div></div>\n''')
    if len(cats['c7d_drift']) > 300:
        parts.append(f'<p class="note">… and {len(cats["c7d_drift"])-300} more.</p>')
    parts.append('</section>\n')

    # --- Check 6 title/slug ---
    parts.append('<section id="sec-c6_titleslug"><h2>Title and slug share &lt;2 distinctive tokens</h2>\n')
    parts.append('<p class="note">Likely an old truncated slug. Renaming changes the URL — needs a redirect from old slug. Many of these are cosmetic; act on the ones where the slug is gibberish (e.g. <code>permat</code>, <code>oran</code>).</p>\n')
    for r, tw, sw in cats['c6_titleslug'][:400]:
        parts.append(f'''<div class="item searchable" data-text="{e(r["slug"]+" "+r["title"])}">
  <div class="head"><div class="lhs">
    <div class="title">{e(g(r,"title"))}</div>
    <div class="slug">{e(r["slug"])} <span class="row">· row {r["_row"]} · {e(g(r,"state"))}</span></div>
    <p class="data">title tokens: <code>{e(", ".join(tw)) or "(none)"}</code></p>
    <p class="data">slug tokens: <code>{e(", ".join(sw)) or "(none)"}</code></p>
  </div>{actions_html(r["_row"], r["slug"], g(r,"title"), r)}</div></div>\n''')
    if len(cats['c6_titleslug']) > 400:
        parts.append(f'<p class="note">… and {len(cats["c6_titleslug"])-400} more.</p>')
    parts.append('</section>\n')

    # --- Warnings ---
    by_row = {}
    for r, msg in cats['warns']:
        rn = r['_row']
        if rn not in by_row:
            by_row[rn] = (r, [])
        by_row[rn][1].append(msg)
    parts.append('<section id="sec-warns"><h2>Soft warnings (missing fields)</h2>\n')
    parts.append('<p class="note">Content-completion gaps grouped per row — easier to triage by facility than by category.</p>\n')
    for rn, (r, msgs) in sorted(by_row.items()):
        slug, title, state = r['slug'], g(r, 'title'), g(r, 'state')
        parts.append(f'''<div class="item searchable" data-text="{e(slug+" "+title)}">
  <div class="head"><div class="lhs">
    <div class="title">{e(title)}</div>
    <div class="slug">{e(slug)} <span class="row">· row {rn} · {e(state)}</span></div>
    <p class="why am">{e(" · ".join(msgs))}</p>
  </div>{actions_html(rn, slug, title, r)}</div></div>\n''')
    parts.append('</section>\n')

    parts.append('''</main>
<script>
  const tabs = document.querySelectorAll('.tab');
  const sections = document.querySelectorAll('section');
  function show(id) {
    sections.forEach(s => s.classList.toggle('active', s.id === 'sec-' + id));
    tabs.forEach(t => t.classList.toggle('active', t.dataset.tab === id));
  }
  tabs.forEach(t => t.addEventListener('click', () => show(t.dataset.tab)));
  // Search filter
  const q = document.getElementById('search');
  q.addEventListener('input', () => {
    const v = q.value.toLowerCase();
    document.querySelectorAll('.searchable').forEach(el => {
      el.classList.toggle('hidden', v && !el.dataset.text.toLowerCase().includes(v));
    });
  });
  // Open the first non-empty tab on load
  const first = [...tabs].find(t => !t.classList.contains('zero'));
  if (first) show(first.dataset.tab);
</script>
</html>''')

    open(OUT, 'w', encoding='utf-8').write(''.join(parts))
    size = os.path.getsize(OUT)
    print(f'wrote {OUT} ({size//1024} KB)')
    print('category counts:')
    for k, v in cat_counts.items():
        print(f'  {k:<15} {v}')


if __name__ == '__main__':
    main()
