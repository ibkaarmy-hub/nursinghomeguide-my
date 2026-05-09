"""Export the remaining 28 Johor + 3 KL facilities needing editorials.
Split into 4 batches of ~8 each. Sorted by review count desc."""
import urllib.request, csv, io, json, math, sys
sys.stdout.reconfigure(encoding='utf-8')

CSV_URL = 'https://docs.google.com/spreadsheets/d/1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk/export?format=csv&gid=292378871'

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
    if r.get('state','').strip() not in ('Johor','Kuala Lumpur'): continue
    if r.get('status','').strip() != '': continue
    ed = (r.get('editorial_summary','') or '').strip()
    if len(ed.split()) >= 50: continue
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
        'state': r.get('state',''),
        '_pri': (parse_int(r.get('review_count')), parse_float(r.get('rating'))),
    })

targets.sort(key=lambda x: x['_pri'], reverse=True)
for t in targets: del t['_pri']
print(f'Total to process: {len(targets)} ({sum(1 for t in targets if t["state"]=="Johor")} Johor + {sum(1 for t in targets if t["state"]=="Kuala Lumpur")} KL)')

BATCH_SIZE = 8
BATCH_START = 20
n_batches = math.ceil(len(targets) / BATCH_SIZE)
for i in range(n_batches):
    chunk = targets[i*BATCH_SIZE:(i+1)*BATCH_SIZE]
    fname = f'final_batch_{BATCH_START + i}.json'
    with open(fname, 'w', encoding='utf-8') as f:
        json.dump(chunk, f, ensure_ascii=False, indent=2)
    states = [c['state'][:3] for c in chunk]
    print(f'  {fname}: {len(chunk)} ({", ".join(states)})')
