# Twilio WhatsApp Webhook Server
# Receives incoming WhatsApp messages and responds as Aminah

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client as TwilioClient
import json, os, csv
from datetime import datetime
from conversation import get_reply, should_close, parse_response
from config import (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN,
                    TWILIO_WHATSAPP_NUMBER, CONVOS_DIR, RESULTS_CSV)

app = Flask(__name__)
twilio = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

os.makedirs(CONVOS_DIR, exist_ok=True)


# ── Helpers ──────────────────────────────────────────────────────────────────

def conv_path(phone):
    clean = phone.replace("whatsapp:", "").replace("+", "").replace(" ", "")
    return os.path.join(CONVOS_DIR, f"{clean}.json")

def load_conv(phone):
    p = conv_path(phone)
    if os.path.exists(p):
        return json.load(open(p))
    return None

def save_conv(phone, data):
    with open(conv_path(phone), "w") as f:
        json.dump(data, f, indent=2)

def save_result(convo):
    row = {
        "facility_name":    convo.get("facility_name", ""),
        "phone":            convo.get("phone", ""),
        "shared_room_price":  convo.get("extracted", {}).get("shared_price", "pricing_unknown") or "pricing_unknown",
        "private_room_price": convo.get("extracted", {}).get("private_price", "pricing_unknown") or "pricing_unknown",
        "services_included":  convo.get("extracted", {}).get("services", "") or "",
        "status":           convo.get("status", ""),
        "updated":          datetime.utcnow().isoformat()
    }

    rows = []
    if os.path.exists(RESULTS_CSV):
        with open(RESULTS_CSV) as f:
            rows = list(csv.DictReader(f))
        rows = [r for r in rows if r["phone"] != row["phone"]]
    rows.append(row)

    with open(RESULTS_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"  💾 Saved: {row['facility_name']}")


# ── Webhook ───────────────────────────────────────────────────────────────────

@app.route("/webhook", methods=["POST"])
def webhook():
    from_number = request.form.get("From", "")
    body = request.form.get("Body", "").strip()

    print(f"\n📩 Message from {from_number}: {body[:80]}")

    convo = load_conv(from_number)
    if not convo:
        print("  ⚠️  Unknown sender — ignoring")
        return str(MessagingResponse())  # empty response

    if convo.get("status") == "completed":
        print("  ✅ Conversation already completed")
        return str(MessagingResponse())

    convo["history"].append({
        "from": "facility", "message": body, "time": datetime.utcnow().isoformat()
    })

    if should_close(convo["history"], convo.get("extracted", {})):
        convo["status"] = "completed"
        save_conv(from_number, convo)
        save_result(convo)
        return str(MessagingResponse())

    # Get Claude reply
    result = get_reply(convo["facility_name"], convo["history"], body)

    ex = result["extracted"]
    ext = convo.setdefault("extracted", {})
    if ex.get("shared_price") and ex["shared_price"] != "null":  ext["shared_price"]  = ex["shared_price"]
    if ex.get("private_price") and ex["private_price"] != "null": ext["private_price"] = ex["private_price"]
    if ex.get("services") and ex["services"] != "null":           ext["services"]      = ex["services"]
    if ex.get("status"):                                          ext["status"]        = ex["status"]

    convo["history"].append({
        "from": "agent", "message": result["message"], "time": datetime.utcnow().isoformat()
    })

    if should_close(convo["history"], ext):
        convo["status"] = "completed"
        save_result(convo)

    save_conv(from_number, convo)

    # Reply via Twilio
    resp = MessagingResponse()
    resp.message(result["message"])
    print(f"  ✉️  Replied: {result['message'][:80]}")
    return str(resp)


@app.route("/health")
def health():
    return "OK", 200


if __name__ == "__main__":
    print("=" * 50)
    print("  Twilio WhatsApp Webhook Server")
    print("=" * 50)
    print("\n⚡ Running on http://localhost:5000")
    print("📡 Webhook endpoint: http://localhost:5000/webhook")
    print("\nMake sure ngrok is running:")
    print("  ngrok http 5000\n")
    app.run(port=5000, debug=False)
