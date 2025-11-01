# Telegram Bot Integration – Quick Start Guide

Get Eva chatting on Telegram in under 10 minutes. This guide walks through the
happy path for the production-ready bot (`telegram_bot.py`) that talks to the
FastAPI proxy.

---

## ✅ Prerequisites

* Python 3.10+
* A running instance of the FastAPI proxy (`proxy_server.py`)
* Telegram account + ability to message @BotFather
* OpenAI (or OpenAI-compatible) API key

---

## 1. Create your Telegram bot (2 minutes)

1. Open Telegram and message **@BotFather**.
2. Send `/newbot`, choose a name, then pick a username ending with `bot`.
3. Copy the token BotFather returns.
4. Message **@userinfobot** to retrieve your Telegram numeric user ID.

Keep both values handy; you will need them for the `.env` file.

---

## 2. Configure environment variables (2 minutes)

1. Copy the template: `cp telegram_env_example.txt .env`
2. Edit `.env` and set at least:
   ```ini
   TELEGRAM_BOT_TOKEN=1234567890:ABCdef...
   TELEGRAM_ADMIN_IDS=123456789
   OPENAI_API_KEY=sk-proj-...
   TELEGRAM_BACKEND_URL=http://localhost:8002
   ```
3. Optional tweaks:
   * `TELEGRAM_ALLOW_ALL=true` to let anyone talk to the bot.
   * `TELEGRAM_CHAT_MODEL`, `TELEGRAM_BOT_SYSTEM_PROMPT`,
     `TELEGRAM_OPENAI_BASE_URL` for advanced routing.

---

## 3. Install dependencies (1 minute)

```bash
pip install -r requirements_telegram.txt
```

This installs `python-telegram-bot`, `httpx`, and `python-dotenv`.

---

## 4. Start the FastAPI proxy (1 minute)

In a dedicated terminal:

```bash
python proxy_server.py
```

Verify the server prints `AI Assistant Proxy Server` and that `http://localhost:8002/health`
returns `{"status": "healthy"}`.

---

## 5. Run the Telegram bot (1 minute)

In a second terminal:

```bash
python telegram_bot.py
```

You should see logs similar to:

```
🤖 Starting Eva Telegram bot...
Authorized user IDs: [123456789]
✅ Bot is running! Press Ctrl+C to stop.
```

---

## 6. Test the integration (3 minutes)

1. Open Telegram, find your bot, and send `/start`.
2. Confirm the welcome message appears.
3. Send any question—Eva should reply via the proxy + OpenAI.
4. Run `/status` to confirm backend health and latency.
5. Run `/clear` to reset the conversation and verify the next response starts
   fresh.

Troubleshooting tips:

* **Bot does not reply** – Ensure `telegram_bot.py` is running and your user ID
  is listed in `TELEGRAM_ADMIN_IDS` (unless `TELEGRAM_ALLOW_ALL=true`).
* **"Failed to reach Eva backend"** – Confirm the proxy server is running and
  `TELEGRAM_BACKEND_URL` points to the correct host/port.
* **HTTP errors from OpenAI** – Validate your API key and model name, and check
  usage limits on the provider dashboard.

---

## Bonus: minimal sandbox script

Need a super-lightweight demo that talks straight to OpenAI without the proxy?
Run [`telegram_bot_minimal_example.py`](telegram_bot_minimal_example.py). It uses
the same environment variables but skips the advanced features. Use it for quick
experiments, then graduate to `telegram_bot.py` for production.

---

## What’s next?

* Explore the architecture and roadmap in
  [`TELEGRAM_INTEGRATION_FEATURE_PLAN.md`](TELEGRAM_INTEGRATION_FEATURE_PLAN.md).
* Track implementation progress with
  [`TELEGRAM_INTEGRATION_CHECKLIST.md`](TELEGRAM_INTEGRATION_CHECKLIST.md).
* Share the elevator pitch using
  [`TELEGRAM_INTEGRATION_SUMMARY.md`](TELEGRAM_INTEGRATION_SUMMARY.md).
