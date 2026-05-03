# Phase A schema upgrade — Sheet columns + parser

Last updated: 2026-05-03
Status: data.js parser + render-layer staleness shipped this session. Sheet column additions still need to be applied by IK (script below). Badge UI is a separate session.

Spec sources:
- [regulatory-framework.md](regulatory-framework.md) §2 (column list, data-logic rules)
- [verification-sop.md](verification-sop.md) §6, §8 (staleness rules, columns referenced by SOP)
- [assisted-living-segment.md](assisted-living-segment.md) §3 (`service_type` field)

---

## 1. Columns to add to Facilities tab

Sheet ID: `1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk`
Tab gid: `292378871`

All headers are lowercase snake_case to match existing convention (`care_types`, `medical_peg`, `nurse_ratio_day`, etc.).

### Service segmentation
| Column | Type | Default | Notes |
|---|---|---|---|
| `service_type` | Text (pipe-separated multi-select) | `nursing_home` | Values: `nursing_home`, `assisted_living`, `home_care`, `day_care`. Drives the future `/assisted-living/`, `/home-care/`, `/day-care/` category pages. |

### Licensing
| Column | Type | Default | Notes |
|---|---|---|---|
| `license_category` | Enum | `Unverified` | `MOH Licensed` / `JKM Registered` / `Unverified`. Render layer auto-downgrades to `Unverified` if `license_expiry` has passed. |
| `license_number` | Text | *(blank)* | **Never displayed publicly.** Stored for IK's records only. |
| `license_verification_date` | Date (YYYY-MM-DD) | *(blank)* | When IK or helper checked the licence document. |
| `license_expiry` | Date (YYYY-MM-DD) | *(blank)* | From the licence document itself. Drives auto-downgrade. |
| `license_expiry_warning` | Boolean (`TRUE`/`FALSE`) | `FALSE` | Auto-derived in the render layer when expiry is within 30 days. The Sheet column exists so a future workflow can also flag it for outreach. |

### Clinical capability detail (extend existing `medical_*` / `care_*` / `nurse_ratio_*`)
| Column | Type | Default | Notes |
|---|---|---|---|
| `acuity_level` | Integer 1–4 | *(blank)* | 1 = Independent, 2 = Low Assistance, 3 = Moderate Dependency, 4 = High Dependency. |
| `rn_24_7` | Enum | `Unverified` | `Confirmed` / `Unverified`. More specific than existing `nurse_ratio_day`/`nurse_ratio_night`. |
| `nurse_in_charge` | Enum | `Unverified` | `Registered Nurse` / `Senior Registered Nurse` / `Caregiver-supervisor` / `Unverified`. |
| `doctor_visit_frequency` | Enum | `Unverified` | `Daily` / `Weekly` / `Fortnightly` / `Monthly` / `On-Call` / `Unverified`. |

### Pricing transparency
| Column | Type | Default | Notes |
|---|---|---|---|
| `pricing_model` | Enum | `Unverified` | `All-In` / `Base + Consumables` / `Base + Medical Add-ons` / `Other` / `Unverified`. |
| `hidden_costs` | Text | *(blank)* | Free text — diapers, feeds, dressings, transport, procedure surcharges. |

### Singapore–Johor pipeline
| Column | Type | Default | Notes |
|---|---|---|---|
| `sg_transfer_ready` | Enum | `Unverified` | `Confirmed` / `Unverified`. Logistics flag, not a clinical guarantee. |

### Verification (per SOP §8)
| Column | Type | Default | Notes |
|---|---|---|---|
| `verification_tier` | Integer 0–3 | `1` | 0 = Unverified, 1 = Operator-attested, 2 = Document-verified, 3 = MD-confirmed. Render layer auto-downgrades stale tiers (Tier 1 > 12mo → 0, Tier 2 > 24mo → 1). |
| `last_verified_on` | Date (YYYY-MM-DD) | `2026-01-01` | One date per facility, covers all badges. |
| `verified_by` | Text | `"Original source scrape"` | Free text — name + (operator-attested / document-verified / MD-confirmed). |
| `evidence_ref` | Text (URL) | *(blank)* | Private Drive folder URL. Never displayed publicly. |

### Outreach workflow (per SOP §3)
| Column | Type | Default | Notes |
|---|---|---|---|
| `outreach_status` | Enum | `pending` | `pending` / `sent` / `delivered` / `read` / `responded` / `no_response` / `declined` / `bounced`. |
| `outreach_last_attempt` | Date (YYYY-MM-DD) | *(blank)* | |
| `outreach_notes` | Text | *(blank)* | |
| `tier_2_review_pending` | Boolean (`TRUE`/`FALSE`) | `FALSE` | Helper sets this when operator volunteers documents; IK reviews in batch. |

### Existing columns reused (do NOT duplicate)
Per regulatory-framework.md §2, the future badge layer reads these existing fields:

- `medical_peg`, `medical_dementia_unit`, `medical_oxygen`, `medical_wound`, `medical_physio` → drive PEG / Dementia / Oxygen / Wound / Physio badges
- `care_palliative`, `care_dementia`, `care_rehab`, `care_respite` → drive corresponding capability badges
- `pricing_display`, `shared_price`, `private_price`, `four_bed_price`, `dorm_price` → feed price estimator
- `halal`, `wheelchair` → service badges
- `state`, `area`, `latitude`, `longitude` → unchanged

A new `tracheostomy_care` column was considered but deferred — currently no facility in our directory has confirmed this capability, and the badge can be added when the first one does.

---

## 2. Sheet update script

Run once. Adds the new columns at the end of the Facilities tab and backfills defaults for the existing 350 live rows. Idempotent — re-running will skip columns that already exist.

```python
# add_phase_a_columns.py
import gspread
from datetime import date

SHEET_ID = "1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk"
WORKSHEET_NAME = "Facilities"  # gid 292378871

NEW_COLUMNS = [
    # service segmentation
    ("service_type", "nursing_home"),
    # licensing
    ("license_category", "Unverified"),
    ("license_number", ""),
    ("license_verification_date", ""),
    ("license_expiry", ""),
    ("license_expiry_warning", "FALSE"),
    # clinical capability
    ("acuity_level", ""),
    ("rn_24_7", "Unverified"),
    ("nurse_in_charge", "Unverified"),
    ("doctor_visit_frequency", "Unverified"),
    # pricing transparency
    ("pricing_model", "Unverified"),
    ("hidden_costs", ""),
    # SG pipeline
    ("sg_transfer_ready", "Unverified"),
    # verification
    ("verification_tier", "1"),
    ("last_verified_on", "2026-01-01"),
    ("verified_by", "Original source scrape"),
    ("evidence_ref", ""),
    # outreach
    ("outreach_status", "pending"),
    ("outreach_last_attempt", ""),
    ("outreach_notes", ""),
    ("tier_2_review_pending", "FALSE"),
]

gc = gspread.service_account()  # uses ~/.config/gspread/service_account.json
sh = gc.open_by_key(SHEET_ID)
ws = sh.worksheet(WORKSHEET_NAME)

header = ws.row_values(1)
existing = set(header)
n_rows = len(ws.col_values(1))  # includes header row
data_rows = n_rows - 1

next_col_idx = len(header) + 1
for col_name, default_value in NEW_COLUMNS:
    if col_name in existing:
        print(f"skip (exists): {col_name}")
        continue
    # Set header
    ws.update_cell(1, next_col_idx, col_name)
    # Backfill default for all data rows
    if default_value != "" and data_rows > 0:
        col_letter = gspread.utils.rowcol_to_a1(1, next_col_idx)[:-1]
        rng = f"{col_letter}2:{col_letter}{n_rows}"
        ws.update(rng, [[default_value]] * data_rows)
    print(f"added: {col_name} (default={default_value!r})")
    next_col_idx += 1

print("done.")
```

Run with: `python add_phase_a_columns.py`

After it finishes, manually re-publish the Facilities tab (File → Share → Publish to web — the existing publish should auto-refresh, but the published CSV has a known 5-minute delay).

---

## 3. data.js render-layer staleness (shipped this session)

The CSV parser is column-name driven, so the new columns flow through automatically. New behaviour added to `loadFacilities()`:

- `applyVerificationStaleness(row)` runs on every facility row
- Reads `verification_tier`, `last_verified_on`, `license_expiry`
- Computes:
  - `_effective_verification_tier` — Tier 1 > 12mo → 0, Tier 2 > 24mo → 1
  - `_effective_license_category` — forced to `'Unverified'` if `license_expiry < today`
  - `_licence_expired` — boolean
  - `_licence_expiry_warning` — boolean, TRUE if expiry within 30 days
- Original Sheet values are preserved on the row; `_effective_*` is what the future badge UI reads

Existing card / profile rendering is unaffected — it doesn't read any of the new fields yet.

---

## 4. What's NOT in this phase

Deferred to follow-up sessions per the task brief:

- Badge UI (clinical + service badge grid on cards and profiles)
- Hybrid need-based search filter (Confirmed match / Possibly suitable, unverified)
- `/assisted-living/` category pages and re-tagging audit
- Updates to `generate_facility_pages.py` and `generate_sitemap.py` for new URL structure
- Operator intake form (Google Form → Sheet tab)
- Drive folder bootstrap (`NursingHomeGuide-Verifications/`)
