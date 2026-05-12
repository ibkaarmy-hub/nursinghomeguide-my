import sys, io, csv, urllib.request
from collections import defaultdict
from datetime import date

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
FAC_URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=292378871'
DET_URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=1104748854'


def fetch_csv(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return list(csv.reader(io.TextIOWrapper(r, encoding='utf-8')))


def make_getter(headers):
    idx = {h: i for i, h in enumerate(headers)}
    def g(row, col):
        i = idx.get(col)
        return (row[i] if i is not None and i < len(row) else '').strip()
    return g


def pct(n, total):
    if total == 0:
        return '0 (0%)'
    return f'{n} ({int(n/total*100)}%)'


print("Fetching Facilities tab...", file=sys.stderr)
fac_rows = fetch_csv(FAC_URL)
fac_headers = fac_rows[0]
g = make_getter(fac_headers)

print("Fetching Details tab...", file=sys.stderr)
det_rows = fetch_csv(DET_URL)
det_headers = det_rows[0]
gd = make_getter(det_headers)

# Build Details index: slug -> set of sections
det_by_slug = defaultdict(set)
for row in det_rows[1:]:
    slug = gd(row, 'slug')
    section = gd(row, 'section')
    if slug and section:
        det_by_slug[slug].add(section)

# Group facilities by state, skip hidden
AMENITY_SECTIONS = {'dining', 'activities', 'services', 'outdoor', 'schedule'}
CLINICAL_SECTIONS = {'clinical', 'staffing'}

by_state = defaultdict(list)
for row in fac_rows[1:]:
    slug = g(row, 'slug')
    if not slug:
        continue
    status = g(row, 'status').lower()
    if status in ('unverified', 'removed'):
        continue
    state = g(row, 'state') or '(unknown)'
    by_state[state].append(row)

# --- Summary table ---
print(f"\n## Enrichment Audit by State — {date.today()}\n")
print(f"| {'State':<20} | {'Live':>4} | {'Editorial':>14} | {'Pricing':>12} | {'Hero photo':>10} | {'PlaceId URL':>11} | {'Details slugs':>13} |")
print(f"|{'-'*22}|{'-'*6}|{'-'*16}|{'-'*14}|{'-'*12}|{'-'*13}|{'-'*15}|")

state_order = sorted(by_state.keys(), key=lambda s: -len(by_state[s]))

for state in state_order:
    rows = by_state[state]
    total = len(rows)
    editorial = sum(1 for r in rows if g(r, 'editorial_summary'))
    has_price = sum(1 for r in rows if (
        g(r, 'shared_price') or
        (g(r, 'pricing_display') and g(r, 'pricing_display').lower() != 'call for pricing')
    ))
    hero = sum(1 for r in rows if g(r, 'hero_image'))
    placeid = sum(1 for r in rows if 'query_place_id' in g(r, 'google_maps_url'))
    det_slugs = sum(1 for r in rows if g(r, 'slug') in det_by_slug)
    print(
        f"| {state:<20} | {total:>4} | {pct(editorial, total):>14} | {pct(has_price, total):>12} | "
        f"{pct(hero, total):>10} | {pct(placeid, total):>11} | {pct(det_slugs, total):>13} |"
    )

# --- Per-state Details breakdown ---
print(f"\n## Details Tab — section breakdown by state\n")
all_sections = sorted({s for sections in det_by_slug.values() for s in sections})
print(f"| {'State':<20} | {'Slugs w/ any':>12} | " + " | ".join(f"{s[:10]:>10}" for s in all_sections) + " |")
print(f"|{'-'*22}|{'-'*14}|" + "|".join("-"*12 for _ in all_sections) + "|")

for state in state_order:
    rows = by_state[state]
    slugs = {g(r, 'slug') for r in rows}
    with_any = sum(1 for s in slugs if s in det_by_slug)
    section_counts = {sec: sum(1 for s in slugs if sec in det_by_slug.get(s, set())) for sec in all_sections}
    print(
        f"| {state:<20} | {with_any:>12} | " +
        " | ".join(f"{section_counts[s]:>10}" for s in all_sections) + " |"
    )

# --- Missing pricing: list by state ---
print(f"\n## Facilities missing pricing (shared_price blank and pricing_display = 'Call for pricing' or blank)\n")
for state in state_order:
    rows = by_state[state]
    missing = [
        g(r, 'title') for r in rows
        if not g(r, 'shared_price') and
           (not g(r, 'pricing_display') or g(r, 'pricing_display').lower() == 'call for pricing')
    ]
    if missing:
        print(f"### {state} ({len(missing)}/{len(rows)} missing pricing)")
        for t in missing:
            print(f"  - {t}")
        print()

# --- Missing Details tab: list by state ---
print(f"\n## Facilities with zero Details tab rows\n")
for state in state_order:
    rows = by_state[state]
    missing = [g(r, 'title') for r in rows if g(r, 'slug') not in det_by_slug]
    if missing:
        print(f"### {state} ({len(missing)}/{len(rows)} without Details rows)")
        for t in missing:
            print(f"  - {t}")
        print()
