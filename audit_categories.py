"""Audit care_types categorisation across all live facilities.

Categories drive URL routing in generate_facility_pages.py:
  /nursing-homes/<slug>/   for care_types containing 'Nursing Home' (default)
  /assisted-living/<slug>/ for care_types = 'Assisted Living' (pure)
  /home-care/<slug>/       for care_types containing 'Home Care' (pure)
  /day-care/<slug>/        for care_types = 'Day Care' (pure)
  Mixed (NH + AL):         canonical /nursing-homes/, mirror /assisted-living/

This audit surfaces:
  1. The distribution of distinct care_types values
  2. Facilities whose title strongly suggests a different category
  3. Facilities with care_assisted=yes but care_types doesn't mention 'Day Care'
  4. Facilities with editorial mentions of services not reflected in care_types
  5. Likely miscategorised rows
"""

import sys, io, csv, re, urllib.request
from collections import Counter, defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
FAC_URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=292378871'


def fetch_csv(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return list(csv.reader(io.TextIOWrapper(r, encoding='utf-8')))


def is_yes(v):
    return v.strip().lower() in ('yes', 'true', 'y', '1')


def main():
    print("Fetching live sheet...", file=sys.stderr)
    rows = fetch_csv(FAC_URL)
    headers = rows[0]
    idx = {h: i for i, h in enumerate(headers)}
    g = lambda r, c: (r[idx[c]] if c in idx and idx[c] < len(r) else '').strip()

    live = []
    for r in rows[1:]:
        slug = g(r, 'slug')
        if not slug: continue
        if g(r, 'status').lower() in ('unverified', 'removed'): continue
        live.append(r)
    total = len(live)
    print(f"\n# Category audit — {total} live facilities\n")

    # ============= 1. Distribution =============
    dist = Counter(g(r, 'care_types') for r in live)
    print("## Distinct care_types values and counts\n")
    print(f"| care_types | Count |")
    print(f"|------------|------:|")
    for ct, n in dist.most_common():
        ct_display = ct if ct else '(blank)'
        print(f"| `{ct_display}` | {n} |")

    # ============= 2. Title hints that suggest miscategory =============
    # Strong title signals per category
    TITLE_HINTS = {
        'Day Care': [
            r'\bday\s*care\b', r'\bdaycare\b', r'\bday\s+centre\b',
            r'\bharian\b',  # Malay for daytime
            r'\bday[-\s]?activity\b', r'\bday\s+programme\b',
        ],
        'Home Care': [
            r'\bhome\s+care\b', r'\bhome[-\s]?nursing\b', r'\bnursing\s+at\s+home\b',
            r'\bcaregiv(?:er|ing)\s+services?\b',
            r'\bhome[-\s]?based\s+care\b',
        ],
        'Assisted Living': [
            r'\bassisted\s+living\b', r'\bsenior\s+living\b',
            r'\bretirement\s+(?:home|resort|village|residence)',
            r'\bactive\s+retirement\b',
        ],
        'Nursing Home': [
            r'\bnursing\s+home\b', r'\bnursing\s+centre\b',
            r'\bcare\s+(?:centre|center|home)\b',
            r'\bjagaan\b',  # Malay for care
            r'\borang\s+tua\b',  # elderly
            r'\bwarga\s+(?:emas|tua)\b',  # senior citizens
            r'\brumah\s+kebajikan\b',  # welfare home
            r'\beldercare\b', r'\belderly\s+care\b',
        ],
    }

    # ============= 3. Per-row category audit =============
    miscategorised_day_care = []   # title says day care but care_types lacks Day Care
    miscategorised_home_care = []  # title says home care but care_types lacks Home Care
    miscategorised_assisted = []   # title says assisted living but care_types lacks AL
    care_assisted_no_dc = []       # care_assisted=yes but care_types doesn't say Day Care
    editorial_says_day_care = []   # editorial mentions day care but care_types doesn't
    editorial_says_home_care = []  # editorial mentions home care but care_types doesn't
    multi_service_unflagged = []   # facility has multiple service signals but care_types is single

    # Patterns that strongly imply a service is offered (not just mentioned generically)
    EDITORIAL_HINTS = {
        'Day Care': [
            r'\bday\s+care\s+(?:service|programme|centre|provided|available|offered)',
            r'\boffers?\s+day\s+care\b',
            r'\bprovides?\s+day\s+care\b',
            r'\bday[-\s]?programme\s+(?:available|offered)',
            r'\bdaytime\s+(?:programme|activities|care)',
        ],
        'Home Care': [
            r'\bhome\s+care\s+(?:service|programme|provided|available|offered)',
            r'\boffers?\s+home\s+care\b',
            r'\bprovides?\s+home\s+care\b',
            r'\bhome[-\s]?based\s+nursing',
            r'\bcaregivers?\s+to\s+your\s+home',
        ],
        'Assisted Living': [
            r'\bassisted\s+living\b',
            r'\bretirement\s+(?:home|resort|residence|village)',
            r'\bsenior\s+living\b',
        ],
    }

    for r in live:
        slug = g(r, 'slug')
        title = g(r, 'title')
        title_l = title.lower()
        ct = g(r, 'care_types')
        ct_l = ct.lower()
        editorial = g(r, 'editorial_summary').lower()
        ca = is_yes(g(r, 'care_assisted'))
        state = g(r, 'state')

        # Skip PAWE — just reclassified
        if 'pawe' in title_l or 'pusat aktiviti warga emas' in title_l:
            continue

        # Check 1: title hints
        title_hits = set()
        for cat, patterns in TITLE_HINTS.items():
            for pat in patterns:
                if re.search(pat, title_l):
                    title_hits.add(cat)
                    break

        # Day care in title but not in care_types
        if 'Day Care' in title_hits and 'day care' not in ct_l:
            miscategorised_day_care.append((slug, title, state, ct))

        # Home care in title but not in care_types — but exclude NH titles that just say "home" generically
        if 'Home Care' in title_hits and 'home care' not in ct_l:
            # Only flag if specifically "home care" or "home nursing"
            if re.search(r'\bhome\s+care\b|\bhome[-\s]?nursing\b|\bnursing\s+at\s+home\b', title_l):
                miscategorised_home_care.append((slug, title, state, ct))

        # Assisted living in title
        if 'Assisted Living' in title_hits and 'assisted living' not in ct_l:
            miscategorised_assisted.append((slug, title, state, ct))

        # Check 2: care_assisted flag set but care_types doesn't say Day Care
        if ca and 'day care' not in ct_l and 'assisted living' not in ct_l:
            care_assisted_no_dc.append((slug, title, state, ct))

        # Check 3: editorial mentions extra services
        for cat, patterns in EDITORIAL_HINTS.items():
            cat_token = cat.lower()
            if cat_token in ct_l: continue
            for pat in patterns:
                if re.search(pat, editorial):
                    if cat == 'Day Care':
                        editorial_says_day_care.append((slug, title, state, ct))
                    elif cat == 'Home Care':
                        editorial_says_home_care.append((slug, title, state, ct))
                    break

    # ============= 4. Print findings =============
    def print_section(label, items, action_hint):
        print(f"\n## {label} ({len(items)})\n")
        if not items:
            print("None found.\n")
            return
        print(action_hint)
        print(f"\n| Slug | State | Current care_types | Title |")
        print(f"|------|-------|--------------------|-------|")
        for slug, title, state, ct in items[:30]:
            ct_d = ct or '(blank)'
            print(f"| `{slug[:42]}` | {state[:14]} | `{ct_d}` | {title[:48]} |")
        if len(items) > 30:
            print(f"\n... and {len(items)-30} more")

    print_section(
        "🚨 Title says Day Care but care_types doesn't",
        miscategorised_day_care,
        "These facilities are explicitly named as day-care centres but are routed to /nursing-homes/. Should be reclassified to 'Day Care' (pure) or 'Mixed' (if they also do NH).",
    )
    print_section(
        "🚨 Title says Home Care but care_types doesn't",
        miscategorised_home_care,
        "These are explicitly named home-care services but routed to /nursing-homes/. Should be 'Home Care' if pure home-based, or 'Mixed' if they also have residential beds.",
    )
    print_section(
        "🚨 Title says Assisted Living / Senior Living / Retirement but care_types doesn't",
        miscategorised_assisted,
        "These are named as retirement/assisted-living facilities but care_types doesn't reflect it. Should be 'Assisted Living' or 'Nursing Home + Assisted Living' (mixed).",
    )
    print_section(
        "⚠ care_assisted='yes' but care_types lacks 'Day Care' or 'Assisted Living'",
        care_assisted_no_dc,
        "Capability flag says they offer assisted/day services but the category doesn't reflect it. These facilities probably should be tagged 'Nursing Home + Day Care' or similar mixed.",
    )
    print_section(
        "📝 Editorial mentions Day Care but care_types doesn't",
        editorial_says_day_care,
        "The editorial explicitly says they offer day care. Add 'Day Care' to care_types — these are mixed NH+DC facilities.",
    )
    print_section(
        "📝 Editorial mentions Home Care but care_types doesn't",
        editorial_says_home_care,
        "The editorial mentions home-care services. Add 'Home Care' or split into separate listings depending on whether the home-care branch is the same registered facility.",
    )

    # ============= 5. Summary =============
    print("\n## Summary\n")
    print(f"- Title-says-Day-Care + not-classified: **{len(miscategorised_day_care)}**")
    print(f"- Title-says-Home-Care + not-classified: **{len(miscategorised_home_care)}**")
    print(f"- Title-says-Assisted-Living + not-classified: **{len(miscategorised_assisted)}**")
    print(f"- care_assisted=yes but no DC/AL in category: **{len(care_assisted_no_dc)}**")
    print(f"- Editorial says Day Care but not in category: **{len(editorial_says_day_care)}**")
    print(f"- Editorial says Home Care but not in category: **{len(editorial_says_home_care)}**")

    print("\n### Recommended fixes")
    print("Definite fixes (title is unambiguous):")
    print(f"  - Day Care: {len(miscategorised_day_care)} facilities")
    print(f"  - Home Care: {len(miscategorised_home_care)} facilities")
    print(f"  - Assisted Living: {len(miscategorised_assisted)} facilities")
    print("\nProbable mixed-category (NH + something):")
    print(f"  - {len(editorial_says_day_care)} should be 'Nursing Home + Day Care'")
    print(f"  - {len(editorial_says_home_care)} should be 'Nursing Home + Home Care'")


if __name__ == '__main__':
    main()
