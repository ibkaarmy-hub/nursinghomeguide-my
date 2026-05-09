# Facebook Page Finder for Nursing Homes with No Website
# Searches Google for each facility and extracts any Facebook page URL
# Results saved to: stages/02-enrich/output/facebook-pages-found.csv

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

INPUT_CSV = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "02-enrich", "output", "STEP3-johor-master.csv")
OUTPUT_CSV = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "02-enrich", "output", "STEP2D-facebook-pages.csv")


def search_facebook(facility_name, city=""):
    query = f'{facility_name} {city} facebook nursing home malaysia'.strip()
    search_url = f"https://www.google.com/search?q={requests.utils.quote(query)}&num=5"

    try:
        r = requests.get(search_url, headers=HEADERS, timeout=12)
        soup = BeautifulSoup(r.text, "html.parser")

        # Extract all URLs from results
        fb_urls = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            # Google wraps links in /url?q=...
            match = re.search(r'/url\?q=(https?://(?:www\.|m\.|web\.)?facebook\.com/[^&]+)', href)
            if match:
                fb_url = match.group(1)
                # Filter out Facebook search pages and ads
                if "/search" not in fb_url and "facebook.com/ads" not in fb_url:
                    fb_urls.append(fb_url)

        # Also check plain facebook.com links
        for a in soup.find_all("a", href=re.compile(r'facebook\.com/')):
            href = a.get("href", "")
            if href.startswith("http") and "facebook.com/" in href:
                if "/search" not in href:
                    fb_urls.append(href)

        return fb_urls[0] if fb_urls else ""

    except Exception as e:
        return ""


def main():
    print("=" * 55)
    print("  Facebook Page Finder")
    print("=" * 55)

    df = pd.read_csv(INPUT_CSV)

    # Only target facilities with no website
    no_website = df[
        df["website"].isna() |
        (df["website"].astype(str).str.strip() == "") |
        (df["website"].astype(str).str.strip() == "nan")
    ].copy()

    print(f"\nFacilities without own website: {len(no_website)}")
    print("Searching Google for Facebook pages...\n")

    results = []
    found_count = 0

    for i, row in no_website.iterrows():
        name = str(row["facility_name"])
        city = str(row["city"]) if pd.notna(row.get("city")) else ""

        print(f"[{len(results)+1}/{len(no_website)}] {name[:45]}", end="  ")

        fb_url = search_facebook(name, city)

        if fb_url:
            print(f"✓ {fb_url[:55]}")
            found_count += 1
        else:
            print("— not found")

        results.append({
            "facility_name": name,
            "city": city,
            "phone": row.get("phone", ""),
            "facebook_url": fb_url,
            "found": "Yes" if fb_url else "No"
        })

        time.sleep(2)  # be polite to Google

    out_df = pd.DataFrame(results)
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    out_df.to_csv(OUTPUT_CSV, index=False)

    print(f"\n{'='*55}")
    print(f"Done! Checked {len(results)} facilities")
    print(f"Facebook pages found: {found_count} / {len(results)}")
    print(f"Saved to: {OUTPUT_CSV}")
    print("="*55)
    input("\nPress Enter to close...")


if __name__ == "__main__":
    main()
