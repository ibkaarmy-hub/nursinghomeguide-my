// WhatsApp Web Agent — Configuration
// Secrets live in .env (see .env.example). Other settings are below.

require("dotenv").config({ path: require("path").join(__dirname, ".env"), override: true });

if (!process.env.OPENROUTER_API_KEY) {
    throw new Error("OPENROUTER_API_KEY missing. Copy .env.example to .env and fill in the key.");
}

module.exports = {
    OPENROUTER_API_KEY: process.env.OPENROUTER_API_KEY,
    MODEL: "anthropic/claude-haiku-4.5",   // OpenRouter model id

    // Project identity (used in outreach messages)
    PROJECT_NAME: "Nursing Home Guide Malaysia",
    PROJECT_URL: "https://nursinghomeguide.my",

    // Files (relative to this folder)
    FACILITIES_CSV: "../../output/STEP3-johor-master.csv",
    RESULTS_CSV: "../../output/STEP4-whatsapp-results.csv",
    CONVERSATIONS_DIR: "./conversations",

    // Outreach settings
    DELAY_BETWEEN_MESSAGES_MS: 30000,   // 30 seconds between each opening message
    MAX_REPLIES: 6,                     // Max back-and-forth per facility
    REPLY_DELAY_MS: 3000,               // Small delay before replying (feels more human)
};
