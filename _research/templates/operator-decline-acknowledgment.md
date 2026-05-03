# Decline acknowledgment — operator says no

Use when an operator explicitly declines to participate ("not interested", "we don't want to be on your site", "please remove us"). Goal: be gracious, set expectations, leave the door open without pressuring.

The profile **stays up** unless the operator asks for removal AND can show they no longer operate. Public-fact directory listings don't require operator consent. But the verification badge stays at Tier 0 / Unverified — we don't badge operators who didn't confirm.

Placeholders:
- `<facility-name>`
- `<facility-url>`
- `<helper-name>`

---

## WhatsApp / Email — generic decline

Thank you for letting me know — completely understood, no problem at all.

Just so you know what happens next:

- Your profile at `<facility-url>` stays online (it's based on public information families can already find on Google, JKM listings, etc.)
- Because you haven't confirmed the details, the profile won't carry a verification badge — it stays in the *"Unverified"* state, which is the default for facilities we haven't heard back from
- If anything on the profile is factually wrong, I'd really appreciate it if you let me know which line is incorrect — I can correct factual errors any time, no verification required
- If you change your mind down the road and want to verify, just message me and I'll send the form again

No further follow-ups from me. Thanks for the time, and all the best with `<facility-name>`.

— `<helper-name>`
NursingHomeGuide.my

---

## Variant — operator asks for the profile to be removed

Use only if removal request is firm. Escalate to IK before acting.

> Thank you for getting in touch. I've passed your removal request to our editorial team and someone will come back to you directly within a few working days. In the meantime, if there is anything factually wrong on the current profile, please do let me know which line is incorrect — we can fix factual errors right away.
>
> — `<helper-name>`

---

## Helper notes (do not send)

- **Always escalate removal requests to IK.** Helper does not remove facilities.
- Set `outreach_status = declined` and add a one-line summary in `outreach_notes` (e.g. "operator declined politely on WhatsApp, no reason given")
- Save the operator's decline message as a screenshot to `<slug>/operator-correspondence/decline-<date>.png`
- Do NOT argue, justify, or attempt to reverse the decision. Don't offer "but we could…" alternatives. The decline is the answer.
- Do not retry this facility for at least 12 months. Add a note to `outreach_notes` with the cooldown date.
