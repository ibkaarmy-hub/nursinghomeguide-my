#!/usr/bin/env python3
"""
Apply schema refactor to existing_facilities.csv:
- Drop 10 placeholder columns
- Rename 2 license_* → licence_*
- Add 3 new columns (address, email, jkm_data_source)
- Reorder columns logically

This is a one-time migration. After this, remaining columns will be uploaded
to the live Google Sheet via Sheets API.
"""
import csv
import os

REPO = os.path.dirname(os.path.abspath(__file__))
INPUT = os.path.join(REPO, 'existing_facilities.csv')
OUTPUT = os.path.join(REPO, 'existing_facilities_refactored.csv')

# Columns to drop (placeholders or unused)
DROP = {
    'license_number',            # US spelling, empty
    'license_category',          # 418/420 = "Unverified" placeholder
    'license_expiry_warning',    # 416/420 = "FALSE" placeholder
    'pricing_model',             # 416/420 = placeholder
    'nurse_in_charge',           # 416/420 = placeholder
    'acuity_level',              # 0/420, never used
    'evidence_ref',              # 0/420, never used
    'outreach_last_attempt',     # 0/420, never used
    'outreach_notes',            # 0/420, never used
    'hidden_costs',              # 0/420, never used
}

# Rename mappings (British spelling)
RENAME = {
    'license_expiry': 'licence_expiry',
    'license_verification_date': 'licence_last_checked',
}

# New columns to add (empty for now, will be populated by enrichments or manual entry)
ADD = ['address', 'email', 'jkm_data_source']

# Target column order (logical grouping)
# Identity, Contact, Location, Pricing, Care, Medical, Facilities, Content, Admin, New
COLUMN_ORDER = [
    # Identity
    'title', 'slug', 'url',
    # Location (area → address now in order)
    'area', 'address', 'latitude', 'longitude', 'google_maps_url', 'state',
    # Contact
    'phone', 'whatsapp', 'facebook', 'website', 'email',
    # Pricing
    'pricing_display', 'shared_price', 'private_price', 'four_bed_price', 'dorm_price',
    # Care types
    'care_types', 'care_nursing', 'care_dementia', 'care_palliative', 'care_rehab', 'care_respite', 'care_assisted',
    # Medical services
    'doctor_visits', 'doctor_visit_frequency', 'nurse_ratio_day', 'nurse_ratio_night',
    'medical_physio', 'medical_ot', 'medical_wound', 'medical_peg', 'medical_dementia_unit', 'medical_dialysis', 'medical_oxygen', 'medical_meds', 'rn_24_7',
    # Facilities
    'total_beds', 'availability', 'visiting_hours', 'parking', 'wheelchair', 'halal',
    # Amenities
    'religion', 'languages', 'subsidy', 'ownership_type',
    # Content
    'editorial_summary', 'hero_image', 'photos', 'photo_count',
    # Verification & admin
    'licence_number', 'jkm_data_source', 'licence_expiry', 'licence_last_checked',
    'status', 'rating', 'review_count', 'last_updated',
    # Deprecated admin fields (kept for reference, but should stay at end)
    'rn_24_7', 'care_category', 'service_type', 'sg_transfer_ready',
    'verification_tier', 'last_verified_on', 'verified_by', 'outreach_status',
    'tier_2_review_pending', 'deactivation_reason', 'remarks', 'screened_date', 'screened_by',
]

def main():
    print(f"📥 Reading {INPUT}")
    with open(INPUT, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"   {len(rows)} facilities, {len(rows[0])} columns")

    # Get original columns
    orig_cols = list(rows[0].keys())

    # Step 1: Drop columns
    print(f"\n🗑️  Dropping {len(DROP)} placeholder columns...")
    kept_cols = [c for c in orig_cols if c not in DROP]
    print(f"   {len(orig_cols)} → {len(kept_cols)} columns")

    # Step 2: Rename columns
    print(f"\n✏️  Renaming {len(RENAME)} columns to British spelling...")
    for old, new in RENAME.items():
        if old in kept_cols:
            idx = kept_cols.index(old)
            kept_cols[idx] = new
            print(f"   {old} → {new}")

    # Step 3: Add new columns
    print(f"\n➕ Adding {len(ADD)} new columns...")
    for col in ADD:
        if col not in kept_cols:
            kept_cols.append(col)
            print(f"   {col}")

    # Step 4: Reorder columns (only those in COLUMN_ORDER; append any extras)
    print(f"\n🔄 Reordering columns...")
    final_cols = []
    for c in COLUMN_ORDER:
        if c in kept_cols:
            final_cols.append(c)
            kept_cols.remove(c)
    # Append any remaining columns (shouldn't be many)
    if kept_cols:
        print(f"   ⚠️  {len(kept_cols)} columns not in target order (appending at end)")
        final_cols.extend(kept_cols)

    print(f"   Final order: {len(final_cols)} columns")

    # Step 5: Update rows with renamed columns + new empty columns
    new_rows = []
    for row in rows:
        new_row = {}

        # Copy old columns, rename as needed
        for col in orig_cols:
            if col in DROP:
                continue  # Skip dropped columns
            new_col_name = RENAME.get(col, col)  # Rename if needed
            new_row[new_col_name] = row.get(col, '')

        # Add new columns (empty for now)
        for col in ADD:
            if col not in new_row:
                new_row[col] = ''

        new_rows.append(new_row)

    # Step 6: Write output with final column order
    print(f"\n💾 Writing {OUTPUT}")
    with open(OUTPUT, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=final_cols)
        writer.writeheader()
        writer.writerows(new_rows)

    print(f"   ✅ {len(new_rows)} facilities, {len(final_cols)} columns")

    print(f"\n✅ Schema refactor complete!")
    print(f"\nNext steps:")
    print(f"  1. Review {OUTPUT}")
    print(f"  2. Replace existing_facilities.csv with refactored version")
    print(f"  3. Upload to Google Sheet via Sheets API (or manual copy-paste)")
    print(f"  4. Run: python3 apply-enrichments.py --apply")
    print(f"  5. Append new_facilities_for_sheet.csv (388 new facilities)")
    print(f"  6. Run: python3 generate_facility_pages.py")
    print(f"  7. Run: python3 generate_sitemap.py")

if __name__ == '__main__':
    main()
