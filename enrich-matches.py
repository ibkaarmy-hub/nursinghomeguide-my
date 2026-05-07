#!/usr/bin/env python3
"""
For 67 confirmed matches, identify fields the JKM record fills in
that the existing sheet has empty or different.

Outputs:
- enrichment_proposed.csv  — fields to update per existing slug
- enrichment_summary.json  — stats by field
"""
import csv, json, re
from collections import Counter

JKM_FILE = '/home/user/nursinghomeguide-my/jkm_full_scraped.csv'
EX_FILE  = '/home/user/nursinghomeguide-my/existing_facilities.csv'
MATCHES  = '/home/user/nursinghomeguide-my/jkm-results/matches.json'
OUT_DIR  = '/home/user/nursinghomeguide-my/jkm-results'

with open(JKM_FILE, encoding='utf-8-sig') as f:
    jkm = {(j.get('phone',''), j.get('name','')): j for j in csv.DictReader(f)}
    # Re-index by name to find back from match record
    jkm_by_name = {}
    for j in csv.DictReader(open(JKM_FILE, encoding='utf-8-sig')):
        jkm_by_name.setdefault(j['name'], []).append(j)

with open(EX_FILE, encoding='utf-8-sig') as f:
    existing = list(csv.DictReader(f))
    ex_by_slug = {e['slug']: e for e in existing}

with open(MATCHES) as f:
    matches = json.load(f)

print(f"📥 Processing {len(matches)} confirmed matches\n")

def normalize_phone(p):
    return re.sub(r'\D', '', (p or '').strip())

# Fields where JKM is authoritative or fills gaps
JKM_FIELDS = {
    'licence_number': 'licence_number',
    'latitude': 'latitude',
    'longitude': 'longitude',
    'google_maps_url': 'maps_url',
    'email': 'email',
    'fax': 'fax',
    'validity_date': 'validity_date',
}

enrichments = []
field_stats = Counter()

for m in matches:
    slug = m['existing_slug']
    if not slug or slug not in ex_by_slug:
        continue
    ex = ex_by_slug[slug]

    # Find the JKM record — match by name first
    jkm_candidates = jkm_by_name.get(m['jkm_name'], [])
    if not jkm_candidates:
        continue
    j = jkm_candidates[0]  # take first if multiple

    updates = {}
    for sheet_col, jkm_col in JKM_FIELDS.items():
        ex_val = (ex.get(sheet_col, '') or '').strip()
        jkm_val = (j.get(jkm_col, '') or '').strip()
        if not jkm_val:
            continue

        # licence_number: only fill if existing is empty
        if sheet_col == 'licence_number':
            if not ex_val:
                updates[sheet_col] = {'old': ex_val, 'new': jkm_val, 'reason': 'fill_empty'}
                field_stats['licence_number_fill'] += 1
            elif ex_val != jkm_val:
                updates[sheet_col] = {'old': ex_val, 'new': jkm_val, 'reason': 'jkm_authoritative'}
                field_stats['licence_number_replace'] += 1

        # GPS: only fill if missing or zero
        elif sheet_col in ('latitude', 'longitude'):
            try:
                if not ex_val or float(ex_val) == 0:
                    updates[sheet_col] = {'old': ex_val, 'new': jkm_val, 'reason': 'fill_empty'}
                    field_stats[f'{sheet_col}_fill'] += 1
            except ValueError:
                updates[sheet_col] = {'old': ex_val, 'new': jkm_val, 'reason': 'fix_invalid'}
                field_stats[f'{sheet_col}_fix'] += 1

        # google_maps_url: only fill if missing
        elif sheet_col == 'google_maps_url':
            if not ex_val:
                updates[sheet_col] = {'old': ex_val, 'new': jkm_val, 'reason': 'fill_empty'}
                field_stats['google_maps_url_fill'] += 1

        # email/fax: only fill if missing
        elif sheet_col in ('email', 'fax'):
            if not ex_val and jkm_val:
                updates[sheet_col] = {'old': ex_val, 'new': jkm_val, 'reason': 'fill_empty'}
                field_stats[f'{sheet_col}_fill'] += 1

        # validity_date: always add (new field)
        elif sheet_col == 'validity_date':
            if not ex_val:
                updates[sheet_col] = {'old': ex_val, 'new': jkm_val, 'reason': 'fill_empty'}
                field_stats['validity_date_fill'] += 1

    if updates:
        enrichments.append({
            'slug': slug,
            'title': ex.get('title'),
            'jkm_name': m['jkm_name'],
            'confidence': m['confidence'],
            'updates': updates,
        })

print(f"📊 Enrichment summary across {len(enrichments)} facilities:\n")
for field, count in sorted(field_stats.items(), key=lambda x: -x[1]):
    print(f"   {field:30} {count:4}")

# Save proposed enrichments
with open(f'{OUT_DIR}/enrichment_proposed.json', 'w') as f:
    json.dump(enrichments, f, indent=2, ensure_ascii=False)

# Also a flat CSV for spreadsheet-style review
csv_rows = []
for e in enrichments:
    for col, change in e['updates'].items():
        csv_rows.append({
            'slug': e['slug'],
            'title': e['title'],
            'field': col,
            'current_value': change['old'],
            'jkm_value': change['new'],
            'reason': change['reason'],
            'confidence': e['confidence'],
        })

with open(f'{OUT_DIR}/enrichment_proposed.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['slug','title','field','current_value','jkm_value','reason','confidence'])
    writer.writeheader()
    writer.writerows(csv_rows)

print(f"\n💾 Saved:")
print(f"   - {OUT_DIR}/enrichment_proposed.json ({len(enrichments)} facilities)")
print(f"   - {OUT_DIR}/enrichment_proposed.csv ({len(csv_rows)} field changes)")

# Show samples
print(f"\n📋 Sample changes:")
for e in enrichments[:3]:
    print(f"\n  {e['title']}  [{e['confidence']}]")
    for col, change in e['updates'].items():
        old = change['old'][:40] if change['old'] else '(empty)'
        new = change['new'][:40]
        print(f"    {col:20}: {old:40} → {new}")
