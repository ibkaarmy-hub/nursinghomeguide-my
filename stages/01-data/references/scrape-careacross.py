# CareAcross.sg Malaysia Nursing Home Scraper
# Saves results to: stages/01-data/output/careacross-malaysia.csv
# Run via: RUN-SCRAPER.bat

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import os

BASE_URL = "https://careacross.sg"
LIST_URL = "https://careacross.sg/my/nursing-homes"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

OUTPUT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "careacross-malaysia.csv")


def get_facility_links(url):
    """Get all facility page links from the listing page."""
    links = []
    page = 1
    while True:
        paged_url = f"{url}?page={page}" if page > 1 else url
        print(f"  Fetching listing page {page}: {paged_url}")
        try:
            r = requests.get(paged_url, headers=HEADERS, timeout=15)
            soup = BeautifulSoup(r.text, "html.parser")

            # Find facility cards/links
            facility_links = soup.find_all("a", href=re.compile(r"/facility/"))
            new_links = [BASE_URL + a["href"] for a in facility_links if a.get("href")]
            new_links = list(set(new_links))  # deduplicate

            if not new_links or new_links == links[-len(new_links):] if links else False:
                break

            links.extend(new_links)
            page += 1
            time.sleep(1)

            if page > 20:  # safety limit
                break
        except Exception as e:
            print(f"  Error on page {page}: {e}")
            break

    return list(set(links))


def scrape_facility(url):
    """Scrape a single facility page."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")

        data = {"url": url, "source": "CareAcross.sg"}

        # Name
        name_tag = soup.find("h1")
        data["facility_name"] = name_tag.get_text(strip=True) if name_tag else ""

        # Address
        for tag in soup.find_all(["p", "div", "span"]):
            text = tag.get_text(strip=True)
            if any(kw in text.lower() for kw in ["jalan", "lorong", "taman", "bandar", "malaysia"]):
                if 10 < len(text) < 200:
                    data["full_address"] = text
                    break

        # Phone
        phone_tag = soup.find("a", href=re.compile(r"tel:"))
        data["phone"] = phone_tag.get_text(strip=True) if phone_tag else ""

        # State - infer from URL or address
        url_lower = url.lower()
        for state in ["johor", "selangor", "penang", "perak", "melaka", "sabah", "sarawak",
                       "kedah", "kelantan", "pahang", "perlis", "terengganu", "negeri-sembilan",
                       "kuala-lumpur", "putrajaya", "labuan"]:
            if state in url_lower:
                data["state"] = state.replace("-", " ").title()
                break
        if "state" not in data:
            data["state"] = "Malaysia"

        # Pricing - look for RM mentions
        page_text = soup.get_text()
        rm_prices = re.findall(r"RM\s*[\d,]+(?:\s*[-–]\s*RM\s*[\d,]+)?(?:\s*/\s*(?:month|mth|mo))?", page_text, re.IGNORECASE)
        data["pricing_raw"] = " | ".join(rm_prices[:5]) if rm_prices else "pricing_unknown"

        # Description
        meta_desc = soup.find("meta", {"name": "description"})
        data["description"] = meta_desc["content"] if meta_desc and meta_desc.get("content") else ""

        print(f"  ✓ {data.get('facility_name', 'Unknown')} — {data.get('state', '')} — {data.get('pricing_raw', '')}")
        return data

    except Exception as e:
        print(f"  ✗ Error scraping {url}: {e}")
        return None


def main():
    print("=" * 60)
    print("CareAcross.sg Malaysia Scraper")
    print("=" * 60)

    print("\n[1/3] Finding all Malaysian facility links...")
    links = get_facility_links(LIST_URL)

    # Also check memory care and assisted living pages
    for category in ["/my/memory-care", "/my/assisted-living", "/my/dementia-care"]:
        extra_links = get_facility_links(BASE_URL + category)
        links.extend(extra_links)

    links = list(set(links))
    print(f"  Found {len(links)} unique facility pages")

    print("\n[2/3] Scraping each facility page...")
    results = []
    for i, link in enumerate(links, 1):
        print(f"  [{i}/{len(links)}] ", end="")
        data = scrape_facility(link)
        if data:
            results.append(data)
        time.sleep(0.8)  # be polite

    print(f"\n[3/3] Saving {len(results)} facilities to CSV...")
    df = pd.DataFrame(results)
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"\n✅ Done! Saved to:\n   {OUTPUT_PATH}")
    print(f"\nSummary:")
    print(f"  Total facilities: {len(df)}")
    if "state" in df.columns:
        print(f"  By state:\n{df['state'].value_counts().to_string()}")
    print("\nPress Enter to close...")
    input()


if __name__ == "__main__":
    main()
