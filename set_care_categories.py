"""
set_care_categories.py — Step 1: Normalise care_category in Google Sheet
==========================================================================
Adds/updates a 'care_category' column in the Facilities tab with one of:
  Nursing Home | Home Care | Day Care | Assisted Living | Mixed

Run: python set_care_categories.py
Requires: google-auth, google-auth-oauthlib, google-api-python-client
"""

import re
import csv
import io
import urllib.request

SHEET_ID  = "1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk"
GID       = "292378871"
CSV_URL   = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

# ── Slugs confirmed as genuine HOME CARE agencies (non-residential) ──────
HOME_CARE_SLUGS = {
    "serim-home-nursing",
    "sam-wound-and-home-nursing-care",
    "aurora-home-care-centre",
    "cality-care-malaysia",
    "caregiver-in-kl",
    "sunway-home-healthcare-双威家庭护理",
    "aliz-nursing-care",
    "pusat-jagaan-nurul-jannah",
    "dr-teo-keng-huat-home-care",
    "dynamic-home-care-james",
    "rebina-home-care-centre-sdn-bhd",  # Home Care + Day Care
}

# ── Slugs confirmed as genuine DAY CARE only centres ────────────────────
DAY_CARE_SLUGS = {
    "amitabha-foundation-amitabha-malaysia",
    "pusat-jagaan-harian-warga-tua-cheras-baru",
    "pusat-jagaan-harian-warga-tua-kluang",
}

# ── Keywords in title that suggest home care (for unclassified rows) ─────
HOME_CARE_TITLE_PATTERNS = [
    r"\bhome\s+nursing\b",
    r"\bhome\s+care\s+service\b",
    r"\bnursing\s+agency\b",
    r"\bhome\s+health\s+care\s+service\b",
]

# ── Keywords in care_types that indicate day care only ───────────────────
DAY_CARE_TYPES = {"adult day care center", "pusat jagaan harian"}


def classify(row: dict) -> str:
    slug       = row.get("slug", "").strip().lower()
    title      = row.get("title", "").strip().lower()
    care_types = row.get("care_types", "").strip().lower()

    if slug in HOME_CARE_SLUGS:
        return "Home Care"
    if slug in DAY_CARE_SLUGS:
        return "Day Care"

    # care_types field analysis
    has_nursing_home = "nursing home" in care_types or "rumah jagaan" in care_types
    has_day_care     = "day care" in care_types or any(k in care_types for k in DAY_CARE_TYPES)
    has_home_care    = "home care" in care_types or "home health care" in care_types
    has_assisted     = "assisted living" in care_types or "assisted" in care_types

    if has_home_care and not has_nursing_home:
        return "Home Care"
    if has_day_care and not has_nursing_home and not has_home_care:
        return "Day Care"
    if has_assisted and not has_nursing_home:
        return "Assisted Living"
    if has_nursing_home and has_day_care:
        return "Mixed"          # nursing home that also offers day care
    if has_nursing_home:
        return "Nursing Home"

    # Title-pattern fallback
    for pat in HOME_CARE_TITLE_PATTERNS:
        if re.search(pat, title):
            return "Home Care"

    # Default: assume nursing home / residential care centre
    return "Nursing Home"


def main():
    print("Fetching CSV …")
    with urllib.request.urlopen(CSV_URL) as resp:
        content = resp.read().decode("utf-8")

    reader = csv.DictReader(io.StringIO(content))
    rows   = list(reader)
    print(f"  {len(rows)} rows loaded")

    # Count classifications
    from collections import Counter
    cats = Counter(classify(r) for r in rows)
    print("\nClassification preview:")
    for cat, n in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"  {cat:<20} {n}")

    # Show home-care and day-care rows for manual review
    print("\n── Home Care rows ──────────────────────────────────")
    for r in rows:
        if classify(r) == "Home Care":
            print(f"  [{r.get('state','?')}] {r.get('title','?')[:60]}  |  {r.get('care_types','')[:60]}")

    print("\n── Day Care rows ───────────────────────────────────")
    for r in rows:
        if classify(r) == "Day Care":
            print(f"  [{r.get('state','?')}] {r.get('title','?')[:60]}  |  {r.get('care_types','')[:60]}")

    print("\n── Assisted Living rows ────────────────────────────")
    for r in rows:
        if classify(r) == "Assisted Living":
            print(f"  [{r.get('state','?')}] {r.get('title','?')[:60]}  |  {r.get('care_types','')[:60]}")

    print("\nDone (dry run — no sheet writes performed).")
    print("To write to the sheet, add Google Sheets API auth and call batchUpdate.")
    print("See: https://developers.google.com/sheets/api/guides/values#writing")


if __name__ == "__main__":
    main()
