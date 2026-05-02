"""
add_new_providers.py — Step 2: Add anchor home care / day care providers
=========================================================================
Adds key home care agencies and day care centres as new rows in the sheet.
These are the brands families already search for — having them in the
directory makes the home care / day care sections credible immediately.

STATUS: Data rows below are pre-filled from research. Verify phone/website
        before writing to the sheet. Set write=True to push to Google Sheets.

Run: python add_new_providers.py
"""

# ── New provider data ─────────────────────────────────────────────────────
# Fields: title, slug, state, area, care_types, phone, website, care_category,
#         editorial_summary, status

NEW_PROVIDERS = [

    # ── HOME CARE AGENCIES ───────────────────────────────────────────────

    {
        "title":    "Homage Malaysia",
        "slug":     "homage-malaysia",
        "state":    "Kuala Lumpur",
        "area":     "Kuala Lumpur (Nationwide)",
        "care_types": "Home Care",
        "care_category": "Home Care",
        "phone":    "+60 16-299 3863",
        "website":  "https://www.homage.com.my",
        "status":   "",
        "editorial_summary": (
            "Malaysia's largest professional home care platform, matching families with trained "
            "caregivers and registered nurses for in-home elderly care. Services include personal "
            "care, wound care, post-surgical recovery, dementia support, and palliative home care. "
            "App-based matching with real-time caregiver tracking. Operates in KL, Selangor, Johor, "
            "Penang, Ipoh, Kedah, and Melaka. Pricing from RM29–40/hour; monthly packages available."
        ),
    },
    {
        "title":    "Care Concierge Malaysia",
        "slug":     "care-concierge-malaysia",
        "state":    "Selangor",
        "area":     "Petaling Jaya",
        "care_types": "Home Care|Palliative",
        "care_category": "Home Care",
        "phone":    "+60 3-7660 1803",
        "website":  "https://www.mycareconcierge.com",
        "status":   "",
        "editorial_summary": (
            "Premium home care provider based in Petaling Jaya offering live-in 24-hour care, "
            "post-stroke rehabilitation packages, palliative home care, and hospital-to-home "
            "transition programmes. Run by a team of nurses and social workers. Operates across "
            "KL, Selangor, Johor, Penang, Ipoh, and Melaka. Live-in stroke care from RM10,800/month."
        ),
    },
    {
        "title":    "Noble Care Malaysia",
        "slug":     "noble-care-malaysia",
        "state":    "Kuala Lumpur",
        "area":     "Kuala Lumpur",
        "care_types": "Home Care",
        "care_category": "Home Care",
        "phone":    "+60 3-7728 2886",
        "website":  "https://www.noblecare.com.my",
        "status":   "",
        "editorial_summary": (
            "Family-run home care agency established in 2005. Provides trained caregivers and "
            "nurses for elderly care at home across KL, Selangor, Johor, Ipoh, Negeri Sembilan, "
            "and Penang. Services include personal care, companionship, medication reminders, "
            "and nursing procedures. One of the longer-established agencies in the market."
        ),
    },
    {
        "title":    "Pillar Care",
        "slug":     "pillar-care",
        "state":    "Selangor",
        "area":     "Petaling Jaya",
        "care_types": "Home Care|Nursing",
        "care_category": "Home Care",
        "phone":    "",
        "website":  "https://www.pillarcare.com.my",
        "status":   "",
        "editorial_summary": (
            "Doctor-managed home care service based in Petaling Jaya. Offers structured care "
            "packages combining caregivers, registered nurses, physiotherapists, and occupational "
            "therapists for home-based elderly care. Packages from RM4,600 for 20 days. "
            "Covers Klang Valley and Johor."
        ),
    },
    {
        "title":    "WhereWeCare",
        "slug":     "whereweare-malaysia",
        "state":    "Kuala Lumpur",
        "area":     "Kuala Lumpur",
        "care_types": "Home Care|Nursing",
        "care_category": "Home Care",
        "phone":    "",
        "website":  "https://www.wherewecaremalaysia.com",
        "status":   "",
        "editorial_summary": (
            "Home care platform providing certified caregivers and registered nurses for elderly "
            "care at home. Operates in KL, Johor Bahru, Penang, Ipoh, and Melaka. Services "
            "include personal care, medication management, wound care, and companionship. "
            "Focuses on transparent pricing and background-checked caregivers."
        ),
    },

    # ── DAY CARE CENTRES ─────────────────────────────────────────────────

    {
        "title":    "Komune Care Senior Day Club",
        "slug":     "komune-care-cheras",
        "state":    "Kuala Lumpur",
        "area":     "Cheras",
        "care_types": "Day Care|Assisted Living",
        "care_category": "Day Care",
        "phone":    "+60 11-2688 6080",
        "website":  "https://www.komunecare.com",
        "status":   "",
        "editorial_summary": (
            "Malaysia's largest senior day club, located in Cheras, Kuala Lumpur. "
            "The Senior Day Club (RM125/day, 8am–6pm) provides supervised activities, meals, "
            "physical exercise, cognitive stimulation, and health monitoring for mobile seniors. "
            "Also offers assisted living studio apartments (from RM6,800/month) and independent "
            "living options (from RM2,100/month). Strong physiotherapy and occupational therapy "
            "programming. Often described as a community rather than a care facility."
        ),
    },
    {
        "title":    "Seniora Elderly Day Care Johor Bahru",
        "slug":     "seniora-johor-bahru",
        "state":    "Johor",
        "area":     "Johor Bahru",
        "care_types": "Day Care",
        "care_category": "Day Care",
        "phone":    "",
        "website":  "https://www.seniora.com.my",
        "status":   "",
        "editorial_summary": (
            "Private elderly day care centre with branches in Johor Bahru and Penang. "
            "Offers structured daily programmes including exercise, cognitive activities, "
            "meals, and health monitoring. Trial day available for RM80. Monthly packages "
            "up to RM3,580. Suitable for mobile seniors with mild to moderate care needs, "
            "including early-stage dementia. Seniors return home each evening."
        ),
    },

]


def preview():
    print(f"New providers to add: {len(NEW_PROVIDERS)}\n")
    for p in NEW_PROVIDERS:
        cat = p.get("care_category", "?")
        print(f"  [{cat:<15}] {p['title'][:50]:<50}  {p.get('state','')}")


def main(write=False):
    preview()

    if not write:
        print("\n── DRY RUN — no rows written ──────────────────────────────")
        print("Set write=True in main() call or use Google Sheets API auth to push.")
        print("\nTo add rows manually:")
        print("1. Open the Google Sheet")
        print("2. Go to the Facilities tab")
        print("3. Add each provider as a new row at the bottom")
        print("4. Fill: title, slug, state, area, care_types, phone, website,")
        print("         care_category, editorial_summary, status (blank = live)")
        return

    # ── Google Sheets API write (requires OAuth credentials) ─────────────
    # Uncomment and configure credentials to push:
    #
    # from google.oauth2.service_account import Credentials
    # from googleapiclient.discovery import build
    #
    # creds = Credentials.from_service_account_file(
    #     "credentials.json",
    #     scopes=["https://www.googleapis.com/auth/spreadsheets"]
    # )
    # service = build("sheets", "v4", credentials=creds)
    # sheet   = service.spreadsheets()
    #
    # COLUMNS = ["title","slug","state","area","care_types","phone",
    #            "website","care_category","editorial_summary","status"]
    #
    # rows = []
    # for p in NEW_PROVIDERS:
    #     rows.append([p.get(c, "") for c in COLUMNS])
    #
    # body = {"values": rows}
    # sheet.values().append(
    #     spreadsheetId=SHEET_ID,
    #     range="Facilities!A1",
    #     valueInputOption="RAW",
    #     body=body
    # ).execute()
    # print(f"✓ {len(rows)} rows written to Google Sheet")

    print("Write mode not yet configured — set up credentials.json first.")


if __name__ == "__main__":
    main(write=False)
