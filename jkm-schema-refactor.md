# JKM Data Integration — Schema Refactor Plan

**Status:** DRAFT — for review before applying
**Date:** 2026-05-07
**Trigger:** JKM scrape brought 388 new facilities + 170 enrichment fields. Audit reveals existing schema has duplicates and unused columns.

---

## 1. Current state

The Facilities sheet has **81 columns**. Audit reveals:

### Duplicates / inconsistencies
- `licence_number` (col 24) AND `license_number` (col 60) — same data, different spelling. **Pick one.**
- `licence_number` is used in data.js / facility.html / nh-profiles.md — keep British spelling (matches Malaysian gov context).
- `license_*` US-spelled columns (60–63) appear unused. Likely scaffolding from an earlier plan.

### Already exists, can be reused
- `license_expiry` (col 62) — **this is exactly what JKM `validity_date` represents.** Don't add a new column.
- `license_verification_date` (col 61) — could store "last JKM check" date.
- `license_category` (col 59) — could store JKM ownership type (Kediaman / NGO / Persendirian).

### Missing from current schema
- `address` — the sheet has NO address column. Currently relying on `area` (state-level only). This is a real gap, not just from JKM.
- `state` exists (col 55) — populate via JKM data for new entries.
- `email` — surprisingly missing (we have `phone`, `whatsapp`, `facebook`, `website` but not `email`).

---

## 2. Recommended changes

### 2.1 Resolve duplicates (blocker — do first)

**Action:** Rename or drop the unused US-spelled column block.

| Column | Action | Reason |
|--------|--------|--------|
| `license_number` (col 60) | **DROP** if unused, OR migrate values into `licence_number` and drop | Duplicate of col 24 |
| `license_category` (col 59) | **RENAME → `licence_ownership`** | More accurate, avoids confusion |
| `license_verification_date` (col 61) | **RENAME → `licence_last_checked`** | Plain English |
| `license_expiry` (col 62) | **RENAME → `licence_expiry`** | Spelling consistency |
| `license_expiry_warning` (col 63) | **RENAME → `licence_expiry_warning`** | Spelling consistency |

Verify which columns are actually populated (run a column-fill audit) before dropping anything.

### 2.2 Add genuinely new columns

| New column | Position | Purpose | Example |
|-----------|----------|---------|---------|
| `address` | After `area` | Actual street address | `No. 112, Jalan Lahat Lama, 31450 Perak` |
| `email` | After `phone` | Contact email | `info@example.my` |
| `jkm_data_source` | After `licence_number` | Where this row was sourced from | `JKM scrape 2026-05-07` |

### 2.3 Fields explicitly NOT to add

Considered but rejected:

- **`validity_date`** — Use existing `licence_expiry`. Same semantics, no need for a new column.
- **`fax`** — Have it in JKM data, but only 1 record had it. Not worth a column for that.
- **`ownership_type` vs `licence_ownership`** — The existing `ownership_type` (col 23) appears to track operator type (private/public/NGO at the facility level). JKM ownership is the licence category. Keep both, distinct purposes:
  - `ownership_type` — who runs it operationally (Operator chain / NGO / Government / Private individual)
  - `licence_ownership` — JKM licence category (Kediaman / Persendirian / NGO)

---

## 3. Migration plan (in order)

### Step 1 — Audit duplicates (read-only)
```python
# Check fill rate of suspect columns
python3 audit-schema.py
```
Output: how many rows have data in `license_number` vs `licence_number`, etc.

### Step 2 — Rename columns (low risk)
- Sheet UI: right-click column → rename header
- No data movement, no JS changes needed yet
- Can be reverted instantly

### Step 3 — Drop or merge duplicate `license_number` column
Only after audit confirms it's empty/redundant. If populated:
- Run a one-off script to merge values into `licence_number` (preferring the populated one per row)
- Then drop the duplicate

### Step 4 — Add new columns (`address`, `email`, `jkm_data_source`)
- Add column headers in sheet
- Update `data.js` parser if it relies on column count (it shouldn't — uses headers)
- No facility.html change needed (these can stay invisible until populated)

### Step 5 — Apply JKM enrichments
Run `apply-enrichments.py --apply` (already built):
- Fills 66 `licence_number` (→ rename target)
- Fills 67 `licence_expiry` (formerly proposed as `validity_date`)
- Fixes 23 invalid `longitude`
- Fills 4 emails, 3 maps URLs, etc.

Update `enrich-matches.py` to map JKM → renamed columns:
```python
JKM_FIELDS = {
    'licence_number': 'licence_number',
    'licence_expiry':  'validity_date',     # ← was validity_date_fill
    'licence_ownership': 'ownership',       # ← Kediaman/NGO/Persendirian
    'latitude': 'latitude',
    'longitude': 'longitude',
    'google_maps_url': 'maps_url',
    'email': 'email',
    'address': 'address',                   # ← new
}
```

### Step 6 — Append 388 new facilities
Already prepared in `jkm-results/new_facilities_for_sheet.csv`:
- Update mapper to write to renamed/new columns
- Append rows with `status=unverified` (hidden until reviewed)

### Step 7 — Update facility.html / data.js
- Surface `licence_expiry` on Overview tab as "JKM licence valid until DD.MM.YYYY"
- Surface `address` on profile page (currently only area is shown)
- Add "Verified by JKM ✓" badge when licence_number + expiry both filled and not lapsed

### Step 8 — Optional: licence-expiry monitoring
- Daily script: flag facilities whose `licence_expiry < today + 30 days`
- Surface a small warning on the facility page
- Useful trust signal for families

---

## 4. Backwards compatibility

- **No URL changes** — slugs stay the same
- **No removed columns** during this refactor (only renames + adds + one merge)
- **`ownership_type` stays** — separate from new `licence_ownership` 
- **`status` column unchanged** — JKM-imported rows enter as `unverified`, won't show on site until manually verified

---

## 5. Open questions

1. **Drop `license_number` (col 60) if empty?** Need audit data first.
2. **Should `validity_date` from JKM map to `licence_expiry` (existing) or create new `licence_validity_period`?** The JKM value is a *range* ("30.06.2022 - 29.06.2027"), not a single expiry. We're currently storing the range as a single string. Three options:
   - **(A)** Store full range in `licence_expiry` (current proposal). Simple but expiry-monitoring scripts need to parse the end date.
   - **(B)** Split into `licence_issued` + `licence_expiry`. Cleaner data model, two more columns.
   - **(C)** Keep `licence_expiry` as the end date only, add `licence_full_term` as the raw range. Best of both.
   - **Recommendation: C.**

3. **State pages for new states?** Currently 3 (Sel/KL/Johor). With JKM data we have facilities in 14 states. Build templates for at least Perak, Penang, Negeri Sembilan first (highest counts). Defer the smaller states until they grow.

4. **Photos for the 388 new entries** — JKM has none. Either:
   - Scrape Google Maps for hero photos (separate Apify actor)
   - Use a placeholder + show "No photo available — request from operator"
   - Leave blank, rely on data-only profile

---

## 6. Risks

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Drop wrong column → data loss | Low (with audit) | Backup sheet before any drop |
| Renamed column breaks JS/HTML | Medium | Grep for old names, test locally |
| 388 new unverified rows clutter UI | Low | `status=unverified` hides them |
| JKM licence number conflicts with operator-supplied | Low | Use `licence_number` from JKM as authoritative; add note column if disputed |

---

## 7. Decision points (user input needed)

- [ ] Confirm spelling: keep `licence_*` (British, gov context) — drop `license_*` US duplicates
- [ ] Choose validity_date strategy: A / B / C from §5.2
- [ ] Approve adding `address` and `email` columns
- [ ] Approve order of migration steps 1–8
