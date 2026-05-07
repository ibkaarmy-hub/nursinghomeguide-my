#!/usr/bin/env python3
"""
Audit duplicate/suspect columns in Facilities sheet to inform refactor.
Reports fill rate per column and overlap between duplicate columns.
"""
import csv
from collections import Counter

EX_FILE = '/home/user/nursinghomeguide-my/existing_facilities.csv'

with open(EX_FILE, encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

print(f"📥 {len(rows)} facilities, {len(rows[0])} columns\n")

# Live only
live = [r for r in rows if r.get('status', '').strip().lower() not in ('removed', 'unverified')]
print(f"   {len(live)} live, {len(rows) - len(live)} hidden\n")

# Suspect column groups (likely duplicates / unused)
groups = [
    ('British vs US spellings', [
        'licence_number', 'license_number',
    ]),
    ('License-related US-spelled', [
        'license_category', 'license_verification_date',
        'license_expiry', 'license_expiry_warning',
    ]),
    ('Verification / outreach (admin)', [
        'verification_tier', 'last_verified_on', 'verified_by', 'evidence_ref',
        'outreach_status', 'outreach_last_attempt', 'outreach_notes',
        'tier_2_review_pending', 'screened_date', 'screened_by',
    ]),
    ('Pricing extras', [
        'pricing_model', 'hidden_costs', 'four_bed_price', 'dorm_price',
    ]),
    ('SG-specific', [
        'sg_transfer_ready', 'acuity_level', 'nurse_in_charge',
        'doctor_visit_frequency',
    ]),
    ('Care taxonomy', [
        'care_types', 'care_category', 'service_type',
    ]),
]

def fill_rate(col):
    filled = sum(1 for r in rows if (r.get(col, '') or '').strip())
    return filled, round(100*filled/len(rows), 1)

# Group reports
for group_name, cols in groups:
    print(f"\n📊 {group_name}")
    print(f"   {'column':30} {'rows filled':>14}  {'%':>6}")
    for c in cols:
        if c not in rows[0]:
            print(f"   {c:30} {'(missing)':>14}")
            continue
        n, pct = fill_rate(c)
        bar = '█' * int(pct/3) if pct > 0 else ''
        print(f"   {c:30} {n:>10}/{len(rows):>3}  {pct:>5}%  {bar}")

# Specifically check overlap of licence_number vs license_number
print(f"\n🔍 Duplicate spelling overlap:")
both_filled = 0
british_only = 0
us_only = 0
neither = 0
disagreement = []
for r in rows:
    british = (r.get('licence_number', '') or '').strip()
    us = (r.get('license_number', '') or '').strip()
    if british and us:
        both_filled += 1
        if british != us:
            disagreement.append((r.get('slug'), british, us))
    elif british:
        british_only += 1
    elif us:
        us_only += 1
    else:
        neither += 1

print(f"   Both filled:  {both_filled}")
print(f"   British only: {british_only}")
print(f"   US only:      {us_only}")
print(f"   Neither:      {neither}")
if disagreement:
    print(f"\n   ⚠️  {len(disagreement)} rows with DIFFERENT values:")
    for s, b, u in disagreement[:5]:
        print(f"      {s}: '{b}' vs '{u}'")

print(f"\n💡 Recommendation:")
if us_only == 0 and not disagreement:
    print(f"   ✅ Safe to DROP 'license_number' — no data unique to it, no conflicts")
elif us_only > 0:
    print(f"   ⚠️  {us_only} rows have US-spelled value with no British equivalent — migrate first")
elif disagreement:
    print(f"   ⚠️  {len(disagreement)} rows disagree — manually resolve before drop")

# License_expiry analysis
print(f"\n🔍 license_expiry usage (target for renaming to licence_expiry):")
n, pct = fill_rate('license_expiry') if 'license_expiry' in rows[0] else (0,0)
print(f"   {n} rows filled ({pct}%)")
if n > 0:
    sample = [r['license_expiry'] for r in rows if r.get('license_expiry')][:5]
    print(f"   Sample values: {sample}")
