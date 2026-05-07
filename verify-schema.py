#!/usr/bin/env python3
"""
Verify that schema refactor has been applied to existing_facilities.csv.
Checks for:
- Unwanted columns have been deleted
- Columns have been renamed
- New columns exist
"""
import csv
import sys

CSV_FILE = 'existing_facilities.csv'

SHOULD_DELETE = {
    'license_number', 'license_category', 'license_expiry_warning',
    'pricing_model', 'nurse_in_charge', 'acuity_level', 'evidence_ref',
    'outreach_last_attempt', 'outreach_notes', 'hidden_costs'
}

SHOULD_RENAME = {
    'license_expiry': 'licence_expiry',
    'license_verification_date': 'licence_last_checked',
}

SHOULD_ADD = {'address', 'email', 'jkm_data_source'}

def main():
    with open(CSV_FILE, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        rows = list(reader)

    print(f"📊 Checking {CSV_FILE}")
    print(f"   {len(rows)} rows, {len(headers)} columns\n")

    errors = []
    warnings = []

    # Check 1: Deleted columns should NOT exist
    print("🗑️  Checking deletions...")
    deleted_found = [c for c in headers if c in SHOULD_DELETE]
    if deleted_found:
        errors.append(f"❌ These columns should have been deleted but still exist: {deleted_found}")
    else:
        print("   ✅ All 10 placeholder columns deleted")

    # Check 2: Renamed columns should exist with new names, old names should NOT exist
    print("\n✏️  Checking renames...")
    for old, new in SHOULD_RENAME.items():
        if old in headers:
            errors.append(f"❌ Column '{old}' should be renamed to '{new}' but still exists as '{old}'")
        elif new not in headers:
            errors.append(f"❌ Column '{new}' should exist (renamed from '{old}') but doesn't")
        else:
            print(f"   ✅ {old} → {new}")

    # Check 3: New columns should exist
    print("\n➕ Checking additions...")
    for col in SHOULD_ADD:
        if col not in headers:
            errors.append(f"❌ New column '{col}' doesn't exist")
        else:
            print(f"   ✅ {col}")

    # Check 4: Data integrity
    print("\n📋 Checking data integrity...")
    if len(rows) < 400:
        warnings.append(f"⚠️  Only {len(rows)} rows (expected ~420)")
    else:
        print(f"   ✅ {len(rows)} facilities intact")

    # Summary
    print(f"\n{'='*60}")
    if errors:
        print(f"\n❌ FAILED — {len(errors)} error(s):\n")
        for err in errors:
            print(f"   {err}")
        sys.exit(1)
    else:
        print(f"\n✅ PASSED — Schema refactor successfully applied!")
        print(f"\n   Next steps:")
        print(f"   1. python3 apply-enrichments.py --apply")
        print(f"   2. Append new_facilities_for_sheet.csv (388 rows)")
        print(f"   3. python3 generate_facility_pages.py")
        print(f"   4. python3 generate_sitemap.py")
        if warnings:
            print(f"\n⚠️  Warnings:")
            for w in warnings:
                print(f"   {w}")

if __name__ == '__main__':
    main()
