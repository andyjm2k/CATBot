# Telegram Bot Integration - Architecture Diagrams

Visual representations of the system architecture for the Telegram bot integration.

---

## 1. Current System (Before Telegram Integration)

```
┌─────────────────────────────────────────────────────────┐
│                    User's Web Browser                   │
│                   (index-dev.html)                      │
│  - Speech-to-Text UI                                    │
│  - Text-to-Speech UI                                    │
│  - Live2D Avatar Display                                │
│  - File Upload Interface                                │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ HTTP/WebSocket
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend Server                     │
│              (proxy_server.py - Port 8002)              │
│                                                          │
│  ┌─────────────────────────────────────────────────┐  │
│  │ Web Proxy Endpoints                             │  │
│  │ /v1/proxy/fetch - Web scraping                  │  │
│  │ /v1/proxy/search - Web search (Brave/DDG)      │  │
│  └─────────────────────────────────────────────────┘  │
│                                                          │
│  ┌─────────────────────────────────────────────────┐  │
│  │ AutoGen Integration                             │  │
│  │ /v1/proxy/autogen - Multi-agent workflows       │  │
│  └─────────────────────────────────────────────────┘  │
│                                                          │
│  ┌─────────────────────────────────────────────────┐  │
│  │ MCP Integration                                  │  │
│  │ /v1/mcp/servers/* - Browser automation          │  │
│  └─────────────────────────────────────────────────┘  │
│                                                          │
│  ┌─────────────────────────────────────────────────┐  │
│  │ File Operations                                  │  │
│  │ /v1/files/* - Read/Write docs, PDFs, Excel     │  │
│  └─────────────────────────────────────────────────┘  │
│                                                          │
│  ┌─────────────────────────────────────────────────┐  │
│  │ Audio Proxy                                      │  │
│  │ /v1/audio/transcriptions - Whisper STT          │  │
│  └─────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ API Calls
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                 External Services                       │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  OpenAI API  │  │  Brave API   │  │    Redis     │ │
│  │  - GPT-4     │  │  - Search    │  │  (optional)  │ │
│  │  - Whisper   │  │              │  │              │ │
│  │  - TTS       │  │              │  │              │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## 2. System with Telegram Integration (Minimal Example)

```
┌──────────────────┐                    ┌──────────────────┐
│  Web Browser     │                    │  Telegram User   │
│  (index-dev)     │                    │  Mobile/Desktop  │
│                  │                    │                  │
│  - Live2D UI     │                    │  - Text Messages │
│  - Voice Input   │                    │  - Voice Notes   │
│  - File Upload   │                    │  - Commands      │
└────────┬─────────┘                    └────────┬─────────┘
         │                                       │
         │                                       │
         │                                       ▼
         │                               ┌────────────────┐
         │                               │  Telegram Bot  │
         │                               │     API        │
         │                               │  (External)    │
         │                               └────────┬───────┘
         │                                        │
         │                                        │ Updates
         │                                        │
         │                                        ▼
         │                            ┌──────────────────────┐
         │                            │  Telegram Bot        │
         │                            │  Handler             │
         │                            │  (telegram_bot_      │
         │                            │   minimal_example.py)│
         │                            │                      │
         │                            │  - Polling Mode      │
         │                            │  - Message Router    │
         │                            │  - Session Manager   │
         │                            │  - Auth Middleware   │
         │                            └──────────┬───────────┘
         │                                       │
         │                                       │
         └───────────────┬───────────────────────┘
                         │
                         │ HTTP Requests
                         │
                         ▼
            ┌────────────────────────────┐
            │  FastAPI Backend           │
            │  (proxy_server.py)         │
            │  - All existing endpoints  │
            │  - OpenAI integration      │
            └────────────┬───────────────┘
                         │
                         │
                         ▼
            ┌────────────────────────────┐
            │  External Services         │
            │  - OpenAI API              │
            │  - Brave Search            │
            └────────────────────────────┘
```

---

## 3. Full Production Architecture (Phase 3)

```
┌──────────────────────────────────────────────────────────────────┐
│                        User Interfaces                           │
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    │
│  │ Web Browser  │    │ Telegram     │    │ Telegram     │    │
│  │ Desktop/     │    │ Mobile       │    │ Desktop      │    │
│  │ Mobile       │    │ App          │    │ App          │    │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘    │
└─────────┼──────────────────┼──────────────────┼──────────────┘
          │                   │                   │
          │                   │                   │
          ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Internet / Load Balancer                     │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Nginx Reverse Proxy                         │
│                     (SSL/TLS Termination)                       │
│                                                                  │
│  ┌───────────────────────┐     ┌──────────────────────────┐   │
│  │ HTTPS :443            │     │ Webhook Endpoint         │   │
│  │ - Web traffic         │     │ /v1/telegram/webhook     │   │
│  └───────────────────────┘     └──────────────────────────┘   │
└──────────┬──────────────────────────────┬──────────────────────┘
           │                               │
           │                               │
           ▼                               ▼
┌────────────────────────┐     ┌───────────────────────────────┐
│  Web Server            │     │  Telegram Bot Service         │
│  (Serves HTML/JS)      │     │  (telegram_bot/bot.py)        │
│  :8000                 │     │  :8003                        │
└────────────────────────┘     │                               │
                               │  ┌─────────────────────────┐  │
                               │  │ Webhook Handler         │  │
                               │  │ - Secret validation     │  │
                               │  │ - Update processing     │  │
                               │  └─────────────────────────┘  │
                               │                               │
                               │  ┌─────────────────────────┐  │
                               │  │ Command Handlers        │  │
                               │  │ - /start, /help         │  │
                               │  │ - /search, /clear       │  │
                               │  └─────────────────────────┘  │
                               │                               │
                               │  ┌─────────────────────────┐  │
                               │  │ Message Handlers        │  │
                               │  │ - Text messages         │  │
                               │  │ - Voice messages        │  │
                               │  │ - Documents             │  │
                               │  │ - Images                │  │
                               │  └─────────────────────────┘  │
                               │                               │
                               │  ┌─────────────────────────┐  │
                               │  │ Middleware              │  │
                               │  │ - Authentication        │  │
                               │  │ - Rate limiting         │  │
                               │  │ - Logging               │  │
                               │  └─────────────────────────┘  │
                               └───────────┬───────────────────┘
                                           │
                                           │
┌──────────────────────────────────────────┼────────────────────┐
│                                          │                     │
│                   FastAPI Backend Server │                     │
│                   (proxy_server.py)      │                     │
│                   :8002                  │                     │
│                                          ▼                     │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ Core API Endpoints                                   │    │
│  │                                                       │    │
│  │  /v1/proxy/fetch         - Web scraping              │    │
│  │  /v1/proxy/search        - Web search                │    │
│  │  /v1/proxy/autogen       - AutoGen workflows         │    │
│  │  /v1/mcp/servers/*       - MCP integration           │    │
│  │  /v1/files/*             - File operations           │    │
│  │  /v1/audio/transcriptions - Whisper proxy            │    │
│  │  /v1/telegram/webhook    - Telegram webhook          │    │
│  │  /v1/telegram/process    - Process messages          │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Business Logic                                        │   │
│  │                                                       │   │
│  │  - Message processing                                 │   │
│  │  - Context management                                 │   │
│  │  - Tool orchestration                                 │   │
│  │  - Response formatting                                │   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│    Redis     │ │  PostgreSQL  │ │  Local Files │
│              │ │              │ │              │
│  - Sessions  │ │  - Users     │ │  - Scratch   │
│  - Cache     │ │  - History   │ │    directory │
│  - Rate      │ │  - Metrics   │ │  - Uploads   │
│    limits    │ │  - Logs      │ │  - Temp      │
│              │ │              │ │    files     │
│  :6379       │ │  :5432       │ │              │
└──────────────┘ └──────────────┘ └──────────────┘

                        │
                        │
        ┌───────────────┼───────────────┬──────────────┐
        │               │               │              │
        ▼               ▼               ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐
│  OpenAI API  │ │  Brave       │ │  Telegram    │ │  Browser   │
│              │ │  Search API  │ │  Bot API     │ │  (MCP)     │
│  - GPT-4     │ │              │ │              │ │            │
│  - Whisper   │ │  - Web       │ │  - Send msg  │ │  - Chrome  │
│  - TTS       │ │    search    │ │  - Get file  │ │  - Selenium│
│              │ │              │ │  - Webhook   │ │            │
└──────────────┘ └──────────────┘ └──────────────┘ └────────────┘
```

---

## 4. Message Flow Diagram (Text Message)

```
User sends text message
         │
         ▼
┌──────────────────────┐
│  Telegram Servers    │  1. User sends message via Telegram app
└──────────┬───────────┘
           │
           │ Webhook POST
           │
           ▼
┌──────────────────────┐
│  Nginx               │  2. Receives webhook POST request
│  (Reverse Proxy)     │     Forwards to bot service
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Telegram Bot        │  3. Validates webhook secret
│  Handler             │  4. Parses update
│  - Webhook endpoint  │  5. Routes to message handler
└──────────┬───────────┘
           │
           │ Check auth
           ▼
┌──────────────────────┐
│  Auth Middleware     │  6. Checks if user is authorized
└──────────┬───────────┘     (whitelist check)
           │
           │ Authorized ✓
           ▼
┌──────────────────────┐
│  Rate Limiter        │  7. Checks rate limits
└──────────┬───────────┘     (messages per minute/hour)
           │
           │ Within limits ✓
           ▼
┌──────────────────────┐
│  Session Manager     │  8. Retrieves user session from Redis
│  (Redis)             │  9. Gets conversation history
└──────────┬───────────┘
           │
           │ History + message
           ▼
┌──────────────────────┐
│  Backend API Client  │  10. Formats request
│                      │  11. Calls FastAPI backend
└──────────┬───────────┘
           │
           │ HTTP POST
           ▼
┌──────────────────────┐
│  FastAPI Backend     │  12. Receives request
│  /v1/telegram/process│  13. Processes message
└──────────┬───────────┘
           │
           │ Chat completion request
           ▼
┌──────────────────────┐
│  OpenAI API          │  14. Sends to GPT-4
│  - GPT-4             │  15. Gets AI response
└──────────┬───────────┘
           │
           │ AI response
           ▼
┌──────────────────────┐
│  FastAPI Backend     │  16. Receives AI response
└──────────┬───────────┘  17. Returns to bot handler
           │
           │ JSON response
           ▼
┌──────────────────────┐
│  Telegram Bot        │  18. Receives response
│  Handler             │  19. Updates conversation history
└──────────┬───────────┘  20. Saves to session (Redis)
           │
           │ Send message
           ▼
┌──────────────────────┐
│  Telegram Servers    │  21. Sends response to user
└──────────┬───────────┘
           │
           ▼
      User receives response

Total time: < 2 seconds
```

---

## 5. Voice Message Flow Diagram

```
User sends voice message
         │
         ▼
┌──────────────────────┐
│  Telegram Servers    │  1. User records and sends voice note
└──────────┬───────────┘
           │
           │ Webhook with voice file reference
           ▼
┌──────────────────────┐
│  Telegram Bot        │  2. Receives voice message update
│  Handler             │  3. Gets file_id from update
└──────────┬───────────┘
           │
           │ Download request
           ▼
┌──────────────────────┐
│  Telegram Bot API    │  4. Downloads voice file (OGG format)
│  getFile endpoint    │  5. Returns file bytes
└──────────┬───────────┘
           │
           │ Voice file (OGG)
           ▼
┌──────────────────────┐
│  Temporary Storage   │  6. Saves to temp file
│  /tmp/voice_*.ogg    │
└──────────┬───────────┘
           │
           │ File path
           ▼
┌──────────────────────┐
│  Backend API         │  7. Uploads to Whisper endpoint
│  /v1/audio/          │  8. Calls OpenAI Whisper API
│   transcriptions     │
└──────────┬───────────┘
           │
           │ Audio file
           ▼
┌──────────────────────┐
│  OpenAI Whisper API  │  9. Transcribes audio to text
└──────────┬───────────┘
           │
           │ Transcription
           ▼
┌──────────────────────┐
│  Telegram Bot        │  10. Receives transcribed text
│  Handler             │  11. Sends "Transcribed: ..." message
└──────────┬───────────┘  12. Deletes temp file
           │
           │ Process as text message
           ▼
   (Follows text message flow)
```

---

## 6. Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Telegram Bot Application                │
│                                                              │
│  ┌────────────────┐     ┌────────────────┐                 │
│  │   Handlers     │────▶│   Middleware   │                 │
│  │                │     │                │                 │
│  │ - Commands     │     │ - Auth         │                 │
│  │ - Messages     │     │ - Rate Limit   │                 │
│  │ - Voice        │     │ - Logging      │                 │
│  │ - Documents    │     └────────┬───────┘                 │
│  │ - Images       │              │                          │
│  │ - Callbacks    │              │                          │
│  └────────┬───────┘              │                          │
│           │                      │                          │
│           └──────────┬───────────┘                          │
│                      │                                      │
│                      ▼                                      │
│           ┌────────────────────┐                           │
│           │   Utils            │                           │
│           │                    │                           │
│           │ - Session Manager  │───────┐                   │
│           │ - API Client       │       │                   │
│           │ - Formatting       │       │                   │
│           │ - File Handler     │       │                   │
│           └────────┬───────────┘       │                   │
│                    │                   │                   │
└────────────────────┼───────────────────┼───────────────────┘
                     │                   │
                     │                   ▼
                     │            ┌─────────────┐
                     │            │   Redis     │
                     │            │             │
                     │            │ - Sessions  │
                     │            │ - Cache     │
                     │            └─────────────┘
                     │
                     ▼
            ┌────────────────────┐
            │  FastAPI Backend   │
            │                    │
            │ - OpenAI proxy     │
            │ - File operations  │
            │ - Web search       │
            │ - MCP integration  │
            │ - AutoGen          │
            └────────┬───────────┘
                     │
         ┌───────────┼───────────┐
         │           │           │
         ▼           ▼           ▼
    ┌────────┐  ┌────────┐  ┌────────┐
    │ OpenAI │  │ Brave  │  │  MCP   │
    │  API   │  │ Search │  │Browser │
    └────────┘  └────────┘  └────────┘
```

---

## 7. Deployment Architecture (Docker)

```
┌─────────────────────────────────────────────────────────────┐
│                         Docker Host                         │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Nginx Container (Port 80/443)                       │  │
│  │  - Reverse proxy                                     │  │
│  │  - SSL termination                                   │  │
│  │  - Load balancing                                    │  │
│  └────┬──────────────────────────────────────────┬──────┘  │
│       │                                           │          │
│       │ :8003                                     │ :8002    │
│       │                                           │          │
│  ┌────▼────────────────────┐        ┌────────────▼──────┐  │
│  │  Telegram Bot Container │        │  Backend Container │  │
│  │  telegram-bot:latest    │        │  backend:latest    │  │
│  │                         │        │                    │  │
│  │  - Python 3.10          │        │  - FastAPI app     │  │
│  │  - Bot handlers         │        │  - All endpoints   │  │
│  │  - Webhook mode         │        │  - OpenAI client   │  │
│  └────┬────────────────────┘        └────────┬───────────┘  │
│       │                                      │               │
│       │                                      │               │
│       └──────────────┬───────────────────────┘               │
│                      │                                       │
│                      │ :6379                                 │
│                      │                                       │
│                 ┌────▼───────────┐                          │
│                 │ Redis Container │                          │
│                 │ redis:7-alpine  │                          │
│                 │                 │                          │
│                 │ - Session store │                          │
│                 │ - Rate limiting │                          │
│                 │ - Cache         │                          │
│                 └─────────────────┘                          │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Volumes                                             │  │
│  │  - redis_data:/data                                  │  │
│  │  - ./logs:/app/logs                                  │  │
│  │  - ./scratch:/app/scratch                            │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Network: eva_network                                │  │
│  │  All containers communicate via internal network     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

External Services (Outside Docker):
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Telegram    │  │  OpenAI      │  │  Brave       │
│  Bot API     │  │  API         │  │  Search API  │
└──────────────┘  └──────────────┘  └──────────────┘
```

---

## 8. Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Security Layers                          │
└─────────────────────────────────────────────────────────────┘

Layer 1: Network Security
┌─────────────────────────────────────────────────────────────┐
│  - Firewall rules (only 80/443 exposed)                    │
│  - DDoS protection                                          │
│  - IP whitelisting (optional)                              │
│  - SSL/TLS (Let's Encrypt)                                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
Layer 2: Application Security
┌─────────────────────────────────────────────────────────────┐
│  - Webhook secret validation                                │
│  - Bot token protection (environment variables)             │
│  - API key encryption at rest                               │
│  - HTTPS only communication                                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
Layer 3: Authentication & Authorization
┌─────────────────────────────────────────────────────────────┐
│  - User whitelist (Telegram user IDs)                      │
│  - Admin role verification                                  │
│  - Session token validation                                 │
│  - Rate limiting per user                                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
Layer 4: Input Validation
┌─────────────────────────────────────────────────────────────┐
│  - Message length limits                                    │
│  - File type validation                                     │
│  - File size limits                                         │
│  - URL filtering                                            │
│  - SQL injection prevention                                 │
│  - XSS prevention                                           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
Layer 5: Data Protection
┌─────────────────────────────────────────────────────────────┐
│  - Conversation encryption (in Redis)                       │
│  - Secure file storage                                      │
│  - Auto-deletion of temp files                              │
│  - Data retention policies                                  │
│  - GDPR compliance                                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
Layer 6: Monitoring & Logging
┌─────────────────────────────────────────────────────────────┐
│  - Audit logs (all actions)                                 │
│  - Error tracking (Sentry)                                  │
│  - Security alerts                                          │
│  - Anomaly detection                                        │
│  - No PII in logs                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 9. Data Flow - Document Processing

```
User uploads document (PDF/DOCX/XLSX)
         │
         ▼
┌──────────────────────┐
│  Telegram Servers    │  1. User sends document
└──────────┬───────────┘
           │
           │ Document metadata + file_id
           ▼
┌──────────────────────┐
│  Bot Handler         │  2. Validates file type and size
│  Document Handler    │  3. Downloads file from Telegram
└──────────┬───────────┘
           │
           │ File bytes
           ▼
┌──────────────────────┐
│  Temp Storage        │  4. Saves to scratch directory
│  scratch/            │
└──────────┬───────────┘
           │
           │ File path
           ▼
┌──────────────────────┐
│  Backend API         │  5. Calls /v1/files/read
│  /v1/files/read      │  6. Processes file based on type
└──────────┬───────────┘
           │
           │ Extracted text
           ▼
┌──────────────────────┐
│  OpenAI API          │  7. Sends text for summarization
│  Chat Completion     │  8. Gets summary
└──────────┬───────────┘
           │
           │ Summary
           ▼
┌──────────────────────┐
│  Bot Handler         │  9. Formats response
└──────────┬───────────┘  10. Sends summary to user
           │              11. Deletes temp file
           │
           ▼
┌──────────────────────┐
│  User receives       │  Summary displayed in chat
│  document summary    │
└──────────────────────┘
```

---

## 10. Scalability Architecture

```
                         ┌──────────────────┐
                         │  Load Balancer   │
                         │  (Nginx/HAProxy) │
                         └────────┬─────────┘
                                  │
                   ┌──────────────┼──────────────┐
                   │              │              │
                   ▼              ▼              ▼
          ┌────────────┐  ┌────────────┐  ┌────────────┐
          │  Bot       │  │  Bot       │  │  Bot       │
          │  Instance 1│  │  Instance 2│  │  Instance 3│
          │  (Webhook) │  │  (Webhook) │  │  (Webhook) │
          └─────┬──────┘  └─────┬──────┘  └─────┬──────┘
                │               │               │
                └───────────────┼───────────────┘
                                │
                    ┌───────────┼───────────┐
                    │           │           │
                    ▼           ▼           ▼
          ┌────────────┐  ┌────────────┐  ┌────────────┐
          │  Backend   │  │  Backend   │  │  Backend   │
          │  Instance 1│  │  Instance 2│  │  Instance 3│
          └─────┬──────┘  └─────┬──────┘  └─────┬──────┘
                │               │               │
                └───────────────┼───────────────┘
                                │
                    ┌───────────┼───────────┐
                    │           │           │
                    ▼           ▼           ▼
          ┌────────────┐  ┌────────────┐  ┌────────────┐
          │  Redis     │  │ PostgreSQL │  │  OpenAI    │
          │  Cluster   │  │  Primary   │  │  API       │
          │  (Master/  │  │  + Replica │  │            │
          │   Slave)   │  │            │  │            │
          └────────────┘  └────────────┘  └────────────┘

Supports:
- 1000+ concurrent users
- Horizontal scaling
- High availability
- Load distribution
```

---

## Legend

```
┌─────────┐
│ Box     │  Component or service
└─────────┘

    │       
    ▼       Arrow showing data flow or connection

────────    Horizontal line for grouping

HTTP/HTTPS  Protocol used for communication

:8002       Port number
```

---

## Notes

1. **Minimal Example**: Uses simple architecture with polling mode, suitable for testing
2. **Production**: Uses webhook mode with SSL, multiple services, and proper security
3. **Scalability**: Can be horizontally scaled by adding more instances
4. **Security**: Multiple layers of security from network to data protection
5. **Monitoring**: Comprehensive logging and monitoring at all levels

For implementation details, see the full documentation in other files.

