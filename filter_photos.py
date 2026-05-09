import csv, json

cls = json.load(open('photo_classification.json', encoding='utf-8'))
photo_map = json.load(open('photo_map.json', encoding='utf-8'))
url_to_status = {url: cls.get(fn, 'KEEP') for url, fn in photo_map.items()}

rows = list(csv.DictReader(open('sheet_with_photos.csv', encoding='utf-8')))
data = json.load(open('photos_results.json', encoding='utf-8'))
by_url = {d.get('inputStartUrl', ''): d for d in data}

removed_count = 0
facilities_now_empty = 0
for r in rows:
    gmap = r.get('google_maps_url','').strip()
    d = by_url.get(gmap)
    if not d:
        continue
    raw = d.get('imageUrls') or []
    real = [u for u in raw if 'googleusercontent' in u]
    if not real:
        continue
    kept = [u for u in real if url_to_status.get(u, 'KEEP') == 'KEEP']
    removed_count += len(real) - len(kept)
    if kept:
        r['hero_image'] = kept[0]
        r['photos'] = '|'.join(kept)
        r['photo_count'] = str(len(kept))
    else:
        r['hero_image'] = ''
        r['photos'] = ''
        r['photo_count'] = '0'
        facilities_now_empty += 1

fieldnames = list(rows[0].keys())
with open('sheet_filtered_photos.csv','w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    for r in rows:
        w.writerow(r)

def count(c):
    return sum(1 for r in rows if r.get(c,'').strip())
total_kept = sum(int(r['photo_count']) for r in rows if r.get('photo_count','').strip().isdigit())
print(f'photos removed for privacy: {removed_count}')
print(f'photos kept (across all facilities): {total_kept}')
print(f'facilities with hero_image: {count("hero_image")}')
print(f'facilities now with no clean photos: {facilities_now_empty}')
print('Wrote sheet_filtered_photos.csv')
