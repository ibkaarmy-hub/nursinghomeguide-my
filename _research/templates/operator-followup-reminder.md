# Follow-up reminder — 5 working days after first contact

Per verification-sop.md §3 step 5: send **once** after 5 working days of no response. If no response 5 working days after this reminder, mark `outreach_status = no_response` and stop chasing.

Use the same channel as the original message (WhatsApp reminder for WhatsApp first-touch, email reminder for email first-touch).

Placeholders:
- `<facility-name>`
- `<facility-url>`
- `<form-url>`
- `<helper-name>`

---

## WhatsApp version

Hi, just a quick follow-up — I sent you a verification request for `<facility-name>` last week.

It's a 5-minute form to confirm key facts about your facility (licensing, staffing, services, pricing model). Once submitted, your profile gets a *"Verified — operator-confirmed"* badge so families can see the information has been confirmed by you directly.

Form: `<form-url>`
Profile: `<facility-url>`

If now isn't a good time, no worries at all — you can come back to it whenever. Happy to take answers by WhatsApp reply if that's easier.

Terima kasih.

— `<helper-name>`

---

## Email version

**Subject:** Re: Verifying your facility profile on NursingHomeGuide.my

Dear `<facility-name>` team,

Following up on my email from last week regarding verifying your facility profile on NursingHomeGuide.my.

The verification form takes about 5 minutes and gives your profile a *"Verified — operator-confirmed"* badge with today's date once submitted.

- Form (pre-filled): `<form-url>`
- Your profile: `<facility-url>`

If you'd prefer to confirm by email reply instead, just let me know and I'll send the questions in this thread. If you'd rather not participate, that's completely fine — please reply with "not interested" and I won't follow up again.

Warm regards,

`<helper-name>`
Verification team, NursingHomeGuide.my

---

## Helper notes (do not send)

- Send only one reminder, full stop. Two reminders = pestering.
- After this reminder, log `outreach_status = sent` (still) and update `outreach_last_attempt`. After another 5 working days of silence, switch to `no_response` and walk away.
- If the operator replies asking what verification means or what we do with their data, answer their question and don't push the form — let them come back when ready.
