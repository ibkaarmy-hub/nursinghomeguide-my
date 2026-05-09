import csv, json

rows = list(csv.DictReader(open('sheet_merged.csv', encoding='utf-8')))
data = json.load(open('firecrawl_results.json', encoding='utf-8'))
by_slug = {d['slug']: d for d in data if d.get('slug')}

YN_FIELDS = [
    'care_nursing','care_dementia','care_palliative','care_rehab','care_respite','care_assisted',
    'rn_24_7','doctor_visits','medical_physio','medical_dialysis','medical_oxygen','medical_dementia_unit',
    'halal',
]

def yn_to_bool_str(v):
    if not v: return ''
    v = str(v).strip().lower()
    if v == 'yes': return 'Yes'
    if v == 'no':  return 'No'
    return ''

updated = 0
for r in rows:
    slug = r.get('slug','').strip()
    d = by_slug.get(slug)
    if not d or d.get('_error'):
        continue
    def fill(col, val):
        if val in (None, '', 'Unknown'): return
        cur = r.get(col,'').strip()
        if not cur:
            r[col] = str(val)
    for f in YN_FIELDS:
        v = yn_to_bool_str(d.get(f))
        if v == 'Yes':
            fill(f, 'Yes')
    fill('languages', d.get('languages'))
    sp = d.get('shared_price_myr')
    pp = d.get('private_price_myr')
    if sp: fill('shared_price', sp)
    if pp: fill('private_price', pp)
    if (sp or pp) and not r.get('pricing_display','').strip():
        bits=[]
        if sp: bits.append(f'Shared from RM{sp}/mo')
        if pp: bits.append(f'Private from RM{pp}/mo')
        r['pricing_display'] = ' • '.join(bits)
    if d.get('services_summary') and not r.get('editorial_summary','').strip():
        r['editorial_summary'] = d['services_summary']
    updated += 1

fieldnames = list(rows[0].keys())
with open('sheet_final.csv', 'w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    for r in rows:
        w.writerow(r)

def count(col):
    return sum(1 for r in rows if r.get(col,'').strip())

print(f'Updated rows: {updated}/{len(rows)}')
print('Post-merge fill counts:')
for c in YN_FIELDS + ['languages','shared_price','private_price','pricing_display','editorial_summary']:
    print(f'  {count(c):3}/{len(rows)}  {c}')
print('Wrote sheet_final.csv')
