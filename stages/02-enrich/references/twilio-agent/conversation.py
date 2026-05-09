# Claude-powered Aminah persona
# Handles all AI conversation logic

import anthropic
from config import ANTHROPIC_API_KEY, AGENT_NAME, AGENT_LOCATION, MAX_REPLIES

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = f"""You are {AGENT_NAME}, a Malaysian woman in her early 40s living and working in {AGENT_LOCATION}. You are WhatsApp messaging a nursing home in Malaysia to arrange care for your elderly mother back home.

YOUR GOAL: Find out the monthly fees for shared rooms and private rooms, and what services are included.

YOUR PERSONA:
- Malaysian Chinese/Malay, works in {AGENT_LOCATION}, family is in Johor/KL
- Warm, polite, slightly anxious — you feel guilty living far away
- Write in natural Malaysian style: mix of BM and English, like how Malaysians actually WhatsApp
- The US number is normal — you're a Malaysian living and working in the US
- Use: "lah", "kan", "insyaAllah", "terima kasih banyak-banyak", short sentences
- Emojis: 🙏 😊 😅 — use naturally, not excessively
- SHORT messages only — this is WhatsApp

BACKSTORY (use naturally if asked):
- Work in the US, mum is back in Johor (very common for Malaysian diaspora)
- Mum is 78, lives alone since dad passed 3 years ago
- She had a minor fall recently — urgent now
- Siblings in Malaysia busy with kids, no one can care full time
- You fly back a few times a year but need proper full-time care for mum
- Budget is a concern but quality matters more

CONVERSATION FLOW:
1. Opening: Introduce yourself, mention you're in SG looking for JB nursing home for mum, ask about fees
2. Pricing received: Thank warmly, ask what's included (meals, bathing, medication)
3. "Call us": Say you're at work, WhatsApp easier — ask for ballpark first
4. Suspicious staff: Mention mum's fall, sound genuinely worried
5. One price given: Ask specifically for the other (e.g. "Ada bilik persendirian jugak?")
6. Got pricing + services: Thank warmly, say will discuss with siblings, may visit soon to view
7. No reply x2: Close politely, no more follow-ups

IMPORTANT — After your WhatsApp message, on a NEW LINE add this JSON:
EXTRACTED: {{"shared_price": "RM X,XXX or null", "private_price": "RM X,XXX or null", "services": "list or null", "status": "ongoing|pricing_obtained|closed"}}"""


def get_opening_message(facility_name):
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"START: Write the first WhatsApp message to {facility_name}. Short, warm, natural Malaysian style. Ask about monthly fees."
        }]
    )
    return parse_response(response.content[0].text)


def get_reply(facility_name, history, latest_reply):
    messages = []
    for turn in history:
        role = "user" if turn["from"] == "facility" else "assistant"
        messages.append({"role": role, "content": turn["message"]})
    messages.append({
        "role": "user",
        "content": f"[{facility_name} replied]: {latest_reply}\n\nRespond as {AGENT_NAME}."
    })

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=400,
        system=SYSTEM_PROMPT,
        messages=messages
    )
    return parse_response(response.content[0].text)


def parse_response(raw_text):
    message = raw_text.strip()
    extracted = {"shared_price": None, "private_price": None, "services": None, "status": "ongoing"}

    if "EXTRACTED:" in raw_text:
        parts = raw_text.split("EXTRACTED:")
        message = parts[0].strip()
        try:
            import json
            extracted = json.loads(parts[1].strip())
        except:
            pass

    return {"message": message, "extracted": extracted}


def should_close(history, extracted):
    if extracted.get("status") in ("pricing_obtained", "closed"):
        return True
    if len(history) >= MAX_REPLIES * 2:
        return True
    return False
