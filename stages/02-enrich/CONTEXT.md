# Stage 02 — Data Enrichment

## Status (audited 2026-05-12)

Per-state editorial coverage (live facilities, status not in removed/unverified):

| State | Live | Ed ≥800 | placeId | Photos |
|-------|------|---------|---------|--------|
| Selangor | 254 | 198 (78%) | 198 (78%) | 247 (97%) |
| Johor | 128 | 76 (59%) | 72 (56%) | 127 (99%) |
| **Perak** ✅ | **92** | **91 (99%)** | **91 (99%)** | **88 (96%)** |
| Kuala Lumpur | 86 | 66 (77%) | 73 (85%) | 83 (97%) |
| Negeri Sembilan | 34 | 3 (9%) | 27 (79%) | 33 (97%) |
| (state column blank) | 31 | 0 | 5 | 28 |
| Penang | 24 | 7 (29%) | 20 (83%) | 21 (88%) |
| Pahang ✅ | 22 | 22 (100%) | 19 (86%) | 22 (100%) |
| Kedah ✅ | 21 | 21 (100%) | 20 (95%) | 20 (95%) |
| Melaka ✅ | 15 | 15 (100%) | 14 (93%) | 15 (100%) |
| Sabah ✅ | 14 | 14 (100%) | 12 (86%) | 14 (100%) |
| Sarawak ✅ | 7 | 7 (100%) | 6 (86%) | 7 (100%) |
| Terengganu ✅ | 7 | 7 (100%) | 6 (86%) | 6 (86%) |
| Kelantan ✅ | 4 | 4 (100%) | 4 (100%) | 3 (75%) |
| Perlis ✅ | 2 | 2 (100%) | 2 (100%) | 2 (100%) |
| Labuan ✅ | 1 | 1 (100%) | 1 (100%) | 1 (100%) |
| **Total** | **742** | **534 (72%)** | **570 (77%)** | **717 (97%)** |

**The real gaps:** Selangor (56 empty editorials), Johor (52 empty), Penang (17 empty), KL (20 empty), Negeri Sembilan (31 empty), and **31 facilities with blank `state` column** (state classification needed before any enrichment).

## The zero-cost enrichment pipeline (locked 2026-05-12)

After running out of Apify credits and discovering ~50% false-positive rate on
Apify social discovery, the workflow has been rebuilt around **Google Places
API (free tier, 10K calls/month)** + a set of automated passes.

**Total cost per state: $0.**

### The four phases

| Phase | Script | What it populates | Cost |
|-------|--------|-------------------|------|
| 1. Foundation | `enrich_places_free.py <State>` | placeId · address · phone · website · rating · review_count · review snippets · photos | $0 (Places API) |
| 2. Editorials | `/nh-profiles` skill + template generator | `editorial_summary` (5-part structure) | $0 (model work) |
| 3. Auto-fill | `enrich_whatsapp_clinical.py` (or inline batch) | `whatsapp` from mobile phones · `care_*` and `medical_*` flags from editorial text | $0 (regex) |
| 4. Publish | `generate_facility_pages.py` + `generate_sitemap.py` | static pages + sitemap | $0 |

### Phase 1 — Places API foundation

For each live facility in a state:

1. **Text search** (`places:searchText`) — returns up to 5 candidates near the
   facility's lat/lng. Validate: title must fuzzy-match facility name AND
   address must contain the target state.
2. **Place Details** (`places/{id}`) — fetches up to 5 reviews with text,
   photos list, opening hours, types.
3. **Photo media** (`places/{id}/photos/{ref}/media?skipHttpRedirect=true`) —
   returns the real `lh3.googleusercontent.com` URL via JSON.

Sheet writes (per facility):
- `T` google_maps_url with `query_place_id`
- `P` / `Q` rating + review_count
- `F` website (only if currently empty)
- `AZ` / `BA` / `BB` hero + photos + photo_count (only if currently empty)
- `U` last_updated
- Details tab: `policies | Address (Google-verified)`, `social | Google reviews` (review snippets), `policies | Photo credits`

Resumable via `_enrich_cache/places_<state>.json`. Re-running skips cached slugs.

### Phase 2 — Editorial writing

Single source of truth: `.claude/commands/nh-profiles.md` (the skill).
Two paths depending on data richness:

**Path A — Curated (operator has website)**
Manual draft following 5-part structure using WebFetch on operator site +
cached Places data. ~10 facilities per batch.

**Path B — Template generator (no website, only Places data)**
Programmatic editorial using `_enrich_cache/places_<state>.json` + sheet data.
The generator handles:
- JKM licence + registration year
- Hospital-by-area matching (Ipoh / Taiping / Sitiawan / Teluk Intan / Kampar / Pusing / Gopeng / Sungai Siput)
- Honest review framing — paraphrase positive content; for rating < 4.0,
  reframe as visit questions, never quote negative content
- "What to ask on visit" 5–7 bullets (extra questions injected when reviews are mixed)

Both paths track in `profile_progress.json` (done + skipped lists).

### Phase 3 — Automated enrichment

After editorials are written, run these zero-cost passes:

1. **WhatsApp from phone** — only Malaysian mobile numbers (`+601XXXXXXXX`).
   Landlines (+603, +605, +607, +609) skipped — they can't WhatsApp.

2. **Clinical capability parser** — case-insensitive regex on
   `editorial_summary`, sets `care_*` / `medical_*` columns to `yes`:
   - `care_nursing` ← "24-hour nursing", "skilled nursing", "registered nurse", "nursing home"
   - `care_palliative` ← "palliative", "end-of-life", "hospice", "臨終"
   - `care_dementia` ← "dementia", "memory care", "alzheimer", "cognitive decline"
   - `care_rehab` ← "rehabilitation", "post-stroke", "post-hospital", "post-surgery"
   - `care_respite` ← "respite", "short-stay"
   - `care_assisted` ← "assisted living", "day care", "daycare", "pusat jagaan harian"
   - `medical_physio` ← "physiotherapy", "physiotherapist"
   - `medical_wound` ← "wound care", "wound management"
   - `medical_peg` ← `\bPEG\b`, "tube feeding", "feeding tube", `\bNGT\b`
   - `medical_oxygen` ← `\boxygen\b`, `\bO2\b`
   - `medical_dialysis` ← "dialysis"
   - `medical_dementia_unit` ← "dementia unit", "secure dementia", "locked dementia"

3. **Facebook URL audit** (when adopting prior Apify discovery data):
   - Reject post URLs (`/posts/`, `/photos/`, `/videos/`, `/share/`, `/mentions`, `photo.php`)
   - Reject blocked handles (gov depts `pkpdaerah*`, `pergigian*`, churches `fgc*`, etc.)
   - Keep only handles that contain a non-stopword from the facility name

### Phase 4 — Publish

```bash
python generate_facility_pages.py        # bakes JSON-LD + AI data block
python generate_sitemap.py
git add nursing-homes/ facility/ sitemap.xml profile_progress.json
git fetch origin main && git rebase origin/main --autostash
git commit -m "<state> editorials + enrichment"
git push origin main
```

## Per-state achievements

**Perak (Phase 1–4 complete, locked 2026-05-12):**
- Editorial: 12% → 99% (91/92, the 1 outlier is data-quality issue)
- Maps placeId: 91% → 99% (via Places API enrichment)
- WhatsApp: 0% → 82% (auto-parsed from mobile phones)
- care_nursing flag: 11% → 86% (regex over editorial text)
- 359 cell writes + 158 Details rows from $0 Places API run
- 46 unverified FB URLs cleared (false-positive cleanup from prior Apify run)

**Johor/KL/Selangor:** Substantial editorial coverage from earlier sessions but **not yet at 100%**. None have had Phase 3 (WhatsApp + capability parse) run yet — easy wins waiting.

**Smaller states (Pahang/Kedah/Melaka/Sabah/Sarawak/Terengganu/Kelantan/Perlis/Labuan):** All have 100% editorial coverage from earlier sessions (template-generator-style writing, likely). placeId coverage typically 85–100%. Ready for Phase 3 auto-fill.

## What's pending (priority order)

1. **Classify the 31 blank-state rows.** Until they have a state, they don't appear in any state listing page and can't be enriched per-state. Probably orphans from MDAC import or sheet edits — needs manual review.
2. **Selangor / Johor / KL / Penang / N. Sembilan editorial backlog** — 176 total empty editorials. Highest-impact remaining write work. Same pipeline as Perak: `enrich_places_free.py <State>` → editorial generation → auto-fill.
3. **Phase 3 backfill on all states** — `enrich_whatsapp_clinical.py` is state-agnostic; run against the full Facilities tab to populate WhatsApp + capability flags everywhere (zero cost, ~5 min).
4. **Pricing outreach** — still the #1 data gap. 0% of any state has concrete monthly prices. Requires direct contact, not scrapeable.
5. **JKM licence backfill** — most rows have licences via the JKM register import; a few facilities still blank.
6. **Duplicate sheet hygiene** — same-slug rows with different JKM licences (Perak row 532/531 lotus; row 765/764 victory). Needs sheet-level dedup decision per pair.

## Hard rules

- **Don't invent.** Empty cell beats fake data.
- If pricing can't be confirmed, leave `shared_price` blank — `pricing_display` shows "Call for pricing" as fallback.
- Update `last_updated` whenever a row is verified or enriched.
- Photos column always pipe-separated; first URL is the hero.
- `care_types` must be populated before a facility is set live (enforced by status filter).
- **Never write to Z (facebook) without verifying the handle matches the facility name.** Yesterday's Apify run created ~50% false positives by accepting any FB URL the actor returned. The audit logic in `_tmp/audit_perak_fb.py` is the canonical filter.
- **Editorial body never quotes negative reviews.** Reframe specific concerns as visit questions. See `.claude/commands/nh-profiles.md` for the locked rule.

## Working scripts (project root)

| Script | Purpose | Cost |
|--------|---------|------|
| **`enrich_places_free.py`** | **Phase 1 foundation enrichment per state** | **$0 — Places API free tier** |
| `generate_facility_pages.py` | Regenerate per-facility static pages | $0 |
| `generate_sitemap.py` | Regenerate sitemap.xml | $0 |
| `process_kl_selangor.py` | (legacy) Process Apify output → upload to sheet | – |
| `upload_details_batch{2,5}.py` | (legacy) One-off Details tab uploaders, kept for reference | $0 |
| `merge_photos_oauth.py` | (legacy) Merge photo URLs into Facilities tab | $0 |
| `update_editorials.py` | (legacy) Batch update editorial_summary column | $0 |
| `batch_maps_placeid.py` | (legacy Apify) Batch Maps placeId resolver — superseded by `enrich_places_free.py` | – |

One-off batch scripts (in `_tmp/`, gitignored, deleted after use):

| Pattern | Purpose |
|---------|---------|
| `_tmp/batchN_<state>_editorials.py` | Per-batch curated editorials |
| `_tmp/batchN_<state>_generator.py` | Template-generated editorials for thin-data facilities |
| `_tmp/enrich_whatsapp_clinical.py` | Phase 3 auto-fill |
| `_tmp/audit_<state>_fb.py` | Facebook URL audit (when adopting Apify FB hits) |
| `_tmp/rollback_<state>_fb.py` | Clear unverified FB URLs |
| `_tmp/mark_unverified.py` | Mark suspect duplicates/wrong-Places matches |

## API credentials

Both keys live in `.env` (gitignored):
- `APIFY_TOKEN` — legacy, only used for older `batch_maps_placeid.py` flow
- `GOOGLE_MAPS_KEY` — Places API key, used by `enrich_places_free.py`

**Places API setup:** Enable "Places API (New)" in GCP Console, create an API
key (not OAuth — Places API doesn't accept OAuth), optionally restrict to
Places API + Geocoding API. Free tier is 10K Details calls + 5K Text Searches
per month — well above project's total scale.
