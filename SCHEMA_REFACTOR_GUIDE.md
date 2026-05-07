# Schema Refactor — Manual Application Guide

**Status:** Ready to apply  
**Date:** 2026-05-07

This guide walks you through applying the schema refactor to the live Google Sheet manually via the UI, then using Python to apply enrichments.

---

## Changes Required

### 1. DELETE 10 Columns (placeholders with no real data)

Delete these columns from the **Facilities** tab in order (right-to-left):

| Column | Letter | Fill | Reason |
|--------|--------|------|--------|
| `screened_by` | AL | 0/420 | Never used |
| `screened_date` | AK | 2/420 | Never used |
| `tier_2_review_pending` | AJ | 416/420 = "FALSE" | Placeholder |
| `outreach_notes` | AI | 0/420 | Never used |
| `outreach_last_attempt` | AH | 0/420 | Never used |
| `evidence_ref` | AG | 0/420 | Never used |
| `verified_by` | AF | 416/420 = placeholder | Placeholder |
| `nurse_in_charge` | T | 416/420 = "Unverified" | Placeholder |
| `acuity_level` | S | 0/420 | Never used |
| `hidden_costs` | Q | 0/420 | Never used |

**Why right-to-left?** Column indices shift after each deletion; deleting from right-to-left prevents index errors.

### 2. RENAME 2 Columns (British spelling)

| Old Name | New Name | Letter |
|----------|----------|--------|
| `license_expiry` | `licence_expiry` | AO (after step 1) |
| `license_verification_date` | `licence_last_checked` | AN (after step 1) |

### 3. ADD 3 Columns

Add three new empty columns at the end:

1. `address` — full address (complements `area`)
2. `email` — facility email
3. `jkm_data_source` — marks facilities from JKM scrape

---

## How to Apply (Via Google Sheets UI)

### Step 1: Delete 10 Columns

1. Open https://docs.google.com/spreadsheets/d/1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk/edit#gid=292378871 (Facilities tab)
2. Right-click column **AL** (`screened_by`) → Delete column
3. Repeat for columns **AK**, **AJ**, **AI**, **AH**, **AG**, **AF**, **T**, **S**, **Q**
4. Verify sheet now has 71 columns (81 - 10 = 71)

### Step 2: Rename 2 Columns

1. Double-click the header cell of `license_expiry` → replace with `licence_expiry`
2. Double-click the header cell of `license_verification_date` → replace with `licence_last_checked`
3. Press Enter to confirm

### Step 3: Add 3 Columns

1. Right-click the last column → Insert 1 column right
2. Repeat 3 times
3. Add headers: `address`, `email`, `jkm_data_source`
4. Verify sheet now has 74 columns (71 + 3 = 74)

---

## How to Apply (Via Python + Sheets API)

**Prerequisite:** `client_secret.json` in repo root with Google OAuth credentials

```bash
# Step 1: Preview changes
python3 apply-schema-to-sheet.py --preview

# Step 2: Apply changes
python3 apply-schema-to-sheet.py --apply
```

The script will:
- Delete columns right-to-left (safe order)
- Rename columns
- Add new columns
- Output summary

---

## Post-Refactor Workflow

After schema changes are applied to the live sheet:

```bash
# 1. Apply enrichments (170 field updates from JKM scrape)
python3 apply-enrichments.py --apply

# 2. Download sheet (for local static page generation)
#    (Usually done automatically when running generate_facility_pages.py)

# 3. Append 388 new JKM facilities
#    (Copy rows from jkm-results/new_facilities_for_sheet.csv and paste into sheet)
#    Mark as status=unverified so they're hidden until reviewed

# 4. Regenerate static facility pages
python3 generate_facility_pages.py

# 5. Regenerate sitemap
python3 generate_sitemap.py

# 6. Commit and push
git add -A
git commit -m "Apply schema refactor + JKM enrichments + 388 new facilities"
git push -u origin claude/review-progress-jUIBV
```

---

## Verification

Before proceeding, verify:

- ✅ Sheet has exactly 74 columns
- ✅ No columns named `license_*` (all renamed to `licence_*`)
- ✅ New columns exist: `address`, `email`, `jkm_data_source`
- ✅ All 420 facility rows intact (no data loss)

```bash
# Download latest sheet state and verify locally
python3 -c "
import csv
from google.colab import auth
import gspread

auth.authenticate_user()
gc = gspread.authorize(auth)
sh = gc.open_by_key('1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk')
ws = sh.worksheet('Facilities')
headers = ws.row_values(1)
print(f'Columns: {len(headers)}')
print(f'Rows: {ws.row_count - 1}')
print(f'New columns present: {\"address\" in headers and \"email\" in headers and \"jkm_data_source\" in headers}')
"
```

---

## Rollback (if needed)

If something goes wrong, you can restore from your backup:

```bash
# 1. Revert to previous state
#    (File → Version history in Google Sheets, or restore from backup)

# 2. Try again with --preview
```

The `apply-enrichments.py` script has a `--backup` flag:

```bash
python3 apply-enrichments.py --backup
```

This will download the current sheet state to `enrichment_backup.csv` before applying changes.

---

## Questions?

See: `jkm-schema-refactor.md` for full audit results and decision rationale.
