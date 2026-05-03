# Verification SOP — for IK and outreach helper

Last updated: 2026-05-03
Status: Operational document. Updated as the workflow evolves. Both IK and the outreach helper follow this; deviations get logged in the facility's private notes, not invented on the fly.

---

## Decisions locked (2026-05-03)

| Topic | Decision |
|---|---|
| Storage | Google Drive folder owned by IK, shared read+write with trusted helper |
| Folder structure | One folder per facility, named by `slug` |
| Publishing licence numbers | **No.** Site shows `tier label + date` only |
| Default tier for existing 350 | **Tier 1** for all by default; bulk-upgrade to **Tier 2** where documentation already exists on file |
| Tier 3 (MD-confirmed) | **Deferred.** Activated only when facilities invite IK for a site visit; will include photos + staff interview. Not part of the launch workflow. |
| Intake mechanism | Google Form writing to a Sheet tab (or standalone claim form), one form per facility submission |
| Outreach by | Trained helper (Tier 1); IK personally for Tier 2 upgrades and disputed cases |

---

## 1. Drive folder structure

Owner: IK. Shared read+write with one helper.

```
NursingHomeGuide-Verifications/
├── _templates/
│   ├── operator-outreach-whatsapp.md      ← canned WhatsApp message
│   ├── operator-outreach-email.md         ← canned email
│   ├── intake-form-questions.md           ← reference copy of the Google Form fields
│   └── evidence-rulebook.md               ← what counts as Tier 2 evidence per badge
├── _logs/
│   └── outreach-log.csv                   ← one row per outreach attempt (slug, date, channel, status)
└── <facility-slug>/
    ├── operator-correspondence/           ← screenshots of WhatsApp / email threads
    ├── licence/                           ← MOH or JKM document scans (private)
    ├── staffing/                          ← staff rosters, RN proof
    ├── pricing/                           ← rate cards, signed quotes
    ├── photos/                            ← photos provided by operator (NOT for site display)
    └── notes.md                           ← private observations from outreach
```

**Rule: nothing in `<facility-slug>/` ever appears on the public site.** The public site reads from the Google Sheet only. The Drive folder is the evidence trail behind the Sheet entries.

---

## 2. Tier definitions (recap)

| Tier | Source of truth | Who can verify | Cadence |
|---|---|---|---|
| **0 — Unverified** | No data on file | — | Default state |
| **1 — Operator-attested** | Operator-completed intake form OR WhatsApp/email confirmation, screenshotted | Helper or IK | 12 months |
| **2 — Document-verified** | Primary documents on file (licence, roster, contract) | IK only (helper flags candidates, IK confirms) | 24 months / on licence expiry |
| **3 — MD-confirmed** | Site visit + staff interview + photos | IK only | Deferred — activated when invited |

---

## 3. Workflow — Helper (Tier 1 outreach)

### Setup (one-time)
1. IK adds helper to the Drive folder (read+write).
2. IK shares the master Google Sheet with helper (edit access on the verification columns: `verification_tier`, `last_verified_on`, `verified_by`, `evidence_ref`, `outreach_status`, `outreach_last_attempt`, `outreach_notes`).
3. Helper reads this SOP end-to-end. IK runs through one facility together as a worked example.

### Daily / weekly outreach loop

**Step 1 — Pick a batch.** Open the Sheet, filter to `outreach_status = pending` AND `verification_tier ≤ 1`. Take 10 facilities at a time (avoid overcommitting; quality > volume).

**Step 2 — Pre-flight per facility.**
- Confirm facility is still operational (quick Google Maps check)
- Confirm primary contact (phone, WhatsApp, email) is current
- Open the facility's Drive folder; create it if it doesn't exist

**Step 3 — Send outreach.** Use one of two templates from `_templates/`:

#### WhatsApp template (preferred)
```
Hi, this is <helper name> from NursingHomeGuide.my, Malaysia's
independent nursing home and assisted living guide.

We've published a profile of <facility name> at:
<facility URL>

To make sure the information is accurate and up-to-date, we'd like
to ask you to confirm a short list of facts about your facility
(licensing, staff coverage, services, pricing model). It takes about
5 minutes.

Once verified, your profile will display a "Verified — operator-
confirmed" badge with today's date, which families looking for care
can see.

Form link: <form URL with prefilled facility ID>

If you'd prefer to confirm by reply on WhatsApp, just say so and
I'll send the questions here.

Terima kasih.
```

#### Email template
Same content, more formal greeting, same form link.

**Step 4 — Log the attempt.** Add a row to `_logs/outreach-log.csv`:
```
slug, date, channel, helper_name, status
```
Statuses: `sent` / `delivered` / `read` / `responded` / `no_response` / `declined` / `bounced`

Update the Sheet:
- `outreach_status = sent`
- `outreach_last_attempt = today`

**Step 5 — Follow up.** If no response after **5 working days**, send one polite reminder. If still no response after another 5 working days, mark `outreach_status = no_response`, **stop chasing**, leave at Tier 0.

**Step 6 — When response arrives.**

If operator filled the form:
- Open the form response in the Sheet tab; copy answered values into the main Facilities tab
- Save a screenshot of the form response to `<slug>/operator-correspondence/intake-<date>.png`
- Update Sheet:
  - `verification_tier = 1`
  - `last_verified_on = response date`
  - `verified_by = <helper name> (operator-attested)`
  - `evidence_ref = <Drive folder URL>`
  - `outreach_status = responded`

If operator answered by WhatsApp/email reply:
- Walk through the form questions one by one in the chat thread
- Screenshot each answer; save the full thread as `<slug>/operator-correspondence/whatsapp-<date>.png`
- Manually enter answers in the Sheet
- Same Sheet updates as above, with `verified_by = <helper name> (operator-attested via WhatsApp)`

**Step 7 — Flag for IK review** *(this is how Tier 2 candidates get surfaced)*

If the operator volunteers documents (licence scan, photo of certificate, signed rate card), save them in the right sub-folder (`/licence/`, `/pricing/`, `/staffing/`). Then in the Sheet, set `tier_2_review_pending = TRUE`. **Do not raise the tier yourself** — IK reviews these in batch and decides which qualify under the rulebook.

### What helper does NOT do
- Does **not** create or change badge values directly. The intake form drives those.
- Does **not** raise verification tier above 1.
- Does **not** publish anything; the Sheet → site pipeline runs on IK's schedule.
- Does **not** make claims about facility quality. Outreach is fact-collection, not opinion.
- Does **not** share Drive contents externally. Documents stay private.

---

## 4. Workflow — IK (Tier 2 review + curation)

### Weekly Tier 2 review session (~1 hour)

**Step 1 — Pull review queue.** Filter Sheet to `tier_2_review_pending = TRUE`.

**Step 2 — For each candidate facility:**
- Open the Drive folder, review documents in `/licence/`, `/staffing/`, `/pricing/`
- Cross-check each badge against the **Evidence Rulebook (§6)** below
- For each badge that has supporting evidence: confirm it qualifies for Tier 2
- Update Sheet:
  - `verification_tier = 2` (only if at least the licence badge qualifies)
  - `last_verified_on = today`
  - `verified_by = "Dr Ibkaar Mohamad Yatim (document-verified)"`
  - `evidence_ref = <Drive folder URL>`
  - `licence_expiry = <date>` (from licence document)
  - `tier_2_review_pending = FALSE`
- If the licence is expired or evidence is insufficient: leave at Tier 1, note in `outreach_notes`, set `tier_2_review_pending = FALSE`

**Step 3 — Bulk-upgrade existing 350 facilities (one-off).**
For the existing directory, IK runs through:
- Identify facilities where licence documentation already exists in IK's archive (JKM directory hits, MDAC listings, brochures collected during the original scrape)
- Move those documents into the appropriate `<slug>/licence/` folder
- Run the Tier 2 review process above
- Estimated: ~50 facilities qualify → ~half a day of focused work

### Disputes / corrections
If an operator disputes their public profile content:
- Helper escalates to IK with the operator's exact message
- IK reviews against current Sheet entry + evidence on file
- IK responds personally; never amends silently
- All correspondence saved in the facility's `operator-correspondence/` folder

---

## 5. Operator intake form — questions

Build as a Google Form, output rows to a tab in the master Sheet. Pre-fill facility name + slug via URL parameters when sending.

### Section A — Identity (pre-filled)
1. Facility name *(read-only, pre-filled)*
2. Address *(read-only, pre-filled)*
3. Your name and role at the facility *(short text)*
4. Date of submission *(auto)*

### Section B — Licensing
5. What licence does your facility hold? *(multiple choice)*
   - MOH-licensed under Act 586 (Private Healthcare Facilities)
   - MOH-licensed under Act 802 (Private Aged Healthcare Facilities)
   - JKM-registered under Act 506 (Pusat Jagaan)
   - Multiple — please specify *(text follow-up)*
   - None / pending
6. Licence expiry month and year *(month/year picker)*
7. Are you willing to share a copy of your licence with us privately for verification? *(yes / no — informational only; not auto-promoted to Tier 2)*

### Section C — Capacity
8. Total bed count *(number)*
9. Room types offered *(multi-select)*: dormitory · 4-bed · shared (2-bed) · single · single en-suite · suite
10. Approximate current occupancy *(percentage; optional)*

### Section D — Staffing
11. Is a registered nurse (RN) on duty 24/7? *(yes / no / no — covered nurse on call)*
12. Person in charge during shifts *(multiple choice)*: Registered Nurse · Senior Registered Nurse · Caregiver-supervisor · Other
13. Doctor visit frequency *(multiple choice)*: Daily · Weekly · Fortnightly · Monthly · On-call only

### Section E — Care capabilities
For each of the following, select: *Yes — we offer this* · *No — we do not* · *Limited — please describe*
14. Dementia care
15. Dedicated dementia secure unit (locked / controlled access)
16. Post-stroke rehabilitation support
17. Palliative care (symptom management, end-of-life support)
18. PEG / tube feeding management
19. Tracheostomy care
20. Advanced wound care (beyond basic dressings)
21. Physiotherapy on-site
22. Oxygen therapy on-site

### Section F — Pricing
23. Pricing model *(multiple choice)*: All-in monthly fee · Base fee + consumables billed separately · Base fee + medical add-ons billed separately · Other
24. Approximate monthly fee range *(text — e.g. "RM 2,800 – RM 4,500 depending on room")*
25. What is NOT included in the base fee? *(multi-select)*: Diapers · Milk feeds / formula · Wound dressings · Medication · Doctor visits · Physiotherapy sessions · Transport to appointments · Special diets · Other (please specify)

### Section G — Service mix
26. Which services do you offer? *(multi-select)*: Long-term residential nursing care · Assisted living / independent senior living · Day care · Home care (carers visit residents at home) · Respite care
27. Do you accept Singaporean residents? *(yes / no)*
28. Halal-certified kitchen? *(yes / no / partially)*
29. Wheelchair accessible throughout? *(yes / no / partially)*
30. Languages spoken by staff *(multi-select)*: English · Bahasa Melayu · Mandarin · Cantonese · Hokkien · Tamil · Other

### Section H — Permission and consent
31. *(checkbox, required)* I confirm that I am authorised to provide this information on behalf of the facility, and I consent to NursingHomeGuide.my displaying this information on the facility's public profile, attributed as "self-reported by the operator" with today's date.
32. *(checkbox, required)* I understand that providing inaccurate information may result in the profile being flagged or marked as unverified.
33. Anything else you'd like us to know? *(long text, optional)*

---

## 6. Evidence rulebook — what qualifies for Tier 2

Tier 2 requires **at least one piece of primary evidence** for the badges being upgraded. Operator email/WhatsApp claims alone are Tier 1, no matter how detailed. Any of the following count as primary evidence:

| Badge | Tier 2 evidence |
|---|---|
| **MOH Licensed** | Photo or scan of MOH licence document with operator name, address, and current expiry date legible |
| **JKM Registered** | (a) JKM registration certificate scan, OR (b) facility appears in current JKM published directory (helper / IK cross-checks) |
| **RN 24/7** | Operator-provided staff roster covering at least 7 consecutive days, showing RN names + shift coverage across all 24-hour periods. Names may be redacted; registration numbers visible. |
| **Doctor frequency (Daily / Weekly / etc.)** | Doctor's letter on letterhead, OR signed visit log, OR named contracted MO/GP with practice details |
| **PEG / tube feeding** | (a) Photo of in-use PEG equipment + nursing certification of trained staff, OR (b) operator letter on letterhead naming trained nurses |
| **Tracheostomy care** | Same standard as PEG |
| **Advanced wound care** | Equipment photo (wound vac etc.) + nursing certification, OR partnership letter with a wound-care specialist |
| **Dementia secure unit** | Photos showing locked-unit access controls + door log, OR floor plan showing controlled access perimeter |
| **Palliative care offered** | Written confirmation on operator letterhead of trained staff + symptom-management protocols, OR partnership letter with a palliative-care service |
| **Pricing model + hidden costs** | Signed contract / quote / dated rate card from the operator |
| **Halal-certified kitchen** | JAKIM halal certification document |
| **SG transfer ready** | Operator letter confirming admission process for Singaporean residents + currency policy |

### What does NOT count as Tier 2 evidence
- Operator's own marketing website screenshots (that's Tier 1)
- Verbal confirmation by phone (Tier 1)
- Third-party blog mentions
- Photos taken from the facility's social media without operator confirmation
- Partial documents (page 1 of 5, illegible scans) — request a clean copy

### Licence expiry handling
- The `licence_expiry` field in the Sheet is set when Tier 2 is granted for a licence badge.
- The render layer in `data.js` checks `licence_expiry < today`. If expired, the licence badge auto-downgrades to `Unverified` regardless of `verification_tier`.
- 30 days before expiry, the Sheet flags `licence_expiry_warning = TRUE` so the helper can re-request a current licence copy.

---

## 7. Tier 3 — deferred plan (not active)

Activated only when:
- A facility invites IK for a site visit, OR
- IK proactively schedules a visit because the facility is editorially significant (premium chain flagship, dispute resolution, etc.)

When activated, Tier 3 verification will additionally include:
- Site walk-through with permission
- Photos taken by IK (some published with operator approval, some kept private)
- Brief staff interview (RN-in-charge, kitchen lead, activity coordinator)
- Resident-environment observation (not interviews — privacy)
- A `visit-notes.md` in the facility's Drive folder
- A 2–3 sentence public visit summary on the facility profile, separate from private notes

For now, Tier 3 is not in the SOP loop. Returns when the model is viable.

---

## 8. Sheet columns referenced by this SOP

These columns must exist on the Facilities tab. Add as part of the Phase A schema upgrade:

| Column | Set by |
|---|---|
| `verification_tier` | Helper (1) or IK (2) |
| `last_verified_on` | Helper or IK |
| `verified_by` | Helper or IK (free text) |
| `evidence_ref` | Helper (Drive folder URL) |
| `licence_expiry` | IK at Tier 2 grant |
| `outreach_status` | Helper |
| `outreach_last_attempt` | Helper |
| `outreach_notes` | Helper or IK |
| `tier_2_review_pending` | Helper (when documents arrive) |
| `licence_expiry_warning` | Auto-flag from render layer |

---

## 9. Helper onboarding checklist

Before first independent outreach:

- [ ] Helper has read this SOP end-to-end
- [ ] Helper has read [regulatory-framework.md](regulatory-framework.md) §1 and §3 to understand what badges mean
- [ ] Helper has read [assisted-living-segment.md](assisted-living-segment.md) §5 to understand AL editorial voice (so they don't tell AL operators we want clinical-style answers)
- [ ] Helper has Drive folder access (read+write)
- [ ] Helper has Sheet edit access (limited columns)
- [ ] Helper has tested the intake form on a fake facility entry
- [ ] IK and helper have walked through one real facility outreach together as a worked example
- [ ] Helper knows when to escalate to IK (any dispute, any document upload, any operator complaint)

---

## 10. Quality checks (monthly)

IK reviews monthly:
- Random sample of 5 helper-completed Tier 1 entries against the operator correspondence in Drive
- Outreach log: response rate, no-response rate, decline rate
- Stale Tier 1 entries approaching 12-month expiry
- Stale Tier 2 entries approaching 24-month expiry or licence expiry
- Any facilities flagged by user reports / public corrections

Track in `_logs/quality-review-<YYYY-MM>.md`. Adjust SOP as patterns emerge.
