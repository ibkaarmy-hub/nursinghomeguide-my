#!/usr/bin/env python3
"""
Integrate MOH Licensed Private Nursing Homes ("Rumah Jagaan Kejururawatan
Swasta Berlesen") with directory.

Source: https://docs.google.com/spreadsheets/d/1G31KErhNmxg6gVe8KFPCj1sLwvnCm9NJ6L752xhpri0/

These are MOH-regulated facilities under Akta 586 (Private Healthcare
Facilities Act) — distinct from JKM-licensed elderly care centres.
Stricter clinical requirements; usually have RN coverage.

Strategy:
1. Match 19 MOH NHs against existing 808 (name + state, with manual override)
2. For matches: add 'MOH NH 2026' to data source, fill bed count + address if missing
3. For non-matches: append as new facility, status=unverified, marked MOH-licensed

Usage:
  python3 integrate-moh-nh.py            # analysis only
  python3 integrate-moh-nh.py --apply    # apply to live sheet
"""
import argparse
import csv
import json
import os
import re
import sys
import urllib.parse
from difflib import SequenceMatcher

REPO = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REPO)
from importlib import import_module
sd = import_module('sheets-direct')

MOH_ID = "1G31KErhNmxg6gVe8KFPCj1sLwvnCm9NJ6L752xhpri0"
MOH_TAB = "Rumah Jagaan Kejururawatan Swasta Berlesen"

STATE_NORMALIZE = {
    'JOHOR': 'Johor', 'KEDAH': 'Kedah', 'MELAKA': 'Melaka',
    'NEGERI \nSEMBILAN': 'Negeri Sembilan', 'NEGERI SEMBILAN': 'Negeri Sembilan',
    'PAHANG': 'Pahang', 'PULAU \nPINANG': 'Penang', 'PULAU PINANG': 'Penang',
    'PERAK': 'Perak', 'SELANGOR': 'Selangor', 'SABAH': 'Sabah', 'SARAWAK': 'Sarawak',
    'W.P. \nKUALA LUMPUR': 'Kuala Lumpur', 'W.P. KUALA LUMPUR': 'Kuala Lumpur',
}


def normalize_name(s):
    s = (s or '').lower().strip()
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'[^\w\s]', '', s)
    for suf in ['sdn bhd', 'berhad', 'bhd', 'sdn', 'pusat penjagaan',
                'pusat jagaan', 'rumah jagaan', 'kejururawatan',
                'nursing home', 'nursing care centre', 'nursing care center',
                'nursing centre', 'medicare centre', 'centre', 'center',
                'home', 'plt', 'sdn']:
        s = s.replace(suf, ' ')
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def name_similarity(a, b):
    return SequenceMatcher(None, normalize_name(a), normalize_name(b)).ratio()


def fetch_moh():
    print("📥 Fetching MOH licensed nursing homes...")
    rng = urllib.parse.quote(f"'{MOH_TAB}'!A2:K", safe='')
    resp = sd.api_request('GET', f"/v4/spreadsheets/{MOH_ID}/values/{rng}")
    rows = resp.get('values', [])
    headers = rows[0]
    nhs = []
    for r in rows[1:]:
        padded = r + [''] * (len(headers) - len(r))
        d = dict(zip(headers, padded))
        if not d.get('NAMA_PENUH_FASILITI'):
            continue
        nhs.append({
            'name': d['NAMA_PENUH_FASILITI'].strip(),
            'state': STATE_NORMALIZE.get(d['NEGERI'].strip(), d['NEGERI'].strip()),
            'address': d.get('ALAMAT', '').strip(),
            'city': d['BANDAR'].strip().title(),
            'postcode': d['POSKOD'].strip(),
            'capacity': d.get('KAPASITI_KESELURUHAN', '').strip(),
            'beds': d.get('KATIL', '').strip(),
        })
    print(f"   ✅ {len(nhs)} licensed nursing homes")
    return nhs


# Manual overrides (MOH name → directory slug). For known matches the auto-matcher misses
# due to overly-aggressive name stripping or state mismatches.
MANUAL_MATCHES = {
    'ECON MEDICARE CENTRE AND NURSING HOME (PUSAT PENJAGAAN KEJURURAWATAN ECON)|Johor':
        'econ-medicare-centre-nursing-home-taman-perling-branch',
    'SEAVOY NURSING HOME SDN. BHD. (DESA MELAWATI)|Kuala Lumpur':
        'seavoy-nursing-home-desa-melawati',
}


def find_match(moh_nh, facilities):
    """Best match by name + state."""
    # Manual override
    key = f"{moh_nh['name']}|{moh_nh['state']}"
    if key in MANUAL_MATCHES:
        target_slug = MANUAL_MATCHES[key]
        for f in facilities:
            if f.get('slug') == target_slug:
                return f, 1.0

    candidates = []
    for f in facilities:
        # Allow slight cross-state slack for KL/Selangor (often confused due to suburbs)
        state_match = f.get('state','').strip() == moh_nh['state']
        if not state_match:
            continue
        score = name_similarity(moh_nh['name'], f.get('title',''))
        if score > 0.55:
            candidates.append((score, f))
    candidates.sort(key=lambda x: -x[0])
    return (candidates[0][1], candidates[0][0]) if candidates else (None, 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()

    nhs = fetch_moh()

    # Fetch live sheet
    print(f"\n📖 Fetching directory facilities...")
    rng = urllib.parse.quote(f"'google-sheets-facilities.csv'!A1:CC", safe='')
    resp = sd.api_request('GET', f"/v4/spreadsheets/{sd.SHEET_ID}/values/{rng}")
    rows = resp.get('values', [])
    sheet_headers = rows[0]
    facilities = [dict(zip(sheet_headers, r + [''] * (len(sheet_headers) - len(r)))) for r in rows[1:]]
    print(f"   ✅ {len(facilities)} facilities")

    print(f"\n🔍 Matching MOH NHs against directory...\n")

    matches = []
    new_entries = []

    for nh in nhs:
        match, score = find_match(nh, facilities)
        if match and score > 0.7:
            matches.append((nh, match, score))
        else:
            new_entries.append(nh)

    # Print loose candidates for review (0.55-0.7 score)
    print("🔎 Loose candidates (0.55-0.70) for review:")
    for nh in nhs:
        match, score = find_match(nh, facilities)
        if match and 0.55 < score <= 0.7:
            print(f"   [{score:.2f}] {nh['name'][:55]} ↔ {match['title'][:55]}")
    print()

    print(f"📊 Summary:")
    print(f"   ✅ Matched to existing:    {len(matches)}")
    print(f"   🆕 Not in directory:       {len(new_entries)}\n")

    if matches:
        print(f"\n✅ Matches (apply MOH NH license + bed count):\n")
        for nh, m, s in matches:
            beds_existing = m.get('total_beds','').strip()
            beds_moh = nh['beds']
            print(f"   [{s:.2f}] {nh['state']:>10}  {nh['name'][:55]}")
            print(f"            ↔ {m['title'][:55]}  (slug: {m['slug']})")
            print(f"            Beds: existing={beds_existing or '(empty)'}, MOH={beds_moh}")

    if new_entries:
        print(f"\n🆕 Not in directory — to add:\n")
        for nh in new_entries:
            print(f"   {nh['state']:>10}  {nh['name'][:55]}  ({nh['beds']} beds)")
            print(f"            {nh['city']} {nh['postcode']}")

    # Save analysis
    with open(os.path.join(REPO, 'moh-nh-matches.json'), 'w') as f:
        json.dump({
            'matches': [{'moh_nh': nh, 'match_slug': m['slug'], 'match_title': m['title'], 'score': round(s,3)}
                        for nh, m, s in matches],
            'new_entries': new_entries,
        }, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Saved analysis: moh-nh-matches.json")

    if not args.apply:
        print(f"\n💡 Run with --apply to:")
        print(f"   1. Tag {len(matches)} matched facilities as MOH NH-licensed")
        print(f"   2. Fill bed count + address for matched facilities (if missing)")
        print(f"   3. Append {len(new_entries)} new facilities (status=unverified)")
        return

    # Apply: enrich matches
    print(f"\n⚙️  Applying enrichments...")
    slug_idx = sheet_headers.index('slug')
    slug_to_row = {r[slug_idx]: i+2 for i, r in enumerate(rows[1:]) if len(r) > slug_idx}

    updates = []
    for nh, m, s in matches:
        slug = m['slug']
        if slug not in slug_to_row:
            continue
        row = slug_to_row[slug]

        # Tag as MOH NH-licensed
        if 'jkm_data_source' in sheet_headers:
            col = sd.col_letter(sheet_headers.index('jkm_data_source'))
            existing = m.get('jkm_data_source','').strip()
            tag = 'MOH NH 2026'
            if tag not in existing:
                new_val = f"{existing}; {tag}".strip('; ') if existing else tag
                updates.append((f"{col}{row}", new_val))

        # Bed count
        if nh['beds'] and 'total_beds' in sheet_headers and not m.get('total_beds','').strip():
            col = sd.col_letter(sheet_headers.index('total_beds'))
            updates.append((f"{col}{row}", nh['beds']))

        # Address
        if nh['address'] and 'address' in sheet_headers and not m.get('address','').strip():
            col = sd.col_letter(sheet_headers.index('address'))
            updates.append((f"{col}{row}", nh['address']))

    if updates:
        print(f"   {len(updates)} cells to update...")
        for i in range(0, len(updates), 100):
            batch = updates[i:i+100]
            data = [{'range': f"'{sd.TAB_NAME}'!{c}", 'values': [[v]]} for c, v in batch]
            resp = sd.api_request('POST',
                f"/v4/spreadsheets/{sd.SHEET_ID}/values:batchUpdate",
                body={'valueInputOption': 'RAW', 'data': data})
            n = resp.get('totalUpdatedCells', len(batch))
            print(f"   Batch {i//100 + 1}: {n} cells")
        print(f"   ✅ {len(updates)} cells across {len(matches)} matched facilities")

    # Append new MOH NHs
    if new_entries:
        print(f"\n   Appending {len(new_entries)} new MOH-licensed nursing homes...")
        new_rows = []
        for nh in new_entries:
            row = [''] * len(sheet_headers)
            slug = re.sub(r'[^\w\s-]', '', nh['name'].lower())
            slug = re.sub(r'\s+', '-', slug.strip())[:60]

            def setval(col, val):
                if col in sheet_headers:
                    row[sheet_headers.index(col)] = val

            setval('title', nh['name'])
            setval('slug', slug)
            setval('state', nh['state'])
            setval('area', nh['city'])
            setval('address', nh['address'])
            setval('care_types', 'Nursing Home')
            setval('care_category', 'Nursing Home')
            setval('care_nursing', 'yes')
            setval('total_beds', nh['beds'])
            setval('status', 'unverified')
            setval('jkm_data_source', 'MOH NH 2026')
            setval('last_updated', '2026-05-07')
            new_rows.append(row)

        rng_append = urllib.parse.quote(f"'{sd.TAB_NAME}'!A:A", safe='')
        resp = sd.api_request('POST',
            f"/v4/spreadsheets/{sd.SHEET_ID}/values/{rng_append}:append?valueInputOption=RAW&insertDataOption=INSERT_ROWS",
            body={'values': new_rows})
        n = resp.get('updates',{}).get('updatedRows', len(new_rows))
        print(f"   ✅ {n} new MOH-licensed nursing homes appended (status=unverified)")

    print(f"\n✅ MOH NH integration complete!")


if __name__ == '__main__':
    main()
