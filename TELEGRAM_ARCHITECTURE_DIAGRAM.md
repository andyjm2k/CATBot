# Telegram Bot Integration – Architecture Diagrams

The diagrams below illustrate the current foundation (text chat via proxy) and
show how future phases extend the flow.

---

## 1. High-Level Architecture (Foundation)

```
┌──────────────┐      ┌────────────────────┐      ┌────────────────────────────┐
│  Telegram    │      │  Telegram Bot      │      │ FastAPI Proxy / Eva Backend │
│   Client     │─────▶│  (python-telegram- │─────▶│  /v1/telegram/chat          │
└──────────────┘      │   bot polling)     │      │  OpenAI-compatible API      │
                       │                    │      └────────────────────────────┘
                       │ Commands:          │
                       │  /start /help      │
                       │  /status /clear    │
                       └────────────────────┘
```

---

## 2. Message Flow Sequence

```
1. User sends text message in Telegram.
2. Telegram forwards update to `telegram_bot.py` (polling mode).
3. Bot validates authorization and sends typing indicator.
4. Bot POSTs `{conversation_id, user_id, message}` to `/v1/telegram/chat`.
5. Proxy appends message to per-user history and builds OpenAI payload.
6. Proxy calls OpenAI-compatible endpoint and receives assistant reply.
7. Proxy stores assistant reply in history and returns it to the bot.
8. Bot sends reply message back to Telegram user.
```

---

## 3. `/clear` Command Flow

```
User ──┐
       │ 1. `/clear`
       ▼
Telegram Bot ── 2. DELETE `/v1/telegram/chat/{conversation_id}` ──▶ Proxy
                                                    │
                                                    ├─ purge cached history
                                                    └─ respond `{cleared: true}`
       ▲
       │ 3. Confirmation message
       └─────────────────────────────────────────────────────────────
```

---

## 4. Future: Voice + Files (Phase 1)

```
Telegram Voice/File
      │
      ▼
Telegram Bot ──▶ `/v1/telegram/voice` or `/v1/telegram/files`
                     │
                     ├─ Download from Telegram
                     ├─ Run safety checks / transcription / summarization
                     └─ Forward results to `/v1/telegram/chat`
```

---

## 5. Future: Webhook Deployment (Phase 2)

```
Telegram Servers ──▶ HTTPS Webhook Endpoint (FastAPI)
                       │
                       ├─ Validate secret + replay protection
                       ├─ Enqueue job for bot worker
                       └─ Worker processes update (same flow as polling)
```

These diagrams are intentionally lightweight—update them as the integration
grows (e.g., add Redis, analytics pipelines, or MCP tool routing when those
features ship).
