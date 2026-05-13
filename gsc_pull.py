"""
GSC pull — top queries + pages for nursinghomeguide.my.

Usage:
    python gsc_pull.py                # last 28 days (default)
    python gsc_pull.py --days 90      # custom window
    python gsc_pull.py --site https://nursinghomeguide.my/

First run opens a browser for OAuth consent; token is cached at
.secrets/gsc-token.json for unattended runs thereafter.
"""

import argparse
import csv
import datetime as dt
import os
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
CLIENT_FILE = Path(".secrets/oauth-client.json")
TOKEN_FILE = Path(".secrets/gsc-token.json")
DEFAULT_SITE = "sc-domain:nursinghomeguide.my"
OUT_DIR = Path("_gsc")


def get_creds():
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CLIENT_FILE.exists():
                sys.exit(f"Missing {CLIENT_FILE}. Download OAuth client JSON from GCP first.")
            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        TOKEN_FILE.write_text(creds.to_json())
    return creds


def query(svc, site, start, end, dimensions, row_limit=1000):
    body = {
        "startDate": start,
        "endDate": end,
        "dimensions": dimensions,
        "rowLimit": row_limit,
    }
    resp = svc.searchanalytics().query(siteUrl=site, body=body).execute()
    return resp.get("rows", [])


def write_csv(path, dimensions, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([*dimensions, "clicks", "impressions", "ctr", "position"])
        for r in rows:
            w.writerow([
                *r["keys"],
                r["clicks"],
                r["impressions"],
                round(r["ctr"], 4),
                round(r["position"], 2),
            ])
    print(f"  → {path} ({len(rows)} rows)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=28)
    ap.add_argument("--site", default=DEFAULT_SITE)
    args = ap.parse_args()

    end = dt.date.today() - dt.timedelta(days=2)  # GSC data lags ~2 days
    start = end - dt.timedelta(days=args.days)
    stamp = end.isoformat()
    print(f"GSC pull: {args.site}  {start} → {end}")

    creds = get_creds()
    svc = build("searchconsole", "v1", credentials=creds, cache_discovery=False)

    sites = [s["siteUrl"] for s in svc.sites().list().execute().get("siteEntry", [])]
    if args.site not in sites:
        sys.exit(f"Site {args.site} not in account. Available: {sites}")

    print("Queries...")
    rows = query(svc, args.site, start.isoformat(), end.isoformat(), ["query"])
    write_csv(OUT_DIR / f"queries_{stamp}.csv", ["query"], rows)

    print("Pages...")
    rows = query(svc, args.site, start.isoformat(), end.isoformat(), ["page"])
    write_csv(OUT_DIR / f"pages_{stamp}.csv", ["page"], rows)

    print("Query × Page...")
    rows = query(svc, args.site, start.isoformat(), end.isoformat(), ["query", "page"])
    write_csv(OUT_DIR / f"query_page_{stamp}.csv", ["query", "page"], rows)


if __name__ == "__main__":
    main()
