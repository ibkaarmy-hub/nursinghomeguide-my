import csv, json, re

rows = list(csv.DictReader(open('sheet.csv', encoding='utf-8')))
data = json.load(open('apify_results.json', encoding='utf-8'))

# index Apify items by inputStartUrl
by_url = {d.get('inputStartUrl', ''): d for d in data}

def fmt_hours(oh):
    if not oh:
        return ''
    return '; '.join(f"{e['day']}: {e['hours']}" for e in oh)

def get_wheelchair(d):
    info = d.get('additionalInfo') or {}
    acc = info.get('Accessibility') or []
    for entry in acc:
        if 'Wheelchair accessible entrance' in entry:
            return 'Yes' if entry['Wheelchair accessible entrance'] else 'No'
    return ''

def get_parking(d):
    info = d.get('additionalInfo') or {}
    pk = info.get('Parking') or []
    items = []
    for entry in pk:
        for k, v in entry.items():
            if v:
                items.append(k)
    return ', '.join(items)

updated = 0
for r in rows:
    gmap = r.get('google_maps_url', '').strip()
    if not gmap or gmap not in by_url:
        continue
    d = by_url[gmap]
    # Only fill if existing is empty, except for these always-overwrite high-confidence fields
    def fill(col, val, overwrite=False):
        if val is None or val == '':
            return
        cur = r.get(col, '').strip()
        if overwrite or not cur:
            r[col] = str(val)

    fill('phone', d.get('phoneUnformatted') or d.get('phone'))
    fill('website', d.get('website'))
    fill('rating', d.get('totalScore'))
    fill('review_count', d.get('reviewsCount'))
    loc = d.get('location') or {}
    fill('latitude', loc.get('lat'))
    fill('longitude', loc.get('lng'))
    fill('area', d.get('city'))
    fill('wheelchair', get_wheelchair(d))
    fill('visiting_hours', fmt_hours(d.get('openingHours')))
    fill('parking', get_parking(d))
    updated += 1

# write merged CSV preserving column order
fieldnames = list(rows[0].keys())
with open('sheet_merged.csv', 'w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    for r in rows:
        w.writerow(r)

# stats: how many rows now have each key field filled
def count(col):
    return sum(1 for r in rows if r.get(col, '').strip())

print(f'Updated rows: {updated}/{len(rows)}')
print('Post-merge fill counts:')
for c in ['phone', 'website', 'rating', 'review_count', 'latitude', 'longitude', 'area', 'wheelchair', 'visiting_hours', 'parking']:
    print(f'  {count(c):3}/{len(rows)}  {c}')
print('Wrote sheet_merged.csv')
