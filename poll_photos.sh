#!/usr/bin/env bash
RUN_ID=y5cEqju08AwT3ztgJ
TOKEN=YOUR_APIFY_TOKEN
while true; do
  resp=$(curl -sS -H "Authorization: Bearer $TOKEN" "https://api.apify.com/v2/actor-runs/$RUN_ID")
  status=$(echo "$resp" | py -c "import json,sys; d=json.load(sys.stdin)['data']; print(d['status'])")
  echo "[$(date +%H:%M:%S)] $status"
  case "$status" in
    SUCCEEDED|FAILED|ABORTED|TIMED-OUT|TIMING-OUT) exit 0 ;;
  esac
  sleep 30
done
