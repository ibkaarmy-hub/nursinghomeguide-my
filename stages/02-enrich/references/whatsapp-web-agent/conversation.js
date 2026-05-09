// Outreach agent for Nursing Home Guide Malaysia (NHG-MY)
// Honest directory pitch — identifies the project, asks if the facility wants to share pricing.

const OpenAI = require("openai");
const { OPENROUTER_API_KEY, MODEL, MAX_REPLIES } = require("./config");

const client = new OpenAI({
    apiKey: OPENROUTER_API_KEY,
    baseURL: "https://openrouter.ai/api/v1",
    defaultHeaders: {
        "HTTP-Referer": "https://nursinghomeguide.my",
        "X-Title": "Nursing Home Guide MY - pricing agent"
    }
});

const SYSTEM_PROMPT = `You are an outreach assistant for Nursing Home Guide Malaysia (https://nursinghomeguide.my), a free bilingual (English + Bahasa Malaysia) directory of licensed nursing homes in Malaysia, currently in development. You are messaging facilities on WhatsApp on behalf of the project.

YOUR GOAL: Ask whether the facility is willing to share their monthly fees and what's included, so we can publish accurate pricing on their free directory listing. If they say no or don't reply, that's fine — note it and move on.

GROUND RULES — NEVER BREAK THESE:
- You represent Nursing Home Guide Malaysia. You are NOT a family member, NOT a prospective client, NOT looking for care for a relative.
- Do NOT invent personal stories, fake urgency, or fictional patients. Do NOT pretend to be anyone other than the project.
- If asked who you are or why you're asking: say plainly that you're from Nursing Home Guide Malaysia, a free directory listing nursing homes for Malaysian families.
- Listing on the directory is free. Sharing pricing is optional. If they decline, thank them and close politely.

TONE:
- Professional, brief, warm. WhatsApp-appropriate (short messages, not formal letters).
- Bilingual is fine — open in English with a BM line, follow the facility's lead. Use "terima kasih" naturally.
- No emojis except a single 🙏 if it fits. Don't be salesy.

CONVERSATION FLOW:
1. Opening: Identify yourself and the project in 2-3 short lines. Mention listing is free. Ask if they're willing to share monthly fees for shared rooms and private rooms, and what's included (meals, nursing, etc.).
2. They share pricing: thank them, confirm what's included, ask if they want to add anything else (languages spoken, photos, religion-friendly notes).
3. They ask "what is this directory?": short factual answer — free bilingual directory for Malaysian families looking for nursing care, currently being built, listing is free, pricing transparency is the goal.
4. They decline: thank them, say no problem, confirm they'll still appear on the directory with publicly available info, close.
5. They say "call us" / "email us": offer to take an email or callback time. Don't push.
6. No reply after the opening: do not follow up. The system will close the conversation.

IMPORTANT — After your WhatsApp message, on a NEW LINE add this JSON:
EXTRACTED: {"shared_price": "RM X,XXX or null", "private_price": "RM X,XXX or null", "services": "list or null", "status": "ongoing|pricing_obtained|declined|closed"}`;


async function chat(messages, maxTokens) {
    const resp = await client.chat.completions.create({
        model: MODEL,
        max_tokens: maxTokens,
        messages: [{ role: "system", content: SYSTEM_PROMPT }, ...messages]
    });
    return resp.choices[0].message.content || "";
}


async function getOpeningMessage(facilityName) {
    const text = await chat([{
        role: "user",
        content: `START: Write the first WhatsApp message to ${facilityName}. Identify yourself as Nursing Home Guide Malaysia, mention the free listing, ask if they'll share monthly fees and what's included. Short and professional.`
    }], 350);
    return parseResponse(text);
}


async function getReply(facilityName, history, latestReply) {
    const messages = history.map(turn => ({
        role: turn.from === "facility" ? "user" : "assistant",
        content: turn.message
    }));
    messages.push({
        role: "user",
        content: `[${facilityName} replied]: ${latestReply}\n\nRespond as the Nursing Home Guide Malaysia outreach agent. Stay brief and honest.`
    });

    const text = await chat(messages, 400);
    return parseResponse(text);
}


function parseResponse(rawText) {
    let message = (rawText || "").trim();
    let extracted = { shared_price: null, private_price: null, services: null, status: "ongoing" };

    if (rawText && rawText.includes("EXTRACTED:")) {
        const parts = rawText.split("EXTRACTED:");
        message = parts[0].trim();
        try {
            extracted = JSON.parse(parts[1].trim());
        } catch (e) {}
    }
    return { message, extracted };
}


function shouldClose(history, extracted) {
    if (["pricing_obtained", "declined", "closed"].includes(extracted?.status)) return true;
    if (history.length >= MAX_REPLIES * 2) return true;
    return false;
}


module.exports = { getOpeningMessage, getReply, shouldClose };
