"""
Fix two editorial issues across the 30 enriched facilities:

1. Remove the "**What it is**" section header (keep the paragraph text below it)
2. Replace the License & verification section with accurate text
   derived from jkm_data_source + licence_number in the CSV

Source:  pending_editorials/uploaded/2026-05-08-license-fix.json
CSV:     facilities_local.csv
Output:  pending_editorials/2026-05-09-header-license-fix.json
"""
import csv, json, re, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

SRC = Path("pending_editorials/uploaded/2026-05-08-license-fix.json")
CSV = Path("facilities_local.csv")
OUT = Path("pending_editorials/2026-05-09-header-license-fix.json")

# Load CSV index by slug
csv_rows = {r["slug"]: r for r in csv.DictReader(CSV.open(encoding="utf-8"))}

# ── Helpers ───────────────────────────────────────────────────────────────────

def license_block(r):
    """Build the correct License & verification bullet from sheet data."""
    src = (r.get("jkm_data_source") or "").strip().lower()
    num = (r.get("licence_number") or "").strip()

    if "moh" in src:
        return "**License & verification**\n- MOH Licensed — confirmed in MOH nursing home registry."
    if "jkm" in src:
        if num:
            return f"**License & verification**\n- JKM Registered — licence number: {num}."
        return "**License & verification**\n- JKM Registered — confirmed in JKM registry."
    # No data
    return "**License & verification**\n- To be verified — confirm JKM or MOH registration on visit."

LICENSE_SECTION = re.compile(
    r'\*\*License & verification\*\*\n(?:- .*\n?)+',
    re.MULTILINE
)

WHAT_IT_IS_HEADER = re.compile(
    r'^\*\*What it is\*\*\n',
    re.MULTILINE
)

def fix_editorial(text, row):
    # 1. Remove "**What it is**" header line (keep the paragraph text below)
    text = WHAT_IT_IS_HEADER.sub('', text)

    # 2. Replace the License section with accurate content
    replacement = license_block(row) + "\n"
    text, n = LICENSE_SECTION.subn(replacement, text)
    if n == 0:
        # Section missing entirely — append it before "What to ask"
        ask_pos = text.find("**What to ask")
        if ask_pos >= 0:
            text = text[:ask_pos] + replacement + "\n" + text[ask_pos:]
        else:
            text = text.rstrip() + "\n\n" + replacement

    return text.strip()

# ── Process ───────────────────────────────────────────────────────────────────

data = json.loads(SRC.read_text(encoding="utf-8"))
fixed = []

for f in data["facilities"]:
    slug = f["slug"]
    row = csv_rows.get(slug, {})
    orig = f.get("editorial_summary", "")
    cleaned = fix_editorial(orig, row)
    f["editorial_summary"] = cleaned
    fixed.append(f)

    src_label = (row.get("jkm_data_source") or "none").strip() or "none"
    lic_label  = (row.get("licence_number")  or "").strip()
    status = "MOH" if "moh" in src_label.lower() else ("JKM" if "jkm" in src_label.lower() else "unverified")
    print(f"  [{status:10}] {slug[:50]}" + (f"  lic={lic_label}" if lic_label else ""))

OUT.parent.mkdir(exist_ok=True)
OUT.write_text(
    json.dumps({"batch_date": "2026-05-09", "total": len(fixed), "facilities": fixed},
               ensure_ascii=False, indent=2),
    encoding="utf-8"
)
print(f"\nWritten → {OUT}")
