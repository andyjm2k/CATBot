# Telegram Bot Integration Feature Plan

This plan captures the architecture, roadmap, and detailed work items required
to bring Eva to Telegram. The foundation (text chat via the proxy +
`telegram_bot.py`) is complete; the remaining phases extend functionality into
voice, files, tooling, and production hardening.

---

## 1. Architecture Snapshot

```
Telegram App ──> python-telegram-bot ──> FastAPI proxy ──> LLM provider (OpenAI compatible)
                   │                         │
                   │                         └─ stores Telegram conversation state
                   └─ command handlers (/start, /help, /status, /clear)
```

Key characteristics:

* **State** – Conversation history is cached per Telegram user inside the proxy.
* **LLM access** – Proxy calls the configured OpenAI-compatible endpoint using
  the server-side API key.
* **Authorization** – Bot enforces a whitelist (`TELEGRAM_ADMIN_IDS`) with an
  opt-in public mode.
* **Observability** – `/status` surfaces backend latency; logs capture request
  failures and authorization attempts.

See [`TELEGRAM_ARCHITECTURE_DIAGRAM.md`](TELEGRAM_ARCHITECTURE_DIAGRAM.md) for
expanded diagrams and sequence flows.

---

## 2. Roadmap Overview

| Phase | Outcome | Highlights |
|-------|---------|-----------|
| **Foundation** (complete) | Text chat via proxy | `/v1/telegram/chat`, polling bot, history reset, status reporting |
| **Phase 1 – Multimodal MVP** | Voice notes + document ingestion | Whisper transcription, file download pipeline, content safety checks |
| **Phase 2 – Tooling & Webhooks** | Production deployment | Telegram webhooks, Redis/Postgres storage, monitoring/alerting |
| **Phase 3 – Advanced Automation** | Full Eva parity | Browser automation, MCP tool routing, group chat support, analytics |

---

## 3. Phase Breakdown

### Phase 1 – Multimodal MVP

* ✅ **Dependencies** – Whisper (or local transcription service), file operations
  endpoints in the proxy.
* 🛠️ **Tasks**
  - Add `/v1/telegram/voice` endpoint to ingest OGG files, transcribe, and hand
    off to chat pipeline.
  - Extend bot to download voice messages, call the new endpoint, and send
    transcripts + responses.
  - Implement secure document download, scanning, and summarization.
  - Update environment template with storage limits and file type allowlist.
* ✅ **Exit Criteria** – Voice note flows mirrored in Telegram; documents produce
  structured summaries within Telegram.

### Phase 2 – Tooling & Webhooks

* ✅ **Dependencies** – Stable Redis/Postgres services, HTTPS endpoint for webhooks.
* 🛠️ **Tasks**
  - Switch from polling to webhooks with signature verification.
  - Persist conversation state to Redis/Postgres and add retention policies.
  - Integrate monitoring (Sentry, Prometheus, or similar) with alert thresholds.
  - Provide admin commands for broadcasting, user management, and diagnostics.
* ✅ **Exit Criteria** – Zero-downtime deploys, persistent history, webhook-based
  delivery, and baseline observability in place.

### Phase 3 – Advanced Automation

* ✅ **Dependencies** – Mature MCP tool catalog, browser automation host.
* 🛠️ **Tasks**
  - Route Telegram commands to MCP tools (search, browser, workflow execution).
  - Support multi-user sessions, including group chats with moderation controls.
  - Surface analytics dashboards (usage, retention, latency) and billing hooks.
  - Implement escalation paths (hand off to human support, email summaries, etc.).
* ✅ **Exit Criteria** – Telegram achieves parity with the web client and supports
  complex workflows directly from chat.

---

## 4. Current Implementation Notes

* Bot uses `AIORateLimiter` to respect Telegram API limits.
* `TELEGRAM_HISTORY_LIMIT` controls in-memory context size. Increase cautiously to
  manage token usage.
* `/clear` maps to `DELETE /v1/telegram/chat/{conversation_id}`; consider
  enforcing retention policies even without manual clears.
* Errors from the LLM provider bubble up through the proxy with sanitized
  messages—review logs for detailed diagnostics.

---

## 5. Security & Compliance

* Tokens and API keys live in `.env`; never commit credentials.
* Optional `TELEGRAM_ALLOW_ALL=true` should be used sparingly. For production,
  keep a vetted allowlist and add rate limiting + abuse detection.
* Plan to encrypt any at-rest history once Redis/Postgres storage is introduced.
* Review provider-specific data handling policies before forwarding attachments.

---

## 6. Testing Strategy

| Layer | Recommended Tests |
|-------|-------------------|
| Bot | Unit tests for command handlers, integration tests using Telegram Bot API sandbox. |
| Proxy | FastAPI `TestClient` tests for `/v1/telegram/chat` and future endpoints. |
| End-to-end | Mock Telegram updates → bot → proxy → fake LLM to validate orchestration. |

Automate regression tests as features from later phases land.

---

## 7. Deployment Considerations

* **Development** – Polling mode is sufficient; run proxy and bot locally.
* **Staging** – Deploy proxy + bot inside the same VPC and restrict Telegram IP
  ranges.
* **Production** – Prioritize webhook mode with HTTPS termination, autoscaling
  for the bot worker, and persistent logging.

---

## 8. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| OpenAI rate limits / outages | Bot responses fail | Add retry/backoff, support multiple providers via environment overrides |
| Unauthorized access | Data leakage | Keep allowlist strict, log unauthorized attempts, add admin alerting |
| High concurrency | Memory growth from in-memory history | Introduce Redis-backed storage with TTL and bounds |
| Telegram API changes | Bot downtime | Track release notes, pin `python-telegram-bot` version, add integration tests |

---

## 9. Documentation Checklist

* Update `TELEGRAM_INTEGRATION_SUMMARY.md` after each phase.
* Keep `telegram_env_example.txt` in sync with new variables.
* Extend `TELEGRAM_QUICK_START.md` with new setup steps when features ship.
* Add screenshots or diagrams to `TELEGRAM_ARCHITECTURE_DIAGRAM.md` as the flow evolves.

The plan intentionally mirrors the web client roadmap so both surfaces share the
same capabilities, tooling, and operational playbook.
