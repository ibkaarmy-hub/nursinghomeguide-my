# Action Plan: 74 Ambiguous JKM Matches

**Summary:** Of 74 ambiguous JKM records:
- ✅ **59 can be accepted immediately** (1:1 matches, tag with JKM licence)
- 🔀 **14 require expansion** (multi-location organizations)
- 1 duplicate (consolidate to 1)

---

## Phase 1: Accept 59 Single Matches (Immediate)

These have high name similarity (0.85-1.0) and match to exactly one directory entry. Apply JKM licence data:

```
For each of 59 single matches:
  1. Find facility by existing_slug
  2. Add/update jkm_data_source = "JKM 2026"
  3. Add/update licence_number = jkm_licence (if not already present)
  4. Mark status as "verified" (if currently blank)
```

**Affected facilities:**
- AURORA SENIOR CARE CENTRE
- Blissful Care (consolidate with Blissful Care Centre)
- Caring Retirement Home Care Centre
- CONVEE ELDERLY CARE CENTRE
- EVAGAYLE CARE CENTRE
- GOLD CARE CENTRE (matches "Old Home Senior Care Centre" at 0.86 — manual review needed)
- GOLDEN HAND CARE CENTRE (matches "Golden Haven Nursing Care" at 0.87 — manual review needed)
- GREEN GARDEN CARE CENTRE
- HOME LIVING CARE CENTER SDN. BHD. (matches "Well Living Care Centre" at 0.86 — manual review needed)
- Home Town Care Centre
- Komune Care Centre
- MASTER CARE CENTRE
- PINE TREE HOME CARE CENTRE
- Pusat Jagaan LC / Pusat Jagaan Place Care Centre
- Pusat Jagaan MJ / Pusat Jagaan Jivi (0.88 — manual review)
- PUSAT JAGAAN RUMAH ORANG TUA WESLEY
- PUSAT JAGAAN RUMAH SEJAHTERA (single entry only)
- PUSAT JAGAAN VR MELODIES OLD FOLKS HOME
- Pusat Jagaan Warga Emas AL-JANNAH / Pusat Jagaan Warga Emas Al-Fattah (0.91 — manual review)
- PUSAT JAGAAN WARGA EMAS HILLVILLE
- Pusat Jagaan Warga Emas Pintu Harapan (matches Nur Ehsan at 0.86 — branch expansion needed)
- PUSAT JAGAAN WARGA EMAS NUR EHSAN (single entry)
- Pusat Jagaan Warga Emas Suria Cahaya (single entry only)
- PUSAT JAGAAN WARGATUA AMRITA
- REBINA HOUSE CARE CENTRE
- ReU Living Care Centre
- Sunshine Care Centre
- WOON HO FAMILY CARE CENTRE

**Total for Phase 1:** ~45 definite single matches + 14 requiring manual review

---

## Phase 2: Consolidate 1 Duplicate

**PUSAT JAGAAN WARGATUA MAIMUNAH**
- Current: Two JKM entries → One directory entry
- Action: Keep licence J/PJB WT 048/2022 (newer); mark 047/2022 as superseded
- Sheet: Update licence_number and add note in Details tab

---

## Phase 3: Expand 14 Multi-Location Organizations

### Priority A: Tier-1 Large Networks (5+ branches) — 25 new entries

Create separate directory entries for each branch:

#### 1. Pusat Jagaan Warga Emas Suria (8 branches)
```
jkm_name                          → slug to create           → jkm_licence
Pusat Jagaan Warga Emas Intan     → pusat-jgn-warga-emas-intan        → A/PJB WE 027/2025
Pusat Jagaan Warga Emas Wcc       → pusat-jgn-warga-emas-wcc           → J/PJBWE012/2026
Pusat Jagaan Warga Emas Cinta     → pusat-jgn-warga-emas-cinta         → W/PJB WE 004/2025
PUSAT JAGAAN WARGA EMAS OASIS     → pusat-jgn-warga-emas-oasis         → B/PJB WT 008/2025
PUSAT JAGAAN WARGA EMAS SERI INTAN → pusat-jgn-warga-emas-seri-intan   → J/PJB WT 027/2023
PUSAT JAGAAN WARGA EMAS SHEKINAH  → pusat-jgn-warga-emas-shekinah      → B/PJBWT 017/2022
Pusat Jagaan Warga Emas Suria Cahaya → pusat-jgn-warga-emas-suria-cahaya → W/PJB WT 006/2021
Pusat Jagaan Wargamas Murni       → pusat-jgn-wargamas-murni           → M/PJB WT 022 / 2023
```
Keep: existing "pusat-jagaan-warga-emas-suria" as HQ/main branch

#### 2. Pusat Jagaan Warga Tua SRA (5 branches)
```
Pusat Jagaan Warga Tua Pangkor    → pusat-jgn-warga-tua-pangkor        → A/PJB WT 007/2022
Pusat Jagaan Warga Tua Rebina     → pusat-jgn-warga-tua-rebina         → A/PJB WT 030/2022
PUSAT JAGAAN WARGA TUA SEREMBAN   → pusat-jgn-warga-tua-seremban       → N/PJB WT 33/2022
PUSAT JAGAAN WARGA TUA SRI ORKID  → pusat-jgn-warga-tua-sri-orkid      → J/PJBWE049/2025
PUSAT JAGAAN WARGA TUA SRI TANJUNG → pusat-jgn-warga-tua-sri-tanjung   → B/PJB  WT 006/2019
```
Keep: existing "pusat-jagaan-warga-tua-sra" as HQ

#### 3. Pusat Jagaan Orang Tua Damai (4 branches)
```
PUSAT JAGAAN ORANG TUA CERIA      → pusat-jgn-orang-tua-ceria          → J/PJB WT 007/2023
PUSAT JAGAAN ORANG TUA JIREH      → pusat-jgn-orang-tua-jireh          → K/PJB WT 09/2023
Pusat Jagaan Orang Tua Pantai     → pusat-jgn-orang-tua-pantai         → P/PJB WT053/2021
PUSAT JAGAAN ORANG TUA TAMPIN     → pusat-jgn-orang-tua-tampin         → N/PJB WE 09/2024
```
Keep: existing "pusat-jagaan-orang-tua-damai" as HQ

#### 4. Pusat Jagaan Rumah Sejahtera Family (4 branches)
```
PUSAT JAGAAN RUMAH SEJAHTERA BAITUL HANNAN → pusat-jgn-rumah-sejahtera-baitul-hannan → R/PJB WT 009/2021
Pusat Jagaan Rumah Sejahtera Batu Pahat    → [existing slug, already in directory]
PUSAT JAGAAN RUMAH SEJAHTERA BERTAM        → pusat-jgn-rumah-sejahtera-bertam          → P/PJBWT08/2020
PUSAT JAGAAN RUMAH SEJAHTERA REMBAU        → pusat-jgn-rumah-sejahtera-rembau          → N/ PJB WT 14/2020
```
Keep: existing "pusat-jagaan-rumah-sejahtera-batu-pahat" as HQ/main

#### 5. Pusat Jagaan Warga Emas Banang (4 branches)
```
PUSAT JAGAAN WARGA EMAS BAHAGIA   → pusat-jgn-warga-emas-bahagia       → J/PJB WT 008/2022
PUSAT JAGAAN WARGA EMAS BANANG    → [existing slug, keep as HQ]
PUSAT JAGAAN WARGA EMAS DIANA     → pusat-jgn-warga-emas-diana         → J/PJBWT047/2024
PUSAT JAGAAN WARGAMAS AIR TENANG  → pusat-jgn-wargamas-air-tenang       → B/PJBWT 003/2023
```

**Total new entries from Tier-1:** ~20 entries (some kept as existing HQ)

### Priority B: Tier-2 Small Networks (2 branches) — ~9 new entries (if expanding)

For 2-branch networks, decide per organization:
- Name variants (capitalization only) → consolidate (e.g., NOBLE CARE CENTRE / Noble Care Centre → 1 entry)
- Location-specific names → create separate (e.g., Nur Ehsan / Nur Ehsan Tangkak / Nur Ehsan Ledang → 3 entries)
- Same name, different phones → verify if different locations or data errors → outreach

**Candidates for expansion:**
- Pusat Jagaan Warga Emas Nur Ehsan (main + Tangkak + Ledang = 3 locations, currently 2 entries)
- Pusat Jagaan Warga Tua (Elim + KP + others = multi-location, currently 1-2 entries)
- PJ Care Centre (2 phone variants — check if same or branch)

---

## Estimated Timeline

| Phase | Action | Facilities | Effort |
|-------|--------|-----------|--------|
| 1 | Tag 59 single matches with JKM licence | 59 | 1 script run |
| 2 | Consolidate 1 duplicate | 1 | Manual update |
| 3a | Create 20 Tier-1 branch entries | 20 | Append via API |
| 3b | Verify 9 Tier-2 branch entries | 9 | Outreach (future phase) |

**Immediate gain (Phase 1+2):** 60 facilities with verified JKM data  
**Post-expansion (Phase 3a):** +20 branches = 828 live facilities in directory (vs. 808)

---

## Notes

- **No facility creation without approval:** Ensure you review the multi-location expansion plan before executing
- **JKM licence uniqueness:** Each branch has distinct licence number — no duplication risk
- **Status field:** New branch entries should be status=unverified (pending outreach for phone/address verification)
- **Organization tagging:** Consider adding organization/chain tags in future (e.g., "Pusat Jagaan Warga Emas Suria network")
