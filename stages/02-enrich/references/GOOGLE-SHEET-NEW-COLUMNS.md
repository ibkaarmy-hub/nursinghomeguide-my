# New Google Sheet Columns — Phase 1 Enrichment
> Add these columns to the right of existing columns in the Google Sheet.
> Leave blank if unknown — the website handles missing data gracefully.

---

## Columns to Add

| Column Name         | Type      | Example Values              | Notes |
|---------------------|-----------|-----------------------------|-------|
| `halal`             | Y / N     | Yes, No                     | Is the facility halal-certified? |
| `ownership_type`    | text      | Private, Government, Religious, VWO | |
| `licence_number`    | text      | JKM-JHR-001                 | JKM licence number |
| `whatsapp`          | phone     | 0167891234                  | Without +60, without spaces |
| `facebook`          | URL       | https://facebook.com/xxx    | Facebook page URL |
| `care_nursing`      | Y / N     | Yes, No                     | Offers nursing care |
| `care_dementia`     | Y / N     | Yes, No                     | Offers dementia care |
| `care_palliative`   | Y / N     | Yes, No                     | Offers palliative/hospice care |
| `care_rehab`        | Y / N     | Yes, No                     | Offers rehab/step-down care |
| `care_respite`      | Y / N     | Yes, No                     | Offers short-stay/respite |
| `care_assisted`     | Y / N     | Yes, No                     | Offers assisted living |
| `rn_24_7`           | Y / N     | Yes, No                     | Registered nurse on site 24/7 |
| `doctor_visits`     | text      | Weekly, On-call, In-house   | |
| `nurse_ratio_day`   | text      | 1:8, 1:10                   | Nurse to resident ratio (day) |
| `nurse_ratio_night` | text      | 1:15                        | Nurse to resident ratio (night) |
| `medical_physio`    | Y / N     | Yes, No                     | Physiotherapy available |
| `medical_ot`        | Y / N     | Yes, No                     | Occupational therapy |
| `medical_wound`     | Y / N     | Yes, No                     | Wound care |
| `medical_peg`       | Y / N     | Yes, No                     | Tube feeding (NG/PEG) |
| `medical_dementia_unit` | Y / N | Yes, No                   | Dedicated dementia unit |
| `medical_dialysis`  | Y / N     | Yes, No                     | Dialysis support |
| `medical_oxygen`    | Y / N     | Yes, No                     | Oxygen therapy |
| `medical_meds`      | Y / N     | Yes, No                     | Medication management |
| `total_beds`        | number    | 80                          | Total bed capacity |
| `availability`      | text      | Immediate, Within 1 month, Waitlist | |
| `four_bed_price`    | text      | RM 2,500                    | 4-bed room monthly fee |
| `dorm_price`        | text      | RM 1,800                    | Open ward / dorm monthly fee |
| `visiting_hours`    | text      | Daily 9am – 8pm             | |
| `parking`           | text      | Yes, Limited, No            | |
| `editorial_summary` | text      | 2–3 sentence editorial note | Written summary for the profile page |

---

## How to Add These Columns

1. Open your Google Sheet
2. Click the header of the last column (currently after `area`)
3. Add new columns one by one, using the exact column names above
4. Re-publish the sheet (File → Share → Publish to web → CSV → Publish)
5. The website reads directly from the sheet — no code changes needed

---

## Priority Order for Filling In

Fill in this order for maximum impact:

1. `halal` — high-demand filter for Muslim families
2. `care_nursing`, `care_dementia`, `care_palliative` — core care type filters
3. `whatsapp` — adds WhatsApp button to profile (high conversion)
4. `total_beds` + `availability` — families want to know if there's space
5. `rn_24_7` + `doctor_visits` — key trust signals
6. `medical_physio`, `medical_peg`, `medical_dialysis` — medical capability filters
7. `editorial_summary` — differentiator, AI can draft these from existing data
8. `ownership_type`, `licence_number` — trust & verification signals

---

## Notes

- The website already handles missing data gracefully (shows "?" for unknown, hides empty sections)
- Care type fields (`care_nursing` etc.) are auto-inferred from existing `care_types` text — but explicit Y/N overrides the inference
- `whatsapp` should be the number only (e.g. `0167891234`), the site adds the `wa.me/60` prefix automatically
