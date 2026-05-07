# JKM Integration — Complete Workflow Checklist

**Date:** 2026-05-07  
**Status:** Schema refactor prepared, ready to execute  

---

## 🎯 Current State

| Item | Status | Details |
|------|--------|---------|
| JKM scrape (529 facilities) | ✅ DONE | Apify with residential proxies, 388 new facilities identified |
| Deduplication (vs 420 existing) | ✅ DONE | 67 high-confidence matches, 74 ambiguous, 388 new |
| Enrichment data prepared | ✅ DONE | 170 field updates identified (licence numbers, GPS, emails) |
| Schema audit | ✅ DONE | 12 placeholder columns identified for removal/rename |
| Schema refactor script | ✅ DONE | Scripts ready: `apply-schema-refactor.py`, `apply-schema-to-sheet.py` |
| State pages generated | ✅ DONE | 13 new state pages (Perak, Penang, Negeri Sembilan, etc.) |
| Enrichment script | ✅ DONE | `apply-enrichments.py` ready with `--backup` and `--apply` flags |
| New facilities CSV | ✅ DONE | `jkm-results/new_facilities_for_sheet.csv` (388 rows, 74 columns) |

---

## 📋 Integration Workflow (In Order)

### Phase 1: Schema Refactor [🔴 TODO]

**Goal:** Update Google Sheet structure to match refactored schema.

**Changes:**
- Delete 10 placeholder columns
- Rename 2 `license_*` → `licence_*`
- Add 3 new columns: `address`, `email`, `jkm_data_source`

**How:**

Option A: Manual UI (safest, takes ~15 minutes)
```
1. Open https://docs.google.com/spreadsheets/d/1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk/edit#gid=292378871
2. Follow SCHEMA_REFACTOR_GUIDE.md
```

Option B: Python + Sheets API (fully automated)
```bash
python3 apply-schema-to-sheet.py --preview     # See changes
python3 apply-schema-to-sheet.py --apply       # Execute
```

**Verification:**
```bash
python3 verify-schema.py
```

**Expected result:** Sheet has 74 columns, all placeholders removed, new columns added.

---

### Phase 2: Apply Enrichments [🔴 TODO]

**Goal:** Update 67 matched facilities with JKM authoritative data (licence numbers, GPS fixes, validity dates, emails).

**Data:** `jkm-results/enrichment_proposed.json` (67 facilities, 170+ field updates)

**How:**
```bash
python3 apply-enrichments.py --backup    # (optional) download backup first
python3 apply-enrichments.py --apply     # Apply 170 changes to live sheet
```

**Expected result:** 
- 67 existing facilities enriched with JKM data
- New `jkm_data_source` column marked for these 67
- `licence_number` filled for ~66 facilities
- Validity dates added

---

### Phase 3: Append 388 New Facilities [🔴 TODO]

**Goal:** Add 388 new JKM facilities to sheet with `status=unverified` (hidden until reviewed).

**Data:** `jkm-results/new_facilities_for_sheet.csv` (388 rows, 74 columns, all schema-aligned)

**How:**
```
1. Open Google Sheet (Facilities tab)
2. Scroll to last row with data (~row 420)
3. Copy new_facilities_for_sheet.csv → Paste starting at row 421
   (Paste as values only to avoid formula issues)
4. Verify 388 rows pasted (now ~808 total rows)
5. Mark status column as 'unverified' for all 388 new rows
```

**Note:** All new facilities marked `status=unverified` so they're hidden from site until manually reviewed.

---

### Phase 4: Regenerate Static Pages [🟡 IN PROGRESS]

**Goal:** Regenerate per-facility detail pages + sitemap using updated CSV data.

**Why:** Site fetches CSV at page load, but static facility detail pages (for SEO/WhatsApp preview) are baked-in. They need to reflect new/updated facilities.

**How:**
```bash
# 1. Download fresh CSV from sheet (automatic via Sheets API)
#    OR manually: Sheet → File → Download → CSV

# 2. Regenerate facility detail pages
python3 generate_facility_pages.py

# 3. Regenerate sitemap
python3 generate_sitemap.py

# 4. Check outputs
ls -l facility/*/index.html | wc -l    # Should be ~808 files (420 existing + 388 new)
head -20 sitemap.xml                    # Should list new URLs
```

**Expected result:** 
- ~808 facility detail pages (one per facility)
- Updated `sitemap.xml` with all URLs
- Facility pages include OG tags + JSON-LD (for social share + SEO)

---

### Phase 5: Commit & Push [🔴 TODO]

**Goal:** Commit all changes to feature branch for review.

```bash
git add -A
git commit -m "Complete JKM integration: schema refactor + 170 enrichments + 388 new facilities

- Applied schema refactor: drop 10 placeholders, rename license_* → licence_*, add address/email/jkm_data_source
- Enriched 67 matched JKM facilities (licence numbers, GPS coordinates, validity dates, emails)
- Appended 388 new JKM-verified facilities from 2026 scrape (status=unverified, hidden until review)
- Generated 13 new state pages (nationwide expansion: Perak, Penang, Negeri Sembilan, Pahang, Kedah, Melaka, Sabah, Sarawak, Terengganu, Kelantan, Perlis, Putrajaya, Labuan)
- Regenerated 808 static facility detail pages + updated sitemap

https://claude.ai/code/session_01ARfLJuTpfazz9sE1cqVR8S"

git push -u origin claude/review-progress-jUIBV
```

---

## 📊 Integration Summary

| Metric | Count |
|--------|-------|
| Existing live facilities | 352 |
| Existing hidden (unverified) | 68 |
| New JKM facilities (to add) | 388 |
| **Total facilities after integration** | **808** |
| States covered (after integration) | 14 (Johor, KL, Selangor + 11 new) |
| Enriched existing facilities | 67 |
| Field updates (enrichments) | 170+ |
| New schema columns | 3 (address, email, jkm_data_source) |
| Dropped placeholder columns | 10 |
| Renamed columns | 2 |

---

## 🔍 Quality Checks (Before Commit)

- [ ] **Schema:** 74 columns, no `license_*` fields, new columns present
- [ ] **Enrichments:** 67 facilities have licence numbers + validity dates
- [ ] **New facilities:** 388 rows added with status=unverified
- [ ] **Static pages:** ~808 facility detail pages generated without errors
- [ ] **Sitemap:** All URLs listed, no broken references
- [ ] **Site behavior:** Homepage loads new state links, new state pages show unverified count
- [ ] **Ambiguous matches:** 74 ambiguous facilities reviewed (optional, for future outreach)

---

## 📝 Remaining Work

| Task | Status | Notes |
|------|--------|-------|
| MOH spreadsheet analysis | 📌 BACKLOG | Review for additional verification/licensing data (separate tab) |
| Hero images for new states | 🔴 TODO | Add img/states/{slug}.jpg or use CSS fallback |
| Ambiguous match review | 🔴 OPTIONAL | 74 facilities with same name, different phone — may indicate branches or duplicates |
| Facility outreach/verification | 🔴 FUTURE | Contact unverified facilities to confirm details |

---

## 🗺️ Files Reference

**Data files:**
- `jkm-results/enrichment_proposed.json` — 170 field updates
- `jkm-results/new_facilities_for_sheet.csv` — 388 new facilities, ready to paste
- `existing_facilities.csv` — Current 420 facilities (local copy)
- `existing_facilities_refactored.csv` — After schema refactor (local copy)

**Scripts:**
- `apply-schema-refactor.py` — Local schema refactor (CSV → CSV)
- `apply-schema-to-sheet.py` — Remote schema refactor (Sheets API)
- `apply-enrichments.py` — Apply 170 field updates to live sheet
- `generate_facility_pages.py` — Generate static detail pages
- `generate_sitemap.py` — Generate sitemap.xml
- `generate_state_pages.py` — Generate state listing pages
- `verify-schema.py` — Verify schema refactor completed

**Documentation:**
- `jkm-schema-refactor.md` — Schema audit results + decisions
- `SCHEMA_REFACTOR_GUIDE.md` — Step-by-step manual guide
- `JKM_INTEGRATION_CHECKLIST.md` — This file

---

## ✅ Next Step

**→ Start with Phase 1: Apply schema refactor (manual or via API script)**

Once schema changes are live in the Google Sheet, Phase 2-5 will proceed automatically.
