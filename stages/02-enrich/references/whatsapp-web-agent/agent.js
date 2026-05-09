// WhatsApp Pricing Agent — Baileys edition
// Uses @whiskeysockets/baileys (WebSocket protocol, no browser).

const { default: makeWASocket, useMultiFileAuthState, DisconnectReason, Browsers, fetchLatestBaileysVersion } = require("baileys");
const qrcodeTerminal = require("qrcode-terminal");
const qrcode = require("qrcode");
const { exec } = require("child_process");
const csv = require("csv-parser");
const fs = require("fs");
const path = require("path");
const { getOpeningMessage, getReply, shouldClose } = require("./conversation");
const config = require("./config");


// ── Setup ──────────────────────────────────────────────────────────────────

const AUTH_DIR = path.join(__dirname, "baileys_auth");
const CONV_DIR = path.resolve(__dirname, config.CONVERSATIONS_DIR);
const RESULTS_CSV = path.resolve(__dirname, config.RESULTS_CSV);
if (!fs.existsSync(CONV_DIR)) fs.mkdirSync(CONV_DIR, { recursive: true });


// ── Helpers ────────────────────────────────────────────────────────────────

function convPath(jid) {
    return path.join(CONV_DIR, `${jid.replace(/\D/g, "")}.json`);
}

function loadConv(jid) {
    const p = convPath(jid);
    if (fs.existsSync(p)) return JSON.parse(fs.readFileSync(p, "utf8"));
    return null;
}

function saveConv(jid, data) {
    fs.writeFileSync(convPath(jid), JSON.stringify(data, null, 2), "utf8");
}

function saveResult(convo) {
    const row = {
        facility_name: convo.facility_name || "",
        phone: convo.phone || "",
        shared_room_price: convo.extracted?.shared_price || "pricing_unknown",
        private_room_price: convo.extracted?.private_price || "pricing_unknown",
        services_included: convo.extracted?.services || "",
        status: convo.status || "",
        updated: new Date().toISOString()
    };

    let rows = [];
    if (fs.existsSync(RESULTS_CSV)) {
        const content = fs.readFileSync(RESULTS_CSV, "utf8");
        rows = content.split("\n").slice(1).filter(Boolean).map(line => {
            const [facility_name, phone, shared, priv, services, status, updated] = line.split(",");
            return { facility_name, phone, shared_room_price: shared, private_room_price: priv, services_included: services, status, updated };
        });
        rows = rows.filter(r => r.phone !== row.phone);
    }
    rows.push(row);

    const header = "facility_name,phone,shared_room_price,private_room_price,services_included,status,updated\n";
    const lines = rows.map(r => Object.values(r).map(v => `"${v || ""}"`).join(",")).join("\n");
    fs.writeFileSync(RESULTS_CSV, header + lines, "utf8");
    console.log(`  💾 Saved result for ${row.facility_name}`);
}

function toJid(phone) {
    if (!phone) return null;
    let p = String(phone).replace(/[\s\-\(\)]/g, "");
    if (p.startsWith("0")) p = "60" + p.slice(1);
    else if (p.startsWith("+")) p = p.slice(1);
    if (!/^\d{8,15}$/.test(p)) return null;
    return p + "@s.whatsapp.net";
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function readFacilities() {
    return new Promise((resolve) => {
        const results = [];
        fs.createReadStream(path.resolve(__dirname, config.FACILITIES_CSV))
            .pipe(csv())
            .on("data", row => results.push(row))
            .on("end", () => resolve(results));
    });
}

function extractText(message) {
    if (!message) return "";
    return message.conversation
        || message.extendedTextMessage?.text
        || message.imageMessage?.caption
        || message.videoMessage?.caption
        || "";
}


// ── Outreach ───────────────────────────────────────────────────────────────

async function runOutreach(sock) {
    const facilities = await readFacilities();
    const targets = facilities.filter(f =>
        f.shared_room_price === "pricing_unknown" &&
        f.phone && String(f.phone).trim() !== "" && String(f.phone) !== "nan"
    );

    console.log(`📋 Facilities needing pricing: ${targets.length}`);
    console.log(`⏱️  Delay between messages: ${config.DELAY_BETWEEN_MESSAGES_MS / 1000}s\n`);
    console.log("Starting outreach in 5 seconds... Press Ctrl+C to stop.\n");
    await sleep(5000);

    let sent = 0;

    for (const facility of targets) {
        const jid = toJid(facility.phone);
        if (!jid) {
            console.log(`  ⚠️  Skip (bad phone): ${facility.facility_name}`);
            continue;
        }

        if (fs.existsSync(convPath(jid))) {
            console.log(`  ⏭️  Already contacted: ${facility.facility_name.slice(0, 40)}`);
            continue;
        }

        console.log(`[${sent + 1}] Messaging: ${facility.facility_name.slice(0, 45)}`);

        try {
            const result = await getOpeningMessage(facility.facility_name);
            console.log(`  💬 "${result.message.slice(0, 70)}..."`);

            const convo = {
                phone: jid,
                facility_name: facility.facility_name,
                history: [{ from: "agent", message: result.message, time: new Date().toISOString() }],
                extracted: {},
                status: "active"
            };

            await sock.sendMessage(jid, { text: result.message });
            saveConv(jid, convo);
            console.log(`  ✅ Sent`);
            sent++;
        } catch (e) {
            console.log(`  ❌ Failed (${facility.facility_name.slice(0, 30)}): ${e.message}`);
        }

        await sleep(config.DELAY_BETWEEN_MESSAGES_MS);
    }

    console.log(`\n✅ Outreach done. Sent: ${sent}`);
    console.log("📡 Listening for replies... (keep this window open)\n");
}


// ── Reply handler ──────────────────────────────────────────────────────────

async function handleReply(sock, msg) {
    const jid = msg.key.remoteJid;
    if (!jid || !jid.endsWith("@s.whatsapp.net")) return; // ignore groups/status
    if (msg.key.fromMe) return;

    const convo = loadConv(jid);
    if (!convo) return; // ignore strangers
    if (convo.status === "completed") return;

    const text = extractText(msg.message);
    if (!text) return;

    console.log(`\n📩 Reply from ${convo.facility_name}: ${text.slice(0, 80)}`);

    convo.history.push({ from: "facility", message: text, time: new Date().toISOString() });

    if (shouldClose(convo.history, convo.extracted)) {
        convo.status = "completed";
        saveConv(jid, convo);
        saveResult(convo);
        return;
    }

    await sleep(config.REPLY_DELAY_MS);
    const result = await getReply(convo.facility_name, convo.history, text);

    const ex = result.extracted;
    if (ex.shared_price && ex.shared_price !== "null") convo.extracted.shared_price = ex.shared_price;
    if (ex.private_price && ex.private_price !== "null") convo.extracted.private_price = ex.private_price;
    if (ex.services && ex.services !== "null") convo.extracted.services = ex.services;
    if (ex.status) convo.extracted.status = ex.status;

    convo.history.push({ from: "agent", message: result.message, time: new Date().toISOString() });

    if (shouldClose(convo.history, convo.extracted)) {
        convo.status = "completed";
        saveResult(convo);
    }

    saveConv(jid, convo);
    await sock.sendMessage(jid, { text: result.message });
    console.log(`  ✉️  Replied: ${result.message.slice(0, 80)}`);
}


// ── Connection ─────────────────────────────────────────────────────────────

let reconnectDelayMs = 2000;

async function start() {
    const { state, saveCreds } = await useMultiFileAuthState(AUTH_DIR);
    const { version, isLatest } = await fetchLatestBaileysVersion();
    console.log(`Using WA Web version ${version.join(".")} (latest: ${isLatest})`);

    const sock = makeWASocket({
        version,
        auth: state,
        browser: Browsers.appropriate("Chrome"),
        printQRInTerminal: false,
        markOnlineOnConnect: false,
        syncFullHistory: false
    });

    sock.ev.on("creds.update", saveCreds);

    sock.ev.on("connection.update", async (update) => {
        const { connection, lastDisconnect, qr } = update;

        if (qr) {
            const qrPath = path.join(__dirname, "qr.png");
            try {
                await qrcode.toFile(qrPath, qr, { width: 400 });
                console.log(`\n📱 QR saved to ${qrPath} — opening it now. Scan with WhatsApp → Linked Devices.`);
                exec(`start "" "${qrPath}"`); // Windows: open PNG with default viewer
            } catch (e) {
                console.log("Failed to write QR PNG:", e.message);
                qrcodeTerminal.generate(qr, { small: true });
            }
        }

        if (connection === "open") {
            console.log("\n✅ WhatsApp connected!\n");
            reconnectDelayMs = 2000;
            await runOutreach(sock);
        }

        if (connection === "close") {
            const code = lastDisconnect?.error?.output?.statusCode;
            const shouldReconnect = code !== DisconnectReason.loggedOut;
            console.log(`⚠️  Disconnected (code ${code}). ${shouldReconnect ? `Reconnecting in ${reconnectDelayMs / 1000}s...` : "Logged out — delete baileys_auth/ and rerun to re-link."}`);
            if (shouldReconnect) {
                setTimeout(() => start().catch(e => console.error("restart failed:", e.message)), reconnectDelayMs);
                reconnectDelayMs = Math.min(reconnectDelayMs * 2, 60000);
            }
        }
    });

    sock.ev.on("messages.upsert", async ({ messages, type }) => {
        if (type !== "notify") return;
        for (const msg of messages) {
            try {
                await handleReply(sock, msg);
            } catch (e) {
                console.log(`  ❌ Reply handler error: ${e.message}`);
            }
        }
    });
}


// ── Start ──────────────────────────────────────────────────────────────────

console.log("=".repeat(50));
console.log("  WhatsApp Pricing Agent (Baileys)");
console.log("=".repeat(50));
console.log("\nConnecting to WhatsApp... please wait\n");

start().catch(err => {
    console.error("Fatal:", err);
    process.exit(1);
});
