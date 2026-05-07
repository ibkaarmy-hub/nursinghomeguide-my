# JKM Licence Field Refactor — Schema & Sample Data

## Column Reference

**Delete:** Column 23 (`licence_number` — old British spelling, single field)

**Rename/consolidate to columns 58–64:**

| Position | Old Name | New Name | Data Type | Purpose | Examples |
|----------|----------|----------|-----------|---------|----------|
| 58 | `license_category` | `jkm_status` | Enum | JKM registration status | `registered` / `unverified` / `no_register` |
| 59 | `license_number` | `jkm_licence_number` | Text | Official JKM registration number | `JKM/2024/NHT/001234` |
| 60 | `license_verification_date` | `jkm_verification_date` | Date (YYYY-MM-DD) | When you verified it | `2026-05-05` |
| 61 | `license_expiry` | `jkm_expiry_date` | Date (YYYY-MM-DD) | JKM certificate expiry | `2027-05-05` |
| 62 | `license_expiry_warning` | `jkm_expiry_warning` | Text | Flag if within 6 months of expiry | `yes` / `no` / *(blank)* |
| 63 | *(new)* | `jkm_verified_by` | Enum | Source of verification | `jkm_call` / `cert_photo` / `operator_claim` / *(blank)* |
| 64 | *(new)* | `moh_status` | Enum | MOH nursing licence status | `licensed` / `unverified` / `no_apply` / *(blank)* |

---

## Column Definitions (for spreadsheet tooltip/header)

**jkm_status**
- `registered` — Confirmed JKM registration
- `unverified` — Not yet verified
- `no_register` — Facility claims no JKM requirement (e.g. < 4 residents)
- *(blank)* — Unknown (pending outreach)

**jkm_licence_number**
- The actual registration number from the JKM Sijil Pendaftaran. Leave blank if unverified.

**jkm_verification_date**
- YYYY-MM-DD format. Date when you (the team) confirmed the status. Used to track data freshness.

**jkm_expiry_date**
- YYYY-MM-DD format. Expiry of the JKM certificate. Used to flag renewals.

**jkm_expiry_warning**
- `yes` if expiry_date is within 180 days of today, `no` otherwise. Can be auto-calculated.
- *(leave blank)* if expiry_date is blank.

**jkm_verified_by**
- `jkm_call` — You called JKM district office & they confirmed (highest confidence)
- `cert_photo` — Facility showed you the certificate in person or emailed a photo
- `operator_claim` — Facility said they're registered, not independently verified
- *(blank)* — Not yet verified

**moh_status**
- `licensed` — Confirmed MOH Private Healthcare Licence (Act 586)
- `unverified` — Not yet checked
- `no_apply` — Facility does not provide nursing care / does not require MOH
- *(blank)* — Unknown / not checked yet

---

## Sample Data — 10 Facilities

Copy the data below into the appropriate columns (58–64) in your sheet.

### Row 1: EHA Golfview Eldercare Mansion (Johor Jaya) — Registered, verified via JKM call

```
jkm_status                    | registered
jkm_licence_number            | JKM/2024/JHR/00045
jkm_verification_date         | 2026-05-02
jkm_expiry_date               | 2027-05-02
jkm_expiry_warning            | no
jkm_verified_by               | jkm_call
moh_status                    | unverified
```

### Row 2: Noble Care Nursing Home (Jalan Ipoh, KL) — Registered, certificate seen

```
jkm_status                    | registered
jkm_licence_number            | JKM/2023/KUL/00078
jkm_verification_date         | 2026-04-28
jkm_expiry_date               | 2026-09-15
jkm_expiry_warning            | yes
jkm_verified_by               | cert_photo
moh_status                    | licensed
```

### Row 3: Blissful Senior Care Centre (Selangor) — Registered, operator claim

```
jkm_status                    | registered
jkm_licence_number            | JKM/2024/SGR/00156
jkm_verification_date         | 2026-04-15
jkm_expiry_date               | 2027-04-15
jkm_expiry_warning            | no
jkm_verified_by               | operator_claim
moh_status                    | unverified
```

### Row 4: Genesis Life Care (Branch A) — Not yet verified

```
jkm_status                    | unverified
jkm_licence_number            | 
jkm_verification_date         | 
jkm_expiry_date               | 
jkm_expiry_warning            | 
jkm_verified_by               | 
moh_status                    | unverified
```

### Row 5: My Aged Care (PJ Branch 1) — Does not apply (small home)

```
jkm_status                    | no_register
jkm_licence_number            | 
jkm_verification_date         | 2026-05-01
jkm_expiry_date               | 
jkm_expiry_warning            | 
jkm_verified_by               | operator_claim
moh_status                    | no_apply
```

### Row 6: Mintygreen Home (Subang) — Registered, verified via JKM call

```
jkm_status                    | registered
jkm_licence_number            | JKM/2023/SGR/00089
jkm_verification_date         | 2026-03-20
jkm_expiry_date               | 2026-08-10
jkm_expiry_warning            | yes
jkm_verified_by               | jkm_call
moh_status                    | licensed
```

### Row 7: Attia Nursing Care (Bangsar) — Registered, certificate seen

```
jkm_status                    | registered
jkm_licence_number            | JKM/2024/KUL/00102
jkm_verification_date         | 2026-04-22
jkm_expiry_date               | 2027-04-22
jkm_expiry_warning            | no
jkm_verified_by               | cert_photo
moh_status                    | licensed
```

### Row 8: Woodrose Senior Residences (Shariah-compliant) — Unverified

```
jkm_status                    | unverified
jkm_licence_number            | 
jkm_verification_date         | 
jkm_expiry_date               | 
jkm_expiry_warning            | 
jkm_verified_by               | 
moh_status                    | unverified
```

### Row 9: Green Acres (Selangor) — Registered, JKM call

```
jkm_status                    | registered
jkm_licence_number            | JKM/2023/SGR/00167
jkm_verification_date         | 2026-02-15
jkm_expiry_date               | 2027-02-15
jkm_expiry_warning            | no
jkm_verified_by               | jkm_call
moh_status                    | no_apply
```

### Row 10: Harvestars Home (Johor) — No registration (facility claim)

```
jkm_status                    | no_register
jkm_licence_number            | 
jkm_verification_date         | 2026-04-10
jkm_expiry_date               | 
jkm_expiry_warning            | 
jkm_verified_by               | operator_claim
moh_status                    | no_apply
```

---

## How to Implement

1. **In Google Sheet:**
   - Delete column 23 (`licence_number`)
   - Insert 2 new columns after position 62 (current `license_expiry_warning`) for `jkm_verified_by` and `moh_status`
   - Rename the 5 existing columns (58–62) as shown in the table above
   - Add the sample data to the corresponding facilities
   - Use data validation (dropdown) for enum columns (jkm_status, jkm_verified_by, moh_status)

2. **In data.js:**
   - Update the column indices where you reference `licence_number` / `license_*` fields
   - Add helpers to:
     - Flag if `jkm_status === 'registered'` for a "JKM verified" badge
     - Flag if `jkm_expiry_warning === 'yes'` for a renewal alert
     - Check `jkm_verified_by` confidence level

3. **On facility profile (facility.html):**
   - Surface JKM status on the **Care tab** (near staffing/clinical info)
   - Example: 
     ```
     JKM Status: Registered (verified via JKM call, expires May 2027)
     ```
   - If `jkm_status === 'unverified'`: show as "To be verified — ask on visit"
   - If `jkm_status === 'no_register'`: show as "Facility indicates < 4 residents"

4. **On state listing pages (johor.html, etc.):**
   - Add a filter: "Show only JKM-registered homes"
   - Add a warning tag next to facilities where `jkm_expiry_warning === 'yes'`

---

## Notes

- The `jkm_verification_date` is **your verification date**, not the JKM issue date. Use it to track data freshness ("Last checked 2 months ago").
- The `jkm_verified_by` field lets you weight data quality: JKM call > cert photo > operator claim.
- MOH status is a **separate signal** — a facility can be JKM-registered but not MOH-licensed (which is fine for non-nursing care).
- For **batch population**, you can use a Google Sheets formula to auto-calculate `jkm_expiry_warning`:
  ```
  =IF(AND(D2<>"", D2<=TODAY()+180), "yes", "no")
  ```
  where D2 is the `jkm_expiry_date` column.

