# JKM Data Integration — Schema Refactor Plan

**Status:** ✅ AUDIT COMPLETE — decisions locked
**Date:** 2026-05-07
**Trigger:** JKM scrape brought 388 new facilities + 170 enrichment fields. Audit reveals existing schema has duplicates and unused columns.

---

## Audit results (2026-05-07)

Run: `python3 audit-schema.py`

### Confirmed safe to act on:

| Column | Fill | Action |
|--------|------|--------|
| `licence_number` (col 24) | 1/420 | **KEEP** (canonical, will fill 66 from JKM) |
| `license_number` (col 60) | 0/420 | **DROP** — completely empty |
| `license_expiry` (col 62) | 0/420 | **RENAME → `licence_expiry`** + populate from JKM |
| `license_verification_date` (col 61) | 0/420 | **RENAME → `licence_last_checked`** |
| `license_category` (col 59) | 418/420 = "Unverified" | **DROP** — placeholder only, no real data |
| `license_expiry_warning` (col 63) | 416/420 = "FALSE" | **DROP** — placeholder only |
| `pricing_model` (col 67) | 416/420 = "Unverified" | **DROP** — placeholder only |
| `nurse_in_charge` (col 65) | 416/420 = "Unverified" | **DROP** — placeholder only |
| `acuity_level` (col 64) | 0/420 | **DROP** — never used |
| `evidence_ref` (col 73) | 0/420 | **DROP** — never used |
| `outreach_last_attempt` (col 75) | 0/420 | **DROP** — never used |
| `outreach_notes` (col 76) | 0/420 | **DROP** — never used |
| `hidden_costs` (col 68) | 0/420 | **DROP** — never used |
| `four_bed_price` (col 47) | 1/420 | **KEEP** — schema documented, may be used |
| `dorm_price` (col 48) | 0/420 | **KEEP** — schema documented |

### Decisions locked:
- ✅ British spelling — drop all `license_*` US duplicates
- ✅ Add `address` column
- ✅ Add `email` column  
- ✅ Build state pages for new states (Perak, Penang, Negeri Sembilan, Pahang, Kedah, etc.)
- ✅ JKM `validity_date` → `licence_expiry` (as a single string range for now; can split later)

---

## Final schema changes

### Drop (12 columns):
`license_number`, `license_category`, `license_expiry_warning`, `pricing_model`, `nurse_in_charge`, `acuity_level`, `evidence_ref`, `outreach_last_attempt`, `outreach_notes`, `hidden_costs`

### Rename (2 columns):
- `license_expiry` → `licence_expiry`
- `license_verification_date` → `licence_last_checked`

### Add (3 columns):
- `address` (after `area`)
- `email` (after `phone`)
- `jkm_data_source` (after `licence_number`)

**Net: 81 → 72 columns** (cleaner schema, more filled).

---

## Migration plan

1. **Backup sheet** (`apply-enrichments.py --backup`)
2. **Drop empty placeholder columns** (12)
3. **Rename `license_*` → `licence_*`** (2)
4. **Add 3 new columns** (`address`, `email`, `jkm_data_source`)
5. **Apply 170 enrichments** (`apply-enrichments.py --apply`)
6. **Append 388 new facilities** (`status=unverified`)
7. **Build state pages** for new states
8. **Regenerate static facility pages** (`generate_facility_pages.py`)
9. **Update sitemap** (`generate_sitemap.py`)

---

## Open: validity_date storage

JKM stores as a range: `"30.06.2022 - 29.06.2027"`.

**Decision: store the raw range in `licence_expiry`** for now. Easy to parse when needed. Can split later into `licence_issued` + `licence_expiry` if monitoring becomes important.
