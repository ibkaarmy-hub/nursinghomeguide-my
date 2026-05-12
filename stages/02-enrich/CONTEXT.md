# Stage 02 — Data Enrichment

## Status: 🟢 Perak 100% complete · Johor/KL/Selangor 100% editorial · other 11 states pending

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

## What's done

| State | Live | Editorial ≥800 | placeId | Photos | Reviews | WhatsApp | Capabilities |
|-------|------|----------------|---------|--------|---------|----------|--------------|
| Johor | 74 | 100% | high | high | high | pending | pending |
| Kuala Lumpur | 66 | 100% | high | high | high | pending | pending |
| Selangor | 206 | 100% | high | high | high | pending | pending |
| **Perak** | **92** | **100%** | **98%** | **95%** | **85%** | **82%** | **86% (nursing)** |
| 11 other states | ~270 | 0% | 0% | 0% | 0% | 0% | 0% |

## What's pending (priority order)

1. **Other 11 states** — run `enrich_places_free.py` then editorials + auto-fill on each. Roughly 270 facilities across Penang, Kedah, Kelantan, Terengganu, Pahang, Negeri Sembilan, Melaka, Sabah, Sarawak, Perlis, Labuan, Putrajaya. ~$0 cost.
2. **Johor/KL/Selangor WhatsApp + capability backfill** — run `enrich_whatsapp_clinical.py` against them (the script is state-agnostic; just change the filter).
3. **Pricing outreach** — still the #1 data gap. 0% of any state has concrete monthly prices. Requires direct contact, not scrapeable.
4. **JKM licence backfill** — most rows have licences via the JKM register import; a few facilities still blank. Bulk lookup pending.
5. **Duplicate sheet hygiene** — same-slug rows with different JKM licences (e.g. Perak row 532/531 lotus; row 765/764 victory). Needs sheet-level dedup decision per pair.

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
| `upload_details_batch*.py` | Upload Details tab rows for specific facilities | $0 |
| `merge_photos_oauth.py` | Merge photo URLs into Facilities tab | $0 |
| `update_editorials.py` | Batch update editorial_summary column | $0 |

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
