import json
import csv

with open('audit_data.json', encoding='utf-8') as f:
    d = json.load(f)

with open('sheet.csv', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

def val(row, key):
    return (row.get(key) or '').strip()

def safe_float(v):
    try:
        return float(v)
    except:
        return 0.0

def safe_int(v):
    try:
        return int(v)
    except:
        return 0

# Potential high-confidence facilities (rating >= 4.0, reviews >= 5)
potential = [r for r in rows if safe_float(val(r,'rating')) >= 4.0 and safe_int(val(r,'review_count')) >= 5]
potential.sort(key=lambda r: (-safe_float(val(r,'rating')), -safe_int(val(r,'review_count'))))

total = d['total']

lines = []
lines.append("# Social Worker Audit Report — Johor Nursing Homes")
lines.append("**Generated:** 2026-05-01  ")
lines.append("**Dataset:** sheet.csv (local snapshot from Google Sheets — Sheet ID 1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk)  ")
lines.append("**Total facilities audited:** " + str(total))
lines.append("")
lines.append("---")
lines.append("")
lines.append("## Section 1: Coverage Gaps")
lines.append("")
lines.append("These facilities are missing key information that families rely on when making care decisions.")
lines.append("")

# 1.1 No phone
lines.append("### 1.1 No Phone Number (" + str(len(d['no_phone'])) + " facilities)")
lines.append("")
for item in d['no_phone']:
    line = "- " + item[0]
    if item[1]:
        line += " (" + item[1] + ")"
    lines.append(line)
lines.append("")

# 1.2 No website
lines.append("### 1.2 No Website (" + str(len(d['no_website'])) + " facilities)")
lines.append("")
for item in d['no_website']:
    line = "- " + item[0]
    if item[1]:
        line += " (" + item[1] + ")"
    lines.append(line)
lines.append("")

# 1.3 No rating
lines.append("### 1.3 No Rating / Never Reviewed Online (" + str(len(d['no_rating'])) + " facilities)")
lines.append("")
lines.append("These facilities have zero Google reviews — invisible to families searching online.")
lines.append("")
for item in d['no_rating']:
    line = "- " + item[0]
    if item[1]:
        line += " (" + item[1] + ")"
    lines.append(line)
lines.append("")

# 1.4 No editorial
lines.append("### 1.4 No Editorial Summary (" + str(len(d['no_editorial'])) + " facilities)")
lines.append("")
lines.append("All " + str(len(d['no_editorial'])) + " facilities currently lack an editorial_summary. This is a content pipeline gap — editorial copy has not been written for any listing yet.")
lines.append("")

# 1.5 Pricing
lines.append("### 1.5 No Pricing Display (" + str(len(d['no_pricing'])) + " facilities)")
lines.append("")
lines.append("**All " + str(total) + " facilities have a pricing_display value.** The pricing transparency goal is met at the data-entry level — though many entries are 'Call for pricing' rather than actual figures.")
lines.append("")

lines.append("---")
lines.append("")
lines.append("## Section 2: Quality Flags")
lines.append("")

# 2.1 Low rating
lines.append("### 2.1 Low Rating (<2.5 stars, with >2 reviews) — " + str(len(d['low_rating'])) + " facilities")
lines.append("")
lines.append("These facilities have sustained low ratings from multiple reviewers, which is a genuine welfare concern.")
lines.append("")
lines.append("| Facility | Rating | Reviews |")
lines.append("|----------|--------|---------|")
for item in d['low_rating']:
    lines.append("| " + item[0] + " | " + item[1] + " | " + item[2] + " |")
lines.append("")
lines.append("**AustinLoyal Care Centre** is the most concerning: rated 1.9 from 260 reviews — a large sample size making this statistically meaningful.")
lines.append("**Golden Age Care Centre Batu Pahat**: rated 1.3 from only 3 reviews — small sample, but warrants a check-in.")
lines.append("")

# 2.2 No care types
pct = round(len(d['no_care']) / total * 100)
lines.append("### 2.2 No Care Types Documented (" + str(len(d['no_care'])) + " of " + str(total) + " facilities — " + str(pct) + "%)")
lines.append("")
lines.append(str(len(d['no_care'])) + " facilities have no care_types field populated. This means families cannot filter by nursing care, dementia care, palliative, rehabilitation, etc.")
lines.append("")
lines.append("**Facilities missing care types (first 20 listed):**")
lines.append("")
for item in d['no_care'][:20]:
    line = "- " + item[0]
    if item[1]:
        line += " (" + item[1] + ")"
    lines.append(line)
if len(d['no_care']) > 20:
    lines.append("- *...and " + str(len(d['no_care']) - 20) + " more*")
lines.append("")

# 2.3 No licence
lines.append("### 2.3 No Licence Number (" + str(len(d['no_licence'])) + " of " + str(total) + " facilities — 100%)")
lines.append("")
lines.append("**Zero facilities have a licence_number recorded.** The licence_number column exists in the schema but has not been populated from JKM records. This is a critical data gap — a social worker cannot verify regulatory compliance for any listing. Sourcing licence numbers from the JKM directory should be a high-priority data enrichment task.")
lines.append("")

# 2.4 No RN
lines.append("### 2.4 No RN 24/7 Coverage Documented (" + str(d['no_rn_count']) + " of " + str(total) + " facilities — 100%)")
lines.append("")
lines.append("The rn_24_7 column is unpopulated across all facilities. For care homes claiming to be nursing homes, overnight registered nurse coverage is a baseline safety requirement. This field requires outreach/verification for every listing.")
lines.append("")

lines.append("---")
lines.append("")
lines.append("## Section 3: Data Completeness Score Per Facility")
lines.append("")
lines.append("**Scoring rubric (1 point each):** phone | website | pricing | editorial_summary | rating | licence_number | care_types | hero_image | lat/lng | total_beds")
lines.append("")
lines.append("**Note:** Because licence_number and editorial_summary are missing across the entire dataset, no facility can currently score above 8/10.")
lines.append("")
lines.append("### Facilities Scoring 5 or Below (" + str(len(d['low_score'])) + " of " + str(total) + ")")
lines.append("")
lines.append("| Score | Facility | Area |")
lines.append("|-------|----------|------|")
for item in d['low_score']:
    area = item[1] if item[1] else "—"
    lines.append("| " + str(item[2]) + " | " + item[0] + " | " + area + " |")
lines.append("")
lines.append("**4 facilities score only 2/10** — these are priority candidates for data collection or removal from the directory if they cannot be verified.")
lines.append("")

lines.append("---")
lines.append("")
lines.append("## Section 4: Subsidy / Welfare Homes")
lines.append("")
lines.append("These facilities accept government subsidy or are welfare-type operations. They are critical for low-income families.")
lines.append("")
lines.append("**Total identified: " + str(len(d['subsidy'])) + "**")
lines.append("")
lines.append("| Facility | Area | Subsidy | Ownership Type |")
lines.append("|----------|------|---------|----------------|")
for item in d['subsidy']:
    area = item[1] if item[1] else "—"
    subsidy = item[2] if item[2] else "—"
    own = item[3] if item[3] else "—"
    lines.append("| " + item[0] + " | " + area + " | " + subsidy + " | " + own + " |")
lines.append("")
lines.append("**Important caveat:** The subsidy field appears to be populated only for EHA Group facilities and Jeta Care. Many genuine welfare homes (e.g., Pusat jagaan kebajikan Manna Sinar Cahaya, Rumah Sejahtera Yong Peng, Persatuan Kebajikan Orang Tua Ceria) have 'kebajikan' or 'rumah' in their name suggesting welfare status but are not flagged in the data. The subsidy field needs systematic verification across the full dataset.")
lines.append("")

lines.append("---")
lines.append("")
lines.append("## Section 5: High-Confidence Listings")
lines.append("")
lines.append("**Criteria: completeness score >= 8 AND rating >= 4.0 AND review_count >= 5**")
lines.append("")
lines.append("**Result: 0 facilities currently meet this threshold.**")
lines.append("")
lines.append("This is expected given that:")
lines.append("1. The licence_number column is empty across all 125 facilities (costs 1 point each)")
lines.append("2. The editorial_summary column is empty across all 125 facilities (costs 1 point each)")
lines.append("3. Maximum achievable score currently is 8/10")
lines.append("")
lines.append("**Facilities that would qualify once editorial and licence fields are populated (rating >= 4.0, reviews >= 5):**")
lines.append("")
lines.append("| Facility | Area | Rating | Reviews |")
lines.append("|----------|------|--------|---------|")
for r in potential[:15]:
    area = val(r,'area') if val(r,'area') else "—"
    lines.append("| " + val(r,'title') + " | " + area + " | " + val(r,'rating') + " | " + val(r,'review_count') + " |")
if len(potential) > 15:
    lines.append("| *...and " + str(len(potential) - 15) + " more* | | | |")
lines.append("")
lines.append("These " + str(len(potential)) + " facilities should be prioritised for editorial copy and licence number lookup — they will immediately become high-confidence listings once those two fields are filled.")
lines.append("")

lines.append("---")
lines.append("")
lines.append("## Section 6: Red Flag Summary")
lines.append("")
lines.append("- **AustinLoyal Care Centre** has a 1.9-star average from 260 reviewers — the largest review sample of any flagged facility. This warrants a direct welfare check or removal from recommended listings until investigated.")
lines.append("")
lines.append("- **Zero facilities have a licence number on file.** The entire dataset is unverifiable against JKM's regulatory register. Families currently have no way to confirm which listings are legally licensed. Sourcing JKM licence numbers must be treated as a pre-launch blocker.")
lines.append("")
lines.append("- **69% of facilities (86 of 125) have no care_types documented**, meaning the directory cannot currently serve its core filtering function. Families searching for dementia care, palliative care, or rehabilitation cannot find appropriate facilities from search results alone.")
lines.append("")
lines.append("- **All 125 facilities are missing RN 24/7 status and editorial summaries.** These are pipeline gaps (data not yet enriched, copy not yet written) rather than individual facility failures — but they collectively prevent the site from differentiating itself as a trustworthy, staff-verified directory.")
lines.append("")
lines.append("- **Only 7 facilities are flagged as subsidy-eligible**, but names like 'Rumah Sejahtera,' 'Persatuan Kebajikan,' and 'Pusat jagaan kebajikan' suggest welfare homes are under-counted. Low-income families are the most vulnerable users of this directory; the subsidy field needs systematic verification before publication.")
lines.append("")
lines.append("---")
lines.append("")
lines.append("*End of report. Data sourced from local sheet.csv snapshot as of 2026-05-01. For the authoritative live dataset, re-run against the published Google Sheet CSV.*")

report = "\n".join(lines)

with open('social_work_audit_report.md', 'w', encoding='utf-8') as f:
    f.write(report)

print("Report written successfully.")
print("Potential high-conf facilities: " + str(len(potential)))
print("Top 3:")
for r in potential[:3]:
    print("  " + val(r,'title') + " | " + val(r,'rating') + " | " + val(r,'review_count') + " reviews")
