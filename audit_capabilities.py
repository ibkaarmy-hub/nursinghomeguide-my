"""Audit care capability flags + amenity Details rows across all live facilities.

Care capabilities live in two places:
  Facilities tab binary columns:
    care_nursing, care_dementia, care_palliative, care_rehab, care_respite, care_assisted
    medical_physio, medical_ot, medical_wound, medical_peg, medical_dementia_unit,
    medical_dialysis, medical_oxygen, medical_meds, doctor_visits, nurse_ratio_day,
    nurse_ratio_night

  Details tab sections:
    clinical    — yes/no/unknown clinical capability grid
    staffing    — RN ratios, doctor visits, etc.
    services    — operator-stated service categories
    dining      — meals, halal, vegetarian
    activities  — daily exercise, religious classes, etc.
    outdoor     — compound size, gardens
    schedule    — daily timetable

Output: a per-state gap summary + a per-facility breakdown of zero-coverage rows.
"""

import sys, io, csv, urllib.request
from collections import defaultdict, Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
FAC_URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=292378871'
DET_URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=1104748854'

CARE_FLAGS = ['care_nursing', 'care_dementia', 'care_palliative', 'care_rehab', 'care_respite', 'care_assisted']
MED_FLAGS = ['medical_physio', 'medical_ot', 'medical_wound', 'medical_peg',
             'medical_dementia_unit', 'medical_dialysis', 'medical_oxygen', 'medical_meds']
STAFFING_FIELDS = ['doctor_visits', 'nurse_ratio_day', 'nurse_ratio_night']
AMENITY_SECTIONS = {'dining', 'activities', 'services', 'outdoor', 'schedule'}
CLINICAL_SECTIONS = {'clinical', 'staffing'}


def fetch_csv(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return list(csv.reader(io.TextIOWrapper(r, encoding='utf-8')))


def is_yes(val):
    return val.strip().lower() in ('yes', 'true', 'y', '1')


def main():
    print("Fetching Facilities tab...", file=sys.stderr)
    fac = fetch_csv(FAC_URL)
    print("Fetching Details tab...", file=sys.stderr)
    det = fetch_csv(DET_URL)

    fh = fac[0]; di = {h: i for i, h in enumerate(fh)}
    g = lambda r, c: (r[di[c]] if c in di and di[c] < len(r) else '').strip()
    dh = det[0]; dxi = {h: i for i, h in enumerate(dh)}
    dg = lambda r, c: (r[dxi[c]] if c in dxi and dxi[c] < len(r) else '').strip()

    # Build Details index: slug → set of sections
    sections_by_slug = defaultdict(set)
    for r in det[1:]:
        slug = dg(r, 'slug')
        section = dg(r, 'section')
        if slug and section:
            sections_by_slug[slug].add(section)

    live = []
    for r in fac[1:]:
        slug = g(r, 'slug')
        if not slug: continue
        if g(r, 'status').lower() in ('unverified', 'removed'): continue
        live.append(r)

    total = len(live)
    print(f"\n# Care-capability & amenity audit — {total} live facilities\n")

    # ============= TABLE 1: per-state coverage =============
    by_state = defaultdict(list)
    for r in live:
        state = g(r, 'state') or '(unknown)'
        by_state[state].append(r)

    print("## Per-state coverage\n")
    print("| State | Live | care_* set | medical_* set | staffing fields | clinical+staffing rows | amenity rows | All-blank facilities |")
    print("|-------|-----:|-----------:|--------------:|----------------:|----------------------:|-------------:|--------------------:|")

    state_order = sorted(by_state.keys(), key=lambda s: -len(by_state[s]))
    grand_all_blank = []

    for st in state_order:
        rows = by_state[st]
        n = len(rows)
        care_set = sum(1 for r in rows if any(is_yes(g(r, f)) for f in CARE_FLAGS))
        med_set = sum(1 for r in rows if any(is_yes(g(r, f)) for f in MED_FLAGS))
        staff_set = sum(1 for r in rows if any(g(r, f) for f in STAFFING_FIELDS))
        clin_rows = sum(1 for r in rows if sections_by_slug.get(g(r, 'slug'), set()) & CLINICAL_SECTIONS)
        amen_rows = sum(1 for r in rows if sections_by_slug.get(g(r, 'slug'), set()) & AMENITY_SECTIONS)
        all_blank = sum(1 for r in rows
                        if not any(is_yes(g(r, f)) for f in CARE_FLAGS + MED_FLAGS)
                        and not (sections_by_slug.get(g(r, 'slug'), set()) & (CLINICAL_SECTIONS | AMENITY_SECTIONS)))
        grand_all_blank.extend(
            (g(r, 'slug'), g(r, 'title'), st)
            for r in rows
            if not any(is_yes(g(r, f)) for f in CARE_FLAGS + MED_FLAGS)
            and not (sections_by_slug.get(g(r, 'slug'), set()) & (CLINICAL_SECTIONS | AMENITY_SECTIONS))
        )
        print(f"| {st:<18} | {n:>4} | {care_set:>3} ({care_set*100//n}%) | {med_set:>3} ({med_set*100//n}%) | {staff_set:>3} ({staff_set*100//n}%) | {clin_rows:>3} ({clin_rows*100//n}%) | {amen_rows:>3} ({amen_rows*100//n}%) | {all_blank:>3} |")

    # ============= TABLE 2: per-flag coverage =============
    print("\n## Per-flag coverage (across all live)\n")
    print("| Flag | Set to 'yes' | % |")
    print("|------|-------------:|--:|")
    for flag in CARE_FLAGS + MED_FLAGS:
        n = sum(1 for r in live if is_yes(g(r, flag)))
        print(f"| {flag:<25} | {n:>4} | {n*100//total}% |")

    # ============= TABLE 3: editorial-says-yes vs flag-set =============
    # If editorial mentions a care type but the binary flag isn't set,
    # that's a fillable gap via regex parsing of editorial text.
    import re
    EDITORIAL_PATTERNS = {
        'care_nursing': [r'\bnursing\s+care\b', r'\b24[-\s]?hour\s+nursing\b', r'\bregistered\s+nurse'],
        'care_dementia': [r'\bdementia\b', r'\balzheimer'],
        'care_palliative': [r'\bpalliative\b', r'\bend[-\s]?of[-\s]?life'],
        'care_rehab': [r'\bpost[-\s]?stroke\b', r'\brehabilitation\b', r'\brecovery\b'],
        'care_respite': [r'\brespite\b', r'\bshort[-\s]?term\s+stay'],
        'care_assisted': [r'\bday\s+care\b', r'\bassisted\s+living\b', r'\bday\s+programme'],
        'medical_physio': [r'\bphysiotherapy\b', r'\bphysical\s+therapy\b', r'\bphysio\b'],
        'medical_ot': [r'\boccupational\s+therapy\b'],
        'medical_wound': [r'\bwound\s+(?:care|dressing|management)\b'],
        'medical_peg': [r'\b(?:peg|nasogastric|tube)\s+feeding\b'],
        'medical_oxygen': [r'\boxygen\s+(?:therapy|support)\b'],
        'medical_meds': [r'\bmedication\s+management\b'],
        'medical_dialysis': [r'\bdialysis\b'],
    }

    # Count: editorial mentions X but flag not set (fillable)
    fillable = Counter()
    fillable_examples = defaultdict(list)
    for r in live:
        slug = g(r, 'slug')
        ed = g(r, 'editorial_summary').lower()
        if not ed or len(ed) < 200: continue
        for flag, patterns in EDITORIAL_PATTERNS.items():
            if is_yes(g(r, flag)): continue
            if any(re.search(p, ed) for p in patterns):
                fillable[flag] += 1
                if len(fillable_examples[flag]) < 3:
                    fillable_examples[flag].append(slug)

    print("\n## Editorial mentions capability but binary flag NOT set\n")
    print("These are fillable by regex-parsing the editorial text. The Perak playbook proved this works.\n")
    print("| Flag | Fillable count | Examples |")
    print("|------|---------------:|----------|")
    for flag in CARE_FLAGS + MED_FLAGS:
        n = fillable.get(flag, 0)
        if n:
            examples = ', '.join(fillable_examples[flag][:2])
            print(f"| {flag} | {n} | {examples} |")

    fillable_total = sum(fillable.values())
    print(f"\n**Total fillable capability flags across all live facilities: {fillable_total}**")

    # ============= TABLE 4: which facilities have NO data at all =============
    print(f"\n## Facilities with ZERO capability data ({len(grand_all_blank)})\n")
    print("No care_* flags, no medical_* flags, no Details rows in clinical/staffing/services/dining/activities/outdoor/schedule. These rows show empty Care + Amenities tabs on the live site.\n")
    by_state_blank = defaultdict(list)
    for slug, title, st in grand_all_blank:
        by_state_blank[st].append((slug, title))
    for st in sorted(by_state_blank.keys(), key=lambda s: -len(by_state_blank[s])):
        n = len(by_state_blank[st])
        if n:
            print(f"### {st} ({n})")
            for slug, title in by_state_blank[st][:15]:
                print(f"  - `{slug}` — {title[:55]}")
            if n > 15:
                print(f"  ... and {n - 15} more")
            print()


if __name__ == '__main__':
    main()
