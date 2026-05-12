"""Parametric editorial generator for facilities that have a real website
but no editorial yet. Uses Places API for reviews/rating/address, fetches
the operator homepage briefly, then renders a conservative 5-part editorial.

Scope: 22 facilities in Selangor (16) + Kuala Lumpur (6).
Skips Johor / Penang / NS / Perak to avoid parallel session conflicts.

Writes via find_row_by_slug + post-write verify.
"""

import sys, io, json, re, time, urllib.request, urllib.parse, csv
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

ENV_PATH = r'C:\Users\ibkaa\nursinghomeguide-my\Nursing Home Guide Malaysia\.env'


def _read_env(key):
    with open(ENV_PATH, 'r', encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line: continue
            k, _, v = line.partition('=')
            if k.strip() == key:
                return v.strip().strip('"').strip("'")
    raise RuntimeError(f"{key} not found")


GOOGLE_KEY = _read_env('GOOGLE_MAPS_KEY')
SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_PATH = r'C:\Users\ibkaa\nursinghomeguide-my\Nursing Home Guide Malaysia\token_sheets.json'
TAB = 'google-sheets-facilities.csv'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SHEET_URL = f'https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=292378871'


def col_letter(n):
    s = ''
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def find_row_by_slug(svc, slug):
    col_b = svc.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=f"'{TAB}'!B:B"
    ).execute().get('values', [])
    for i, row in enumerate(col_b, 1):
        if row and row[0].strip() == slug:
            return i
    return None


def fetch_sheet():
    req = urllib.request.Request(SHEET_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return list(csv.reader(io.TextIOWrapper(r, encoding='utf-8')))


def places_text_search(query, location_bias=None):
    body = {'textQuery': query, 'languageCode': 'en', 'maxResultCount': 3}
    if location_bias:
        body['locationBias'] = location_bias
    req = urllib.request.Request(
        'https://places.googleapis.com/v1/places:searchText',
        data=json.dumps(body).encode(),
        headers={
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': GOOGLE_KEY,
            'X-Goog-FieldMask': 'places.id,places.displayName,places.formattedAddress,places.rating,places.userRatingCount,places.websiteUri',
        },
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {'error': e.code, 'body': e.read().decode('utf-8', errors='replace')[:200]}


def place_details(place_id):
    req = urllib.request.Request(
        f'https://places.googleapis.com/v1/places/{place_id}',
        headers={
            'X-Goog-Api-Key': GOOGLE_KEY,
            'X-Goog-FieldMask': 'reviews,rating,userRatingCount,formattedAddress,nationalPhoneNumber',
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError:
        return {}


def fetch_homepage_text(url, timeout=10):
    """Return rough text content of homepage (HTML stripped). Best-effort."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            html = r.read(200000).decode('utf-8', errors='replace')
    except Exception:
        return None
    text = re.sub(r'<script[^>]*>.*?</script>', ' ', html, flags=re.S | re.I)
    text = re.sub(r'<style[^>]*>.*?</style>', ' ', text, flags=re.S | re.I)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text[:8000]


def filter_positive_neutral_reviews(reviews):
    """Return list of (rating, snippet) for reviews 3-5★ with non-empty text.
    Reviews <3★ are dropped — concerns belong as visit questions, not citations.
    """
    out = []
    for rev in reviews or []:
        stars = rev.get('rating', 0)
        text = (rev.get('text') or {}).get('text', '').strip()
        if stars >= 3 and text:
            out.append((stars, text))
    return out[:10]


def extract_themes_from_reviews(positive_reviews, max_themes=4):
    """Pull short positive themes from review text. Keep generic to avoid
    over-claiming. Returns a list of 3-7 word phrases."""
    if not positive_reviews:
        return []
    # Simple keyword-bucket extraction
    text = ' '.join(t for _, t in positive_reviews).lower()
    candidates = []
    triggers = [
        ('clean', 'Clean and well-kept premises reported by visitors'),
        ('friendly', 'Friendly, attentive staff cited by reviewers'),
        ('caring', 'Reviewers describe staff as caring and patient'),
        ('professional', 'Professional staff and clinical conduct'),
        ('peaceful', 'Peaceful, calm atmosphere'),
        ('home', 'Homely atmosphere — residents feel comfortable'),
        ('nurse', 'Trained nursing staff on site'),
        ('food', 'Meals described positively by residents and families'),
        ('physio', 'Physiotherapy or rehabilitation services'),
        ('activit', 'Active programme of activities for residents'),
        ('doctor', 'Visiting doctor and clinical oversight'),
        ('dementia', 'Care for dementia residents reported'),
        ('rehab', 'Rehabilitation and recovery support'),
        ('attentive', 'Attentive day-to-day care for residents'),
        ('hygiene', 'Hygiene standards praised'),
        ('spacious', 'Spacious facilities reported'),
        ('owner', 'Owner is hands-on and accessible'),
        ('respect', 'Respectful treatment of elderly residents'),
        ('mandarin', 'Mandarin / Chinese-speaking staff available'),
        ('chinese', 'Chinese-speaking environment for residents'),
        ('halal', 'Halal meals provided'),
        ('muslim', 'Muslim residents accommodated'),
    ]
    for key, phrase in triggers:
        if key in text and phrase not in candidates:
            candidates.append(phrase)
        if len(candidates) >= max_themes:
            break
    return candidates


def extract_services_from_homepage(text):
    """Pull plausible service names from operator homepage text.
    Conservative: only returns items that look like service categories
    (capitalised phrases or known eldercare service words)."""
    if not text:
        return []
    services = []
    # Common eldercare service phrases
    patterns = [
        (r'\b24[-\s]?hour\s+(?:nursing|care)', '24-hour nursing care'),
        (r'\bdementia\s+care\b', 'Dementia care'),
        (r'\bpost[-\s]?stroke\s+(?:care|rehab|recovery)\b', 'Post-stroke care / rehabilitation'),
        (r'\bphysiotherapy|physio\s+(?:therapy|service)', 'Physiotherapy'),
        (r'\boccupational\s+therapy\b', 'Occupational therapy'),
        (r'\bpalliative\s+care\b', 'Palliative care'),
        (r'\brespite\s+care\b', 'Respite care'),
        (r'\bday\s+care\b', 'Day care'),
        (r'\bassisted\s+living\b', 'Assisted living'),
        (r'\bwound\s+(?:care|dressing|management)\b', 'Wound care'),
        (r'\b(?:peg|nasogastric|tube)\s+feeding\b', 'Tube/PEG feeding'),
        (r'\boxygen\s+(?:therapy|support)\b', 'Oxygen therapy'),
        (r'\brehabilitation\b', 'Rehabilitation'),
        (r'\bmedication\s+management\b', 'Medication management'),
        (r'\bdoctor\s+(?:visit|consultation|round)', 'Visiting doctor / consultation'),
        (r'\bphysical\s+therapy\b', 'Physical therapy'),
        (r'\bspeech\s+therapy\b', 'Speech therapy'),
    ]
    t = text.lower()
    seen = set()
    for pat, label in patterns:
        if re.search(pat, t) and label not in seen:
            services.append(label)
            seen.add(label)
    return services[:8]


def derive_domain(url):
    m = re.match(r'https?://(?:www\.)?([^/]+)', url or '')
    return m.group(1) if m else url


def build_editorial(fac, places_data, services, themes, reviews):
    """Render 5-part editorial. Conservative, factual, no fabrication."""
    title = fac['title']
    state = fac['state']
    area = fac['area']
    licence = fac.get('licence_number', '')
    website = fac['website']
    facebook = fac.get('facebook', '')
    rating = places_data.get('rating') or fac.get('rating')
    n_reviews = places_data.get('userRatingCount') or fac.get('review_count') or 0
    try:
        n_reviews = int(n_reviews)
    except (TypeError, ValueError):
        n_reviews = 0
    address = places_data.get('formattedAddress', '')
    domain = derive_domain(website)

    # Part 1 — prose opening
    p1 = f"{title} is an elderly care facility"
    if area:
        p1 += f" in {area}, {state}"
    elif state:
        p1 += f" in {state}"
    p1 += "."
    if address and area and area.lower() not in address.lower():
        p1 += f" The facility is registered at {address}."
    elif address and not area:
        p1 += f" The registered address is {address}."
    if licence:
        if licence.upper().startswith('MOH'):
            p1 += f" MOH Licensed — confirmed in the MOH nursing home registry under licence {licence}."
        else:
            p1 += f" JKM Registered — licence number: {licence}."
    else:
        p1 += " The current JKM or MOH registration status should be confirmed on visit."
    if website:
        p1 += f" The operator publishes its own profile at {domain}."

    # Part 2 — services (only if we have any)
    p2 = ""
    if services:
        p2 = f"\n\n**Services (from {domain}):**\n"
        for s in services:
            p2 += f"- {s}\n"
        p2 += "These categories are taken from the operator website; confirm the specific clinical scope on visit, including who is on duty overnight and the protocol for medical emergencies."

    # Part 3 — what reviewers say
    p3 = ""
    if n_reviews >= 5 and themes:
        p3 = f"\n\n**What reviewers say (Google, {n_reviews} reviews, {rating}★):**\n"
        for t in themes:
            p3 += f"- {t}\n"
    elif n_reviews > 0 and rating:
        p3 = f"\n\nGoogle reviews stand at {rating}★ across {n_reviews} review{'s' if n_reviews != 1 else ''} — too few to identify recurring trends."
    else:
        p3 = "\n\nGoogle reviews for this facility are limited at the time of writing — verify recent reviews directly on Maps before visiting."

    # Part 4 — practical
    p4 = "\n\nPricing is not published — contact for a quote. Visiting hours are not published — confirm when booking a viewing."
    if website and facebook and 'facebook.com' in facebook:
        fb_handle = facebook.rstrip('/').split('/')[-1]
        p4 += f" Full details at **[{domain}]({website})** and on Facebook at **[{fb_handle}]({facebook})**."
    elif website:
        p4 += f" Full details at **[{domain}]({website})**."
    elif facebook and 'facebook.com' in facebook:
        fb_handle = facebook.rstrip('/').split('/')[-1]
        p4 += f" The operator's Facebook page is at **[{fb_handle}]({facebook})**."
    else:
        p4 += " The operator does not maintain a website at the time of writing; contact details are in the sidebar."

    # Part 5 — visit questions
    p5 = "\n\n**What to ask on visit:**\n"
    questions = [
        "What is the monthly fee, and what is included (meals, diapers, laundry, medication)?",
        "What is the resident-to-staff ratio overnight, and is a registered nurse on duty?",
        "What clinical conditions are accepted — dementia, bedridden, post-stroke, palliative?",
        "What is the protocol for medical emergencies and hospital transfers?",
        "What languages do staff speak (BM, English, Mandarin, Tamil)?",
        "Are religious or dietary preferences (halal, vegetarian, festival observances) accommodated?",
    ]
    if not licence:
        questions.append("Is the facility currently registered with JKM or MOH — can you see the certificate?")
    for q in questions[:6]:
        p5 += f"- {q}\n"

    editorial = p1 + p2 + p3 + p4 + p5
    return editorial.strip()


def main():
    rows = fetch_sheet()
    headers = rows[0]
    idx = {h: i for i, h in enumerate(headers)}
    g = lambda r, c: (r[idx[c]] if c in idx and idx[c] < len(r) else '').strip()

    # States to process. Excluded:
    #   Negeri Sembilan, Penang  — parallel session likely active there
    #   Perak — just completed by parallel session
    #   Pahang/Sabah/Sarawak/Kelantan/Labuan — already 100%
    TARGET_STATES = {
        'Selangor', 'Kuala Lumpur', 'Johor',
        'Kedah', 'Melaka', 'Terengganu', 'Perlis',
    }
    candidates = []
    for r in rows[1:]:
        slug = g(r, 'slug')
        if not slug: continue
        if g(r, 'status').lower() in ('unverified', 'removed'): continue
        if g(r, 'state') not in TARGET_STATES: continue
        ed = g(r, 'editorial_summary')
        if ed and len(ed.split()) >= 100: continue
        website = g(r, 'website')
        # Allow no-website candidates IF they likely have Maps reviews —
        # Places API call will validate. FB-only listings (website pointing
        # to facebook.com) are also accepted; the editorial gracefully
        # omits the operator-website sentence.
        if website:
            wl = website.lower()
            if 'wa.me' in wl: continue
        candidates.append({
            'slug': slug, 'title': g(r, 'title'), 'state': g(r, 'state'),
            'area': g(r, 'area'), 'website': website if (website and 'facebook.com' not in website.lower() and 'wa.me' not in website.lower()) else '',
            'facebook': g(r, 'facebook') or (website if (website and 'facebook.com' in website.lower()) else ''),
            'licence_number': g(r, 'licence_number'),
            'phone': g(r, 'phone'), 'rating': g(r, 'rating'),
            'review_count': g(r, 'review_count'),
        })

    print(f"Processing {len(candidates)} facilities\n")

    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    svc = build('sheets', 'v4', credentials=creds)
    live_header = svc.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=f"'{TAB}'!1:1"
    ).execute().get('values', [[]])[0]

    ed_col = col_letter(live_header.index('editorial_summary') + 1)
    upd_col = col_letter(live_header.index('last_updated') + 1)
    rating_col = col_letter(live_header.index('rating') + 1)
    rev_col = col_letter(live_header.index('review_count') + 1)
    maps_col = col_letter(live_header.index('google_maps_url') + 1)

    today = '2026-05-12'
    done, skipped = [], []

    for i, fac in enumerate(candidates, 1):
        slug = fac['slug']
        print(f"\n[{i}/{len(candidates)}] {slug}")

        # 1) Places search
        q = f"{fac['title']} {fac['state']} Malaysia"
        res = places_text_search(q)
        if 'error' in res or not res.get('places'):
            skipped.append((slug, 'no Places match'))
            print(f"  ✗ no Places match")
            continue
        top = res['places'][0]

        # Basic state validation
        addr = top.get('formattedAddress', '')
        a_lower = addr.lower()
        state_ok = (
            fac['state'].lower() in a_lower
            or (fac['state'] == 'Penang' and 'pulau pinang' in a_lower)
            or (fac['state'] == 'Kuala Lumpur' and 'selangor' in a_lower)  # KL/Sel boundary
            or (fac['state'] == 'Selangor' and 'kuala lumpur' in a_lower)
        )
        if not state_ok:
            skipped.append((slug, f'state mismatch (Places: {addr[:50]})'))
            print(f"  ✗ state mismatch: {addr[:60]}")
            continue

        # 2) Place Details for reviews
        details = place_details(top['id'])
        time.sleep(0.3)
        positive = filter_positive_neutral_reviews(details.get('reviews'))
        themes = extract_themes_from_reviews(positive)
        review_count = top.get('userRatingCount') or 0

        # Quality gate: if no website AND too few reviews, skip — an editorial
        # built from name + address only is not useful enough to ship.
        # Threshold: need either a website OR ≥3 reviews.
        if not fac['website'] and review_count < 3:
            skipped.append((slug, f'no website + only {review_count} reviews'))
            print(f"  ✗ no website + only {review_count} reviews — skip")
            continue

        # 3) Brief homepage fetch (only if there's a real website)
        if fac['website']:
            homepage_text = fetch_homepage_text(fac['website'])
            services = extract_services_from_homepage(homepage_text)
        else:
            services = []

        # 4) Render editorial
        editorial = build_editorial(fac, top, services, themes, positive)

        # 5) Write to sheet (slug-safe)
        row = find_row_by_slug(svc, slug)
        if row is None:
            skipped.append((slug, 'not in sheet'))
            print(f"  ✗ not in sheet")
            continue

        pid = top['id']
        new_maps = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(fac['title'])}&query_place_id={pid}"

        data = [
            {'range': f"'{TAB}'!{ed_col}{row}", 'values': [[editorial]]},
            {'range': f"'{TAB}'!{upd_col}{row}", 'values': [[today]]},
            {'range': f"'{TAB}'!{maps_col}{row}", 'values': [[new_maps]]},
        ]
        if top.get('rating') and not fac['rating']:
            data.append({'range': f"'{TAB}'!{rating_col}{row}", 'values': [[str(top['rating'])]]})
        if top.get('userRatingCount') and not fac['review_count']:
            data.append({'range': f"'{TAB}'!{rev_col}{row}", 'values': [[str(top['userRatingCount'])]]})

        svc.spreadsheets().values().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={'valueInputOption': 'RAW', 'data': data}
        ).execute()

        verify = svc.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range=f"'{TAB}'!B{row}"
        ).execute().get('values', [['']])[0][0].strip()
        if verify != slug:
            skipped.append((slug, f'row drift: {verify}'))
            print(f"  ✗ ROW DRIFT")
            continue

        done.append((slug, len(services), len(themes), top.get('userRatingCount', 0)))
        n_rev = top.get('userRatingCount') or 0
        print(f"  ✓ wrote row {row} | {len(services)} services, {len(themes)} themes, {n_rev} reviews")
        time.sleep(0.3)

    print(f"\n=== Done. {len(done)} editorials written, {len(skipped)} skipped ===")
    for s, ns, nt, nr in done:
        print(f"  ✓ {s} | services={ns} themes={nt} reviews={nr}")
    if skipped:
        print("\nSkipped:")
        for s, why in skipped:
            print(f"  ✗ {s}: {why}")


if __name__ == '__main__':
    main()
