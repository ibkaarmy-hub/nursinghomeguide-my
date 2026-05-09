# Nursing Home Website Pricing Scraper
# Visits each facility website and extracts pricing info
# Results saved to: stages/02-enrich/output/website-pricing-results.csv

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

INPUT_CSV = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "clean-facilities.csv")
OUTPUT_CSV = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "02-enrich", "output", "website-pricing-results.csv")

PRICING_KEYWORDS = ["fee", "fees", "price", "pricing", "package", "rate", "rates", "cost", "charges",
                    "yuran", "harga", "pakej", "bayaran", "kadar"]

PRICING_PAGES = ["fees", "pricing", "packages", "rates", "services", "cost",
                 "yuran", "harga", "pakej", "about", "contact"]


def find_pricing_pages(soup, base_url):
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"].lower()
        text = a.get_text(strip=True).lower()
        if any(kw in href or kw in text for kw in PRICING_PAGES):
            full = href if href.startswith("http") else base_url.rstrip("/") + "/" + href.lstrip("/")
            links.append(full)
    return list(set(links))[:5]


def extract_pricing(text):
    patterns = [
        r"RM\s*[\d,]+(?:\s*[-–to]+\s*RM\s*[\d,]+)?(?:\s*/\s*(?:month|mth|mo|bulan))?",
        r"RM\s*[\d,]+",
        r"\b[\d,]+\s*(?:per\s+)?(?:month|mth|monthly|bulan)\b",
    ]
    found = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        found.extend(matches)
    cleaned = list(set(m.strip() for m in found if len(m.strip()) > 2))
    return " | ".join(cleaned[:6]) if cleaned else ""


def scrape_site(url, facility_name):
    result = {
        "facility_name": facility_name,
        "website": url,
        "pricing_found": "",
        "pricing_page_url": "",
        "phone_found": "",
        "email_found": "",
        "status": "ok"
    }

    try:
        r = requests.get(url, headers=HEADERS, timeout=12, allow_redirects=True)
        if r.status_code != 200:
            result["status"] = f"HTTP {r.status_code}"
            return result

        soup = BeautifulSoup(r.text, "html.parser")
        page_text = soup.get_text(" ", strip=True)

        # Try pricing from homepage first
        pricing = extract_pricing(page_text)

        # Find pricing subpages
        pricing_links = find_pricing_pages(soup, url)
        for link in pricing_links:
            try:
                sub = requests.get(link, headers=HEADERS, timeout=10, allow_redirects=True)
                sub_soup = BeautifulSoup(sub.text, "html.parser")
                sub_text = sub_soup.get_text(" ", strip=True)
                sub_pricing = extract_pricing(sub_text)
                if sub_pricing and len(sub_pricing) > len(pricing):
                    pricing = sub_pricing
                    result["pricing_page_url"] = link
                time.sleep(0.5)
            except:
                continue

        result["pricing_found"] = pricing

        # Phone
        phones = re.findall(r"(?:\+?60|0)\d[\d\s-]{7,12}", page_text)
        result["phone_found"] = phones[0].strip() if phones else ""

        # Email
        emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", page_text)
        result["email_found"] = emails[0] if emails else ""

    except requests.exceptions.Timeout:
        result["status"] = "timeout"
    except requests.exceptions.ConnectionError:
        result["status"] = "connection_error"
    except Exception as e:
        result["status"] = f"error: {str(e)[:50]}"

    return result


def main():
    print("=" * 55)
    print("  Facility Website Pricing Scraper")
    print("=" * 55)

    df = pd.read_csv(INPUT_CSV)
    has_website = df[df["website"].notna() & df["website"].str.startswith("http", na=False)].copy()

    print(f"\nFacilities with websites: {len(has_website)}")
    print("Scraping each site for pricing...\n")

    results = []
    for i, row in has_website.iterrows():
        name = str(row["facility_name"])[:50]
        url = str(row["website"])
        print(f"[{len(results)+1}/{len(has_website)}] {name[:40]}")
        result = scrape_site(url, row["facility_name"])
        status = "✓ Pricing found" if result["pricing_found"] else "— No pricing"
        print(f"         {status}: {result['pricing_found'][:60] if result['pricing_found'] else result['status']}")
        results.append(result)
        time.sleep(0.8)

    out_df = pd.DataFrame(results)
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    out_df.to_csv(OUTPUT_CSV, index=False)

    found = out_df[out_df["pricing_found"] != ""]
    print(f"\n{'='*55}")
    print(f"Done! Scraped {len(results)} websites")
    print(f"Pricing found: {len(found)} / {len(results)}")
    print(f"Saved to: {OUTPUT_CSV}")
    print("="*55)
    input("\nPress Enter to close...")


if __name__ == "__main__":
    main()
