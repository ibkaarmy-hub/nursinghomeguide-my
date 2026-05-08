"""
Fix the "What to ask on visit" section in 30 enriched editorials.

Rules:
- MOH licensed  → remove ALL JKM-related ask bullets (MOH ≠ JKM; they won't have one)
- JKM confirmed → remove "Is [it] registered with JKM?" bullets (we already confirmed it)
                  keep other JKM questions (e.g. eligibility criteria, specific branch details)
- Unverified    → keep as-is

Reads:  pending_editorials/uploaded/2026-05-09-header-license-fix.json
CSV:    facilities_local.csv
Writes: pending_editorials/2026-05-09-jkm-ask-fix.json
"""
import csv, json, re, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

SRC = Path("pending_editorials/uploaded/2026-05-09-header-license-fix.json")
CSV = Path("facilities_local.csv")
OUT = Path("pending_editorials/2026-05-09-jkm-ask-fix.json")

csv_rows = {r["slug"]: r for r in csv.DictReader(CSV.open(encoding="utf-8"))}

def get_status(row):
    src = (row.get("jkm_data_source") or "").strip().lower()
    if "moh" in src: return "MOH"
    if "jkm" in src: return "JKM"
    return "unverified"

def is_redundant_jkm_ask(bullet, status):
    """
    Returns True if the bullet should be removed given the facility's confirmed status.

    MOH:  remove any bullet that mentions JKM (they're MOH, not JKM)
    JKM:  remove bullets that ask WHETHER it's registered with JKM
          (i.e. the question is redundant — we already know it is)
          Keep questions about eligibility criteria, admission process, etc.
    """
    low = bullet.lower()
    if "jkm" not in low:
        return False  # not about JKM at all — keep

    if status == "MOH":
        # Any JKM ask is irrelevant for MOH-licensed facilities
        return True

    if status == "JKM":
        # Remove "Is [it] registered with JKM?" style bullets
        # Pattern: starts with "Is" (or question form) asking about registration status
        registration_patterns = [
            r"^is (the|this|a) (facility|home|centre|association)\b.*(registered|licence|license|certificate)",
            r"^can you show the jkm registration certificate",
        ]
        for pat in registration_patterns:
            if re.search(pat, low.strip("- ").strip()):
                return True

    return False

def fix_ask_section(text, status):
    """Strip redundant JKM bullets from 'What to ask on visit' block."""
    ask_marker = "**What to ask"
    ask_pos = text.find(ask_marker)
    if ask_pos < 0:
        return text

    before = text[:ask_pos]
    ask_block = text[ask_pos:]

    lines = ask_block.split("\n")
    kept = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- ") and is_redundant_jkm_ask(stripped[2:], status):
            continue  # drop it
        kept.append(line)

    return before + "\n".join(kept)

data = json.loads(SRC.read_text(encoding="utf-8"))
fixed = []

for f in data["facilities"]:
    slug = f["slug"]
    row = csv_rows.get(slug, {})
    status = get_status(row)
    orig = f.get("editorial_summary", "")
    cleaned = fix_ask_section(orig, status)
    f["editorial_summary"] = cleaned.strip()
    fixed.append(f)

    changed = "✓" if cleaned != orig else " "
    print(f"  {changed} [{status:10}] {slug[:55]}")

OUT.parent.mkdir(exist_ok=True)
OUT.write_text(
    json.dumps({"batch_date": "2026-05-09", "total": len(fixed), "facilities": fixed},
               ensure_ascii=False, indent=2),
    encoding="utf-8"
)
print(f"\nWritten → {OUT}")
