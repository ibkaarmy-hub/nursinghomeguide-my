"""
Reusable operator-website scrape step.

Runs Apify's website-content-crawler (Playwright/Firefox — renders JavaScript)
over a facility operator's website and saves the cleaned page text to
_scrape_cache/<slug-or-domain>.json. The /nh-profiles editorial process reads
that cache to source services, branch lists, and other facts straight from the
operator's own site — without scraping live each time.

Usage:
    python scrape_website.py <url>                 # scrape one site
    python scrape_website.py <url> --slug <slug>   # name the cache file by slug
    python scrape_website.py --slug <slug>         # look the website up in the live sheet

Apify token comes from .env (APIFY_TOKEN) — never hard-coded. Cached runs are
skipped unless --force is passed.
"""
import os, sys, json, re, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(HERE, '.env')
CACHE_DIR = os.path.join(HERE, '_scrape_cache')
SHEET_CSV = ('https://docs.google.com/spreadsheets/d/'
             '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk/export?format=csv&gid=292378871')
ACTOR = 'apify~website-content-crawler'


def env(key):
    for line in open(ENV_PATH, encoding='utf-8'):
        if line.startswith(key + '='):
            return line.split('=', 1)[1].strip()
    raise RuntimeError(f'{key} missing from .env')


def domain_of(url):
    d = re.sub(r'^https?://', '', url.strip().lower()).split('/')[0]
    return re.sub(r'^www\.', '', d)


def website_for_slug(slug):
    import csv, io
    raw = urllib.request.urlopen(urllib.request.Request(
        SHEET_CSV, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30).read()
    for r in csv.DictReader(io.StringIO(raw.decode('utf-8'))):
        if (r.get('slug') or '').strip() == slug:
            return (r.get('website') or '').strip()
    raise RuntimeError(f'slug not found in sheet: {slug}')


def scrape(url, token, max_pages=25):
    """Run website-content-crawler synchronously, return list of page dicts."""
    body = {
        'startUrls': [{'url': url}],
        'crawlerType': 'playwright:firefox',   # renders JS
        'maxCrawlPages': max_pages,
        'maxCrawlDepth': 3,
        'saveMarkdown': True,
        'proxyConfiguration': {'useApifyProxy': True},
        'removeCookieWarnings': True,
    }
    api = (f'https://api.apify.com/v2/acts/{ACTOR}/run-sync-get-dataset-items'
           f'?token={urllib.parse.quote(token)}')
    req = urllib.request.Request(
        api, data=json.dumps(body).encode('utf-8'),
        headers={'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.load(r)


def main():
    args = sys.argv[1:]
    force = '--force' in args
    args = [a for a in args if a != '--force']
    slug = None
    if '--slug' in args:
        i = args.index('--slug')
        slug = args[i + 1]
        args = args[:i] + args[i + 2:]
    url = args[0] if args else None
    if not url and slug:
        url = website_for_slug(slug)
        print(f'  resolved {slug} -> {url}')
    if not url:
        print(__doc__)
        sys.exit(1)
    if not url.startswith('http'):
        url = 'https://' + url

    os.makedirs(CACHE_DIR, exist_ok=True)
    name = slug or domain_of(url)
    cache_path = os.path.join(CACHE_DIR, f'{name}.json')
    if os.path.exists(cache_path) and not force:
        print(f'  cached: {cache_path} (pass --force to re-scrape)')
        items = json.load(open(cache_path, encoding='utf-8'))['pages']
    else:
        print(f'  scraping {url} via Apify {ACTOR} ...')
        items = scrape(url, env('APIFY_TOKEN'))
        json.dump({'url': url, 'slug': slug, 'scraped_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
                   'pages': items}, open(cache_path, 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
        print(f'  saved {len(items)} pages -> {cache_path}')

    # human-readable summary
    print(f'\n=== {len(items)} pages from {url} ===')
    for p in items:
        text = (p.get('markdown') or p.get('text') or '').strip()
        print(f'\n--- {p.get("url", "?")}  ({len(text)} chars) ---')
        print(text[:1200])


if __name__ == '__main__':
    main()
