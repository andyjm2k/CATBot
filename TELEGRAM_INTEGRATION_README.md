# Telegram Bot Integration Documentation

Welcome to the home for everything related to connecting Eva to Telegram. This
folder now ships with a working end-to-end path: the FastAPI proxy exposes a
Telegram-aware chat endpoint and `telegram_bot.py` consumes it using the
official `python-telegram-bot` library. Use this README as the map for the other
resources in the directory.

---

## 🚀 Integration Overview

| Component | Purpose | Key File |
|-----------|---------|----------|
| FastAPI proxy | Exposes `/v1/telegram/chat` and manages conversation state before forwarding to OpenAI (or any compatible endpoint). | `proxy_server.py` |
| Telegram bot | Polls Telegram, enforces access rules, and forwards user messages to the proxy. | `telegram_bot.py` |
| Environment template | Documents every environment variable required by the proxy and bot. | `telegram_env_example.txt` |
| Requirements | Dependency list for the bot runtime. | `requirements_telegram.txt` |

What you get out of the box:

* `/v1/telegram/chat` – POST endpoint that stores per-user history, injects a
  configurable system prompt, and calls the configured OpenAI-compatible API.
* `/v1/telegram/chat/{conversation_id}` – DELETE endpoint that clears cached
  history (used by the `/clear` Telegram command).
* A production-ready polling bot with `/start`, `/help`, `/status`, `/clear`,
  authorization controls, and structured error handling.

---

## 🧭 Quick Setup (TL;DR)

1. Create your bot with @BotFather and collect your Telegram user ID.
2. Copy `telegram_env_example.txt` to `.env` and fill in the required values.
3. Install dependencies: `pip install -r requirements_telegram.txt`.
4. Start the FastAPI proxy (`python proxy_server.py`).
5. Launch the bot (`python telegram_bot.py`).

For a step-by-step walkthrough (including screenshots and troubleshooting) see
[`TELEGRAM_QUICK_START.md`](TELEGRAM_QUICK_START.md).

---

## 📚 Document Map

| If you need… | Read this |
|--------------|-----------|
| Step-by-step setup instructions | [`TELEGRAM_QUICK_START.md`](TELEGRAM_QUICK_START.md) |
| Architectural context and phased roadmap | [`TELEGRAM_INTEGRATION_FEATURE_PLAN.md`](TELEGRAM_INTEGRATION_FEATURE_PLAN.md) |
| Checkbox-level progress tracking | [`TELEGRAM_INTEGRATION_CHECKLIST.md`](TELEGRAM_INTEGRATION_CHECKLIST.md) |
| Task breakdown with owners/estimates | [`TELEGRAM_IMPLEMENTATION_TASKS.md`](TELEGRAM_IMPLEMENTATION_TASKS.md) |
| Executive overview for stakeholders | [`TELEGRAM_INTEGRATION_SUMMARY.md`](TELEGRAM_INTEGRATION_SUMMARY.md) |
| Visual architecture sketches | [`TELEGRAM_ARCHITECTURE_DIAGRAM.md`](TELEGRAM_ARCHITECTURE_DIAGRAM.md) |
| Minimal self-contained demo | [`telegram_bot_minimal_example.py`](telegram_bot_minimal_example.py) |

---

## 🔧 Runtime Essentials

* **Environment variables** – The bot and proxy both rely on the `.env` file.
  Key entries include `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ADMIN_IDS` (or
  `TELEGRAM_ALLOW_ALL=true`), `OPENAI_API_KEY`, and optional overrides for
  models, system prompts, and base URLs. See
  [`telegram_env_example.txt`](telegram_env_example.txt).
* **Dependencies** – Install from `requirements_telegram.txt`. The proxy already
  depends on FastAPI and httpx, so no extra steps are required there.
* **Commands inside the bot** – Users get `/start`, `/help`, `/status`, and
  `/clear`. `/status` pings the proxy `/health` endpoint and reports latency and
  personal usage counts.
* **Proxy endpoint contract** – `telegram_bot.py` posts JSON in the form:
  ```json
  {
    "conversation_id": "123456789",
    "user_id": "123456789",
    "message": "Hello Eva!",
    "system_prompt": "optional",
    "model": "optional"
  }
  ```
  and expects `{ "reply": "…" }` back. The proxy keeps a small rolling history
  (configurable via `TELEGRAM_HISTORY_LIMIT`).

---

## 🧪 Testing the Loop

Once the proxy and bot are running:

1. Send `/start` to the bot from an authorized Telegram account.
2. Exchange a few messages and verify responses come from the configured LLM.
3. Run `/status` to confirm connectivity and message counts.
4. Run `/clear` and confirm the next message starts a fresh conversation.

If something breaks, check:

* Proxy logs for HTTP 4xx/5xx responses from the OpenAI-compatible endpoint.
* Bot logs for authorization failures or connectivity issues.
* Environment variables (typos in user IDs and tokens are the most common issue).

---

## 🔮 Next Steps

* Enable webhook delivery for production (tracked in the feature plan).
* Add voice, files, and tool usage once the underlying proxy endpoints are in
  place.
* Connect analytics/observability (e.g., Sentry) to the bot process.

When you extend the integration, update the relevant sections in the feature
plan and checklist so the documentation stays in lockstep with the code.
