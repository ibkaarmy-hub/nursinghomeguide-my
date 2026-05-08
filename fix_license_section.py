"""
Fix the License & verification section in the 30 enriched editorials.

When all three fields (JKM status, JKM verified via, MOH status) are
"unverified", replace the entire bullet list with a single clean line:
  - To be verified — confirm JKM registration on visit.

Also removes the "jkm_verified_via" bullet which is always redundant.

Reads from:  pending_editorials/uploaded/2026-05-08-enriched-batch.json
Writes to:   pending_editorials/2026-05-08-license-fix.json  (new batch for upload)
"""
import json, re, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

SRC  = Path("pending_editorials/uploaded/2026-05-08-enriched-batch.json")
OUT  = Path("pending_editorials/2026-05-08-license-fix.json")

data = json.loads(SRC.read_text(encoding="utf-8"))

# Pattern: the full License & verification section block
LICENSE_BLOCK = re.compile(
    r'\*\*License & verification\*\*\n'   # header line
    r'(?:- .*\n?)*',                       # one or more bullet lines
    re.MULTILINE
)

def fix_license(editorial):
    def replace_block(m):
        block = m.group(0)
        # Check if ALL status values in block are unverified / not_applicable
        statuses = re.findall(r':\*\*\s*(.*)', block)
        all_unverified = all(
            s.strip().lower() in ('unverified', 'not_applicable', 'not applicable', '')
            for s in statuses
        )
        if all_unverified:
            return "**License & verification**\n- To be verified — confirm JKM and MOH registration on visit.\n"
        # Partially verified: keep registered/licensed items, drop unverified lines
        lines = block.split('\n')
        kept = [lines[0]]  # keep the header
        for line in lines[1:]:
            if not line.strip():
                continue
            val = re.search(r':\*\*\s*(.*)', line)
            if val and val.group(1).strip().lower() not in ('unverified', 'not_applicable', 'not applicable'):
                kept.append(line)
        if len(kept) == 1:
            kept.append("- To be verified — confirm JKM and MOH registration on visit.")
        return '\n'.join(kept) + '\n'
    return LICENSE_BLOCK.sub(replace_block, editorial)

fixed = []
for f in data["facilities"]:
    orig = f.get("editorial_summary", "")
    cleaned = fix_license(orig)
    f["editorial_summary"] = cleaned
    fixed.append(f)
    changed = "✓ fixed" if cleaned != orig else "  same"
    print(f"{changed}  {f['slug'][:55]}")

out_data = {"batch_date": data["batch_date"], "total": len(fixed), "facilities": fixed}
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(out_data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nWritten → {OUT}")
