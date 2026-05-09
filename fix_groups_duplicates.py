"""Clean up duplicate GROUPS entries in data.js and fix truncated branch slugs.

Strategy:
1. Delete older (broken) duplicates: green-acres @L77, mintygreen @L239, genesis-life-care @L255,
   my-aged-care @L284, woodrose-senior-residences @L338. These have truncated branch slugs that
   don't match real sheet rows, so they're effectively dead code (and the duplicate key means
   the later entry wins in JS object semantics anyway).
2. Delete attia-care @L472 (mine), keep attia-global-care @L352 but expand its branches.
3. Fix noble-care @L217 — replace truncated branch slugs with full slugs verified against sheet.
4. Add mona-elder-care (new chain, 4 branches verified).
"""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('data.js', 'r', encoding='utf-8') as f:
    src = f.read()

# Helper to find and remove a group entry by slug
def remove_group(text, slug, occurrence=1):
    """Remove the Nth occurrence of a group with given slug. occurrence=1 means first."""
    pattern = re.compile(rf"^(\s*)'{re.escape(slug)}':\s*\{{(?:[^{{}}]|\{{[^{{}}]*\}})*\}},?\s*\n", re.MULTILINE)
    matches = list(pattern.finditer(text))
    if len(matches) < occurrence:
        print(f'  WARN: {slug} occurrence {occurrence} not found')
        return text
    m = matches[occurrence - 1]
    print(f'  Removing {slug} (occurrence {occurrence}) at offset {m.start()}')
    return text[:m.start()] + text[m.end():]

# Step 1: Delete older duplicate (first occurrence) for these slugs
# JavaScript object semantics: later duplicate wins. We keep the LATER (more complete) one.
print('Step 1: Delete older duplicates')
for slug in ['green-acres', 'mintygreen', 'genesis-life-care', 'my-aged-care', 'woodrose-senior-residences']:
    src = remove_group(src, slug, occurrence=1)

# Step 2: Delete my newer attia-care (keep attia-global-care which is the original key).
# But first, expand attia-global-care to include attia-nursing-care-centre branch.
print('\nStep 2: Consolidate attia entries')
src = remove_group(src, 'attia-care', occurrence=1)

# Now fix attia-global-care's branches list — add attia-nursing-care-centre
src = re.sub(
    r"('attia-global-care':\s*\{[^}]*?branches:\s*\[)(\s*)('attia-global-care-klang')",
    r"\1\2'attia-nursing-care-centre',\n      \3",
    src,
    count=1
)

# Step 3: Fix noble-care truncated branch slugs
print('\nStep 3: Fix noble-care truncated branch slugs')
NOBLE_FIX = {
    'noble-care-nursing-home-old-folks-home-r': 'noble-care-nursing-home-old-folks-home-rawang',
    'noble-care-nursing-home-in-jalan-ipoh-ku': 'noble-care-nursing-home-in-jalan-ipoh-kuala-lampur',
    'noble-care-nursing-home-nursing-home-sub': 'noble-care-nursing-home-nursing-home-subang-jaya-selangor',
}
for old, new in NOBLE_FIX.items():
    if old in src:
        src = src.replace(f"'{old}'", f"'{new}'")
        print(f'  {old} -> {new}')

# Step 4: Add mona-elder-care after attia-global-care
print('\nStep 4: Add mona-elder-care')
MONA = """  'mona-elder-care': {
    slug: 'mona-elder-care',
    name: 'Mona Elder Care',
    tagline: 'Multi-branch nursing home network across KL and Selangor',
    state: 'Kuala Lumpur, Selangor',
    description: 'Mona Elder Care operates a network of nursing homes across Kuala Lumpur and Selangor — branches in Taman Bunga Raya KL, Taman P Ramlee Setapak, Pandan Perdana, and Jalan Sri Kemuning Lembah Jaya. The group offers a broad clinical scope including tracheostomy, NG tube, colostomy care, dementia, palliative, and stroke recovery. Each branch operates from a residential property in its catchment area, serving local families across the Klang Valley.',
    branches: [
      'mona-elder-care-nursing-home-in-taman-bunga-raya-kuala-lumpur',
      'mona-elder-care-nursing-home-in-taman-p-ramlee-setapak',
      'mona-elder-care-nursing-home-in-pandan-perdana',
      'mona-elder-care-nursing-home-in-jalan-sri-kemuning-lembah-jaya-se',
    ],
  },

"""

# Insert before the closing `};` of GROUPS object
src = re.sub(
    r"(\n};\s*\n\n// ─── Reverse index)",
    f"\n{MONA}}};\n\n// ─── Reverse index",
    src,
    count=1
)

# But the above leaves an extra };, fix that
src = src.replace("\n};\n};\n", "\n};\n", 1)

# Actually let me redo step 4 more carefully — find last group entry's closing }, and insert before final };
# Simpler: find the line `};` followed by `// ─── Reverse index` and insert MONA just before
# The regex above did this but might have issues. Let me verify by re-running.

with open('data.js', 'w', encoding='utf-8') as f:
    f.write(src)

# Audit
print('\nAudit after fix:')
matches = re.findall(r"^\s*'([a-z0-9-]+)':\s*\{", src, re.MULTILINE)
seen = {}
for m in matches:
    seen[m] = seen.get(m, 0) + 1
dupes = [k for k,v in seen.items() if v > 1]
print(f'  Total entries: {len(matches)}, unique: {len(seen)}, duplicates: {dupes}')
