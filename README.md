# AI Assistant Project

A comprehensive AI assistant system featuring browser automation, speech-to-text, text-to-speech, multi-agent collaboration, and 3D avatar integration with VRM/Live2D support.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Dependencies](#dependencies)
- [Installation Guide](#installation-guide)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Additional Resources](#additional-resources)

## Prerequisites

Before installing this project, ensure you have the following installed:

### System Requirements

- **Node.js** (v16 or higher)
  - Download: https://nodejs.org/
  - Verify: `node --version`

- **Python** (v3.11 or higher)
  - Download: https://www.python.org/downloads/
  - Verify: `python --version`
  - Note: Python 3.11+ is required for browser-use and MCP dependencies

- **Chrome/Chromium Browser**
  - Required for browser automation features
  - Download: https://www.google.com/chrome/

### API Keys and Endpoints

You will need the following API keys and service endpoints:

1. **OpenAI-Compatible LLM Endpoint**
   - For text generation and chat functionality
   - Examples: OpenAI API, Azure OpenAI, or any OpenAI-compatible endpoint
   - Environment variable: `OPENAI_API_KEY` or `OPENAI_API_BASE`

2. **OpenAI-Compatible TTS (Text-to-Speech) Endpoint**
   - For converting text to speech
   - Examples: OpenAI TTS API, Azure TTS, or compatible service
   - Environment variable: `OPENAI_API_KEY` (shared with LLM) or separate TTS endpoint

3. **OpenAI-Compatible Whisper Endpoint (STT - Speech-to-Text)**
   - For converting speech to text
   - Examples: OpenAI Whisper API, or compatible Whisper service
   - Default: `http://localhost:8001/v1/audio/transcriptions`
   - Environment variable: `WHISPER_ENDPOINT`

4. **Brave Search API Key** (Required for web search)
   - For web search functionality
   - Get your key: https://brave.com/search/api/
   - Environment variable: `BRAVE_API_KEY`
   - Note: If not configured, web search will fall back to DuckDuckGo

5. **News API Key** (Optional, can be configured in UI)
   - For news aggregation features
   - Get your key: https://newsapi.org/
   - Can be configured in the application settings UI (stored in browser localStorage)
   - Environment variable: `NEWS_API_KEY` (not currently used - use UI settings instead)

6. **Telegram Bot Token** (Optional, for Telegram integration)
   - Create a bot: https://core.telegram.org/bots#botfather
   - Environment variable: `TELEGRAM_BOT_TOKEN`

### Additional Dependencies

- **Microsoft PyAutoGen / AutoGen**
  - Python package for multi-agent collaboration
  - GitHub: https://github.com/microsoft/autogen
  - Installation: `pip install autogen-agentchat autogen-core autogen-ext`

- **Browser-Use Agent**
  - Autonomous browser automation agent
  - GitHub: https://github.com/browser-use/browser-use
  - Installation: Included via `mcp-browser-use` submodule

- **VRoid VRM Model Files**
  - 3D avatar models in VRM format
  - Place in `model_avatar/` directory
  - Resources: https://vroid.com/studio

- **VMA Files (VRM Animation)**
  - Emotive animations for VRM models
  - Place alongside VRM files in `model_avatar/` directories
  - Resources: https://github.com/vrm-c/vrm-specification

- **Live2D Models** (Alternative to VRM)
  - 2D avatar models for Live2D option
  - Place in appropriate model directories
  - Resources: https://www.live2d.com/

## Dependencies

### NPM Packages

The following npm packages are required (see `package.json`):

| Package | Version | Purpose |
|---------|---------|----------|
| `@langchain/mcp-adapters` | ^0.6.0 | LangChain integration with Model Context Protocol |
| `@modelcontextprotocol/sdk` | ^1.0.0 | Model Context Protocol SDK for Node.js |
| `axios` | ^1.6.2 | HTTP client for API requests |
| `cors` | ^2.8.5 | Cross-Origin Resource Sharing middleware |
| `express` | ^4.18.2 | Web server framework |
| `ogg-opus-decoder` | ^1.7.3 | Audio decoder for Opus codec |

### Python Packages

#### Core Dependencies

| Package | Version | Purpose |
|---------|---------|----------|
| `fastapi` | Latest | Modern web framework for building APIs |
| `uvicorn` | Latest | ASGI server for FastAPI |
| `httpx` | Latest | Async HTTP client |
| `pydantic` | Latest | Data validation using Python type annotations |
| `python-dotenv` | Latest | Load environment variables from .env files |

#### File Operations

| Package | Version | Purpose |
|---------|---------|----------|
| `python-docx` | Latest | Read/write Microsoft Word documents |
| `openpyxl` | Latest | Read/write Excel files |
| `PyPDF2` | Latest | Read PDF files |
| `Pillow` | Latest | Image processing |
| `reportlab` | Latest | Generate PDF files |

#### AI & Agent Frameworks

| Package | Version | Purpose |
|---------|---------|----------|
| `autogen-agentchat` | Latest | Microsoft AutoGen multi-agent chat framework |
| `autogen-core` | Latest | AutoGen core components |
| `autogen-ext` | Latest | AutoGen extensions |
| `mcp` | >=1.6.0 | Model Context Protocol Python SDK |

#### Browser Automation

| Package | Version | Purpose |
|---------|---------|----------|
| `browser-use` | 0.1.41 | Autonomous browser automation agent |
| `playwright` | Latest | Browser automation framework |
| `pyperclip` | 1.9.0 | Clipboard operations |

#### LangChain Integration

| Package | Version | Purpose |
|---------|---------|----------|
| `langchain-community` | Latest | Community LangChain integrations |
| `langchain-mistralai` | 0.2.4 | Mistral AI integration |
| `langchain-ibm` | 0.3.10 | IBM Watson integration |
| `langchain_mcp_adapters` | 0.0.9 | MCP adapters for LangChain |
| `langgraph` | 0.3.34 | Graph-based agent orchestration |

#### Additional Utilities

| Package | Version | Purpose |
|---------|---------|----------|
| `json-repair` | Latest | Repair malformed JSON |
| `MainContentExtractor` | 0.0.4 | Extract main content from web pages |
| `pydantic-settings` | >=2.0.0 | Settings management with Pydantic |
| `typer` | >=0.12.0 | CLI framework |
| `python-telegram-bot` | Latest | Telegram bot API wrapper |
| `flask` | Latest | Flask web framework for MCP Browser HTTP server |
| `flask-cors` | Latest | CORS support for Flask server |

#### MCP Browser-Use Submodule Dependencies

The `mcp-browser-use` submodule has its own dependencies (see `mcp-browser-use/pyproject.toml`):

- `pydantic-settings>=2.0.0`
- `mcp>=1.6.0`
- `typer>=0.12.0`
- `browser-use==0.1.41`
- `pyperclip==1.9.0`
- `json-repair`
- `langchain-mistralai==0.2.4`
- `MainContentExtractor==0.0.4`
- `langchain-ibm==0.3.10`
- `langchain_mcp_adapters==0.0.9`
- `langgraph==0.3.34`
- `langchain-community`

## Installation Guide

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd AI_assistant
```

### Step 2: Install Node.js Dependencies

```bash
npm install
```

This will install all npm packages listed in `package.json`.

### Step 3: Install Python Dependencies

#### Option A: Using pip (Recommended for main project)

```bash
# Create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install core dependencies
pip install fastapi uvicorn httpx pydantic python-dotenv

# Install file operations dependencies
pip install python-docx openpyxl PyPDF2 Pillow reportlab

# Install AI frameworks
pip install autogen-agentchat autogen-core autogen-ext

# Install MCP and browser automation
pip install "mcp>=1.6.0" "browser-use==0.1.41" playwright pyperclip

# Install LangChain dependencies
pip install langchain-community langchain-mistralai==0.2.4 langchain-ibm==0.3.10 langchain_mcp_adapters==0.0.9 langgraph==0.3.34

# Install additional utilities
pip install json-repair MainContentExtractor==0.0.4 pydantic-settings typer python-telegram-bot flask flask-cors

# Install Playwright browsers
playwright install
```

#### Option B: Using UV (For mcp-browser-use submodule)

The `mcp-browser-use` submodule uses `uv` as its package manager:

```bash
# Install UV package manager
pip install uv
# OR
# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows (PowerShell):
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Navigate to mcp-browser-use directory
cd mcp-browser-use

# Sync dependencies using uv
uv sync

# Install Playwright browsers for uv environment
uv run playwright install

# Return to project root
cd ..
```

**GitHub Resources:**
- UV Package Manager: https://github.com/astral-sh/uv
- MCP Browser-Use: https://github.com/Saik0s/mcp-browser-use

### Step 4: Install Microsoft AutoGen

```bash
# Install AutoGen packages
pip install autogen-agentchat autogen-core autogen-ext

# Optional: Install AutoGen Studio for visual team configuration
pip install autogenstudio
```

**GitHub Resources:**
- Microsoft AutoGen: https://github.com/microsoft/autogen
- AutoGen Studio: https://github.com/microsoft/autogen-studio

### Step 5: Set Up Browser-Use Agent

The browser-use agent is included via the `mcp-browser-use` submodule. Ensure it's properly installed:

```bash
# Verify browser-use installation
cd mcp-browser-use
uv run mcp-server-browser-use --help
cd ..
```

**GitHub Resources:**
- Browser-Use: https://github.com/browser-use/browser-use

### Step 6: Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Copy example configuration
cp mcp_config.env.example .env
# Windows:
copy mcp_config.env.example .env
```

Edit `.env` with your configuration:

```env
# OpenAI-Compatible LLM Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini

# TTS Configuration (OpenAI-Compatible)
# Uses same OPENAI_API_KEY or configure separate endpoint
TTS_ENDPOINT=https://api.openai.com/v1/audio/speech

# STT Configuration (Whisper-Compatible)
WHISPER_ENDPOINT=http://localhost:8001/v1/audio/transcriptions

# Brave Search API
BRAVE_API_KEY=your_brave_api_key_here

# News API
NEWS_API_KEY=your_news_api_key_here

# Telegram Bot (Optional)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_ADMIN_IDS=123456789,987654321
TELEGRAM_ALLOW_ALL=false

# MCP Browser-Use Configuration
MCP_LLM_PROVIDER=google
MCP_LLM_MODEL_NAME=gemini-2.0-flash-exp
GOOGLE_API_KEY=your_google_api_key_here
MCP_BROWSER_HEADLESS=true
MCP_RESEARCH_TOOL_SAVE_DIR=./research_output

# AutoGen Configuration
AUTOGEN_CONFIG_PATH=./team-config.json
```

### Step 7: Set Up Avatar Models

#### VRM Models (VRoid)

1. Download or create VRM models from VRoid Studio
2. Place `.vrm` files in `model_avatar/<model_name>/` directories
3. Example structure:
   ```
   model_avatar/
     ├── Eva/
     │   └── Eva.vrm
     ├── Alicia/
     │   └── Alicia.vrm
     └── ...
   ```

**Resources:**
- VRoid Studio: https://vroid.com/studio
- VRM Specification: https://github.com/vrm-c/vrm-specification

#### VMA Animation Files

1. Download or create VMA (VRM Animation) files
2. Place `.vrma` files alongside VRM models
3. Example:
   ```
   model_avatar/
     └── Eva/
         ├── Eva.vrm
         ├── 001_motion_pose.vrma
         ├── 002_dogeza.vrma
         └── ...
   ```

**Resources:**
- VRM Animation: https://github.com/vrm-c/vrm-specification/tree/master/specification/VRMC_vrm_animation-1.0

#### Live2D Models (Alternative)

1. Download Live2D Cubism models
2. Place model files in appropriate directories
3. Configure Live2D runtime in your application

**Resources:**
- Live2D Cubism: https://www.live2d.com/
- Live2D SDK: https://www.live2d.com/sdk/

### Step 8: Create Required Directories

```bash
# Create scratch directory for file operations
mkdir scratch

# Create research output directory
mkdir research_output

# Create directories for optional features
mkdir -p recordings      # If using browser recording
mkdir -p agent_history   # If saving agent history
mkdir -p traces          # If using Playwright tracing
```

### Step 9: Verify Installation

```bash
# Test Node.js dependencies
node -e "console.log('Node.js OK')"
npm list --depth=0

# Test Python dependencies
python -c "import fastapi; print('FastAPI OK')"
python -c "import autogen_agentchat; print('AutoGen OK')"
python -c "import mcp; print('MCP OK')"
python -c "import browser_use; print('Browser-Use OK')"

# Test Playwright
python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"

# Test MCP Browser-Use server
cd mcp-browser-use
uv run mcp-server-browser-use --help
cd ..
```

## Configuration

### Environment Variables

Key environment variables (see `mcp_config.env.example` for complete list):

#### LLM Configuration
- `OPENAI_API_KEY`: OpenAI API key
- `OPENAI_API_BASE`: OpenAI-compatible endpoint base URL
- `OPENAI_MODEL`: Model name to use
- `GOOGLE_API_KEY`: Google AI API key (for Gemini)
- `ANTHROPIC_API_KEY`: Anthropic API key (for Claude)

#### MCP Browser-Use Configuration
- `MCP_LLM_PROVIDER`: LLM provider (openai, google, anthropic, azure_openai, deepseek, mistral, ollama, openrouter, alibaba, moonshot, unbound_ai)
- `MCP_LLM_MODEL_NAME`: Specific model name (e.g., gemini-2.0-flash-exp, gpt-4o-mini)
- `MCP_LLM_PLANNER_PROVIDER`: Optional separate planner LLM provider
- `MCP_LLM_PLANNER_MODEL_NAME`: Optional separate planner model name
- `MCP_BROWSER_HEADLESS`: Run browser in headless mode (true/false)
- `MCP_BROWSER_DISABLE_SECURITY`: Disable browser security features (use with caution)
- `MCP_BROWSER_KEEP_OPEN`: Keep browser open between requests (improves performance)
- `MCP_BROWSER_WINDOW_WIDTH`: Browser window width (default: 1280)
- `MCP_BROWSER_WINDOW_HEIGHT`: Browser window height (default: 1100)
- `MCP_BROWSER_USE_OWN_BROWSER`: Connect to existing browser instance (true/false)
- `MCP_BROWSER_CDP_URL`: Chrome DevTools Protocol URL (if using own browser)
- `MCP_RESEARCH_TOOL_SAVE_DIR`: Directory for research outputs (required)
- `MCP_RESEARCH_TOOL_MAX_PARALLEL_BROWSERS`: Maximum parallel browsers for research (default: 3)
- `MCP_AGENT_TOOL_MAX_STEPS`: Maximum steps per task (default: 100)
- `MCP_AGENT_TOOL_MAX_ACTIONS_PER_STEP`: Maximum actions per step (default: 5)
- `MCP_AGENT_TOOL_USE_VISION`: Enable screenshot analysis (true/false)
- `MCP_AGENT_TOOL_TOOL_CALLING_METHOD`: Tool calling method (auto, json_schema, function_calling)
- `MCP_AGENT_TOOL_MAX_INPUT_TOKENS`: Maximum input tokens (default: 128000)
- `MCP_AGENT_TOOL_ENABLE_RECORDING`: Enable video recording (true/false)
- `MCP_SERVER_LOGGING_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `MCP_SERVER_ANONYMIZED_TELEMETRY`: Enable anonymized telemetry (true/false)

#### Service Endpoints
- `WHISPER_ENDPOINT`: Whisper STT service endpoint (default: http://localhost:8001/v1/audio/transcriptions)
- `TTS_ENDPOINT`: TTS service endpoint (default: http://localhost:4123/v1)
- `BRAVE_API_KEY`: Brave Search API key (required for Brave Search, falls back to DuckDuckGo if not set)
- `NEWS_API_KEY`: News API key (configure in UI settings, stored in browser localStorage)

#### Telegram Bot Configuration
- `TELEGRAM_BOT_TOKEN`: Telegram bot token from BotFather (required)
- `TELEGRAM_ADMIN_IDS`: Comma-separated list of allowed Telegram user IDs
- `TELEGRAM_ALLOW_ALL`: Set to "true" to allow all users (default: false)
- `TELEGRAM_BACKEND_URL`: Backend URL for chat requests (default: http://localhost:8002)
- `TELEGRAM_CHAT_ENDPOINT`: Chat endpoint path (default: /v1/telegram/chat)
- `TELEGRAM_CHAT_TIMEOUT`: Request timeout in seconds (default: 30)
- `TELEGRAM_HISTORY_LIMIT`: Maximum conversation history messages (default: 12)
- `TELEGRAM_BOT_SYSTEM_PROMPT`: Optional system prompt override
- `TELEGRAM_CHAT_MODEL`: Optional model override

### Team Configuration (AutoGen)

Edit `team-config.json` to configure your AutoGen team:

```json
{
  "label": "My AI Team",
  "type": "team",
  "members": [
    {
      "name": "assistant",
      "type": "assistant",
      "model": "gpt-4o-mini"
    }
  ]
}
```

**Resources:**
- AutoGen Documentation: https://microsoft.github.io/autogen/
- AutoGen Studio: https://github.com/microsoft/autogen-studio

## Usage

### Starting the Services

#### Option 1: Start All Services (Windows)

```bash
python start_all.py
```

This will start:
- HTTP server (port 8000)
- Whisper API server (port 8001)
- Proxy server (port 8002)
- AutoGen Studio (port 8084)
- MCP Browser-Use server
- MCP Browser HTTP server (port 5001)

#### Option 1b: Stop All Services (Windows)

```bash
python stop_all.py
```

This will stop all running services including:
- Python processes (http.server, Whisper, Proxy server)
- Node.js processes
- AutoGen Studio
- All command windows

#### Option 2: Start Services Individually

```bash
# Start HTTP server
python -m http.server 8000

# Start Whisper server (if separate)
cd ../whisper-api-server
python main.py

# Start proxy server
python proxy_server.py

# Start AutoGen Studio
autogenstudio serve --team team-config.json --port 8084

# Start MCP Browser-Use server
cd mcp-browser-use
uv run mcp-server-browser-use

# Start MCP Browser HTTP server
python start_mcp_browser_server.py
# OR use the startup script with environment validation
python start_mcp_browser_server.py
```

### Accessing the Application

1. **Web Interface**: Open `index-dev.html` in your browser (served on port 8000)
2. **AutoGen Studio**: Navigate to `http://localhost:8084`
3. **Proxy Server API**: `http://localhost:8002` (FastAPI with comprehensive endpoints)
4. **MCP Browser HTTP Server**: `http://localhost:5001` (Flask-based HTTP bridge for browser automation)

### API Endpoints

#### Proxy Server Endpoints (Port 8002)

The FastAPI proxy server provides the following endpoints:

**Web Operations:**
- `GET /v1/proxy/fetch` - Fetch web content from a URL
- `GET /v1/proxy/search` - Perform web search (Brave Search or DuckDuckGo fallback)

**AI & Chat:**
- `POST /v1/proxy/autogen` - AutoGen team-based chat endpoint
- `POST /v1/telegram/chat` - Telegram bot chat endpoint
- `DELETE /v1/telegram/chat/{conversation_id}` - Clear Telegram conversation history

**Speech & Audio:**
- `POST /v1/audio/transcriptions` - Whisper STT proxy endpoint (handles CORS)
- `GET /v1/proxy/tts/voices` - Get available TTS voices
- `POST /v1/proxy/tts/speech` - Generate TTS speech (supports streaming)

**MCP Server Management:**
- `POST /v1/mcp/servers` - Add or update MCP server configuration
- `GET /v1/mcp/servers` - List all configured MCP servers
- `POST /v1/mcp/servers/{server_id}/connect` - Connect to an MCP server
- `POST /v1/mcp/servers/{server_id}/disconnect` - Disconnect from an MCP server
- `POST /v1/mcp/servers/{server_id}/tools/call` - Call an MCP tool
- `POST /v1/mcp/servers/{server_id}/tools/list` - List available MCP tools

**File Operations:**
- `POST /v1/files/read` - Read files (supports: txt, docx, xlsx, pdf, png, jpg)
- `POST /v1/files/write` - Write files (supports: txt, docx, xlsx, pdf)
- `GET /v1/files/list` - List all files in scratch directory
- `DELETE /v1/files/delete/{filename}` - Delete a file from scratch directory

**Utility:**
- `GET /health` - Health check endpoint
- `GET /test` - Simple test endpoint

#### MCP Browser HTTP Server Endpoints (Port 5001)

The Flask-based HTTP bridge provides browser automation endpoints:

- `POST /api/browser-agent` - Execute browser automation task
  ```json
  {
    "task": "Go to example.com and get the page title"
  }
  ```

- `POST /api/deep-research` - Execute deep research task
  ```json
  {
    "research_task": "Research topic description",
    "max_parallel_browsers": 3
  }
  ```

- `GET /api/health` - Check server health and MCP availability
- `POST /api/disconnect` - Disconnect MCP client (compatibility endpoint)

### Using Browser Automation

The browser automation features are accessible through the MCP Browser-Use integration:

```bash
# Via HTTP API (MCP Browser HTTP Server)
curl -X POST http://localhost:5001/api/browser-agent \
  -H "Content-Type: application/json" \
  -d '{"task": "Go to example.com and get the page title"}'

# Via Proxy Server MCP endpoints
curl -X POST http://localhost:8002/v1/mcp/servers/browser-use/tools/call \
  -H "Content-Type: application/json" \
  -d '{"toolName": "run_browser_agent", "parameters": {"task": "Your task here"}}'

# Via MCP tools in the frontend
# Use the browser automation tool in the web interface
```

### Using File Operations

The proxy server provides file operations for working with documents in the `scratch/` directory:

```bash
# Read a file
curl -X POST http://localhost:8002/v1/files/read \
  -H "Content-Type: application/json" \
  -d '{"filename": "document.docx"}'

# Write a file
curl -X POST http://localhost:8002/v1/files/write \
  -H "Content-Type: application/json" \
  -d '{"filename": "output.docx", "content": "Your content here", "format": "docx"}'

# List all files
curl http://localhost:8002/v1/files/list

# Delete a file
curl -X DELETE http://localhost:8002/v1/files/delete/document.docx
```

Supported file formats:
- **Read**: txt, docx, xlsx, pdf, png, jpg, jpeg
- **Write**: txt, docx, xlsx, pdf

**File Operations Details:**
- All file operations work within the `scratch/` directory
- Text files (`.txt`) are read/written as plain text
- Word documents (`.docx`) support full document structure
- Excel files (`.xlsx`) can be read and written with formatting
- PDF files (`.pdf`) support text extraction and generation
- Images (`.png`, `.jpg`, `.jpeg`) can be read and analyzed
- Files are automatically organized by modification time when listing

### Using Telegram Bot

The Telegram bot integration allows users to interact with the AI assistant via Telegram:

**Setup:**
1. Create a bot with [@BotFather](https://core.telegram.org/bots#botfather)
2. Set `TELEGRAM_BOT_TOKEN` in your `.env` file
3. Configure `TELEGRAM_ADMIN_IDS` (comma-separated user IDs) or set `TELEGRAM_ALLOW_ALL=true`
4. Start the bot: `python telegram_bot.py`

**Bot Commands:**
- `/start` - Greet the user and register the conversation
- `/help` - Display available commands
- `/status` - Report backend status and message counts
- `/clear` - Clear the conversation history on the backend

**Environment Variables:**
- `TELEGRAM_BOT_TOKEN` - Bot token from BotFather (required)
- `TELEGRAM_ADMIN_IDS` - Comma-separated list of allowed user IDs
- `TELEGRAM_ALLOW_ALL` - Set to "true" to allow all users
- `TELEGRAM_BACKEND_URL` - Backend URL (default: http://localhost:8002)
- `TELEGRAM_CHAT_ENDPOINT` - Chat endpoint path (default: /v1/telegram/chat)
- `TELEGRAM_CHAT_TIMEOUT` - Request timeout in seconds (default: 30)

## Project Structure

```
AI_assistant/
├── model_avatar/          # VRM/Live2D avatar models
│   ├── Eva/              # Eva VRM model and animations
│   ├── Alicia/           # Alicia VRM model
│   └── ...
├── mcp-browser-use/      # MCP Browser-Use submodule
│   ├── pyproject.toml    # UV project configuration
│   └── src/             # Source code
├── libs/                 # Third-party libraries
│   └── ogg-opus-decoder/ # Audio decoder
├── scratch/              # File operations workspace
├── research_output/      # Research tool outputs
├── proxy_server.py       # FastAPI proxy server (port 8002)
├── telegram_bot.py       # Telegram bot integration
├── telegram_bot_minimal_example.py # Minimal Telegram bot example
├── mcp_browser_client.py # MCP browser client wrapper
├── mcp_browser_server.py # MCP browser HTTP server (Flask, port 5001)
├── start_mcp_browser_server.py # Startup script for MCP browser server
├── start_all.py         # Start all services script (Windows)
├── stop_all.py           # Stop all services script (Windows)
├── team-config.json      # AutoGen team configuration
├── mcp_servers.json      # MCP server configurations
├── mcp_config.env.example # Environment variables template
├── telegram_env_example.txt # Telegram bot environment example
├── package.json          # Node.js dependencies
├── index-dev.html        # Web interface (development)
├── recorder-worklet-processor.js # Audio recording worklet
├── test_*.py             # Various test files
└── README.md             # This file
```

## Additional Resources

### Official Documentation

- **Microsoft AutoGen**: https://microsoft.github.io/autogen/
  - GitHub: https://github.com/microsoft/autogen
  - AutoGen Studio: https://github.com/microsoft/autogen-studio

- **Browser-Use**: https://docs.browser-use.com/
  - GitHub: https://github.com/browser-use/browser-use

- **MCP Browser-Use Server**: https://github.com/Saik0s/mcp-browser-use
  - Documentation: See `mcp-browser-use/README.md`

- **Model Context Protocol (MCP)**: https://modelcontextprotocol.io/
  - Python SDK: https://github.com/modelcontextprotocol/python-sdk
  - Node.js SDK: https://github.com/modelcontextprotocol/typescript-sdk

- **UV Package Manager**: https://github.com/astral-sh/uv
  - Documentation: https://docs.astral.sh/uv/

- **Playwright**: https://playwright.dev/python/
  - GitHub: https://github.com/microsoft/playwright

- **FastAPI**: https://fastapi.tiangolo.com/
  - GitHub: https://github.com/tiangolo/fastapi

### Avatar Resources

- **VRoid Studio**: https://vroid.com/studio
- **VRM Specification**: https://github.com/vrm-c/vrm-specification
- **VRM Animation**: https://github.com/vrm-c/vrm-specification/tree/master/specification/VRMC_vrm_animation-1.0
- **Live2D Cubism**: https://www.live2d.com/

### API Services

- **OpenAI API**: https://platform.openai.com/docs
- **Brave Search API**: https://brave.com/search/api/
- **News API**: https://newsapi.org/
- **Telegram Bot API**: https://core.telegram.org/bots/api

## Troubleshooting

### Common Issues

1. **UV Command Not Found**
   ```bash
   pip install uv
   # Or use official installer (see Step 3)
   ```

2. **Playwright Browsers Not Found**
   ```bash
   playwright install
   # Or for uv environment:
   cd mcp-browser-use
   uv run playwright install
   ```

3. **MCP Server Won't Start**
   ```bash
   cd mcp-browser-use
   uv sync
   uv run mcp-server-browser-use --help
   ```

4. **Missing API Keys**
   - Ensure all required API keys are set in `.env` file
   - Verify environment variables are loaded correctly
   - Check `mcp_config.env.example` for all available configuration options

5. **Port Already in Use**
   - Change port numbers in configuration files
   - Or stop the process using the port
   - Use `python stop_all.py` to stop all services on Windows

6. **File Operations Not Working**
   - Ensure file operation libraries are installed: `pip install python-docx openpyxl PyPDF2 reportlab Pillow`
   - Check that files are in the `scratch/` directory
   - Verify file format is supported (txt, docx, xlsx, pdf, png, jpg)

7. **Telegram Bot Not Responding**
   - Verify `TELEGRAM_BOT_TOKEN` is set correctly
   - Check that `TELEGRAM_ADMIN_IDS` is configured or `TELEGRAM_ALLOW_ALL=true`
   - Ensure proxy server is running on port 8002
   - Check bot logs for connection errors

8. **MCP Browser Server Connection Issues**
   - Verify MCP Browser-Use server is running
   - Check environment variables in `.env` file
   - Ensure `MCP_RESEARCH_TOOL_SAVE_DIR` directory exists
   - Review `start_mcp_browser_server.py` output for configuration errors

9. **CORS Errors in Browser**
   - Proxy server includes CORS middleware - ensure it's running
   - Check that requests are going to the correct port (8002 for proxy, 5001 for MCP browser server)
   - Verify browser console for specific CORS error messages

### Getting Help

- Check the installation guide: `INSTALL_GUIDE.md`
- Review MCP Browser-Use README: `mcp-browser-use/README.md`
- Enable debug logging: Set `MCP_SERVER_LOGGING_LEVEL=DEBUG` in `.env`
- Check proxy server logs for API endpoint errors
- Review test files (`test_*.py`) for usage examples
- Check GitHub issues for related projects

### Testing the Installation

Several test files are available to verify functionality:

```bash
# Test file operations
python test_file_operations.py

# Test MCP browser integration
python test_mcp_browser_integration.py

# Test MCP client connection
python test_mcp_client.py

# Test HTTP client
python test_http_client.py

# Test server endpoints
python test_server.py
```

## License

See individual project licenses:
- MCP Browser-Use: MIT (see `mcp-browser-use/LICENSE`)
- AutoGen: MIT (see Microsoft AutoGen repository)
- Browser-Use: MIT (see browser-use repository)

## Contributing

Contributions are welcome! Please ensure:
- Code follows project style guidelines
- Tests are included for new features
- Documentation is updated
- Dependencies are properly listed

---

**Last Updated**: 2024
**Project Version**: 1.0.0

