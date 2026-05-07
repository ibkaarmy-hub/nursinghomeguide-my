#!/usr/bin/env python3
"""
Deduplicate JKM scraped data against existing sheet facilities.
Match strategy:
1. Phone number (high confidence)
2. Name fuzzy match (medium)
3. GPS coordinates within ~500m (medium)
"""
import csv
import json
import re
from difflib import SequenceMatcher
from math import radians, sin, cos, sqrt, atan2

JKM_FILE = '/home/user/nursinghomeguide-my/jkm_full_scraped.csv'
EXISTING_FILE = '/home/user/nursinghomeguide-my/existing_facilities.csv'
OUTPUT_DIR = '/home/user/nursinghomeguide-my/jkm-results'

import os
os.makedirs(OUTPUT_DIR, exist_ok=True)

def normalize_phone(p):
    if not p: return ''
    digits = re.sub(r'\D', '', p)
    if digits.startswith('60'): digits = digits[2:]
    if digits.startswith('0'): digits = digits[1:]
    return digits

def all_phones(p):
    """Return set of normalized phones (a record may have multiple, comma-separated)"""
    if not p: return set()
    parts = re.split(r'[,/;]', p)
    return {normalize_phone(x) for x in parts if normalize_phone(x)}

def normalize_name(n):
    if not n: return ''
    n = re.sub(r"['\"]", '', n.lower())
    n = re.sub(r'\b(care|centre|center|home|elderly|senior|residence|retirement|nursing|sdn bhd|berhad)\b', '', n)
    return re.sub(r'\s+', ' ', n).strip()

def name_sim(a, b):
    return SequenceMatcher(None, normalize_name(a), normalize_name(b)).ratio()

def haversine_m(lat1, lon1, lat2, lon2):
    try:
        lat1, lon1, lat2, lon2 = float(lat1), float(lon1), float(lat2), float(lon2)
    except (ValueError, TypeError):
        return None
    R = 6371000
    p1, p2 = radians(lat1), radians(lat2)
    dp, dl = radians(lat2-lat1), radians(lon2-lon1)
    a = sin(dp/2)**2 + cos(p1)*cos(p2)*sin(dl/2)**2
    return 2*R*atan2(sqrt(a), sqrt(1-a))

# Load data
with open(JKM_FILE) as f:
    jkm = list(csv.DictReader(f))
print(f"📥 JKM scraped: {len(jkm)}")

with open(EXISTING_FILE) as f:
    existing = list(csv.DictReader(f))
print(f"📥 Existing: {len(existing)}")

# Build phone index for existing
phone_to_existing = {}
for ex in existing:
    for p in all_phones(ex.get('phone', '')):
        phone_to_existing.setdefault(p, []).append(ex)

print(f"📊 Phone index built: {len(phone_to_existing)} unique phones")

# Match each JKM record
matches = []
new_facilities = []
ambiguous = []

for j in jkm:
    j_phones = all_phones(j.get('phone', ''))
    j_name = j.get('name', '')
    j_lat, j_lng = j.get('latitude', ''), j.get('longitude', '')

    # 1. Phone match (highest confidence)
    phone_matches = []
    for p in j_phones:
        if p in phone_to_existing:
            phone_matches.extend(phone_to_existing[p])
    phone_matches = list({m['slug']: m for m in phone_matches}.values())

    if phone_matches:
        # Confirm with name similarity
        best = max(phone_matches, key=lambda m: name_sim(j_name, m.get('title', '')))
        sim = name_sim(j_name, best.get('title', ''))
        matches.append({
            'jkm_name': j_name,
            'jkm_phone': j.get('phone'),
            'jkm_licence': j.get('licence_number'),
            'existing_slug': best.get('slug'),
            'existing_title': best.get('title'),
            'existing_phone': best.get('phone'),
            'match_type': 'phone',
            'name_similarity': round(sim, 2),
            'confidence': 'high' if sim > 0.5 else 'medium',
        })
        continue

    # 2. GPS match within 200m + name similarity > 0.5
    gps_candidates = []
    if j_lat and j_lng:
        for ex in existing:
            d = haversine_m(j_lat, j_lng, ex.get('latitude'), ex.get('longitude'))
            if d is not None and d < 200:
                sim = name_sim(j_name, ex.get('title', ''))
                if sim > 0.4:
                    gps_candidates.append((ex, d, sim))

    if gps_candidates:
        gps_candidates.sort(key=lambda x: (-x[2], x[1]))
        best, dist, sim = gps_candidates[0]
        matches.append({
            'jkm_name': j_name,
            'jkm_phone': j.get('phone'),
            'jkm_licence': j.get('licence_number'),
            'existing_slug': best.get('slug'),
            'existing_title': best.get('title'),
            'gps_distance_m': round(dist),
            'name_similarity': round(sim, 2),
            'match_type': 'gps+name',
            'confidence': 'medium' if sim > 0.6 else 'low',
        })
        continue

    # 3. Pure name match - fuzzy >0.85
    name_candidates = [(ex, name_sim(j_name, ex.get('title', '')))
                        for ex in existing]
    name_candidates = [c for c in name_candidates if c[1] > 0.85]

    if name_candidates:
        name_candidates.sort(key=lambda x: -x[1])
        best, sim = name_candidates[0]
        ambiguous.append({
            'jkm_name': j_name,
            'jkm_phone': j.get('phone'),
            'jkm_licence': j.get('licence_number'),
            'existing_slug': best.get('slug'),
            'existing_title': best.get('title'),
            'name_similarity': round(sim, 2),
            'match_type': 'name_only',
            'confidence': 'low',
        })
        continue

    # No match — new facility
    new_facilities.append(j)

print(f"\n📊 Results:")
print(f"   ✅ High/Medium confidence matches: {len(matches)}")
print(f"   ❓ Ambiguous (name only): {len(ambiguous)}")
print(f"   🆕 NEW facilities: {len(new_facilities)}")
print(f"   ─── Total processed: {len(matches) + len(ambiguous) + len(new_facilities)} / {len(jkm)}")

# Save outputs
with open(f'{OUTPUT_DIR}/matches.json', 'w') as f:
    json.dump(matches, f, indent=2, ensure_ascii=False)
with open(f'{OUTPUT_DIR}/ambiguous.json', 'w') as f:
    json.dump(ambiguous, f, indent=2, ensure_ascii=False)

# New facilities CSV
if new_facilities:
    with open(f'{OUTPUT_DIR}/new_facilities.csv', 'w') as f:
        writer = csv.DictWriter(f, fieldnames=new_facilities[0].keys())
        writer.writeheader()
        writer.writerows(new_facilities)

print(f"\n💾 Saved to {OUTPUT_DIR}/:")
print(f"   - matches.json ({len(matches)} entries)")
print(f"   - ambiguous.json ({len(ambiguous)} entries)")
print(f"   - new_facilities.csv ({len(new_facilities)} entries)")

# Quick preview of new facilities
print(f"\n🆕 First 5 NEW facilities:")
for n in new_facilities[:5]:
    print(f"   • {n['name']} ({n.get('phone', '')[:30]})")
