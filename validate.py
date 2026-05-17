"""
Pre-push integrity validator for the Facilities sheet.

Fast (no API calls — just reads the published CSV), runs in seconds. Designed
to be the gate before any commit/push of data changes. Hard-fails (exit 1) on
the integrity violations that have repeatedly bitten this project:

  ERRORs (exit 1):
    * Duplicate slug across live rows  — site renders first match; the
      "wrong row wins" silent bug
    * Live row missing address but has a place_id  — the "column added,
      populate-step never wired" pattern
    * Live row with photos but no place_id  — wrong-facility photo
      bleed-through (place_id was cleared, photos weren't)
    * Invalid status value (anything other than '', unverified, removed)
    * Slug contains uppercase or spaces or non [a-z0-9-] characters
    * Empty title or empty slug on a non-blank row
    * google_maps_url present but malformed (no query_place_id=)

  WARNs (does not fail):
    * Live row missing state, area, phone, or editorial
    * Title and slug share fewer than 2 distinctive tokens (likely mis-sluggued)

Usage:
    python validate.py                # hits the live published CSV
    python validate.py --csv path.csv # validate a local snapshot
    python validate.py --strict       # promote all warnings to errors
"""
import sys, csv, io, re, urllib.request
from collections import Counter, defaultdict

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

LIVE_CSV = ('https://docs.google.com/spreadsheets/d/'
            '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk/export'
            '?format=csv&gid=292378871')

VALID_STATUS = {'', 'unverified', 'removed'}
SLUG_RE = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
TITLE_STOPWORDS = {
    'care', 'centre', 'center', 'home', 'homes', 'pusat', 'jagaan', 'sdn', 'bhd',
    'nursing', 'senior', 'elderly', 'elder', 'aged', 'orang', 'tua', 'warga', 'emas',
    'old', 'folks', 'folk', 'rumah', 'kebajikan', 'house', 'and', 'for', 'the', 'of',
    'a', 'an', 'in', 'at', 'by', 'pte', 'ltd', 'plt', 'enterprise', 'group', 'services',
    'service', 'aktiviti', 'pawe', 'malaysia', 'retirement', 'living', 'residence',
    'residences', 'cawangan', 'branch', 'no', 'sendirian', 'berhad',
    'persatuan', 'pertubuhan', 'limited', 'co', 'company',
}


def sig_tokens(s):
    return {t for t in re.split(r'[^a-z0-9]+', (s or '').lower())
            if len(t) >= 3 and t not in TITLE_STOPWORDS}


def main():
    args = sys.argv[1:]
    strict = '--strict' in args
    csv_path = None
    if '--csv' in args:
        csv_path = args[args.index('--csv') + 1]

    if csv_path:
        text = open(csv_path, encoding='utf-8').read()
    else:
        print(f'fetching live CSV ...', file=sys.stderr)
        text = urllib.request.urlopen(urllib.request.Request(
            LIVE_CSV, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30).read().decode('utf-8')

    rows = list(csv.DictReader(io.StringIO(text)))
    print(f'{len(rows)} rows loaded', file=sys.stderr)

    errors, warnings = [], []
    g = lambda r, k: (r.get(k) or '').strip()

    def has_place_id(r):
        return bool(re.search(r'query_place_id=([\w-]+)', g(r, 'google_maps_url')))

    live = [(i + 2, r) for i, r in enumerate(rows) if g(r, 'status') not in ('unverified', 'removed')]

    # ── status values ────────────────────────────────────────────────────────
    for rn, r in [(i + 2, r) for i, r in enumerate(rows)]:
        if g(r, 'status') not in VALID_STATUS:
            errors.append((rn, r.get('slug',''), f"invalid status {g(r,'status')!r} (allowed: {sorted(VALID_STATUS)})"))

    # ── empty title/slug on a non-blank row ─────────────────────────────────
    for rn, r in [(i + 2, r) for i, r in enumerate(rows)]:
        non_blank = any(g(r, k) for k in r.keys())
        if non_blank and (not g(r, 'title') or not g(r, 'slug')):
            errors.append((rn, g(r, 'slug') or '?', 'missing title or slug on a non-blank row'))

    # ── slug format ─────────────────────────────────────────────────────────
    for rn, r in live:
        s = g(r, 'slug')
        if s and not SLUG_RE.match(s):
            errors.append((rn, s, 'slug not in [a-z0-9-] (lowercase, dash-separated)'))

    # ── duplicate slugs across live rows ────────────────────────────────────
    slug_rows = defaultdict(list)
    for rn, r in live:
        s = g(r, 'slug')
        if s:
            slug_rows[s].append(rn)
    dup = {s: rs for s, rs in slug_rows.items() if len(rs) > 1}
    for s, rs in sorted(dup.items()):
        errors.append((rs[0], s, f'duplicate slug — also on rows {rs[1:]} (site renders first match silently)'))

    # ── google_maps_url format ──────────────────────────────────────────────
    for rn, r in live:
        u = g(r, 'google_maps_url')
        if u and 'query_place_id=' not in u:
            errors.append((rn, g(r, 'slug'), 'google_maps_url present but has no query_place_id='))

    # ── address present whenever a place_id exists ─────────────────────────
    for rn, r in live:
        if has_place_id(r) and not g(r, 'address'):
            errors.append((rn, g(r, 'slug'),
                           'live row has a place_id but no address (populate from Places formatted_address)'))

    # ── photos with no place_id  -> bleed-through risk ─────────────────────
    for rn, r in live:
        photos_present = bool(g(r, 'photos') or g(r, 'hero_image'))
        if photos_present and not has_place_id(r):
            errors.append((rn, g(r, 'slug'),
                           'live row has photos/hero_image but no place_id (likely wrong-facility bleed)'))

    # ── soft checks ──────────────────────────────────────────────────────────
    for rn, r in live:
        for col, label in [('state', 'state'), ('area', 'area'),
                           ('phone', 'phone'), ('editorial_summary', 'editorial')]:
            if not g(r, col):
                warnings.append((rn, g(r, 'slug'), f'missing {label}'))
        title_t, slug_t = sig_tokens(g(r, 'title')), sig_tokens(g(r, 'slug'))
        if title_t and len(title_t & slug_t) < 2 and len(title_t) >= 2:
            warnings.append((rn, g(r, 'slug'),
                             f'title/slug share < 2 distinctive tokens '
                             f'(title={sorted(title_t)} slug={sorted(slug_t)})'))

    # ── report ───────────────────────────────────────────────────────────────
    def report(label, items):
        print(f'\n=== {label}: {len(items)} ===')
        for rn, slug, msg in items[:200]:
            print(f'  row {rn:>4}  {slug:<55} {msg}')
        if len(items) > 200:
            print(f'  ... and {len(items) - 200} more')

    by_cat = Counter(msg.split('(')[0].split('—')[0].strip().split(' (')[0] for _, _, msg in errors)
    if errors:
        report('ERRORS', errors)
        print('\nerror categories:')
        for k, n in by_cat.most_common():
            print(f'  {n:>4}  {k}')
    if warnings:
        report('WARNINGS', warnings)

    if errors or (strict and warnings):
        print(f'\nFAIL: {len(errors)} error(s)' + (f' + {len(warnings)} warning(s) [--strict]' if strict else ''))
        sys.exit(1)
    if warnings:
        print(f'\nOK with {len(warnings)} warning(s) (run --strict to fail on warnings)')
    else:
        print('\nOK — all checks passed')


if __name__ == '__main__':
    main()
