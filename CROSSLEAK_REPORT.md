# Cross-leak deep-research pass — 2026-05-17 overnight

**Scope:** the 21 `Check 3` website-cross-leak pairs from the deep audit, across 14 unique domains. Each domain was fetched (WebFetch where possible, Apify for sites that blocked direct requests), and each shared-domain pair was triaged into one of:

1. **Real chain** — add a `GROUPS` entry so the cross-leak warning is suppressed and branches cross-link on profile cards / get an `org.html` page.
2. **Wrong website on one row** — clear the website from the wrong row.
3. **Same-facility duplicate** — deactivate the duplicate row.
4. **Flag for manual follow-up** — when the call is genuinely uncertain (e.g. Google's record corroborates a website that the operator's own site contradicts).

Every Places-API place_id used for verification was confirmed against Google's live data this session.

---

## 1. MultiCare Nursing Home — `multicarehomes.com`

**Decision: real chain → GROUPS entry added.**

Branches:
- `multicare-nursing-home` (PJ Seksyen 5 HQ)
- `multicare-nursing-home-johor` (JB, 13 Jalan Harimau Akar — opened Aug 2025)

The JB expansion was verified directly via the operator's own Facebook announcement post dated 2025-07-23 (post ID `1228147445993051`): *"Multicare Nursing Home is Expanding to JOHOR BAHRU! …our new branch in Johor Bahru will be opening in August 2025."* So the editorial's previously-unsourced "August 2025 opening" claim is now sourced.

**Note on the website you asked about:** `multicarehomes.com` lists "PRIVATE NURSING" as a service link distinct from the residential packages — that confirms your "multicare has private nursing service as well" point. The new GROUPS description records this.

The packages.html pricing applied to the PJ row earlier today is the same chain-wide tariff already present on the JB row from an earlier hand-fix.

---

## 2. Care Concierge — `mycareconcierge.com`

**Decision: real chain → GROUPS entry added.**

Branches in sheet:
- `care-concierge-malaysia` (HQ at Jaya One, PJ)
- `care-concierge-care-luxe-ampang`
- `ara-woods-senior-care-centre` (The Mansion Ara Woods)

The operator site lists ~10 properties under "The Mansion" and "Care Luxe" brands plus Penang (Angsana Home, Tanjung Point Residences) and a Sarawak opening in 2026. Our three rows are confirmed in their network. **Possible additions for future enrichment:** Mansion Gasing 58/136, Mansion Sri Aman, Mansion Ampang, Mansion Pantai, Angsana Home, Tanjung Point Residences — not currently in the sheet.

---

## 3. Mega Senior Care Centre — `megaseniorcarecentre.com`

**Decision: wrong website on `house-of-megaways-care-centre` → cleared.**

The operator's own site explicitly states "Single Location" at 29 Jalan Pantai 9/7, Seksyen 9, 46000 PJ. The two sheet rows that referenced this site:

- `goldleaf-villa-care-centre` (row 241, Cheras KL): Google itself attributes this website + the Mega phone `+60 10-238 3848` to GoldLeaf. This is contradictory with the operator's own site (which says PJ only). **Left as-is and flagged below for manual review** — could be Google data drift or a sister operation that isn't documented on the Mega site.
- `house-of-megaways-care-centre` (row 509, Seremban NS): Google has no website attribution for the Seremban listing (place_id `ChIJF0uXOgDdzTER…` resolves to `美嘉威安老院` with no website). Our row's `megaseniorcarecentre.com` reference is therefore unsupported and was **cleared**.

---

## 4. My Joyful Home Care Centre — `myjoyfulhome.com.my`

**Decision: same-facility duplicate → row 517 deactivated.**

Rows 300 (`my-joyful-home-care-centre`) and 517 (`joyful-home-elderly-care-centre`) share:
- identical place_id `ChIJP9Kd9ZRNzDERFHk-ZbGg3zo` (Google name: "My Joyful Home Care Centre")
- identical address (12, Jalan SS 19/3, SS 19, 47500 Subang Jaya)
- identical rating 5★/8

Row 300 carries the canonical brand-matching slug; row 517 is the older legacy slug. Row 517 set to `status=removed`.

---

## 5. My Precious Home Care — `myprecioushomecare.com`

**Decision: real chain (two distinct branches) → GROUPS entry added.**

The two slugs are genuinely different facilities:
- `my-precious-home-care-elder-care` — 27 Jalan USJ 1/3B, Grandville, Subang Jaya (4.7★/122) — verified by Places API
- `my-precious-home-care-retirement-home` — No. 38 Jalan SS1/39, Kampung Tunku, PJ (5★/11) — verified by Places API

Different addresses, different phones, different place_ids — both real branches under one operator. The operator's own site only describes the Subang Jaya site, but Google attributes both to the same domain.

---

## 6. Merry Care — `elderlycare.my`

**Decision: existing GROUPS entry updated to include the parent slug.**

The `merry-care-centre` GROUPS entry already existed with 6 branches but was missing the parent `merry-care-centre` slug itself — that's why the audit kept pairing it with each of its 6 own branches. Added to branches list. Now 7-branch chain (Kuchai Lama HQ + 4 Kepong Baru + Desa Jaya + Selayang Baru), all confirmed against the operator site.

---

## 7. Seavoy Nursing Home — `seavoynursinghome.com`

**Decision: real chain → GROUPS entry added.**

- `seavoy-nursing-home-desa-melawati` (row 344): place_id verified — "Seavoy Nursing Home, Desa Melawati" at 20 Jalan 5/4C, 53100 KL.
- `seavoy-nursing-home-taman-setapak-indah` (row 343): no Places place_id but distinct phone (03-4021 1337 vs the Melawati branch's 03-4108 4740), distinct rating (4.7/3 vs 2.8/5), and distinct area — treating as a real second branch.

There's a third slug `pusat-jagaan-seavoy` (KL) which may belong here too — not added to GROUPS in this pass because it carries no website cross-link evidence; flagged for the next round.

---

## 8. Rumah Victory — `rumahvictory.org.my`

**Decision: real chain (multi-service welfare org) → GROUPS entry added.**

The Rumah Victory site describes a welfare association running multiple service centres (Drug Rehab, Children & Youth, Elderly Home). Both rows share the website per Google's own attribution:

- `rumah-victory-elderly-home` (HQ at Bukit Kuchai, Puchong) — the Elderly Home arm
- `true-house-of-victory-care-centre` (Kampung Baru, Seremban NS) — Google itself attributes the `rumahvictory.org.my` site to this listing (place_id `ChIJF5BhJKDnzTER…`). Treating as a related branch.

---

## 9. Alexa Villa — `alexahealthcare.com`

**Decision: real chain → GROUPS entry added.**

The operator runs separate male and female single-gender senior care centres in the Sendayan / Seremban district:
- `alexa-villa-senior-care-centre` → likely the Tiara Sendayan (female) branch
- `alexa-villa-senior-care-centre-caw` → likely the Suriaman Sendayan (male) branch

---

## 10. Edelweiss / Elders Home — `eldershome.com.my`

**Decision: wrong website on `edelweiss-elderly-care-centre` → cleared.**

The site (eldershome.com.my) only describes two Elders Home branches in Melaka (Klebang Besar and Malim). **"Edelweiss" is not mentioned anywhere on the operator's site.** Note that the `edelweiss-elderly-care-centre` row carries `area: Taman Muhibbah` which happens to match the Klebang Besar branch — so this row may actually *be* the Elders Home Care Centre, mistitled "Edelweiss" at some point in enrichment history. Cleared the wrong website attribution; the **title** is left for your call (verify with the operator on a call whether Edelweiss is a real distinct facility or a renamed Elders Home).

`elders-home-plus-care-centre-sdn-bhd` keeps the website — that's the Malim branch and it matches.

---

## 11. Elderlove — `elderlovemissi.com.my`

**Decision: existing GROUPS entry expanded.**

The operator site lists five branches (Sungai Long, Puchong Skypod, Sg Buloh/Kota Damansara/Pinggiran Subang, Bercham Ipoh, SKGV Pudu KL). Our sheet has four slugs that look at this site: `elderlove-care-centre`, `elderlove-living-care-centre`, `-puchong`, `-sglong`. The existing `elderlove-living` GROUPS entry only listed two; expanded to all four. All four are now suppressed from cross-leak warnings.

---

## 12. Keepers — `myknc.com.my`

**Decision: real chain → GROUPS entry added.**

The Keepers (KNC) network on Penang runs Wellesley Assisted Living + Concordia Dementia Care + a Specialised Care Centre + a private nursing-to-home service. Our two slugs (`-dementia-care-centre-sdn-bhd`, `-medi-care-centre-sdn-bhd`) align with two of those branches.

---

## 13. Pusat Jagaan Mak Swee — `thedementiasocietyperak.wordpress.com`

**Decision: wrong website on `pusat-jagaan-mak-swee-cawangan-1` → cleared.**

The "The Dementia Society Perak" site describes the BebeLEC Day Centre in Ipoh and makes no mention of Mak Swee. The Mak Swee row sits in Muar Johor (verified place_id resolves to "Pusat Jagaan Orang Tua Mak Swee (Cawangan 1)" at 205-3 Jln Ismail, Taman Bakariah). Unrelated facilities — website cleared.

The `pusat-jagaan-harian-pertubuhan-dimensia-perak` row keeps the website — that's the Dimensia Perak / BebeLEC entity itself.

---

## 14. Pusat Jagaan Rumah Sejahtera Gopeng — `tbspinghe.org`

**Decision: wrong website → cleared.**

The tbspinghe.org site is exclusively the "平和養老院 Harmopeace Oldfolks Home" in Gopeng. "Rumah Sejahtera Gopeng" is not mentioned anywhere. The two are likely distinct facilities — website cleared from the Sejahtera Gopeng row.

The `harmopeace-oldfolks-home-gopeng` row keeps the website — that's the real Harmopeace.

---

## Sheet writes this pass (6 ops)

| row | slug | action |
|---|---|---|
| 337 | dementia-care-centre | deactivated (no Google listing, no operator site) |
| 464 | edelweiss-elderly-care-centre | website cleared |
| 509 | house-of-megaways-care-centre | website cleared |
| 517 | joyful-home-elderly-care-centre | **deactivated — duplicate of row 300** |
| 621 | pusat-jagaan-mak-swee-cawangan-1 | website cleared |
| 671 | pusat-jagaan-rumah-sejahtera-gopeng | website cleared |

## GROUPS entries added/updated in `data.js` (8)

- Updated: `merry-care-centre` (added missing parent slug)
- Updated: `elderlove` / `elderlove-living` (expanded to 4 slugs)
- New: `multicare-nursing-home`, `care-concierge`, `seavoy-nursing-home`, `alexa-villa`, `keepers`, `my-precious-home-care`, `rumah-victory`

## One flagged for your call

- **`goldleaf-villa-care-centre` (row 241):** Google itself attributes `megaseniorcarecentre.com` and the Mega phone `+60 10-238 3848` to this listing, but the Mega site explicitly says it has a single PJ location. Either GoldLeaf is genuinely a sister operation Mega doesn't advertise, or Google has stale data here. Not auto-changed — needs an operator call to settle. The original "megaway-class" diagnosis sub-section in the audit report covers this lineage.

## Multicare private-nursing service note

`multicarehomes.com` advertises **"PRIVATE NURSING"** as a service distinct from the residential packages we already wrote into the row. It's described as a separate offering on the homepage but the service description redirects elsewhere on the site. The new GROUPS description for MultiCare records this. If you want it surfaced on the profile, the cleanest move is to add a `details` row of section=`services` with label=`Private nursing` value=`yes` on the PJ row.

---

## Cross-leak score change — confirmed

| Check | Before this pass | **After (fresh re-audit)** |
|---|---:|---:|
| 3. Website cross-leak | 21 pairs | **0** |
| 4. Shared assets | 88 groups | **65 groups** (GROUPS expansions suppressed 23) |
| 7a / 7b / 7c / 5 / 1 | all 0 | **all 0** |

The full integrity baseline is clean. The remaining manual-review work is content-completion (Check 2 missing address proxy, Check 8 address suggestions, Check 7d phone/website drift, Check 6 title/slug mismatch) — not data-integrity bugs.
