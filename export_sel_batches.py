"""Export Selangor facilities needing editorials, sorted by priority,
split into batches for parallel research."""
import urllib.request, csv, io, json, math

CSV_URL = 'https://docs.google.com/spreadsheets/d/1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk/export?format=csv&gid=292378871'
TOP_N = 50  # process top 50 by priority
BATCH_SIZE = 10

def parse_int(x):
    try: return int(str(x).replace(',','').strip() or 0)
    except: return 0
def parse_float(x):
    try: return float(str(x).strip() or 0)
    except: return 0

data = urllib.request.urlopen(CSV_URL).read().decode('utf-8')
reader = list(csv.DictReader(io.StringIO(data)))

targets = []
for idx, r in enumerate(reader, start=2):
    if r.get('state','').strip() != 'Selangor':
        continue
    if r.get('status','').strip() != '':
        continue
    ed = (r.get('editorial_summary','') or '').strip()
    word_count = len(ed.split())
    if word_count >= 50:
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
        '_priority': (parse_int(r.get('review_count')), parse_float(r.get('rating')),
                      1 if (r.get('website') or '').strip() else 0),
    })

# Sort by review count desc, rating desc, has-website desc
targets.sort(key=lambda x: x['_priority'], reverse=True)

print(f'Total Selangor facilities needing editorials: {len(targets)}')
print(f'Processing top {TOP_N} by priority...')

# Strip private _priority field before saving
top = targets[:TOP_N]
for t in top: del t['_priority']

n_batches = math.ceil(len(top) / BATCH_SIZE)
for i in range(n_batches):
    chunk = top[i*BATCH_SIZE:(i+1)*BATCH_SIZE]
    fname = f'sel_batch_{i+1}.json'
    with open(fname, 'w', encoding='utf-8') as f:
        json.dump(chunk, f, ensure_ascii=False, indent=2)
    print(f'  {fname}: {len(chunk)} facilities (top review counts: {[c["review_count"] for c in chunk[:3]]})')

# Save remaining list for next session
remaining = targets[TOP_N:]
for t in remaining:
    if '_priority' in t: del t['_priority']
with open('sel_remaining_for_later.json','w',encoding='utf-8') as f:
    json.dump(remaining, f, ensure_ascii=False, indent=2)
print(f'\\nRemaining {len(remaining)} saved to sel_remaining_for_later.json (next session)')
