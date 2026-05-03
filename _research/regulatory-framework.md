# Regulatory framework & data architecture (next-phase research)

Last updated: 2026-05-03
Source: External AI research (Perplexity), pasted in by IK 2026-05-03 and stress-tested through two evaluation passes. The composite "Clinical Acuity Score" was dropped after evaluation; this file reflects the **adopted** approach: licensing-first trust labels, descriptive capability badges, contextual need-based search, and tiered verification.

---

## 1. Regulatory classification (primary trust filter)

Three Malaysian statutes govern aged-care facilities. The site labels each facility against this framework, but **avoids implying that licensing alone proves quality** — care-level matching, staffing, and pricing transparency still determine fit.

| Statute | Body | Scope |
|---|---|---|
| **Act 586** (Private Healthcare Facilities and Services Act 1998) | MOH | Private healthcare facilities — clinical oversight, doctor-led |
| **Act 506** (Care Centres Act 1993) | JKM | Pusat Jagaan — social-welfare residential or day care |
| **Act 802** (Private Aged Healthcare Facilities and Services Act) | MOH | Newer, more comprehensive elder-care framework. Widely discussed but not yet the universal operating standard. **Don't present as the live rule until verified per facility.** |

### Trust labels

| Label | When used |
|---|---|
| **MOH Licensed** | Confirmed under Act 586 / Act 802 with verified licence details |
| **JKM Registered** | Pusat Jagaan under Act 506 (the implicit baseline for our directory) |
| **Unverified listing** | No licence evidence found, or pending verification |

### Card rendering rule
**JKM Registered is the silent default — don't render it on facility cards.** ~96% of our directory is JKM, so showing it on every card is visual noise. Only render `MOH Licensed` (rare positive signal) or `Unverified listing` (warning) on cards. JKM status is shown on the facility profile detail view, not the card.

### Wording rules (avoid liability + overclaiming)

- ❌ "Gold Standard" → ✅ "Highest regulatory confidence"
- ❌ "High-dependency, doctor-led" → ✅ "Confirmed higher-acuity care capability, where documented"
- ❌ "morphine protocols" → ✅ "palliative symptom-management capability, where confirmed"
- ❌ "Cross-Border Transfer guide" → ✅ "Cross-border admission and transfer guidance"
- ❌ "Palliative Ready" → ✅ "Palliative care offered" *(descriptive, not endorsing)*
- RN 24/7 is a **verification field, not a promise** — show whether registered nurses are confirmed on duty at all times.

---

## 2. Schema upgrade

Augment the existing 56-column Facilities tab. **Don't duplicate existing columns** — the new badges READ from existing fields (`care_*`, `medical_*`, `nurse_ratio_*`) where they overlap. Add only the genuinely new fields.

### New columns to add

| Column | Type | Notes |
|---|---|---|
| Service_Type | Multi-select | `nursing_home` / `assisted_living` / `home_care` / `day_care`. Drives which top-level category page(s) the facility appears on. See [assisted-living-segment.md](assisted-living-segment.md). |
| License_Category | Enum | `MOH Licensed` / `JKM Registered` / `Unverified` |
| License_Number | Text | As shown on licence document |
| License_Verification_Date | Date | When licence evidence was checked |
| Acuity_Level | 1–4 | 1 = Independent · 2 = Low Assistance · 3 = Moderate Dependency · 4 = High Dependency (NG-tube, tracheostomy, Stage 4 sores) |
| RN_24_7 | `Confirmed` / `Unverified` | Registered nurse on-site at all times (more specific than existing `nurse_ratio_*`) |
| Nurse_In_Charge | Enum | Registered Nurse / Senior Registered Nurse / Unverified |
| Doctor_Visit_Frequency | Enum | Daily / Weekly / On-Call / Unverified |
| Pricing_Model | Enum | All-In / Base + Consumables / Base + Medical Add-ons / Unverified |
| Hidden_Costs | Text | Diapers, feeds, dressings, transport, procedure surcharges |
| SG_Transfer_Ready | `Confirmed` / `Unverified` | Logistics for Singapore→Johor family flow |
| Verification_Tier | 1 / 2 / 3 | See §4 |
| Last_Verified_On | Date | One date per facility, covers all its badges |
| Evidence_URLs | Text | Pipe-separated: licence docs, photos, contracts, brochures |

### Existing columns reused (don't duplicate)
- `medical_peg`, `medical_dementia_unit`, `medical_oxygen`, `medical_wound`, `medical_physio` → drive PEG / Dementia / Oxygen / Wound / Physio badges
- `care_palliative`, `care_dementia`, `care_rehab`, `care_respite` → drive corresponding capability badges
- `pricing_display`, `shared_price`, `private_price`, `four_bed_price`, `dorm_price` → feed price estimator

### Migration policy
Leave old columns in place. The new badge layer reads from old + new. Don't deprecate anything until the new system is fully shipped and verified.

### Data-logic rules
1. **Eligibility filter first** — down-rank `Unverified listing` facilities until licence is confirmed
2. **Care match second** — match resident needs to facility capabilities
3. **Price transparency third** — show what's included vs. billed separately
4. **Recency matters** — every facility shows a verification date and source trail

---

## 3. Capability badges

**No composite score.** Independent flags rendered alongside each facility, in two groups.

### Two-state model
Each badge is one of:
- **Confirmed** — positive evidence on file
- **Unverified** — no data (rendered greyed-out / muted)

A third "Not available" state was considered and dropped — operators don't volunteer denials, so in practice the third state was always empty. Explicit denials, when received, are captured as facility notes, not badge states.

### Group A — Clinical capability
| Badge | Source column | Definition (one-liner; publish as tooltip) |
|---|---|---|
| `RN 24/7` | `RN_24_7` | Registered nurse on duty around the clock |
| `PEG / tube feeding` | `medical_peg` | Staff trained to manage percutaneous gastrostomy and NG feeds |
| `Tracheostomy care` | new field | Staff trained to suction and manage tracheostomies |
| `Advanced wound care` | `medical_wound` | Pressure-injury management beyond basic dressings (e.g. wound vac, debridement support) |
| `Dementia secure unit` | `medical_dementia_unit` | Locked or controlled-access ward designed to prevent wandering, with trained staff |
| `Palliative care offered` | `care_palliative` | Symptom management and end-of-life support; not a guarantee of hospice-level capability |
| `Rehabilitation support` | `care_rehab` + `medical_physio` | On-site or scheduled physiotherapy and post-hospital recovery |

### Group B — Service / logistics
| Badge | Source column | Definition |
|---|---|---|
| `SG transfer ready` | `SG_Transfer_Ready` | Accepts Singaporean residents — admission workflow, currency handling, transfer logistics |
| `Halal-certified kitchen` | existing `halal` | Confirmed halal food preparation |
| `Wheelchair accessible` | existing `wheelchair` | Confirmed wheelchair-friendly throughout |

### Tag pills (not badges)
Doctor visit frequency is a 3-value enum, not a yes/no. Render as a **tag pill** (`Doctor: Weekly`, `Doctor: On-call`) alongside the badge grid, not inside it.

### Per-badge definitions
Every badge has a one-line definition published in a `badge_definitions.md` (or shown in a tooltip on hover). Definitions are written before the UI ships — an undefined badge is unfalsifiable.

---

## 4. Verification tiering

"Last verified by MD" implies the user personally checked. Doesn't scale to 350 facilities. Three tiers, each rendered with its own visual marker. **Operational workflow lives in [verification-sop.md](verification-sop.md).**

| Tier | Source | Who verifies | Card display |
|---|---|---|---|
| **1 — Operator-attested** | Operator-completed intake form / WhatsApp confirmation | Helper or IK | Badge with a small "self-reported" qualifier |
| **2 — Document-verified** | Licence, staff roster, signed contract on file | IK only (helper flags candidates) | Badge rendered plain |
| **3 — MD-confirmed** | Site visit + staff interview + photos | IK only — **deferred** until invited by facilities | Badge with a small MD-verified mark |

**One verification date per facility** (`last_verified_on`) covers all that facility's badges. If a single capability changes, bump the date and re-check the lot. Per-badge dates were considered and rejected — 2,800 states across 350 facilities is unmaintainable.

### Default state of existing 350 facilities (decision 2026-05-03)
- Default to **Tier 1** for all facilities (their original-source data was effectively operator-attested via marketing material)
- Bulk-upgrade to **Tier 2** the ~50 facilities where IK already has licence documentation on file
- Tier 3 inactive until site-visit programme starts

---

## 5. Need-based search — hybrid filter

Filter behaviour balances usefulness on launch (when most data is `Unverified`) with strictness once verification catches up.

When a user searches by need (e.g. "post-stroke"), results split into **two sections**:

1. **Confirmed match** *(top, highlighted)*
   Facilities where every required badge is `Confirmed`. The required-badge set per need:
   - Post-stroke → `RN 24/7` + `Rehabilitation support`
   - Advanced dementia → `Dementia secure unit` + `RN 24/7`
   - PEG feeding → `PEG / tube feeding` + `RN 24/7`
   - Palliative → `Palliative care offered` + `RN 24/7`
   - Tracheostomy → `Tracheostomy care` + `RN 24/7`

2. **Possibly suitable, unverified** *(below, with "we haven't verified these capabilities yet" note)*
   Facilities where required badges are `Unverified` but no badge says otherwise. Avoids hiding new or unaudited facilities while making the strictness explicit.

Section labels make the verification gap visible to users without making the filter useless on launch.

---

## 6. Differentiation pillars

Three areas where families struggle to compare and where clinical authority adds the most value:

- **Care depth** — palliative + comfort-care readiness, stroke / dementia / post-hospital rehab support, wound management, tube-feeding capability
- **Price transparency** — base monthly fee, room-type surcharge, nursing procedure fees, consumables (diapers, milk feeds, catheters, dressings), transport / escort / special-therapy charges
- **Singapore–Johor pipeline** — admission workflow, transfer guidance, currency handling, family visit logistics, emergency escalation path. **Logistics, not a clinical guarantee.**

---

## 7. UI / UX features

### Need-based search
Search by medical condition, not just location: post-stroke · dementia · bedridden · PEG feeding · tracheostomy · palliative · rehab. Hybrid filter behaviour per §5.

### Filters
Licence tier · RN coverage · doctor frequency · specific capabilities · price model. Optional "high-acuity only" toggle.

### Capability badges
See §3. Two groups (Clinical / Service), two states (Confirmed / Unverified), tooltip definitions.

### Verification display
Per-facility `Last verified` date + tier marker (1/2/3) + evidence link. No per-badge timestamps.

### Price estimator
Base fee + room type + capability surcharges (PEG, daily physio, etc.) + consumables + optional services. Cross-reference [pricing-benchmarks.md](pricing-benchmarks.md).

---

## 8. Example facility display (target)

```
[Card view]
Sunway Sanctuary                            ⭐ MOH Licensed
Sunway City, Selangor

Clinical:  RN 24/7 ✓   PEG ✓   Dementia secure ✓   Palliative ✓
Service:   SG transfer ✓   Halal ✓   Wheelchair ✓
Doctor:    Weekly

RM 6,500–15,000 / month · Base + medical add-ons
Last verified: 2026-04-18 · Tier 3 (MD-confirmed)
```

```
[Lower-data facility]
Pusat Jagaan Example                        Unverified listing
Cheras, Kuala Lumpur

Clinical:  RN 24/7 ?   PEG ?   Dementia secure ?   Palliative ?
Service:   Halal ✓
Doctor:    Unverified

RM 2,800–4,200 / month · Base + consumables
Last verified: 2026-03-02 · Tier 1 (operator-attested)
```

✓ = Confirmed · ? = Unverified

---

## 9. Caveats before implementation

- Verify Act 802's actual operational status with MOH before labelling facilities under it
- Confirm RN-staffing claims against MOH staffing standards (registered nurse / senior registered nurse in charge) before publishing as a badge
- Don't apply "Palliative care offered" badge unless the facility explicitly confirms trained symptom-management capability
- Cross-reference [pricing-benchmarks.md](pricing-benchmarks.md) before publishing any price estimator output
- Write `badge_definitions.md` before the badge UI ships — every badge needs a published one-line definition
- Decide a default verification tier for the 350 existing facilities (likely Tier 1 for everything until re-verified) before bulk migration
