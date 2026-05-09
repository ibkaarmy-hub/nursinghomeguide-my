# Send opening WhatsApp messages to all facilities needing pricing
# Run this ONCE to kick off the outreach campaign

import csv, json, os, time
from twilio.rest import Client as TwilioClient
from conversation import get_opening_message
from config import (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN,
                    TWILIO_WHATSAPP_NUMBER, FACILITIES_CSV,
                    CONVOS_DIR, DELAY_BETWEEN_MESSAGES_SEC)

twilio = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
os.makedirs(CONVOS_DIR, exist_ok=True)


def clean_phone(phone):
    if not phone or str(phone).strip() in ("", "nan"):
        return None
    p = str(phone).replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if p.startswith("0"):
        p = "60" + p[1:]
    elif p.startswith("+"):
        p = p[1:]
    return f"whatsapp:+{p}"

def conv_path(phone):
    clean = phone.replace("whatsapp:", "").replace("+", "").replace(" ", "")
    return os.path.join(CONVOS_DIR, f"{clean}.json")


def main():
    print("=" * 55)
    print("  Twilio WhatsApp Outreach — Aminah")
    print("=" * 55)

    facilities = []
    with open(FACILITIES_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("shared_room_price", "pricing_unknown") == "pricing_unknown":
                if row.get("phone", "").strip() not in ("", "nan"):
                    facilities.append(row)

    print(f"\n📋 Facilities needing pricing: {len(facilities)}")
    print(f"⏱️  Delay between messages: {DELAY_BETWEEN_MESSAGES_SEC}s")
    print("\nStarting in 5 seconds... Press Ctrl+C to stop.\n")
    time.sleep(5)

    sent = 0
    for facility in facilities:
        wa_phone = clean_phone(facility["phone"])
        if not wa_phone:
            continue

        # Skip already contacted
        if os.path.exists(conv_path(wa_phone)):
            print(f"  ⏭️  Already contacted: {facility['facility_name'][:40]}")
            continue

        print(f"[{sent+1}] {facility['facility_name'][:50]}")

        result = get_opening_message(facility["facility_name"])
        print(f"  💬 \"{result['message'][:70]}...\"")

        convo = {
            "phone":         wa_phone,
            "facility_name": facility["facility_name"],
            "history":       [{"from": "agent", "message": result["message"], "time": __import__('datetime').datetime.utcnow().isoformat()}],
            "extracted":     {},
            "status":        "active"
        }

        try:
            twilio.messages.create(
                from_=TWILIO_WHATSAPP_NUMBER,
                to=wa_phone,
                body=result["message"]
            )
            with open(conv_path(wa_phone), "w") as f:
                json.dump(convo, f, indent=2)
            print(f"  ✅ Sent")
            sent += 1
        except Exception as e:
            print(f"  ❌ Failed: {e}")

        time.sleep(DELAY_BETWEEN_MESSAGES_SEC)

    print(f"\n✅ Done. Sent: {sent}")
    print("Now start app.py + ngrok to handle replies.")
    input("\nPress Enter to close...")


if __name__ == "__main__":
    main()
