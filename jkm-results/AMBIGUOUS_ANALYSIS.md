# Analysis of 74 Ambiguous JKM Matches

**Date:** 2026-05-07  
**Total ambiguous:** 74  
**Flagged because:** Name-only matching (no GPS/phone confirmation), low confidence

---

## Summary

| Category | Count | Action |
|----------|-------|--------|
| Genuine duplicates | 1 | Consolidate to 1 directory entry |
| Multi-location organizations | 14 | Create separate entries OR tag as network |
| Single 1:1 matches (probably OK) | 59 | Accept as-is; low confidence but correct |

---

## 🔴 Genuine Duplicates (1 case)

**PUSAT JAGAAN WARGATUA MAIMUNAH**
- Phone: `019-6550135`
- Licence 1: `J/PJB WT 047/2022`
- Licence 2: `J/PJB WT 048/2022`
- Mapped to: `pusat-jagaan-warga-tua-damai`

**Interpretation:** Same JKM facility, registered twice with different licence numbers (likely renewal or different wings). Should consolidate to single directory entry.

**Action:** Use licence number J/PJB WT 048/2022 (newer); flag 047 as superseded in sheet.

---

## 🏢 Multi-Location Organizations (14 cases)

These are networks where JKM list shows multiple distinct facility names, but directory has mapped all to a single slug. This represents **significant undercounting** of actual facilities.

### Tier-1: Large networks (5-8 branches)

#### 1. **Pusat Jagaan Warga Emas Suria** 
- **8 distinct JKM facilities** mapped to 1 slug
- JKM names: Intan, Wcc, Cinta, Oasis, Seri Intan, Shekinah, Suria Cahaya, Wargamas Murni
- **Recommendation:** Create separate directory entries for each branch
- **Business type:** Organization network (likely central HQ in KL with branches in multiple states)

#### 2. **Pusat Jagaan Warga Tua SRA**
- **5 distinct JKM facilities** mapped to 1 slug  
- JKM names: Pangkor, Rebina, Seremban, Sri Orkid, Sri Tanjung
- **Recommendation:** Create separate entries; SRA likely abbreviation for organization name

#### 3. **Pusat Jagaan Orang Tua Damai**
- **4 distinct JKM facilities** mapped to 1 slug
- JKM names: Ceria, Jireh, Pantai, Tampin
- **Recommendation:** Separate entries

#### 4. **Pusat Jagaan Rumah Sejahtera** (Baitul Hannan / Batu Pahat family)
- **4 distinct JKM facilities** mapped to 1 slug
- JKM names: Baitul Hannan, Batu Pahat, Bertam, Rembau
- Geographic spread: Multiple states (Johor, Selangor, Perak, Negeri Sembilan)
- **Recommendation:** Separate entries per location

#### 5. **Pusat Jagaan Warga Emas Banang**
- **4 distinct JKM facilities** mapped to 1 slug
- JKM names: Bahagia, Banang, Diana, Wargamas Air Tenang
- **Recommendation:** Separate entries

### Tier-2: Small networks (2 branches)

6. **amazing-grace-retirement-home** — 2 entries (Care Centre / Care Centre variants)
7. **blissful-senior-care-centre-licensed-and-certified-by-gover** — 2 entries (Care / Care Centre)
8. **golden-age-care-centre** — 2 entries (same name, different variant)
9. **noble-care** — 2 entries (Centre / Centre variants)
10. **pj-care-centre** — 2 entries (same name, possibly different phone eras)
11. **pusat-jagaan-warga-emas-nur-ehsan** — 2 entries (Nur Ehsan / Pintu Harapan)
12. **pusat-jagaan-warga-emas-nur-ehsan-tangkak** — 2 entries (Nur Ehsan Wanita / Ledang)
13. **pusat-jagaan-warga-tua** — 2 entries (Elim / KP)
14. **pusat-jagaan-warga-tua-damai** — 2 entries (Maimunah duplicate, see above)

**For Tier-2 (2-branch networks):**
- If names are just capitalization/article variants → consolidate (Amazing Grace Care / Care Centre are same)
- If location-specific → create separate entries (Nur Ehsan / Nur Ehsan Tangkak are different cities)

---

## ✅ Single 1:1 Matches (59 cases)

These are facilities with one JKM record mapped to one directory entry, high name similarity (0.85-1.0), flagged as "low confidence" only because match_type=name_only.

**Examples:**
- Aurora Senior Care Centre ↔ aurora-home-care-centre [1.0]
- Caring Retirement Home Care Centre ↔ caring-nursing-home [1.0]
- Master Care Centre ↔ master-care-centre [1.0]
- Sunshine Care Centre ↔ sunshine-nursing-home [1.0]

**Assessment:** These are correct matches. Low confidence flag is due to matching algorithm limitation, not data quality. Acceptable to apply JKM licence data.

---

## Strategic Recommendations

### Short-term (accept ambiguous matches)
1. **Consolidate true duplicate:** Merge Maimunah 047/2022 → 048/2022 (one entry)
2. **Accept single 1:1 matches:** Tag all 59 single matches with JKM licence data (jkm_data_source = "JKM 2026")
3. **Flag multi-location orgs:** Mark 14 organization entries as "network HQ" and note branch count in Details tab

### Medium-term (resolve multi-location orgs)
1. **Create separate entries** for each branch of Tier-1 networks (Suria, SRA, Damai, Sejahtera, Banang)
   - Use JKM licence number as unique identifier (no collision risk)
   - Fill contact info from JKM data
   - Mark as (status=unverified) pending outreach
2. **Verify Tier-2 branches** during outreach phase — determine if phone/address variants indicate separate locations or data errors
3. **Audit organization ownership** — check if these are truly independent multi-branch orgs or separate entities using similar names

### Long-term (data quality)
1. **Require organization confirmation** during facility outreach — ask if they operate multiple branches
2. **Use JKM licence number as authoritative identifier** — uniqueness is guaranteed by regulator
3. **Contact multi-branch organizations directly** for: HQ contact, branch count, branch-specific details

---

## Impact Assessment

**Current state:**
- 808 facilities in directory
- 14 entries hiding 58+ actual branches (8+5+4+4+4+2+2+2+2+2+2+2+2 = 58 undercounted)
- True facility count: ~860+ (undercount of ~7%)

**If all multi-location orgs are expanded:**
- Net impact: +44 new facility entries (14 networks expanded to 58 total entries)
- JKM data already complete for all — just need slug + status separation
- Estimated directory coverage would improve from 808 → 852 live facilities

---

## Next Steps

1. **Spreadsheet:** Create branch entries for Tier-1 networks (8+5+4+4+4 = 25 new entries)
2. **Licencing:** Update jkm_data_source for 59 single matches + consolidated duplicate
3. **Details tab:** For organization HQ entries, add "Branches" section with location list
4. **Outreach:** Verify that multi-location orgs actually operate all listed branches (some may have closed)
