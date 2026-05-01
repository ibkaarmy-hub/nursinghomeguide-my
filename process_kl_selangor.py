"""
Process KL/Selangor Apify results → clean, dedupe, slug, and upload to Google Sheet.
"""
import sys, io, json, re, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE     = 'token_sheets.json'
SCOPES         = ['https://www.googleapis.com/auth/spreadsheets']

creds   = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
service = build('sheets', 'v4', credentials=creds)
ss      = service.spreadsheets()

# ── Load existing slugs to avoid duplicates ──────────────────────────────────
existing = ss.values().get(
    spreadsheetId=SPREADSHEET_ID,
    range="'google-sheets-facilities.csv'"
).execute().get('values', [])
headers      = existing[0]
existing_slugs = set(r[headers.index('slug')] for r in existing[1:] if len(r) > headers.index('slug'))
existing_titles= set(r[0].lower().strip() for r in existing[1:])
print(f"Existing slugs: {len(existing_slugs)}")

# ── Load raw Apify results ────────────────────────────────────────────────────
with open('kl_selangor_raw.json', encoding='utf-8') as f:
    raw = json.load(f)

# ── Helper: assign state ──────────────────────────────────────────────────────
def assign_state(x):
    addr   = (x.get('address') or '').lower()
    city   = (x.get('city') or '').lower()
    state_ = (x.get('state') or '').lower()
    search = (x.get('searchString') or '').lower()
    text   = addr + ' ' + city + ' ' + state_
    country= (x.get('countryCode') or '').upper()

    # Drop non-Malaysian
    if country and country != 'MY':
        return None

    sel_terms = ['selangor','petaling jaya',' pj ','shah alam','subang',
                 'klang','kajang','rawang','sepang','gombak','ampang jaya',
                 'seri kembangan','semenyih','sungai buloh','batu caves',
                 'balakong','puchong, s','kapar','kuala selangor']
    kl_terms  = ['kuala lumpur','wilayah persekutuan','bangsar','cheras',
                 'kepong','setapak','wangsa maju','titiwangsa','six mile',
                 'jalan ipoh','taman desa','taman p ramlee','pandan perdana']

    for t in sel_terms:
        if t in text or t in search: return 'Selangor'
    for t in kl_terms:
        if t in text or t in search: return 'Kuala Lumpur'

    # Fallback: if "KL" in search → KL, else Selangor
    if 'kuala lumpur' in search or ' kl' in search: return 'Kuala Lumpur'
    return 'Selangor'

# ── Helper: is nursing home ───────────────────────────────────────────────────
def is_nh(x):
    text = ' '.join([
        x.get('title') or '', x.get('categoryName') or '',
        ' '.join(x.get('categories') or []),
        x.get('description') or ''
    ]).lower()
    nh_terms = ['nursing','care centre','care center','elderly','old folk',
                'warga emas','jagaan','penjagaan','senior living',
                'assisted living','eldercare','retirement','hospice',
                'rehabilitation','老人','疗养','安老','乐龄','oku']
    exclude  = ['hospital','clinic','pharmacy','hotel','school','restaurant',
                'grocery','beauty','spa','gym','hardware','insurance','bank']
    if any(e in text for e in exclude): return False
    return any(t in text for t in nh_terms)

# ── Helper: slugify ───────────────────────────────────────────────────────────
def slugify(s):
    s = s.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_-]+', '-', s)
    s = re.sub(r'^-+|-+$', '', s)
    # Remove common suffixes for cleaner slugs
    for suffix in ['-sdn-bhd','-plt','-bhd']:
        if s.endswith(suffix):
            s = s[:-len(suffix)]
    return s[:80]  # max 80 chars

def make_unique_slug(base, used):
    slug = base
    i = 2
    while slug in used:
        slug = f"{base}-{i}"
        i += 1
    return slug

# ── Filter and deduplicate ───────────────────────────────────────────────────
seen_place_ids = set()
seen_titles    = set()
clean = []

for x in raw:
    # Skip non-NH
    if not is_nh(x): continue

    # Skip permanently closed
    if x.get('permanentlyClosed') or x.get('temporarilyClosed'): continue

    # Assign state (None = non-Malaysian, skip)
    state = assign_state(x)
    if state is None: continue

    title = (x.get('title') or '').strip()
    if not title: continue

    # Deduplicate by placeId
    pid = x.get('placeId','')
    if pid and pid in seen_place_ids: continue
    if pid: seen_place_ids.add(pid)

    # Deduplicate by normalised title
    title_norm = re.sub(r'\s+', ' ', title.lower().strip())
    if title_norm in seen_titles: continue
    seen_titles.add(title_norm)

    # Skip if title already in sheet (case-insensitive)
    if title.lower().strip() in existing_titles: continue

    x['_state'] = state
    clean.append(x)

print(f"Clean, unique, new: {len(clean)}")
kl_n  = sum(1 for x in clean if x['_state'] == 'Kuala Lumpur')
sel_n = sum(1 for x in clean if x['_state'] == 'Selangor')
print(f"  KL: {kl_n}  Selangor: {sel_n}")

# ── Build sheet rows ──────────────────────────────────────────────────────────
used_slugs = set(existing_slugs)
new_rows   = []

def pick(x, *keys, default=''):
    for k in keys:
        v = x.get(k)
        if v: return str(v).strip()
    return default

def get_website(x):
    # webResults is a list of {url, title, ...}
    wr = x.get('webResults') or []
    for w in wr:
        url = w.get('url','')
        if url and 'google.com/maps' not in url and 'facebook.com' not in url.lower():
            return url
    return ''

def get_facebook(x):
    wr = x.get('webResults') or []
    for w in wr:
        url = w.get('url','')
        if 'facebook.com' in url.lower():
            return url
    return ''

def get_photos(x):
    urls = x.get('imageUrls') or []
    return '|'.join(urls[:10])

def get_hero(x):
    urls = x.get('imageUrls') or []
    return urls[0] if urls else (x.get('imageUrl') or '')

def get_area(x):
    # Prefer neighborhood > city
    nb = (x.get('neighborhood') or '').strip()
    ci = (x.get('city') or '').strip()
    # Clean up area
    if nb and nb not in ('Kuala Lumpur','Selangor','Malaysia'): return nb
    if ci and ci not in ('Kuala Lumpur','Selangor','Malaysia'): return ci
    return x['_state']

def get_address(x):
    return (x.get('address') or x.get('street') or '').strip()

# Map headers to column indices
h = {v: i for i, v in enumerate(headers)}

for x in clean:
    title  = (x.get('title') or '').strip()
    slug   = make_unique_slug(slugify(title), used_slugs)
    used_slugs.add(slug)

    rating  = str(x.get('totalScore') or '')
    reviews = str(x.get('reviewsCount') or '')
    phone   = pick(x, 'phone', 'phoneUnformatted')
    website = get_website(x)
    fb      = get_facebook(x)
    lat     = str((x.get('location') or {}).get('lat',''))
    lng     = str((x.get('location') or {}).get('lng',''))
    maps_url= x.get('url','')
    area    = get_area(x)
    state   = x['_state']
    hero    = get_hero(x)
    photos  = get_photos(x)
    photo_n = str(len((x.get('imageUrls') or [])))
    addr    = get_address(x)
    cats    = ', '.join((x.get('categories') or [])[:3])

    # Build a row matching the sheet column order
    row = [''] * len(headers)
    row[h['title']]        = title
    row[h['slug']]         = slug
    row[h['url']]          = f'/facilities/{slug}'
    row[h['area']]         = area
    row[h['phone']]        = phone
    row[h['website']]      = website
    row[h['facebook']]     = fb if 'facebook' in fb else ''
    row[h['rating']]       = rating
    row[h['review_count']] = reviews
    row[h['latitude']]     = lat
    row[h['longitude']]    = lng
    row[h['google_maps_url']] = maps_url
    row[h['hero_image']]   = hero
    row[h['photos']]       = photos
    row[h['photo_count']]  = photo_n
    row[h['care_types']]   = cats
    row[h['last_updated']] = '2026-05-01'
    # pricing_display: default "Call for pricing" until enriched
    row[h['pricing_display']] = 'Call for pricing'
    # state column (last, BC = index 54)
    if len(row) > 54:
        row[54] = state
    else:
        row.append(state)

    new_rows.append(row)

print(f"\nRows to upload: {len(new_rows)}")

# ── Preview first 5 ───────────────────────────────────────────────────────────
print("\nPreview (title | slug | area | state | rating):")
for r in new_rows[:10]:
    print(f"  {r[0][:50]:50s} | {r[1][:35]:35s} | {r[3]:20s} | {r[54] if len(r)>54 else '?'} | ★{r[15]}")

# ── Upload ────────────────────────────────────────────────────────────────────
if not new_rows:
    print("Nothing to upload.")
    sys.exit(0)

BATCH = 50
total_uploaded = 0
for i in range(0, len(new_rows), BATCH):
    chunk = new_rows[i:i+BATCH]
    ss.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range="'google-sheets-facilities.csv'",
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body={'values': chunk}
    ).execute()
    total_uploaded += len(chunk)
    print(f"  Uploaded batch {i//BATCH+1}: {len(chunk)} rows (total {total_uploaded})")
    time.sleep(1)

print(f"\n✅ Done — {total_uploaded} new KL/Selangor facilities added to sheet")

# ── Save slug list for editorial work ────────────────────────────────────────
with open('kl_selangor_slugs.json', 'w', encoding='utf-8') as f:
    json.dump([{'slug': r[h['slug']], 'title': r[0], 'area': r[3], 'state': r[54] if len(r)>54 else r[-1],
                'website': r[h['website']], 'rating': r[h['rating']], 'reviews': r[h['review_count']]}
               for r in new_rows], f, indent=2, ensure_ascii=False)
print("Slug list saved to kl_selangor_slugs.json")
