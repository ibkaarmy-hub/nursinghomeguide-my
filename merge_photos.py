import csv, json

rows = list(csv.DictReader(open('sheet_final.csv', encoding='utf-8')))
data = json.load(open('photos_results.json', encoding='utf-8'))
by_url = {d.get('inputStartUrl', ''): d for d in data}

def filter_imgs(urls):
    real = [u for u in urls if 'googleusercontent' in u]
    sv = [u for u in urls if 'streetview' in u]
    return real if real else sv  # use streetview only if no real photo

if 'hero_image' not in rows[0]:
    for r in rows:
        r['hero_image'] = ''
        r['photos'] = ''
        r['photo_count'] = ''

updated = 0
for r in rows:
    gmap = r.get('google_maps_url','').strip()
    d = by_url.get(gmap)
    if not d:
        continue
    imgs = filter_imgs(d.get('imageUrls') or [])
    if not imgs:
        continue
    r['hero_image'] = imgs[0]
    r['photos'] = '|'.join(imgs)
    r['photo_count'] = str(len(imgs))
    updated += 1

fieldnames = list(rows[0].keys())
with open('sheet_with_photos.csv','w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    for r in rows:
        w.writerow(r)

def count(c):
    return sum(1 for r in rows if r.get(c,'').strip())
print(f'Updated rows: {updated}/{len(rows)}')
print(f'  hero_image filled: {count("hero_image")}')
print(f'  photos filled:     {count("photos")}')
total_photos = sum(int(r['photo_count']) for r in rows if r.get('photo_count','').strip())
print(f'  total photos:      {total_photos}')
print('Wrote sheet_with_photos.csv')
