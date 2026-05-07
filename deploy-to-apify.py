#!/usr/bin/env python3
"""
Deploy JKM scraper actor to Apify and run a 1-page test.
Run locally: python3 deploy-to-apify.py
"""

import json
import os
import time
import urllib.request
import urllib.parse

APIFY_TOKEN = os.environ.get("APIFY_TOKEN") or input("Enter your Apify API token: ").strip()
ACTOR_NAME = "jkm-elderly-care-scraper"
SOURCE_FILE = os.path.join(os.path.dirname(__file__), "apify-jkm-scraper.js")

def api_call(method, path, body=None):
    url = f"https://api.apify.com/v2{path}?token={APIFY_TOKEN}"
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

def main():
    # 1. Read actor source
    with open(SOURCE_FILE) as f:
        source_code = f.read()
    print(f"✅ Read source: {SOURCE_FILE} ({len(source_code)} chars)")

    # 2. Create actor
    print(f"\n🚀 Creating actor '{ACTOR_NAME}'...")
    try:
        actor = api_call("POST", "/acts", {
            "name": ACTOR_NAME,
            "title": "JKM Elderly Care Centre Scraper",
            "description": "Scrapes 529 elderly care centres from jkm.gov.my",
        })
        actor_id = actor["data"]["id"]
        print(f"✅ Actor created: {actor_id}")
    except urllib.error.HTTPError as e:
        if e.code == 409:
            # Already exists — get it
            print("ℹ️  Actor already exists, fetching...")
            actors = api_call("GET", "/acts")
            actor_id = next(a["id"] for a in actors["data"]["items"] if a["name"] == ACTOR_NAME)
            print(f"✅ Found existing actor: {actor_id}")
        else:
            raise

    # 3. Create version with source code
    print("\n📦 Uploading source code...")
    api_call("POST", f"/acts/{actor_id}/versions", {
        "versionNumber": "0.1",
        "sourceType": "SOURCE_FILES",
        "sourceFiles": [
            {
                "name": "main.js",
                "format": "TEXT",
                "content": source_code,
            },
            {
                "name": "package.json",
                "format": "TEXT",
                "content": json.dumps({
                    "name": "jkm-scraper",
                    "version": "0.1.0",
                    "dependencies": {
                        "apify": "^2.3.2",
                        "cheerio": "^1.0.0-rc.12"
                    }
                }, indent=2),
            }
        ],
        "buildTag": "latest",
    })
    print("✅ Source uploaded")

    # 4. Build the actor
    print("\n🔨 Triggering build...")
    build = api_call("POST", f"/acts/{actor_id}/builds", {"version": "0.1", "tag": "latest"})
    build_id = build["data"]["id"]
    print(f"✅ Build started: {build_id}")

    # Wait for build to complete
    print("⏳ Waiting for build to finish...")
    for i in range(24):  # up to 2 minutes
        time.sleep(5)
        build_status = api_call("GET", f"/acts/{actor_id}/builds/{build_id}")
        status = build_status["data"]["status"]
        print(f"   Build status: {status}")
        if status == "SUCCEEDED":
            break
        elif status in ("FAILED", "ABORTED", "TIMED-OUT"):
            print(f"❌ Build failed: {status}")
            return

    # 5. Run actor (1-page test)
    print("\n▶️  Running 1-page test...")
    run = api_call("POST", f"/acts/{actor_id}/runs", {
        "memory": 512,
        "timeout": 120,
    })
    run_id = run["data"]["id"]
    print(f"✅ Run started: {run_id}")
    print(f"🔗 View run: https://console.apify.com/actors/{actor_id}/runs/{run_id}")

    # Wait for run
    print("⏳ Waiting for run to finish...")
    for i in range(30):  # up to 2.5 minutes
        time.sleep(5)
        run_status = api_call("GET", f"/acts/{actor_id}/runs/{run_id}")
        status = run_status["data"]["status"]
        print(f"   Run status: {status}")
        if status == "SUCCEEDED":
            break
        elif status in ("FAILED", "ABORTED", "TIMED-OUT"):
            print(f"❌ Run failed: {status}")
            return

    # 6. Get results
    print("\n📊 Fetching results...")
    dataset_id = run_status["data"]["defaultDatasetId"]
    results = api_call("GET", f"/datasets/{dataset_id}/items")
    items = results.get("data", {}).get("items", [])

    print(f"\n✅ Scraped {len(items)} centres on page 1")
    if items:
        print("\nSample (first result):")
        print(json.dumps(items[0], indent=2, ensure_ascii=False))

    # Save results
    out_file = "jkm-results/jkm_page1_test.json"
    os.makedirs("jkm-results", exist_ok=True)
    with open(out_file, "w") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Saved to: {out_file}")
    print(f"\nActor ID (save this): {actor_id}")
    print(f"To run full scrape: edit MAX_PAGES=60 in apify-jkm-scraper.js, then re-deploy.")

if __name__ == "__main__":
    main()
