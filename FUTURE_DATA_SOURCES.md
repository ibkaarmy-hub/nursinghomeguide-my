# Future Data Sources — To Review & Integrate

**Purpose:** Track additional data sources for later analysis and potential integration.  
**Status:** Backlog

---

## 1. MOH Licensed Private Hospices

**Source:** Ministry of Health (MOH) / Malaysia — "11. Hospis Swasta Berlesen"  
**URL:** https://docs.google.com/spreadsheets/d/1c9V9NsYVmAAAzThby9G_qRfEE8pBWARZrKHo8XxKmVM/edit?gid=0#gid=0  
**Added:** 2026-05-07  
**Status:** ✅ Stored in separate `Hospices` tab — https://docs.google.com/spreadsheets/d/1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk/edit#gid=1328825619  
**Decision:** ❌ NOT integrated into main nursing home directory — hospices are separate entities

### Why excluded

Hospices are **palliative care facilities for end-of-life care** — distinct from nursing homes:

| Aspect | Nursing Homes | Hospices |
|--------|---------------|----------|
| Regulator | JKM (welfare) + MOH | MOH only |
| Care type | Long-term residential elder care | End-of-life palliative care |
| Duration | Months to years | Days to weeks (typical) |
| Patient profile | Frail elderly, dementia, chronic conditions | Terminal illness |
| Family use case | "Where to live for ongoing care" | "Final dignified care" |

Mixing them would confuse the directory's purpose and family-side audience.

### Data summary (for future reference)

23 MOH-licensed hospices in Malaysia:
- **3 residential hospices with beds:** Pure Lotus Hospice (Penang, 21 beds), Kuching Life Care Society (Sarawak, 8 beds), Hospis Malaysia (KL, 4 beds)
- **20 service-only providers** (palliative home care, no residential facility): including Hospis Malaysia network — Hospis Kedah, Hospis Melaka, Hospis Klang, Assisi Palliative, Yayasan Kasih Hospis, etc.

### Hospices tab schema (Hospices tab in main sheet)

20 columns: `title, slug, state, area, address, postcode, beds, capacity, has_facility, care_palliative, organisation_type, service_type, phone, email, website, moh_licensed, data_source, last_updated, status, notes`

### Future option: separate hospice directory site/section

If we want to serve families looking for hospice care:
- Build dedicated `hospice.html` and `/hospices/<state>/` pages (similar to current state pages)
- Pull from the `Hospices` tab in same Google Sheet
- Cross-link from nursing home pages where palliative care is relevant
- Could be a separate landing page or sub-section of nursinghomeguide.my

### Files (kept for future use)

- `integrate-moh-hospices.py` — Pull script + matching logic (was used to populate Hospices tab)
- `moh-hospice-matches.json` — 23 hospices with parsed data + bed capacity

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
