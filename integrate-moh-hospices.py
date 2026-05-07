#!/usr/bin/env python3
"""
Integrate MOH Licensed Private Hospices ("Hospis Swasta Berlesen") with directory.

Source: https://docs.google.com/spreadsheets/d/1c9V9NsYVmAAAzThby9G_qRfEE8pBWARZrKHo8XxKmVM/

Strategy:
1. Match 23 hospices against existing 808 facilities (name + address + state)
2. For matches: enrich with `moh_hospice_licensed=yes`, `address`, palliative care flag
3. For non-matches: classify residential vs non-residential
   - Residential (with beds) → propose as new facilities
   - Service-only (no beds) → propose as new entries with care_category='Home Care' or skip

Usage:
  python3 integrate-moh-hospices.py            # analysis only
  python3 integrate-moh-hospices.py --apply    # apply matches to live sheet
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

MOH_ID = "1c9V9NsYVmAAAzThby9G_qRfEE8pBWARZrKHo8XxKmVM"
MOH_TAB = "Hospis Swasta Berlesen"

# State name normalization
STATE_NORMALIZE = {
    'JOHOR': 'Johor',
    'KEDAH': 'Kedah',
    'MELAKA': 'Melaka',
    'NEGERI \nSEMBILAN': 'Negeri Sembilan',
    'NEGERI SEMBILAN': 'Negeri Sembilan',
    'PAHANG': 'Pahang',
    'PULAU \nPINANG': 'Penang',
    'PULAU PINANG': 'Penang',
    'PERAK': 'Perak',
    'SELANGOR': 'Selangor',
    'SABAH': 'Sabah',
    'SARAWAK': 'Sarawak',
    'W.P. KUALA \nLUMPUR': 'Kuala Lumpur',
    'W.P. KUALA LUMPUR': 'Kuala Lumpur',
    'KUALA LUMPUR': 'Kuala Lumpur',
}


def normalize_name(s):
    """Lowercase, strip, collapse whitespace, remove common suffixes."""
    s = (s or '').lower().strip()
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'[^\w\s]', '', s)
    # Remove common Malay/English business suffixes
    for suf in ['sdn bhd', 'berhad', 'bhd', 'sdn', 'pertubuhan', 'persatuan',
                'association of', 'association', 'society', 'centre', 'center',
                'malaysia', 'pusat']:
        s = s.replace(suf, ' ')
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def name_similarity(a, b):
    return SequenceMatcher(None, normalize_name(a), normalize_name(b)).ratio()


def fetch_moh():
    print("📥 Fetching MOH hospices...")
    rng = urllib.parse.quote(f"'{MOH_TAB}'!A2:L", safe='')
    resp = sd.api_request('GET', f"/v4/spreadsheets/{MOH_ID}/values/{rng}")
    rows = resp.get('values', [])
    headers = rows[0]
    hospices = []
    for r in rows[1:]:
        padded = r + [''] * (len(headers) - len(r))
        d = dict(zip(headers, padded))
        if not d.get('NAMA_PENUH_FASILITI'):
            continue
        hospices.append({
            'name': d['NAMA_PENUH_FASILITI'].strip(),
            'state': STATE_NORMALIZE.get(d['NEGERI'].strip(), d['NEGERI'].strip()),
            'address': d['ALAMAT_FASILITI'].strip(),
            'city': d['BANDAR'].strip(),
            'postcode': d['POSKOD'].strip(),
            'beds': d.get('KATIL', '').strip(),
            'capacity': d.get('KAPASITI_KESELURUHAN', '').strip(),
            'has_facility': d.get('KEMUDAHAN', '').strip().upper() == 'KEMUDAHAN',
        })
    print(f"   ✅ {len(hospices)} hospices")
    return hospices


def fetch_existing():
    print("📖 Loading existing facilities...")
    with open(os.path.join(REPO, 'existing_facilities.csv'), encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
    print(f"   ✅ {len(rows)} facilities")
    return rows


def find_match(hospice, facilities):
    """Find best match by name + state. Must contain core distinguishing token."""
    # Extract distinguishing tokens (not generic care/centre/society)
    h_norm = normalize_name(hospice['name'])
    h_tokens = set(h_norm.split()) - {'care', 'palliative', 'hospice', 'hospis', 'paliatif', 'rawatan', 'persatuan', 'pertubuhan', 'cancer', 'national'}
    if not h_tokens:
        return None, 0

    candidates = []
    for f in facilities:
        if f.get('state','').strip() != hospice['state']:
            continue
        f_norm = normalize_name(f.get('title',''))
        f_tokens = set(f_norm.split())

        # Require at least one distinguishing token in common
        common = h_tokens & f_tokens
        if not common:
            continue

        score = name_similarity(hospice['name'], f.get('title',''))
        if score > 0.7:
            candidates.append((score, f))
    candidates.sort(key=lambda x: -x[0])
    if not candidates:
        return None, 0
    return candidates[0][1], candidates[0][0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()

    hospices = fetch_moh()
    facilities = fetch_existing()

    print(f"\n🔍 Matching hospices against {len(facilities)} facilities...\n")

    matches = []   # (hospice, existing_match, score)
    new_with_beds = []
    service_only = []

    for h in hospices:
        match, score = find_match(h, facilities)
        if match and score > 0.8:  # tighter threshold for confidence
            matches.append((h, match, score))
        else:
            if h['has_facility']:
                new_with_beds.append(h)
            else:
                service_only.append(h)

    # Print results
    print(f"📊 Summary:")
    print(f"   ✅ Matched to existing:    {len(matches)}")
    print(f"   🆕 Residential hospice:   {len(new_with_beds)}")
    print(f"   🏠 Service-only:          {len(service_only)}\n")

    if matches:
        print(f"\n✅ Matches (apply MOH hospice license + address):\n")
        for h, m, s in matches:
            print(f"   [{s:.2f}] {h['state']:>10}  {h['name'][:50]}")
            print(f"            ↔ {m['title'][:50]}  (slug: {m['slug']})")

    if new_with_beds:
        print(f"\n🆕 Residential hospices NOT in directory (add as new):\n")
        for h in new_with_beds:
            print(f"   {h['state']:>10}  {h['name']}  ({h['beds']} beds)")
            print(f"            {h['address']}")

    if service_only:
        print(f"\n🏠 Service-only (palliative home care, no facility):\n")
        for h in service_only:
            print(f"   {h['state']:>10}  {h['name'][:60]}")

    # Save analysis
    out_file = os.path.join(REPO, 'moh-hospice-matches.json')
    with open(out_file, 'w') as f:
        json.dump({
            'matches': [{'hospice': h, 'match_slug': m['slug'], 'match_title': m['title'], 'score': round(s,3)}
                        for h, m, s in matches],
            'new_with_beds': new_with_beds,
            'service_only': service_only,
        }, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Saved analysis: {out_file}")

    if not args.apply:
        print(f"\n💡 Run with --apply to:")
        print(f"   1. Mark {len(matches)} matched facilities as MOH-hospice-licensed")
        print(f"   2. Fill missing address from MOH source")
        print(f"   3. Append {len(new_with_beds)} new residential hospices (status=unverified)")
        return

    # Apply: enrich matches
    print(f"\n⚙️  Applying enrichments...")

    # Build slug → row index map
    rng = urllib.parse.quote(f"'google-sheets-facilities.csv'!A1:CC", safe='')
    resp = sd.api_request('GET', f"/v4/spreadsheets/{sd.SHEET_ID}/values/{rng}")
    sheet_rows = resp.get('values', [])
    sheet_headers = sheet_rows[0]
    slug_idx = sheet_headers.index('slug')
    slug_to_row = {r[slug_idx]: i+2 for i, r in enumerate(sheet_rows[1:]) if len(r) > slug_idx}

    updates = []
    for h, m, s in matches:
        slug = m['slug']
        if slug not in slug_to_row:
            continue
        row = slug_to_row[slug]

        # Mark MOH source
        if 'jkm_data_source' in sheet_headers:
            col = sd.col_letter(sheet_headers.index('jkm_data_source'))
            existing_src = m.get('jkm_data_source','').strip()
            new_src = (existing_src + '; MOH Hospice 2026').strip('; ') if existing_src else 'MOH Hospice 2026'
            updates.append((f"{col}{row}", new_src))

        # Add address if missing
        if 'address' in sheet_headers and h['address'] and not m.get('address','').strip():
            col = sd.col_letter(sheet_headers.index('address'))
            updates.append((f"{col}{row}", h['address']))

        # Mark palliative care
        if 'care_palliative' in sheet_headers and not m.get('care_palliative','').strip().lower() == 'yes':
            col = sd.col_letter(sheet_headers.index('care_palliative'))
            updates.append((f"{col}{row}", 'yes'))

        # Update bed capacity if MOH has it and existing is missing
        if h['beds'] and 'total_beds' in sheet_headers and not m.get('total_beds','').strip():
            col = sd.col_letter(sheet_headers.index('total_beds'))
            updates.append((f"{col}{row}", h['beds']))

    if updates:
        # Apply in batches
        batch_size = 100
        for i in range(0, len(updates), batch_size):
            batch = updates[i:i+batch_size]
            data = []
            for cell, val in batch:
                rng_ = f"'{sd.TAB_NAME}'!{cell}"
                data.append({'range': rng_, 'values': [[val]]})
            resp = sd.api_request('POST',
                f"/v4/spreadsheets/{sd.SHEET_ID}/values:batchUpdate",
                body={'valueInputOption': 'RAW', 'data': data})
            n = resp.get('totalUpdatedCells', len(batch))
            print(f"   Batch {i//batch_size + 1}: {n} cells")
        print(f"   ✅ {len(updates)} cells updated across {len(matches)} hospice matches")

    # Append all unmatched hospices (residential + service-only)
    new_entries = []
    for h in new_with_beds:
        new_entries.append((h, 'Hospice'))         # residential with beds
    for h in service_only:
        new_entries.append((h, 'Home Care'))       # palliative home-care providers

    if new_entries:
        print(f"\n   Appending {len(new_entries)} new MOH hospice entries...")
        new_rows = []
        for h, category in new_entries:
            row = [''] * len(sheet_headers)
            slug = re.sub(r'[^\w\s-]', '', h['name'].lower())
            slug = re.sub(r'\s+', '-', slug.strip())[:60]

            def setval(col, val):
                if col in sheet_headers:
                    row[sheet_headers.index(col)] = val

            setval('title', h['name'])
            setval('slug', slug)
            setval('state', h['state'])
            setval('area', h['city'])
            setval('address', h['address'])
            setval('care_types', 'Palliative Care' + ('; Hospice' if category == 'Hospice' else ''))
            setval('care_palliative', 'yes')
            setval('care_category', category)
            setval('total_beds', h['beds'] if h['beds'] else '')
            setval('status', 'unverified')
            setval('jkm_data_source', 'MOH Hospice 2026')
            setval('last_updated', '2026-05-07')
            new_rows.append(row)

        rng_append = urllib.parse.quote(f"'{sd.TAB_NAME}'!A:A", safe='')
        resp = sd.api_request('POST',
            f"/v4/spreadsheets/{sd.SHEET_ID}/values/{rng_append}:append?valueInputOption=RAW&insertDataOption=INSERT_ROWS",
            body={'values': new_rows})
        n = resp.get('updates',{}).get('updatedRows', len(new_rows))
        n_residential = len(new_with_beds)
        n_service = len(service_only)
        print(f"   ✅ {n} new entries appended (status=unverified):")
        print(f"      • {n_residential} residential hospices (with beds)")
        print(f"      • {n_service} palliative home care providers")

    print(f"\n✅ MOH hospice integration complete!")


if __name__ == '__main__':
    main()
