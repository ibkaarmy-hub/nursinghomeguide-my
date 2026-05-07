#!/usr/bin/env python3
"""
Deploy JKM scraper actor to Apify and run a 1-page test.
Run: APIFY_TOKEN=apify_api_... python3 deploy-to-apify.py
"""

import json, os, time, urllib.request, urllib.parse, urllib.error

APIFY_TOKEN = os.environ.get("APIFY_TOKEN") or input("Enter your Apify API token: ").strip()
ACTOR_NAME  = "jkm-elderly-care-scraper"
SOURCE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "apify-jkm-scraper.js")

def api(method, path, body=None, params=None):
    qs  = urllib.parse.urlencode({"token": APIFY_TOKEN, **(params or {})})
    url = f"https://api.apify.com/v2{path}?{qs}"
    data = json.dumps(body).encode() if body else None
    req  = urllib.request.Request(url, data=data,
                                  headers={"Content-Type": "application/json"},
                                  method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise Exception(f"HTTP {e.code}: {e.read().decode()[:300]}") from None

def wait_for(kind, actor_id, run_id, poll=5, retries=36):
    for _ in range(retries):
        time.sleep(poll)
        r = api("GET", f"/acts/{actor_id}/{kind}/{run_id}")
        status = r["data"]["status"]
        print(f"   {status}", flush=True)
        if status == "SUCCEEDED":
            return r
        if status in ("FAILED", "ABORTED", "TIMED-OUT"):
            raise Exception(f"{kind} {status}")
    raise Exception(f"{kind} timed out")

def source_payload(code):
    return {
        "versionNumber": "0.1",
        "sourceType": "SOURCE_FILES",
        "buildTag": "latest",
        "sourceFiles": [
            {"name": "main.js", "format": "TEXT", "content": code},
            {"name": "package.json", "format": "TEXT",
             "content": json.dumps({
                 "name": "jkm-scraper", "version": "0.1.0",
                 "type": "module",
                 "dependencies": {"apify": "^3.0.0", "crawlee": "^3.0.0"}
             }, indent=2)},
        ],
    }

def main():
    with open(SOURCE_FILE) as f:
        code = f.read()
    print(f"✅ Source read ({len(code)} chars)")

    # --- 1. Get or create actor ---
    print(f"\n🔍 Looking up actor '{ACTOR_NAME}'...")
    actors = api("GET", "/acts", params={"limit": 100})
    existing = [a for a in actors["data"]["items"] if a["name"] == ACTOR_NAME]

    if existing:
        actor_id = existing[0]["id"]
        print(f"✅ Found existing actor: {actor_id}")
        # Update the version
        print("📦 Updating source code...")
        try:
            api("PUT", f"/acts/{actor_id}/versions/0.1", source_payload(code))
        except Exception:
            api("POST", f"/acts/{actor_id}/versions", source_payload(code))
    else:
        print(f"🚀 Creating actor...")
        r = api("POST", "/acts", {
            "name": ACTOR_NAME,
            "title": "JKM Elderly Care Centre Scraper",
        })
        actor_id = r["data"]["id"]
        print(f"✅ Actor created: {actor_id}")
        print("📦 Uploading source code...")
        api("POST", f"/acts/{actor_id}/versions", source_payload(code))
    print("✅ Source uploaded")

    # --- 2. Build ---
    print("\n🔨 Building...")
    build = api("POST", f"/acts/{actor_id}/builds", params={"version": "0.1", "tag": "latest"})
    build_id = build["data"]["id"]
    print(f"   Build ID: {build_id}")
    wait_for("builds", actor_id, build_id)
    print("✅ Build succeeded")

    # --- 3. Run (1-page test) ---
    print("\n▶️  Starting 1-page test run...")
    run = api("POST", f"/acts/{actor_id}/runs", {"memory": 512, "timeout": 180})
    run_id  = run["data"]["id"]
    print(f"   Run ID: {run_id}")
    print(f"🔗 https://console.apify.com/actors/{actor_id}/runs/{run_id}")
    run_result = wait_for("runs", actor_id, run_id)
    print("✅ Run succeeded")

    # --- 4. Fetch results ---
    ds_id = run_result["data"]["defaultDatasetId"]
    items = api("GET", f"/datasets/{ds_id}/items")["data"]["items"]
    print(f"\n📊 Scraped {len(items)} centres")

    os.makedirs("jkm-results", exist_ok=True)
    out = "jkm-results/jkm_page1_test.json"
    with open(out, "w") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved: {out}")

    if items:
        print("\nSample result:")
        print(json.dumps(items[0], indent=2, ensure_ascii=False))
    else:
        print("⚠️  No items — check selectors or proxy settings")

    print(f"\nActor ID: {actor_id}  (save this for future runs)")

if __name__ == "__main__":
    main()
