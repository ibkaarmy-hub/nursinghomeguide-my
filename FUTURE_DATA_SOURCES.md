# Future Data Sources — To Review & Integrate

**Purpose:** Track additional data sources for later analysis and potential integration.  
**Status:** Backlog

---

## 1. MOH Licensed Nursing Homes Spreadsheet

**Source:** Ministry of Health (MOH) / Malaysia  
**URL:** https://docs.google.com/spreadsheets/d/1c9V9NsYVmAAAzThby9G_qRfEE8pBWARZrKHo8XxKmVM/edit?gid=0#gid=0  
**Added:** 2026-05-07  
**Gid:** 0

### Analysis Needed

- [ ] **Data overview:** What columns does it have? How many facilities?
- [ ] **Overlap with JKM:** Are these the same 529 facilities? Different set?
- [ ] **Verification status:** Are these MOH-verified, MOH-licensed, or something else?
- [ ] **Integration approach:** 
  - Add as `moh_verification_status` column?
  - Cross-reference for licensing confirmation?
  - Separate data source tag?
- [ ] **Data quality:** Completeness, recency, contact info availability
- [ ] **Outreach value:** Can we use MOH verification to validate/enrich JKM data?

### Potential Integration Plan

Once analyzed:

1. **Deduplication:** Match MOH facilities against current 808 (352 existing + 388 new JKM)
2. **Enrichment:** Add `moh_licensed=yes/no/unknown` to matched facilities
3. **New facilities:** Identify MOH facilities NOT in JKM/existing set
4. **Credibility:** Use MOH listing as verification signal (improves family trust)

---

## Notes

- **Why backlog?** JKM integration is the priority (nationwide coverage). MOH data is secondary (verification layer).
- **Next step after JKM:** Once JKM integration is live and stabilized, revisit this for enrichment.
- **Access:** Sheet appears public/shared; may be able to fetch via Sheets API or manual download.

---

## Related Files

- `JKM_INTEGRATION_CHECKLIST.md` — Current primary integration workflow
- `jkm-results/` — JKM data (529 facilities, 388 new)
- `SCHEMA_REFACTOR_GUIDE.md` — Schema changes to support new data sources
