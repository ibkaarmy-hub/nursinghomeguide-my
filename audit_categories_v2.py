"""Find HIGH-CONFIDENCE miscategorisations only.

Strategy: compute current category routing (same logic as generate_facility_pages.py)
then compare to evidence in title + editorial. Flag only when evidence is unambiguous.

CURRENT routing (from generate_facility_pages.py main loop):
  care_types_raw = lower
  if "assisted living" in raw and "nursing home" not in raw: AL
  elif "home care" in raw and "nursing home" not in raw:     HC
  elif "day care" in raw and "nursing home" not in raw:      DC
  else:                                                       NH (default)

So ANY mention of "nursing home" in care_types → routed to /nursing-homes/.
"""

import sys, io, csv, re, urllib.request
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
FAC_URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=292378871'


def fetch_csv(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return list(csv.reader(io.TextIOWrapper(r, encoding='utf-8')))


def current_category(care_types):
    """Mirror the generator's classifier."""
    raw = (care_types or '').lower()
    if 'assisted living' in raw and 'nursing home' not in raw:
        return 'Assisted Living'
    if 'home care' in raw and 'nursing home' not in raw:
        return 'Home Care'
    if 'day care' in raw and 'nursing home' not in raw:
        return 'Day Care'
    return 'Nursing Home'  # default


def infer_correct_category(title, editorial, care_types):
    """Return (correct_category, evidence) where correct_category is one of
    Nursing Home / Assisted Living / Home Care / Day Care / Mixed / None.
    Only returns a non-None inference if there's STRONG evidence."""
    title_l = (title or '').lower()
    ed = (editorial or '').lower()

    evidence = []
    is_pawe = 'pawe' in title_l or 'pusat aktiviti warga emas' in title_l or 'aktiviti warga emas' in title_l

    # Day Care signals
    dc_strong = []
    if is_pawe:
        dc_strong.append("PAWE community centre")
    if re.search(r'\bharian\b', title_l):
        dc_strong.append("'Harian' (daytime) in title")
    if re.search(r'\bday[-\s]?activity\s+centre\b', ed):
        dc_strong.append("editorial: 'day-activity centre'")
    if re.search(r'\bdaytime\s+(?:gathering|programme|venue|centre)', ed):
        dc_strong.append("editorial: daytime gathering/programme")
    if re.search(r'\bnot\s+a\s+residential\s+(?:nursing\s+home|facility)', ed):
        dc_strong.append("editorial: 'not a residential nursing home'")
    if re.search(r'\battendees\s+(?:live\s+at\s+home|go\s+home)', ed):
        dc_strong.append("editorial: attendees live at home")
    if re.search(r'\bday[-\s]?care\s+(?:only|service|programme|centre)\s+(?:run|operated|by)', ed):
        dc_strong.append("editorial: 'day care only/service/programme'")

    # NH counter-signals (override DC if present)
    nh_counter = []
    if re.search(r'\b24[-\s]?hour\s+(?:nursing|care|residential)', ed):
        nh_counter.append("24-hour residential")
    if re.search(r'\bresidential\s+(?:nursing\s+home|elderly\s+care|care\s+home)', ed):
        nh_counter.append("residential nursing")
    if re.search(r'\b(?:bedridden|tube[-\s]?fed)\s+residents?', ed):
        nh_counter.append("bedridden residents")
    if re.search(r'\bovernight\s+(?:staff|nurse|care|stay)', ed):
        nh_counter.append("overnight staffing")

    # Home Care signals (in the Western sense — care delivered to client's home)
    hc_strong = []
    if re.search(r'\bcaregivers?\s+(?:come\s+to|are\s+sent\s+to|visit)\s+(?:your|the\s+patient)', ed):
        hc_strong.append("editorial: caregivers visit home")
    if re.search(r'\bhome[-\s]?based\s+(?:nursing|caregiving|care)\s+service', ed):
        hc_strong.append("editorial: home-based service")
    if re.search(r'\bin[-\s]?home\s+(?:nursing|care)', ed):
        hc_strong.append("editorial: in-home care")

    # Assisted Living signals
    al_strong = []
    if re.search(r'\b(?:retirement\s+(?:resort|residence|village)|active\s+retirement|senior\s+living\s+resort)', title_l):
        al_strong.append("title: retirement resort/village")
    if re.search(r'\bindependent\s+living\b', ed):
        al_strong.append("editorial: independent living")
    if re.search(r'\bservic(?:e|ed)\s+apartment', ed) and 'nursing home' not in ed:
        al_strong.append("editorial: serviced apartments")

    # Decide
    if dc_strong and not nh_counter:
        if hc_strong or al_strong:
            return ('Mixed', f"DC: {'; '.join(dc_strong)} | Mixed signals present")
        return ('Day Care', '; '.join(dc_strong))
    if hc_strong and not nh_counter:
        return ('Home Care', '; '.join(hc_strong))
    if al_strong and not nh_counter:
        return ('Assisted Living', '; '.join(al_strong))
    if dc_strong and nh_counter:
        return ('NH + Day Care', f"{'; '.join(nh_counter)} + DC: {'; '.join(dc_strong)}")
    if hc_strong and nh_counter:
        return ('NH + Home Care', f"{'; '.join(nh_counter)} + HC: {'; '.join(hc_strong)}")
    if al_strong and nh_counter:
        return ('NH + Assisted Living', f"{'; '.join(nh_counter)} + AL: {'; '.join(al_strong)}")
    return (None, None)


def main():
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

    print(f"# High-confidence category audit — {len(live)} live facilities\n")

    issues = defaultdict(list)
    for r in live:
        slug = g(r, 'slug')
        title = g(r, 'title')
        ct = g(r, 'care_types')
        ed = g(r, 'editorial_summary')
        state = g(r, 'state')
        current = current_category(ct)
        inferred, evidence = infer_correct_category(title, ed, ct)

        if not inferred:
            continue
        # Normalise: routing-equivalent categories shouldn't be flagged
        if current == 'Nursing Home' and inferred in ('Mixed', 'NH + Day Care', 'NH + Home Care', 'NH + Assisted Living'):
            # Already correctly in /nursing-homes/. Just a care_types tidy-up nice-to-have.
            issues['nice-to-have: NH with additional services in editorial'].append({
                'slug': slug, 'title': title, 'state': state, 'ct': ct,
                'current': current, 'inferred': inferred, 'evidence': evidence,
            })
            continue
        # Real miscategory
        if inferred != current:
            issues[f'WRONG: currently {current} → should be {inferred}'].append({
                'slug': slug, 'title': title, 'state': state, 'ct': ct,
                'current': current, 'inferred': inferred, 'evidence': evidence,
            })

    # ============= Output =============
    # Real miscategories first
    print("## Real miscategorisations (URL routing is wrong)\n")
    real_count = 0
    for label, items in issues.items():
        if not label.startswith('WRONG'): continue
        real_count += len(items)
        print(f"### {label} ({len(items)})\n")
        print("| Slug | State | Current care_types | Evidence |")
        print("|------|-------|--------------------|----------|")
        for it in items[:30]:
            ct_d = it['ct'] or '(blank)'
            print(f"| `{it['slug'][:42]}` | {it['state'][:14]} | `{ct_d[:32]}` | {it['evidence'][:80]} |")
        if len(items) > 30:
            print(f"\n... and {len(items)-30} more")
        print()

    # Nice-to-haves
    nice = issues.get('nice-to-have: NH with additional services in editorial', [])
    print(f"\n## Tidy-ups (already in correct category but care_types could be richer) ({len(nice)})\n")
    print("These facilities are in /nursing-homes/ — correct since they have residential beds. But editorial mentions additional services (day care, home care, assisted living) that aren't reflected in care_types. Updating care_types to a Mixed value would surface them on more state listing pages.\n")
    print("| Slug | State | Current ct | Should add | Evidence |")
    print("|------|-------|-----------|------------|----------|")
    for it in nice[:30]:
        ct_d = it['ct'] or '(blank)'
        add = it['inferred'].replace('NH + ', '+ ') if 'NH +' in it['inferred'] else it['inferred']
        print(f"| `{it['slug'][:42]}` | {it['state'][:12]} | `{ct_d[:24]}` | {add[:18]} | {it['evidence'][:50]} |")
    if len(nice) > 30:
        print(f"\n... and {len(nice)-30} more")

    print(f"\n## Totals\n")
    print(f"- **Real miscategorisations: {real_count}** (these affect URL routing — should be fixed)")
    print(f"- **Tidy-ups: {len(nice)}** (already in right category, care_types could include extra services)")


if __name__ == '__main__':
    main()
