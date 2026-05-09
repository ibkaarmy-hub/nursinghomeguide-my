"""Export the 56 KL facilities that have stub editorials needing replacement
with proper deep-research editorials. Splits them into N batches.
"""
import urllib.request, csv, io, json, math

CSV_URL = 'https://docs.google.com/spreadsheets/d/1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk/export?format=csv&gid=292378871'
N_BATCHES = 6  # ~9-10 facilities per batch

data = urllib.request.urlopen(CSV_URL).read().decode('utf-8')
reader = list(csv.DictReader(io.StringIO(data)))

# Stub editorials are the ones I just wrote — they all start with "<title> is" and contain
# "have not yet been verified". That signature distinguishes them from researched editorials.
STUB_SIG = 'have not yet been verified'

targets = []
for idx, r in enumerate(reader, start=2):
    if r.get('state','').strip() != 'Kuala Lumpur':
        continue
    if r.get('status','').strip() != '':
        continue
    ed = (r.get('editorial_summary','') or '').strip()
    if STUB_SIG not in ed:
        continue
    targets.append({
        'row_idx': idx,
        'slug': r.get('slug',''),
        'title': r.get('title',''),
        'area': r.get('area',''),
        'phone': r.get('phone',''),
        'website': r.get('website',''),
        'facebook': r.get('facebook',''),
        'whatsapp': r.get('whatsapp',''),
        'google_maps_url': r.get('google_maps_url',''),
        'care_types': r.get('care_types',''),
        'rating': r.get('rating',''),
        'review_count': r.get('review_count',''),
        'total_beds': r.get('total_beds',''),
        'religion': r.get('religion',''),
        'languages': r.get('languages',''),
    })

print(f'Exporting {len(targets)} facilities')
batch_size = math.ceil(len(targets) / N_BATCHES)
for i in range(N_BATCHES):
    chunk = targets[i*batch_size:(i+1)*batch_size]
    if not chunk:
        continue
    fname = f'kl_batch_{i+7}.json'
    with open(fname, 'w', encoding='utf-8') as f:
        json.dump(chunk, f, ensure_ascii=False, indent=2)
    print(f'  {fname}: {len(chunk)} facilities')
