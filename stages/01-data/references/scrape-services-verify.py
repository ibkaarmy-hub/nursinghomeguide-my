# Facility Services & Care Type Verifier
# Visits each website and determines:
#   - Confirmed care type (nursing home / day care / assisted living / rehab)
#   - Services included (meals, laundry, nursing, physio, etc.)
#   - Who they accept (religion, language, subsidy)
# Results saved to: stages/02-enrich/output/services-verify-results.csv

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9,ms;q=0.8"
}

INPUT_CSV = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "clean-facilities.csv")
OUTPUT_CSV = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "02-enrich", "output", "services-verify-results.csv")

# Care type keyword signals
NURSING_HOME_KW   = ["24 hour", "24-hour", "24/7", "round the clock", "residential", "nursing home",
                     "pusat jagaan", "penjagaan penuh", "inpatient", "stay", "live-in", "live in"]
DAY_CARE_KW       = ["day care", "daycare", "day centre", "day center", "daytime only", "pusat jagaan harian",
                     "tidak bermalam", "morning to evening", "9am", "8am", "collect"]
ASSISTED_LIVING_KW= ["assisted living", "independent living", "retirement", "semi-independent",
                     "villa", "apartment", "suite", "residence", "komuniti warga emas"]
REHAB_KW          = ["rehabilitation", "physio", "physiotherapy", "post surgery", "post-surgery",
                     "stroke recovery", "stroke rehab", "occupational therapy", "pemulihan"]

# Services keywords
SERVICES = {
    "meals":        ["meal", "meals", "breakfast", "lunch", "dinner", "food", "makan", "makanan"],
    "laundry":      ["laundry", "laundering", "washing", "basuh", "dobi"],
    "nursing_care": ["nursing", "nurse", "jururawat", "medical", "medication", "ubat"],
    "physio":       ["physio", "physiotherapy", "rehabilitation", "pemulihan"],
    "doctor_visit": ["doctor", "physician", "gp visit", "medical check", "doctor visit", "doktor"],
    "transport":    ["transport", "ambulance", "pickup", "pengangkutan"],
    "activities":   ["activity", "activities", "recreation", "exercise", "programme", "aktiviti"],
    "dementia_care":["dementia", "alzheimer", "memory care", "cognitive"],
    "palliative":   ["palliative", "hospice", "end of life", "terminal"],
}

# Who they accept
RELIGION = {
    "Muslim-friendly": ["halal", "muslim", "solat", "prayer room", "islam", "sembahyang"],
    "Chinese-run":     ["mandarin", "cantonese", "chinese speaking", "华", "中文", "普通话"],
    "Tamil-friendly":  ["tamil", "indian", "hindu"],
}

SUBSIDY_KW = ["subsidy", "subsidised", "subsidized", "bantuan", "welfare", "socso", "perkeso",
              "government scheme", "skim", "jkm"]

LANGUAGES_KW = {
    "English":   ["english"],
    "BM":        ["bahasa", "melayu", "bm", "malay"],
    "Mandarin":  ["mandarin", "chinese", "cantonese", "hokkien"],
    "Tamil":     ["tamil", "indian"],
}


def fetch_page(url, timeout=12):
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        if r.status_code == 200:
            return BeautifulSoup(r.text, "html.parser"), r.text
    except:
        pass
    return None, ""


def get_subpages(soup, base_url):
    subpage_keywords = ["about", "services", "care", "facilities", "admission",
                        "contact", "faq", "packages", "accommodation", "tentang"]
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"].lower()
        text = a.get_text(strip=True).lower()
        if any(kw in href or kw in text for kw in subpage_keywords):
            full = href if href.startswith("http") else base_url.rstrip("/") + "/" + href.lstrip("/")
            if base_url.split("//")[1].split("/")[0] in full:  # same domain only
                links.append(full)
    return list(set(links))[:6]


def detect_care_types(text):
    text_lower = text.lower()
    types = []
    if any(kw in text_lower for kw in NURSING_HOME_KW):
        types.append("Nursing Home")
    if any(kw in text_lower for kw in DAY_CARE_KW):
        types.append("Day Care")
    if any(kw in text_lower for kw in ASSISTED_LIVING_KW):
        types.append("Assisted Living")
    if any(kw in text_lower for kw in REHAB_KW):
        types.append("Rehabilitation")
    return types if types else ["Nursing Home"]  # default


def detect_services(text):
    text_lower = text.lower()
    found = []
    for service, keywords in SERVICES.items():
        if any(kw in text_lower for kw in keywords):
            found.append(service)
    return found


def detect_religion(text):
    text_lower = text.lower()
    for label, keywords in RELIGION.items():
        if any(kw in text_lower for kw in keywords):
            return label
    return "All"


def detect_languages(text):
    text_lower = text.lower()
    langs = []
    for lang, keywords in LANGUAGES_KW.items():
        if any(kw in text_lower for kw in keywords):
            langs.append(lang)
    return langs if langs else ["English", "BM"]


def detect_subsidy(text):
    text_lower = text.lower()
    return "Yes" if any(kw in text_lower for kw in SUBSIDY_KW) else "Unknown"


def scrape_site(url, facility_name):
    result = {
        "facility_name": facility_name,
        "website": url,
        "confirmed_care_types": "",
        "services_included": "",
        "religion_friendly": "",
        "languages": "",
        "subsidy_accepted": "",
        "beds_mentioned": "",
        "status": "ok"
    }

    soup, raw = fetch_page(url)
    if not soup:
        result["status"] = "unreachable"
        return result

    all_text = soup.get_text(" ", strip=True)

    # Scrape subpages too
    subpages = get_subpages(soup, url)
    for sub_url in subpages:
        sub_soup, sub_raw = fetch_page(sub_url, timeout=10)
        if sub_soup:
            all_text += " " + sub_soup.get_text(" ", strip=True)
        time.sleep(0.4)

    # Detect care types
    care_types = detect_care_types(all_text)
    result["confirmed_care_types"] = " + ".join(care_types)

    # Detect services
    services = detect_services(all_text)
    result["services_included"] = ", ".join(services)

    # Religion
    result["religion_friendly"] = detect_religion(all_text)

    # Languages
    langs = detect_languages(all_text)
    result["languages"] = ", ".join(langs)

    # Subsidy
    result["subsidy_accepted"] = detect_subsidy(all_text)

    # Bed count mention
    beds = re.findall(r"\b(\d{1,3})\s*(?:bed|beds|room|rooms|tempat tidur)\b", all_text, re.IGNORECASE)
    result["beds_mentioned"] = beds[0] if beds else ""

    return result


def main():
    print("=" * 55)
    print("  Facility Services & Care Type Verifier")
    print("=" * 55)

    df = pd.read_csv(INPUT_CSV)
    has_website = df[df["website"].notna() & df["website"].str.startswith("http", na=False)].copy()

    print(f"\nFacilities with websites: {len(has_website)}")
    print("Analysing each site...\n")

    results = []
    for i, row in has_website.iterrows():
        name = str(row["facility_name"])[:45]
        url = str(row["website"])
        print(f"[{len(results)+1}/{len(has_website)}] {name[:42]}")
        result = scrape_site(url, row["facility_name"])
        print(f"         Care: {result['confirmed_care_types']} | Services: {result['services_included'][:40]}")
        results.append(result)
        time.sleep(0.8)

    out_df = pd.DataFrame(results)
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    out_df.to_csv(OUTPUT_CSV, index=False)

    print(f"\n{'='*55}")
    print(f"Done! Analysed {len(results)} websites")
    print(f"\nCare type breakdown:")
    print(out_df["confirmed_care_types"].value_counts().to_string())
    print(f"\nSaved to: {OUTPUT_CSV}")
    print("="*55)
    input("\nPress Enter to close...")


if __name__ == "__main__":
    main()
