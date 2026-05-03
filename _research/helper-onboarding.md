# Helper onboarding pack — outreach helper

Welcome. This pack consolidates everything you need to start. Read it once end-to-end, then keep it open as a reference for your first few weeks.

Last updated: 2026-05-03

---

## How this works in 5 minutes

NursingHomeGuide.my is an independent directory of nursing homes, assisted-living, day-care, and home-care providers in Malaysia. The site is run by Dr Ibkaar Mohamad Yatim ("IK"). It's built around two ideas:

1. **Families deserve verified facts**, not advertorial. Every claim on a facility profile is sourced — public records, operator-confirmed, or document-verified.
2. **A tiered trust badge tells families how confident we are.** Unverified → operator-attested (Tier 1) → document-verified (Tier 2) → MD-confirmed (Tier 3, deferred).

**Your role** is the engine for Tier 1: contact each facility, walk them through a 5-minute Google Form, log the response, and update the master Sheet. You do not do Tier 2 (document review — IK's job) or Tier 3 (site visits — also IK).

You are part of the "verification team". Sign with your own first name in operator messages. Never sign as IK. Never claim to be a doctor or to make medical judgements.

**Volume expectation:** ~10 facilities/week is a reasonable starting cadence. Quality over speed — a slow, accurate verification beats a fast, sloppy one. Growth into 15–20/week is fine once the workflow feels routine.

---

## Onboarding checklist (from verification-sop.md §9)

Before your first independent outreach:

- [ ] Read [verification-sop.md](verification-sop.md) end-to-end
- [ ] Read [regulatory-framework.md](regulatory-framework.md) §1 and §3 to understand what each badge means
- [ ] Read [assisted-living-segment.md](assisted-living-segment.md) §5 to understand AL editorial voice (so you don't tell AL operators we want clinical-style answers)
- [ ] Confirm Drive folder access (read+write to `NursingHomeGuide-Verifications/`)
- [ ] Confirm Sheet edit access (verification columns only — `verification_tier`, `last_verified_on`, `verified_by`, `evidence_ref`, `outreach_status`, `outreach_last_attempt`, `outreach_notes`, `tier_2_review_pending`)
- [ ] Test the intake form on a fake facility entry
- [ ] Walk through one real facility outreach with IK as a worked example
- [ ] Save the four templates from `_templates/` somewhere quick to copy from

---

## The daily loop (from verification-sop.md §3)

1. **Pick a batch of 10.** Filter the Sheet to `outreach_status = pending` AND `verification_tier ≤ 1`.
2. **Pre-flight each facility.** Quick Google Maps check (still operational?), confirm the contact (phone / WhatsApp / email is current), open or create the facility's Drive folder.
3. **Send outreach.** WhatsApp template preferred; email if WhatsApp not available. Pre-fill the Google Form with facility name + address using the Forms "Get pre-filled link" feature.
4. **Log the attempt** in `_logs/outreach-log.csv` and update the Sheet (`outreach_status = sent`, `outreach_last_attempt = today`).
5. **Wait 5 working days.** No response? Send the reminder template once.
6. **5 more working days?** Mark `no_response`, walk away.
7. **Response arrives?** Save the screenshot, copy the answers into the Sheet, update verification fields per SOP §3 step 6.

---

## Common scenarios

### Operator says yes (filled the form)

Standard happy path. Per SOP §3 step 6:
- Open form responses in the linked Sheet tab → copy values into main Facilities tab
- Save screenshot of submission to `<slug>/operator-correspondence/intake-<date>.png`
- Update Sheet: `verification_tier = 1`, `last_verified_on = response date`, `verified_by = "<your name> (operator-attested)"`, `evidence_ref = <Drive folder URL>`, `outreach_status = responded`
- Send a brief thank-you message: *"Got it, thanks. Your profile will show the verified badge within a few working days."* Done.

### Operator says yes (replied on WhatsApp/email instead of form)

Walk them through the form questions one by one in the chat thread. Screenshot every answer. Save the full thread as `<slug>/operator-correspondence/whatsapp-<date>.png` (or `email-<date>.png`). Manually enter the answers in the Sheet. Tag `verified_by = "<your name> (operator-attested via WhatsApp)"`.

### Operator says no

Use [operator-decline-acknowledgment.md](templates/operator-decline-acknowledgment.md). Be gracious. Set `outreach_status = declined`, log a one-line note. Don't argue. Don't retry for 12 months.

### Operator non-responsive (5 working days, no read receipt or response)

Send the reminder ([operator-followup-reminder.md](templates/operator-followup-reminder.md)) — once. Same channel. If silent for another 5 working days, mark `outreach_status = no_response` and stop chasing. Profile stays Unverified — that's fine.

### Operator wants to negotiate the badge text

This comes up. They'll ask for things like *"can you remove the unverified label"* or *"can you call us 'premium-verified'"*.

**Your answer:** "The badge text is set by the same rules for every facility on the site, so I can't change yours specifically. The way to get a verified badge is through the form. If you want to talk through the badge tiers, I can pass you to Dr Ibkaar."

Do not negotiate. Do not invent custom badges. Do not tell them the rule is flexible. **Escalate to IK** if they push.

### Operator offers documents (licence scan, roster, rate card, etc.)

This is **good** — they're a Tier 2 candidate.

- Save the document in the right sub-folder: `/licence/`, `/staffing/`, `/pricing/` as appropriate
- Add a note in `outreach_notes` describing what was uploaded
- Set `tier_2_review_pending = TRUE`
- **Do not raise the verification tier yourself.** Tier 2 is IK-only. He reviews the queue weekly and makes the call against the evidence rulebook.
- Reply to the operator: *"Thanks, I've passed this to our review team. They check evidence in batches every week — your profile will be updated to the document-verified badge once the review is complete."*

### Operator disputes something on the public profile

Don't try to resolve. Capture their exact message, screenshot it to `operator-correspondence/`, and **escalate to IK immediately** (same day, not next batch). IK responds personally. Helper does not amend public content during a dispute.

### Operator volunteers photos for the public profile

Politely decline for now: *"Thanks. We don't currently swap profile photos based on operator requests, but I'll note this for our team."* (Photos for the public site come from Google or operator websites, with a separate photo-curation pass — not from outreach.) Save what they sent in `<slug>/photos/` for the record.

### Operator asks "who is behind this site?"

*"NursingHomeGuide.my is run by Dr Ibkaar Mohamad Yatim, a Malaysian doctor. I'm part of the verification team. The site is independent — we don't take payment from facilities, and verification is free."*

### Operator asks if there's a fee

*"No fee. Verification is free for every facility. The site is independent and not advertising-funded."*

### Operator asks for the licence number to be displayed

*"We don't display licence numbers publicly — only the verification status and date. Documents you share with us privately stay private."*

---

## When to escalate to IK

Escalate (don't decide yourself) when:

- Operator disputes any factual claim on the public profile
- Operator requests profile removal
- Operator wants to negotiate the badge wording or tier
- Operator uploads documents (Tier 2 review queue — flag the row, don't act on the docs)
- Operator complains about anything beyond their own profile
- Anything legal-sounding ("we'll have our lawyers contact you", "you don't have permission")
- You're not sure

Mode: WhatsApp message to IK with the facility slug, the operator's verbatim message, and a screenshot. Don't reply to the operator until IK has weighed in.

---

## What you do NOT do

From SOP §3:
- Do not create or change badge values directly. The intake form drives those.
- Do not raise verification tier above 1.
- Do not publish anything; the Sheet → site pipeline runs on IK's schedule.
- Do not make claims about facility quality. Outreach is fact-collection, not opinion.
- Do not share Drive contents externally. Documents stay private.

Add to that:
- Do not improvise message wording outside the templates without checking with IK
- Do not contact the same facility through multiple channels in parallel (one channel, one reminder)
- Do not use IK's name to sign messages — sign with your own
- Do not remove or edit a public profile yourself

---

## Cadence

| Cadence | What |
|---|---|
| **Daily (work days)** | 2–3 new outreaches; check responses on yesterday's batch |
| **Weekly (~10 facilities)** | Pick a fresh batch of 10 from the pending queue; send reminders due today |
| **Weekly (Friday)** | Quick scan of the outreach log; report any escalation backlog to IK |
| **Monthly** | IK does the quality review (SOP §10) — be available to discuss any flagged entries |

10/week is the **starting** target. Don't over-extend. Over time, as the workflow gets routine and the ratio of "responses to chase" to "new outreaches" balances out, 15–20/week is reasonable. Don't push past that — quality drops, screenshots get sloppy, log entries get skipped.

---

## Useful files

- [verification-sop.md](verification-sop.md) — the master SOP, this onboarding is a digest
- [regulatory-framework.md](regulatory-framework.md) — what each badge actually means
- [assisted-living-segment.md](assisted-living-segment.md) — AL editorial voice
- [templates/operator-outreach-whatsapp.md](templates/operator-outreach-whatsapp.md)
- [templates/operator-outreach-email.md](templates/operator-outreach-email.md)
- [templates/operator-followup-reminder.md](templates/operator-followup-reminder.md)
- [templates/operator-decline-acknowledgment.md](templates/operator-decline-acknowledgment.md)
- `_logs/outreach-log.csv` — append one row per outreach attempt

If a question isn't covered here or in the SOP, ask IK rather than guessing. The cost of a 30-second WhatsApp question is much lower than the cost of an inconsistent process.
