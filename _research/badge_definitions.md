# Capability badge definitions

Last updated: 2026-05-03
Status: Locked. These are the published one-liner definitions surfaced as tooltips on the badge UI. Per [regulatory-framework.md §3](regulatory-framework.md), every badge MUST have a definition here before it ships in the UI.

Each badge has two states only:

- **Confirmed** — positive evidence is on file (operator-attested at Tier 1, or document-verified at Tier 2)
- **Unverified** — no positive evidence yet (rendered greyed out; absent ≠ denied)

Badge values are derived from the live data per the source-column mapping below. A value of `yes` (case-insensitive) on the source column flips the badge to Confirmed; everything else (blank, `no`, `not stated`, `unknown`) is Unverified.

---

## Trust label (card + profile)

| Label | Definition | Source |
|---|---|---|
| **MOH Licensed** | Confirmed under Act 586 (Private Healthcare Facilities) or Act 802 (Private Aged Healthcare Facilities), with verified licence details on file. | `_effective_license_category` = `MOH Licensed` |
| **Unverified listing** | No licence evidence on file yet, or licence has expired and not been re-verified. We have not yet confirmed regulatory standing. | `_effective_license_category` = `Unverified` |
| **JKM Registered** *(silent default — profile only, never on cards)* | Pusat Jagaan registered under Act 506 (Care Centres Act 1993). The implicit baseline for ~96% of our directory; rendered on the profile detail view only, to avoid visual noise. | `_effective_license_category` = `JKM Registered` |

---

## Group A — Clinical capability

| Badge | One-liner (tooltip) | Source column |
|---|---|---|
| **RN 24/7** | Registered nurse confirmed on duty around the clock. | `rn_24_7` |
| **PEG / tube feeding** | Staff trained to manage percutaneous gastrostomy (PEG) and nasogastric tube feeds. | `medical_peg` |
| **Tracheostomy care** | Staff trained to suction and manage tracheostomies. | `medical_tracheostomy` (new — falls back to Unverified until rolled out) |
| **Advanced wound care** | Pressure-injury management beyond basic dressings (e.g. wound vac, debridement support). | `medical_wound` |
| **Dementia secure unit** | Locked or controlled-access ward designed to prevent wandering, with trained staff. | `medical_dementia_unit` |
| **Palliative care offered** | Symptom management and end-of-life support. Not a guarantee of hospice-level capability. | `care_palliative` |
| **Rehabilitation support** | On-site or scheduled physiotherapy and post-hospital recovery support. | `care_rehab` + `medical_physio` (either `yes` flips it Confirmed) |

## Group B — Service / logistics

| Badge | One-liner (tooltip) | Source column |
|---|---|---|
| **SG transfer ready** | Accepts Singaporean residents — admission workflow, currency handling, and transfer logistics in place. | `sg_transfer_ready` |
| **Halal-certified kitchen** | Halal food preparation, typically with JAKIM certification. | `halal` |
| **Wheelchair accessible** | Confirmed wheelchair-friendly throughout. | `wheelchair` |

---

## Tag pills (separate from the badge grid)

Doctor visit frequency is a multi-value enum, not a yes/no, so it renders as a tag pill alongside the badge grid:

| Pill | Possible values |
|---|---|
| **Doctor: Daily / Weekly / On-call / Unverified** | From `doctor_visit_frequency`. Rendered in muted style when `Unverified`. |

---

## Verification marker (profile only — not on cards)

The badge grid is followed by a small per-facility line:

```
Last verified: <date> · Tier <1/2/3> (<source>)
```

| Tier | Source phrase |
|---|---|
| 1 | operator-attested |
| 2 | document-verified |
| 3 | MD-confirmed |

Read from `_effective_verification_tier` and `last_verified_on` (after staleness handling in `data.js`). If the licence has expired (`_licence_expired = true`), the trust label is forced to `Unverified listing` regardless of the stored category.

---

## Hybrid need-based search — required badge sets

Per [regulatory-framework.md §5](regulatory-framework.md), each clinical need maps to a set of required badges that must ALL be Confirmed for the facility to land in the "Confirmed match" section. Otherwise it falls into "Possibly suitable, unverified".

| User need | Required badges (all Confirmed) |
|---|---|
| Post-stroke | `RN 24/7` + `Rehabilitation support` |
| Advanced dementia | `Dementia secure unit` + `RN 24/7` |
| PEG feeding | `PEG / tube feeding` + `RN 24/7` |
| Palliative | `Palliative care offered` + `RN 24/7` |
| Tracheostomy | `Tracheostomy care` + `RN 24/7` |

If the user filters by a need and zero facilities have all required badges confirmed, the UI shows the "Possibly suitable, unverified" section only and a banner explaining that verification is in progress.

---

## What is NOT a badge

These are recorded but rendered elsewhere on the profile, NOT in the badge grid:

- Acuity level (1–4) — shown as a context line in the Care tab, not a badge
- Pricing model — Pricing tab
- Hidden costs — Pricing tab
- Bed count, room types — Pricing tab
- Languages, religion — Quick Facts on Overview tab
- Visiting hours — Quick Facts

Adding a new badge requires:
1. A definition row in this file (one-liner + source column)
2. A backing column in the Sheet
3. A UI render path in `badges.js`
4. A note here in the changelog below
