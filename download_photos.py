import json, os, urllib.request, hashlib, concurrent.futures as cf

urls = json.load(open('photo_urls.json', encoding='utf-8'))
os.makedirs('photos', exist_ok=True)

def fname(u):
    return hashlib.sha1(u.encode()).hexdigest()[:16] + '.jpg'

# Use medium res to save bandwidth: rewrite =w1920-h1080 -> =w800
def shrink(u):
    import re
    return re.sub(r'=w\d+-h\d+(-k-no)?$', '=w800', u)

def fetch(u):
    path = os.path.join('photos', fname(u))
    if os.path.exists(path):
        return path
    try:
        req = urllib.request.Request(shrink(u), headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as r:
            with open(path, 'wb') as f:
                f.write(r.read())
        return path
    except Exception as e:
        return f'ERROR:{e}'

with cf.ThreadPoolExecutor(max_workers=20) as ex:
    results = list(ex.map(fetch, urls))

ok = sum(1 for r in results if not r.startswith('ERROR'))
print(f'downloaded: {ok}/{len(urls)}')
mapping = {u: fname(u) for u in urls}
json.dump(mapping, open('photo_map.json','w', encoding='utf-8'))
print('wrote photo_map.json')
