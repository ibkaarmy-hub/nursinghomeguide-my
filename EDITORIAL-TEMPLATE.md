# Editorial Format — Clean Segments (Replaces 3-Paragraph Style)

## Template Structure

```
**What it is**
[1–2 sentences: facility type, location, operator, care focus]

**Care services**
- [Service 1]
- [Service 2]
- [Service 3]

**Staffing & support**
- [Nursing level / RN presence]
- [Language support]
- [Caregiver ratio if known]

**Capacity & pricing**
- [Bed count if published]
- [Price range or "Call for pricing"]
- [Pricing source: published website / call for quote]

**License & verification**
- **JKM status:** [registered / unverified / no registration required]
- **JKM verified via:** [JKM call / cert photo / operator claim / unverified]
- **JKM expires:** [date or "unknown"]
- **MOH status:** [licensed / unverified / not applicable]

**Special programs**
- [If any: respite care, day care, rehabilitation focus, etc.]

**What to ask on visit**
- [Practical questions for unverified items]
- [Specific care needs confirmations]
```

---

## Example 1: Well-Documented Chain Branch

**Noble Care Nursing Home — Jalan Ipoh, KL**

**What it is**
Noble Care is a mid-sized nursing home in Kuala Lumpur's Jalan Ipoh area, part of the Noble Care chain. Provides long-term residential care with emphasis on dementia and palliative support.

**Care services**
- Long-term residential care
- Dementia & memory care
- Palliative care
- Post-operative recovery
- Physiotherapy (on-site)

**Staffing & support**
- Registered nurses on-site 24/7
- Caregiver ratio: 1:3 (day), 1:5 (night)
- Languages: English, Malay, Cantonese

**Capacity & pricing**
- 45 beds (mixed occupancy)
- RM 2,500–3,500/month (shared to private)
- Pricing published on operator website

**License & verification**
- **JKM status:** Registered
- **JKM verified via:** Certificate viewed in-person
- **JKM expires:** September 2026
- **MOH status:** Licensed (Act 586)

**What to ask on visit**
- Scope of MOH-licensed clinical services (wound care, PEG feeds, oxygen, dialysis)
- Individualised care plan process
- Doctor visit frequency
- Family involvement in care decisions

---

## Example 2: Smaller Home, Limited Info

**Blissful Senior Care Centre — Selangor**

**What it is**
Blissful Senior Care is a residential care home in Selangor serving mobile to low-dependency elders. Focus on safe housing, meals, and daily activities rather than intensive medical care.

**Care services**
- Residential care (assisted living)
- Basic nursing support
- Activities & recreation

**Staffing & support**
- Caregiver staff on-site; nurse availability unverified
- Languages: Malay, English

**Capacity & pricing**
- Bed count not published
- Pricing not posted on website — request a written quote during visit

**License & verification**
- **JKM status:** Unverified
- **JKM verified via:** None yet (pending outreach)
- **JKM expires:** Unknown
- **MOH status:** Unverified

**What to ask on visit**
- JKM registration number and certificate
- Nursing staff availability (registered nurse on-site?)
- Caregiver qualifications and ratio
- Medical oversight (doctor visits, emergency protocols)
- Facility capacity and current occupancy

---

## Example 3: Chain with Multiple Branches

**Genesis Life Care — PJ Branch 2**

**What it is**
Genesis Life Care is a multi-branch chain operating 5+ locations across Malaysia. The PJ Branch 2 facility offers nursing-level care with a focus on post-acute rehabilitation and dementia support.

**Care services**
- Long-term nursing care
- Dementia & memory care
- Post-acute rehabilitation (stroke, orthopaedic)
- Respite stays (flexible duration)
- Day care (select locations)
- Physiotherapy & occupational therapy

**Staffing & support**
- Registered nurses 24/7 (chain-wide standard)
- Physiotherapists and occupational therapists on-site
- Languages: English, Malay, Mandarin

**Capacity & pricing**
- Bed count varies by branch; PJ Branch 2 has approximately 60 beds
- RM 2,200–4,000/month depending on care level and room type
- Pricing published on operator website (chain-wide rates; final fee depends on assessed care needs)

**License & verification**
- **JKM status:** Registered
- **JKM verified via:** JKM district office call (chain-wide registration confirmed)
- **JKM expires:** May 2027
- **MOH status:** Licensed (Act 586, chain-wide)

**Special programs**
- Respite care: 1-week to 3-month stays
- Post-stroke rehabilitation: physiotherapy-led program
- Day care: for mobile elders; respite for families

**What to ask on visit**
- Branch-specific doctor visit frequency
- Rehabilitation program structure (therapy frequency, outcome tracking)
- Family involvement in care planning
- Visiting hours and family access

---

## Formatting Rules

### Segment headers
- **Bold + plain text** (not all caps)
- Descriptive label ("Care services" not "Services")
- No colons after headers

### Bullet points
- Short, scannable lines (1–2 lines max)
- No full sentences in bullets (drop subject when possible)
- Example ✅: `Registered nurses on-site 24/7`
- Example ❌: `The facility has registered nurses on-site 24/7`

### Verification segment (always include)
- **JKM status:** explicit value (registered / unverified / no requirement)
- **JKM verified via:** method (JKM call / cert photo / operator claim / unverified)
- **JKM expires:** date (or "unknown")
- **MOH status:** explicit value (licensed / unverified / not applicable)

### Length per section
- **What it is:** 1–2 sentences max
- **Care services:** 3–7 bullets
- **Staffing & support:** 3–4 bullets
- **Capacity & pricing:** 3 bullets
- **Special programs:** 2–4 bullets (or omit if none)
- **What to ask on visit:** 3–5 bullets

**Total:** ~200–300 words (shorter than old 3-paragraph style, more scannable)

---

## Tone & Content Rules (Same as Before)

- **Never invent data.** Only verified facts.
- **Frame unverified items as practical questions** in the "What to ask on visit" section.
- **Red flags go nowhere** — only "ask on visit" prompts.
- **No generic phrases** ("warm and caring", "dedicated team").
- **No operator self-comparative content** (blog rankings, "best of" posts).
- **Explicit about what's not published** ("Pricing not posted on website — request quote").

---

## Implementation

Update `nh-profiles.md` Step 4 ("Write the editorial") to:
1. Use this template structure instead of 3 paragraphs
2. Output each segment as shown above
3. Render in Google Sheet `editorial_summary` column using this format (Markdown bold + bullets preserved as plain text)
4. Update Details rows (`section=policies`, `section=rooms`, etc.) to complement the main editorial

---

## Benefits

✅ **Scannable** — readers can skim headers and bullets  
✅ **Data-led** — facts are explicit and separated  
✅ **Verification upfront** — license status is clear, not buried in prose  
✅ **Shorter** — less cognitive load than 3 dense paragraphs  
✅ **Easier to maintain** — segments can be updated independently  
✅ **Aligned with US model** — structured, directory-like feel
