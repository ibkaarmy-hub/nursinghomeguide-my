#!/usr/bin/env python3
"""
Update home care profile rows in the Google Sheet.
Adds pricing, corrects editorial, fixes websites for:
  - homage-malaysia
  - care-concierge-malaysia
  - pillar-care
  - noble-care-malaysia (fix wrong care_types)
  - whereweare-malaysia
"""

import sys, os
sys.stdout.reconfigure(encoding='utf-8')

# Token lives in main repo root
TOKEN_PATH = r"C:\Users\ibkaa\nursinghomeguide-my\Nursing Home Guide Malaysia\token_sheets.json"
SHEET_ID   = "1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk"
SHEET_TAB  = "google-sheets-facilities.csv"
DETAILS_TAB = "Details"

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import json, csv, urllib.request, io
from datetime import date

TODAY = str(date.today())

# ── Auth ────────────────────────────────────────────────────────────────────
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
service = build('sheets', 'v4', credentials=creds)
sheets = service.spreadsheets()

# ── Fetch sheet headers + all rows ───────────────────────────────────────────
result = sheets.values().get(spreadsheetId=SHEET_ID, range=f"{SHEET_TAB}!A1:BH1").execute()
headers = result['values'][0]
print("Columns found:", len(headers))

def col(name):
    return headers.index(name)

def a1(row_idx, col_name):
    """1-indexed row, column name → A1 notation"""
    c = col(col_name)
    col_letter = ""
    n = c + 1
    while n:
        n, r = divmod(n - 1, 26)
        col_letter = chr(65 + r) + col_letter
    return f"{SHEET_TAB}!{col_letter}{row_idx}"

# Fetch all slugs to find row indices — slug is column B (index 1)
result = sheets.values().get(spreadsheetId=SHEET_ID, range=f"{SHEET_TAB}!B:B").execute()
slugs = [r[0] if r else "" for r in result['values']]

def find_row(slug):
    for i, s in enumerate(slugs):
        if s == slug:
            return i + 1  # 1-indexed
    return None

# ── Updates to apply ─────────────────────────────────────────────────────────
UPDATES = [
    {
        "slug": "homage-malaysia",
        "fields": {
            "care_types": "Home Care",
            "pricing_display": "From RM30/hr (caregiver); RM36/hr (nurse); RM135/hr (therapist)",
            "website": "https://www.homage.com.my",
            "last_updated": TODAY,
            "editorial_summary": (
                "Homage is Malaysia's largest app-based home care platform, connecting families with trained caregivers, "
                "licensed nurses, and certified therapists for care delivered in the client's own home. The service operates "
                "in Kuala Lumpur, Selangor, Johor, Penang, Perak (Ipoh), and Kedah. Booking is done through the Homage app "
                "(iOS and Android), which shows each Care Pro's qualifications and experience. Care can start within five "
                "working days of confirmed booking; 24-hour care is available using two Care Pros in rotating 12-hour shifts. "
                "The Care Pro pool is described as 3,000+ Malaysians, with a less-than-5% acceptance rate and a 4.8-star "
                "professional rating.\n\n"
                "Services cover three categories: Home Personal Care (ADLs — bathing, dressing, toileting, transfers, meal "
                "preparation, companionship), Home Nursing by licensed nurses (wound care, NGT feeding, catheter, stoma, "
                "medication administration, post-surgery procedures), and Home Therapy by certified therapists (physiotherapy, "
                "occupational therapy, speech therapy). Specialised programmes are available for dementia, stroke rehabilitation, "
                "cancer care, Parkinson's disease, palliative care, and end-of-life support. Hospital partners include Qualitas, "
                "SunMed, and CVSKL.\n\n"
                "Published floor rates are: daily living care from RM30/hour (certified caregivers), home nursing from RM36/hour "
                "(licensed nurses), and home therapy from RM135/hour (therapists). Multi-session packages reduce the per-hour "
                "cost — speak with a Care Advisor for package pricing. Homage is best suited to families who want flexible, "
                "on-demand care — from a single hour to full 24-hour cover — without committing to a residential facility."
            ),
        },
        "details_rows": [
            ("rooms", "Daily living care (per hour)", "From RM30 — by certified local caregiver"),
            ("rooms", "Home nursing (per hour)", "From RM36 — by licensed nurse"),
            ("rooms", "Home therapy (per hour)", "From RM135 — by certified therapist"),
            ("rooms", "24-hour care", "Yes — 2 Care Pros in 12-hour shifts"),
            ("rooms", "Minimum booking", "1 hour"),
            ("rooms", "Pricing source", "https://www.homage.com.my/services/home-care/ — published on operator website"),
            ("services", "Home Personal Care", "ADLs, companionship, medical escort, respite"),
            ("services", "Home Nursing", "Wound care, NGT, catheter, stoma, post-surgery, medication"),
            ("services", "Home Therapy", "Physiotherapy, occupational therapy, speech therapy"),
            ("services", "Dementia Care", "Specialist programme"),
            ("services", "Stroke Rehabilitation", "Post-stroke at-home care"),
            ("services", "Palliative / End-of-Life Care", "Available"),
            ("policies", "Coverage", "KL, Selangor, Johor, Penang, Perak (Ipoh), Kedah"),
            ("policies", "Booking method", "Homage app (iOS / Android) — caregivers listed with qualifications"),
            ("policies", "Care start time", "Within 5 working days of confirmed booking"),
        ],
    },
    {
        "slug": "care-concierge-malaysia",
        "fields": {
            "care_types": "Home Care|Day Care|Palliative",
            "pricing_display": "From RM235/day (live-in caregiver); from RM200 for 4h visit; RM10,800/mo (stroke/dementia bundle)",
            "phone": "+603 2724 3828",
            "whatsapp": "60189815128",
            "last_updated": TODAY,
            "editorial_summary": (
                "Care Concierge is a Malaysian senior care specialist offering home-based caregiving, assisted living "
                "residences, and senior day care under one brand. The company focuses on specialised care for Alzheimer's, "
                "Parkinson's, dementia, cancer, and post-stroke and post-surgery recovery. At-home services are available "
                "in Penang, Perak (Ipoh), KL, Selangor, Melaka, Negeri Sembilan, and Johor. Assisted living residences "
                "are located in KL, Petaling Jaya, Penang, and Kuching, Sarawak. A senior day care programme and the "
                "company's own care-tracking app round out the offering.\n\n"
                "Care Concierge publishes its full price list online, which is unusual in the Malaysian home care market. "
                "The Care Plus live-in package starts from RM235/day on a 20-day monthly plan (RM300/day on a daily basis). "
                "Flexible Flexi Care visits start from RM200 for a 4-hour plan. Comprehensive specialist bundles for stroke "
                "and dementia are priced at RM10,800/month — this includes a nurse/care manager, a neurologist consultation, "
                "physiotherapy three times weekly, and a full month of professional caregiving. A Doctor House Call service "
                "is available at RM300/visit (Medical Officer) or RM500/visit (Specialist). Physiotherapy sessions are "
                "RM200 each, occupational therapy RM180, and speech therapy RM300 for 45 minutes.\n\n"
                "Care Concierge is one of the few Malaysian operators that bridges home care and residential care under one "
                "roof, which is useful for families not yet certain which route to take. The published price schedule makes "
                "it straightforward to compare costs against nursing home placement. Reach them at +603 2724 3828 or via "
                "WhatsApp at 60189815128."
            ),
        },
        "details_rows": [
            ("rooms", "Care Plus live-in (20-day monthly min)", "From RM235/day (RM300 daily rate)"),
            ("rooms", "Care Plus day care (20-day monthly min)", "From RM270/day (RM320 daily rate)"),
            ("rooms", "Care Palliative live-in (7-day monthly)", "From RM2,200 (RM8,000 for 28-day monthly)"),
            ("rooms", "Flexi Care 4h plan (1-month validity)", "RM200"),
            ("rooms", "Flexi Care 20h plan (1-month validity)", "RM950"),
            ("rooms", "Flexi Care 100h plan (3-month validity)", "RM4,250"),
            ("rooms", "Flexi Nurse 4h plan (1-month validity)", "RM230"),
            ("rooms", "Flexi Nurse 20h plan (1-month validity)", "RM1,010"),
            ("rooms", "Flexi Nurse 100h plan (3-month validity)", "RM4,750"),
            ("rooms", "Stroke Care bundle (monthly)", "RM10,800 — includes nurse/care manager, neurologist consult (1x), physio 3x/wk, medical chaperone 2x/mo, 1mo caregiving"),
            ("rooms", "Dementia Care bundle (monthly)", "RM10,800 — includes nurse/care manager, neurologist consult (1x), physio/OT 3x/wk, 1mo caregiving"),
            ("rooms", "Care Companion (daily, max 12h)", "From RM260/day; RM4,000/mo (6 working days/wk)"),
            ("rooms", "Doctor House Call (Medical Officer)", "RM300/visit — available KL, Selangor, Cyberjaya, Putrajaya, Rawang"),
            ("rooms", "Doctor House Call (Medical Specialist)", "RM500/visit"),
            ("rooms", "Physiotherapy (1h session)", "RM200 single; RM950 / 5 sessions; RM1,800 / 10 sessions"),
            ("rooms", "Occupational Therapy (1h)", "RM180/session"),
            ("rooms", "Speech Therapy (45 min)", "RM300/session"),
            ("rooms", "Medical Chaperone (2-way, 5h)", "RM220 — excludes transport charges"),
            ("rooms", "Medical Nursing Procedure (1h)", "RM180"),
            ("rooms", "Pricing source", "https://mycareconcierge.com/at-home-care/ — full price list published on operator website"),
            ("services", "At-Home Care", "Live-in (24/7) or Flexi (part-time) — caregivers and registered nurses"),
            ("services", "Assisted Living Residences", "KL, Petaling Jaya, Penang, Kuching (Sarawak)"),
            ("services", "Senior Day Care", "Multiple locations — see Care Concierge website"),
            ("services", "Stroke Care", "Multidisciplinary bundle with neurologist, physio, caregiving"),
            ("services", "Dementia / Alzheimer's Care", "Multidisciplinary bundle with neurologist, physio/OT, caregiving"),
            ("services", "Palliative Care", "Advanced care needs — live-in or palliative package"),
            ("services", "Geriatric Physiotherapy", "Specialised programme"),
            ("policies", "Coverage", "Penang, Perak (Ipoh), KL, Selangor, Melaka, Negeri Sembilan, Johor"),
            ("policies", "Care Academy", "Khazanah-sponsored K-Youth training programme for caregivers (May–Sep 2026)"),
        ],
    },
    {
        "slug": "pillar-care",
        "fields": {
            "care_types": "Home Care|Nursing",
            "pricing_display": "RM4,600 / 20 working days (home care or nursing support)",
            "website": "https://www.pillarcare.com",
            "phone": "+60182046966",
            "last_updated": TODAY,
            "editorial_summary": (
                "Pillar Care (Pillar Health Sdn Bhd) is a Petaling Jaya–based home care agency delivering in-home personal "
                "care and nursing services for elderly Malaysians. Operating from PJ21 Commercial Centre in SS3, the "
                "company places trained caregivers and private duty nurses who visit clients at home. Services cover "
                "companion care, personal care assistance (ADLs), senior transportation, medication management, and full "
                "home nursing procedures including wound dressing, nasogastric tube care, catheter management, and stoma "
                "care. Private duty nurses are available around the clock, 24 hours a day, seven days a week, for both "
                "scheduled visits and hourly care.\n\n"
                "Specialised programmes are offered for dementia, stroke, Parkinson's, diabetes, cancer, multiple sclerosis, "
                "palliative care, and end-of-life care. The company states that 8,582 Malaysian families have used their "
                "service, and all Care Specialists go through training reviewed by external auditors. Published pricing is "
                "RM4,600 for a 20-working-day package — equivalent to approximately RM230/day — applicable to both home "
                "care and home nursing support. The company notes that hourly rates from other providers typically run "
                "RM30–RM50/hour by comparison.\n\n"
                "Pillar suits Klang Valley families who want a committed package-based arrangement rather than ad-hoc "
                "app bookings. The standard billing unit is a 20-day care block. Contact at +6018 2046966 or "
                "hello@pillarcare.com; the active website is pillarcare.com (the .com.my variant redirects)."
            ),
        },
        "details_rows": [
            ("rooms", "Home Care/Nursing Support (20-day package)", "RM4,600"),
            ("rooms", "Equivalent daily rate", "~RM230/day"),
            ("rooms", "Market comparison (operator-cited)", "RM30–50/hr for hourly home care in Malaysia"),
            ("rooms", "Pricing source", "https://www.pillarcare.com/home-care/ — published on operator website"),
            ("services", "Home Personal Care", "ADLs, companion care, senior transportation, medication management"),
            ("services", "Home Nursing", "Wound dressing, NGT, catheter, stoma, injections, medical procedures"),
            ("services", "Dementia Care", "Guided dementia programme available"),
            ("services", "Stroke Care", "Available"),
            ("services", "Palliative / End-of-Life Care", "Available"),
            ("services", "Respite Care", "Available"),
            ("services", "Hospital In Care", "Short-term hospital companion/care available"),
            ("policies", "Coverage area", "Klang Valley (based in PJ SS3)"),
            ("policies", "Standard billing cycle", "20 working days per package"),
            ("policies", "Availability", "24/7 — nurses available any hour"),
        ],
    },
    {
        "slug": "noble-care-malaysia",
        "fields": {
            "care_types": "Nursing Home",
            "website": "https://www.mynoblecare.com",
            "last_updated": TODAY,
            "editorial_summary": (
                "Noble Care (Noble Care (M) Sdn Bhd, reg. 903876-P) is a Malaysian nursing home chain with over 15 "
                "residential branches across the country, including Cheras, Rawang, Klang, Petaling Jaya, USJ-9 Subang "
                "Jaya, USJ-18, Jalan IPOH, Ampang, Semenyih, Kajang, Mid Valley, Seremban, and Serendah in the central "
                "region, plus branches in Johor Bahru, Ipoh, and Penang. The head office is at USJ 9 Subang Business "
                "Centre, Subang Jaya. Noble Care has been operating for 16+ years and positions itself as a full-service "
                "nursing home group.\n\n"
                "Care offerings at residential branches include nursing care, dementia and Alzheimer's care, palliative "
                "care, stroke and cancer recovery, respite admissions, handicapped adult and children care, and "
                "physiotherapy. The group also offers home nursing as a secondary service. Each residential branch "
                "maintains doctors and nurses available 24/7. The chain provides private and shared living spaces, "
                "social and recreational activities, nutritious meals, and outdoor areas across its branches.\n\n"
                "This entry covers the Noble Care brand and head office. Individual branch profiles are listed separately "
                "in this directory for Rawang, Klang, Subang Jaya (USJ-9 and USJ-18), Jalan IPOH, and other locations. "
                "For specific pricing and availability, contact the relevant branch directly. Head office: "
                "+60-167786795 or +60-162786993."
            ),
        },
        "details_rows": [],
    },
    {
        "slug": "whereweare-malaysia",
        "fields": {
            "care_types": "Home Care|Nursing",
            "pricing_display": "From RM3,700/28 days (live-in caregiver); RM1,200/week; RM200/day",
            "website": "https://wherewecare.com",
            "whatsapp": "601161963941",
            "last_updated": TODAY,
            "editorial_summary": (
                "WhereWeCare is a Malaysian home care agency placing certified caregivers and registered nurses for "
                "in-home elderly care across major Malaysian cities — Kuala Lumpur, Penang, Johor Bahru, Ipoh, "
                "Melaka, and Perak, with nationwide coverage on request. The agency operates on a placement model: "
                "it assesses care needs, matches a suitable caregiver, and manages the ongoing arrangement. Key "
                "features include no long-term contracts, free carer replacement if needed, and transparent published "
                "pricing with no hidden costs. The company cites 500+ satisfied clients and over 10 years of "
                "experience in elderly care.\n\n"
                "Services focus on live-in caregiving arrangements. All plans cover nutritious meal preparation, "
                "mobility support, physiotherapy exercises, bedsore prevention, medical appointment accompaniment, "
                "and companionship. Specialised programmes are available for dementia, palliative care, post-surgery "
                "recovery, and customised wellness plans including nutrition guidance and mental health support. "
                "Registered nurses are also available for nursing-level procedures at home.\n\n"
                "Published pricing: the 28-day live-in package starts from RM3,700 per four weeks (approximately "
                "RM132/day), the 7-day package from RM1,200/week, and daily bookings from RM200/day. The monthly "
                "package price is competitive against shared-room nursing home rates in the Klang Valley, making "
                "it a genuine option for seniors who can manage at home with round-the-clock support. Enquire via "
                "WhatsApp at +60 11-6196 3941 or visit wherewecare.com."
            ),
        },
        "details_rows": [
            ("rooms", "28-day Live-In package", "From RM3,700 (~RM132/day)"),
            ("rooms", "7-day Live-In package", "From RM1,200/week (~RM171/day)"),
            ("rooms", "1-day Live-In (daily rate)", "From RM200/day"),
            ("rooms", "Pricing source", "https://wherewecare.com/live-in-care — published on operator website"),
            ("services", "Live-In Home Care", "24/7 in-home support, companionship, basic health monitoring, emergency support"),
            ("services", "Dementia Care", "Tailored live-in programme"),
            ("services", "Palliative Care", "Comfort-focused live-in care for serious illness"),
            ("services", "Post-Surgery Recovery", "At-home assistance during recovery"),
            ("services", "Customised Wellness Program", "Exercise, nutrition guidance, mental health support"),
            ("services", "Home Nursing", "Registered nurses available for nursing procedures"),
            ("policies", "Contract", "No long-term contract required"),
            ("policies", "Carer replacement", "Free replacement if needed"),
            ("policies", "Coverage", "KL, Penang, Johor Bahru, Ipoh, Melaka, Perak — nationwide on request"),
            ("included", "Meal preparation", "yes"),
            ("included", "Mobility support", "yes"),
            ("included", "Bedsore prevention", "yes"),
            ("included", "Medical appointment accompaniment", "yes"),
            ("included", "Companionship", "yes"),
        ],
    },
]

# ── Validation: check all editorials are clean ──────────────────────────────
for u in UPDATES:
    ed = u["fields"].get("editorial_summary", "")
    assert '"' not in ed, f"Straight double-quote found in editorial for {u['slug']}!"
print("Editorial validation passed.")

# ── Push facility row updates ────────────────────────────────────────────────
batch_data = []
errors = []
for u in UPDATES:
    row_idx = find_row(u["slug"])
    if row_idx is None:
        errors.append(f"Slug not found: {u['slug']}")
        continue
    print(f"Found {u['slug']} at row {row_idx}")
    for field, value in u["fields"].items():
        if field not in headers:
            errors.append(f"Column not found: {field} (for {u['slug']})")
            continue
        batch_data.append({
            "range": a1(row_idx, field),
            "values": [[value]]
        })

if errors:
    print("\nERRORS:")
    for e in errors:
        print(" ", e)
    sys.exit(1)

print(f"\nPushing {len(batch_data)} cell updates...")
sheets.values().batchUpdate(
    spreadsheetId=SHEET_ID,
    body={"valueInputOption": "RAW", "data": batch_data}
).execute()
print("Facility rows updated.")

# ── Push Details tab rows ─────────────────────────────────────────────────────
# First fetch all existing Details rows to avoid duplication
det_result = sheets.values().get(
    spreadsheetId=SHEET_ID,
    range=f"{DETAILS_TAB}!A:D"
).execute()
det_rows = det_result.get('values', [])
det_headers = det_rows[0] if det_rows else ["slug", "section", "label", "value"]
# Build set of existing (slug, section, label)
existing_keys = set()
for row in det_rows[1:]:
    if len(row) >= 3:
        existing_keys.add((row[0], row[1], row[2]))

new_detail_rows = []
for u in UPDATES:
    slug = u["slug"]
    for section, label, value in u.get("details_rows", []):
        if (slug, section, label) not in existing_keys:
            new_detail_rows.append([slug, section, label, value])
            existing_keys.add((slug, section, label))

if new_detail_rows:
    print(f"\nAppending {len(new_detail_rows)} new Details rows...")
    sheets.values().append(
        spreadsheetId=SHEET_ID,
        range=f"{DETAILS_TAB}!A:D",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": new_detail_rows}
    ).execute()
    print("Details rows appended.")
else:
    print("No new Details rows to append.")

print(f"\nDone. Updated {len(UPDATES)} facilities.")
print("Slugs updated:")
for u in UPDATES:
    print(f"  - {u['slug']}")
