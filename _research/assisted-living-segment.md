# Assisted living segment — separate category, separate page

Last updated: 2026-05-03
Source: Strategy decision IK 2026-05-03, prompted by [market-landscape.md](market-landscape.md) brand audit. The site already promises coverage of "nursing homes, assisted living, day care, and home care" but the current UX is entirely nursing-home-centric. This file captures the assisted-living workstream as a distinct product.

---

## 1. Why assisted living is a different product

Nursing home and assisted living represent **different decisions** by different families with different evaluation criteria. Treating them as filters within one directory miscategorises both.

| Dimension | Nursing home | Assisted living |
|---|---|---|
| **Trigger event** | Hospital discharge, post-stroke, dementia escalation, immobility | Pre-emptive lifestyle move; downsizing; widowhood; "while still healthy" |
| **Resident profile** | Higher acuity (Acuity 3–4) | Independent or low assistance (Acuity 1–2) |
| **Decision criteria** | Clinical safety, RN coverage, doctor frequency, capacity for procedures | Community, amenities, food, location, autonomy, social calendar |
| **Family question** | "Will my mother be safe?" | "Will my mother be happy?" |
| **Price model** | RM 3,500–8,500 / month, often base + add-ons | RM 4,500–15,000+ / month, often all-in or membership-style |
| **Editorial voice** | Clinical guide; verification rigour; safety-first | Property/community guide; lifestyle-first; verification rigour kept but applied to amenities, ownership, financial model |
| **SEO market** | "nursing home <city>", "skilled nursing <state>", "dementia care" | "assisted living <city>", "retirement village", "senior living community" |

Same trust-and-verification standards apply. The difference is **what we're verifying for** — clinical capability vs. amenity/community claims.

---

## 2. Site architecture (Option A — separate top-level pages)

Decision: build `/assisted-living/` as a peer to the existing nursing-home pages, not as a filter inside them.

### URL structure

```
/                              → top-level landing (state picker for nursing home — current)
/nursing-homes/                → renamed, made explicit (was implicit)
/nursing-homes/johor/          → current johor.html, moved
/nursing-homes/kuala-lumpur/   → current kl.html, moved
/nursing-homes/selangor/       → current selangor.html, moved
/nursing-homes/<slug>/         → current /facility/<slug>/

/assisted-living/              → new landing (category overview + state picker)
/assisted-living/selangor/     → new state page
/assisted-living/kuala-lumpur/ → new state page
/assisted-living/johor/        → new state page
/assisted-living/<slug>/       → new per-facility static pages

/home-care/                    → later phase
/day-care/                     → later phase
```

### Cross-listing
A facility offering both AL and NH service (e.g. Pacific Senior Living, Eden-on-the-Park dual-key) appears on **both** category pages, with `service_type` containing both tags. The facility's own profile page lives at one canonical URL — pick the dominant service for the URL slug, list both service types in the profile body.

### Redirects
Old `/facility/<slug>/` URLs continue to work — 301 to whichever new category-prefixed URL the facility now lives at. Don't break the SEO already accumulated by the static facility pages.

### Generator updates
- `generate_facility_pages.py` reads `service_type`, writes to the appropriate category folder
- New `generate_state_listings.py` (or extension of current) builds NH and AL state pages from the same CSV, filtered by `service_type`
- `generate_sitemap.py` picks up all category-prefixed URLs

---

## 3. Schema field

Single new column in the Facilities tab (referenced from [regulatory-framework.md §2](regulatory-framework.md)):

| Column | Type | Values |
|---|---|---|
| `service_type` | Multi-select (pipe-separated) | `nursing_home` / `assisted_living` / `home_care` / `day_care` |

Default for the existing 350 facilities = `nursing_home`. Re-tagging audit in §6.

---

## 4. Assisted-living seed brands

### Already in our directory but currently miscategorised
*(need re-tagging in the audit pass)*

| Facility | Current state | Notes |
|---|---|---|
| **Acacia by Pacific Senior Living** | Klang, Selangor | Repurposed 4-star hotel; "Silver Club" daycare; resort-style. Pure AL, currently filed as nursing home. |
| **Komune Care / Komune Living & Wellness** | Kuala Lumpur | Premium AL + day club. Multiple Komune entries in directory currently treated as nursing home. |
| **Haywood Senior Living (Bangsar)** | KL | Boutique hotel concept, urban seniors. Hybrid lean toward AL. |
| **Haywood Senior Living (Medini JB)** | Johor | Hotel-style premium; near Gleneagles Medini. Hybrid. |
| **Eden retirement village** | Johor | Name suggests AL; verify on re-tagging pass — distinct from Eden-on-the-Park Kuching. |
| **Capella Senior Living** | KL | Domestic-scale assisted living. |
| **Meridian Care Living Centre** | Bangsar | Has rehab slant but markets as assisted living. Hybrid. |

### Missing from directory (in covered states — add as new entries)

| Brand | Location | Service type |
|---|---|---|
| **Sunway Sanctuary** | Sunway City, Selangor | AL (premium retirement community, 473 suites, annexed to Sunway Medical) |
| **ReU Living** | KLCC | Hybrid (post-hospitalisation + TCM, "hotel-in-a-hospital") |
| **Care Concierge (residential branches)** | KL | Mixed — some branches are AL, some home-care. Audit each branch. |

### Out of coverage (Phase D when those states ship)

| Brand | State | Service type |
|---|---|---|
| GreenAcres Retirement Village | Perak (Ipoh) | AL — Australian-model, lease-for-life ILUs |
| Penang Retirement Resort | Penang | AL — 49 assisted + 77 independent units |
| Eden-on-the-Park | Sarawak (Kuching) | Hybrid — dual-key independent + nursing |
| Millennia Village | Negeri Sembilan (Seremban) | AL |

---

## 5. Editorial voice for assisted-living profiles

Different copy register from nursing-home editorials. Keep the verification rigour; shift the emphasis.

### Lead with
- Community character (active vs quiet, urban vs garden, age range, social calendar)
- Built environment (apartment vs suite, kitchenette, private balcony, communal spaces)
- Amenity programme (pool, gym, library, classes, outings, dining model)
- Location (proximity to family, hospitals as backup not primary, walkability)
- Financial model (monthly fee vs membership vs lease-for-life — material difference for families)

### De-emphasise (still record, but not headline)
- Acuity level, RN coverage, doctor frequency — these are **fallback questions** for AL, not the lead
- Nursing-grade procedure capability — most AL residents don't need it, and over-emphasising it makes the segment feel medical when it shouldn't

### Keep at parity with nursing home editorials
- Licence verification (Act 506 / 802 + amenities licensing if applicable)
- Ownership and operator background
- Pricing transparency (including hidden costs — assisted living has different ones: utilities, meals not in plan, additional care if needs increase)
- Red flags in the facts block (not in the published body)

### Tone reference
Closer to a property/community review than a clinical guide. Imagine a knowledgeable friend showing your parent around — they'd talk about the food, the neighbours, the morning routine, and *also* tell you what happens if mum has a fall, in that order.

---

## 6. Re-tagging audit (one-off task)

Before launching `/assisted-living/`, audit the existing 350 directory entries. Most stay as `nursing_home`; a minority move or dual-list.

**Heuristic for re-tagging:**

| Signal | Likely service type |
|---|---|
| Facility advertises "retirement community", "senior living", "ILU", "lease-for-life" | `assisted_living` |
| Facility markets primarily on lifestyle (pool, cinema, library, social calendar) | `assisted_living` (possibly + `nursing_home` if has care wing) |
| Facility markets primarily on clinical care (RN, dementia, post-stroke, palliative) | `nursing_home` |
| Facility describes "stay-in residential care" with nursing | `nursing_home` |
| Facility dispatches carers to homes, no beds | `home_care` |
| Facility offers daytime-only programme, residents return home | `day_care` (often + another type) |
| Boutique hotel concept, premium pricing, low clinical signage | `assisted_living` (sometimes + `nursing_home` for hybrid) |

**Estimated re-tag scope:** ~15–25 of 350 facilities move to AL or dual-list. Most of those are the premium-named entries already flagged above. The bulk of the JKM Pusat Jagaan stays as `nursing_home`.

---

## 7. Phase A.5 scope (between schema upgrade and badge UI)

1. Add `service_type` column to Sheet (default `nursing_home` for existing 350)
2. Re-tag the ~15–25 facilities that should be AL or dual-listed (§6 audit)
3. Add Sunway Sanctuary + ReU Living to directory with `service_type=assisted_living`
4. Build `/assisted-living/` landing page (category overview + state picker)
5. Build `/assisted-living/<state>/` listing pages for KL, Selangor, Johor (mirror existing state-page structure)
6. Update `generate_facility_pages.py` to write to category-prefixed paths; add 301s from old paths
7. Update `generate_sitemap.py` for new URLs
8. Write 3–5 seed AL editorials in the new voice (Sunway Sanctuary, ReU Living, Acacia, Haywood, Komune) as voice exemplars
9. Cross-link from main landing page so AL is discoverable

**Size estimate:** 3–5 days for architecture + re-tagging audit, plus ~half a day per seed AL editorial.

---

## 8. Pricing tier reference (for AL editorials)

From [market-landscape.md](market-landscape.md):

| AL tier | Range (RM/month) | Examples |
|---|---|---|
| Standard assisted living | 3,500 – 5,500 | Most JKM-registered AL homes |
| Mid-premium boutique | 5,000 – 8,500 | Haywood, Capella, Meridian |
| Premium resort / community | 6,500 – 15,000+ | Sunway Sanctuary, Pacific Senior Living, Eden-on-the-Park |

Always show what's included vs. extra. AL hidden costs differ from NH ones — utilities, meal plan tiers, extra-care surcharges if a resident's needs escalate, and exit/transfer fees on lease-for-life models.

---

## 9. Caveats before implementation

- The `nursing_home` brand domain (`nursinghomeguide.my`) hosting an `/assisted-living/` section is fine for SEO if the navigation makes the relationship clear ("we cover all elder-care options in Malaysia")
- Don't dilute the nursing-home content authority by making AL feel like an afterthought — the AL section needs its own landing copy, not just a listing page
- Verify each premium AL brand's licensing status — they may operate under different statutes (some retirement villages are property developments + service contracts rather than Act 506 care centres)
- Confirm financial models (lease-for-life, refundable deposits, membership fees) per facility — mis-stating these is a financial-advice liability we want to avoid
- Re-read [pricing-benchmarks.md](pricing-benchmarks.md) before publishing AL pricing — it currently focuses on nursing home benchmarks
