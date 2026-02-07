<img src="CATBot_logo.png" alt="CATBot Logo" width="60" height="60" align="center"># CATBot — Personal AI Assistant

<p align="center">
  <strong>Your comprehensive AI assistant with browser automation, speech, and 3D avatars</strong>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="MIT License"></a>
  <a href="https://github.com/microsoft/autogen"><img src="https://img.shields.io/badge/AutoGen-Microsoft-blue?style=for-the-badge" alt="AutoGen"></a>
  <a href="https://modelcontextprotocol.io/"><img src="https://img.shields.io/badge/MCP-Protocol-green?style=for-the-badge" alt="MCP"></a>
</p>

**CATBot** is a _comprehensive AI assistant system_ you run on your own devices. It features browser automation, speech-to-text, text-to-speech, multi-agent collaboration, and 3D avatar integration with VRM/Live2D support. The system provides a unified interface for interacting with AI models through multiple channels and capabilities.

If you want a personal, feature-rich assistant that combines conversational AI, browser automation, and immersive 3D avatars, this is it.

[Installation Guide](INSTALL_GUIDE.md) · [Configuration](#configuration) · [Usage](#usage) · [Troubleshooting](#troubleshooting)

## Quick Start

Runtime: **Node.js ≥16** and **Python ≥3.11**.

```bash
# Clone the repository
git clone <repository-url>
cd AI_assistant

# Install Node.js dependencies
npm install

# Create Python virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install Python dependencies
pip install fastapi uvicorn httpx pydantic python-dotenv
pip install python-docx openpyxl PyPDF2 Pillow reportlab
pip install autogen-agentchat autogen-core autogen-ext
pip install "mcp>=1.6.0" "browser-use==0.1.41" playwright pyperclip
pip install langchain-community langchain-mistralai==0.2.4 langchain-ibm==0.3.10 langchain_mcp_adapters==0.0.9 langgraph==0.3.34
pip install json-repair MainContentExtractor==0.0.4 pydantic-settings typer python-telegram-bot flask flask-cors

# Install Playwright browsers
playwright install

# Set up MCP Browser-Use submodule
cd mcp-browser-use
pip install uv
uv sync
uv run playwright install
cd ..

# Configure environment variables
cp mcp_config.env.example .env
# Edit .env with your API keys

# Start all services
python start_all.py
```

Full setup guide: [Installation Guide](#installation-guide)

## Highlights

- **[Multi-Agent Collaboration](https://github.com/microsoft/autogen)** — Microsoft AutoGen integration for team-based AI interactions
- **[Browser Automation](https://github.com/browser-use/browser-use)** — Autonomous browser agent powered by browser-use and Playwright
- **[Speech Capabilities](https://openai.com/)** — Speech-to-text (Whisper) and text-to-speech (OpenAI-compatible) integration
- **[3D Avatar Support](https://vroid.com/studio)** — VRM and Live2D avatar integration with emotive animations
- **[Model Context Protocol](https://modelcontextprotocol.io/)** — MCP integration for extensible tooling
- **[File Operations](proxy_server.py)** — Read/write support for txt, docx, xlsx, pdf, and images
- **[Web Search](proxy_server.py)** — Brave Search API with DuckDuckGo fallback
- **[Telegram Integration](telegram_bot.py)** — Bot interface for Telegram messaging
- **[Memory System](memory/)** — Vector-based memory storage and retrieval for conversation context

## Prerequisites

### System Requirements

- **Node.js** (v16 or higher) — [Download](https://nodejs.org/)
- **Python** (v3.11 or higher) — [Download](https://www.python.org/downloads/)
- **Chrome/Chromium Browser** — Required for browser automation

### API Keys and Endpoints

1. **OpenAI-Compatible LLM Endpoint**
   - For text generation and chat functionality
   - Environment variable: `OPENAI_API_KEY` or `OPENAI_API_BASE`

2. **OpenAI-Compatible TTS (Text-to-Speech) Endpoint**
   - For converting text to speech
   - Environment variable: `OPENAI_API_KEY` (shared with LLM) or separate TTS endpoint

3. **OpenAI-Compatible Whisper Endpoint (STT)**
   - For converting speech to text
   - Default: `http://localhost:8001/v1/audio/transcriptions`
   - Environment variable: `WHISPER_ENDPOINT`

4. **Brave Search API Key** (Required for web search)
   - Get your key: https://brave.com/search/api/
   - Environment variable: `BRAVE_API_KEY`
   - Note: Falls back to DuckDuckGo if not configured

5. **News API Key** (Optional)
   - Get your key: https://newsapi.org/
   - Can be configured in the application settings UI

6. **Telegram Bot Token** (Optional)
   - Create a bot: https://core.telegram.org/bots#botfather
   - Environment variable: `TELEGRAM_BOT_TOKEN`

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

### Step 3: Install Python Dependencies

#### Option A: Using pip (Recommended)

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

**Resources:**
- [UV Package Manager](https://github.com/astral-sh/uv)
- [MCP Browser-Use](https://github.com/Saik0s/mcp-browser-use)

### Step 4: Configure Environment Variables

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

### Step 5: Set Up Avatar Models

#### VRM Models (VRoid)

1. Download or create VRM models from VRoid Studio
2. Place `.vrm` files in `model_avatar/<model_name>/` directories

**Resources:**
- [VRoid Studio](https://vroid.com/studio)
- [VRM Specification](https://github.com/vrm-c/vrm-specification)

#### VMA Animation Files

1. Download or create VMA (VRM Animation) files
2. Place `.vrma` files alongside VRM models

**Resources:**
- [VRM Animation](https://github.com/vrm-c/vrm-specification/tree/master/specification/VRMC_vrm_animation-1.0)

#### Live2D Models (Alternative)

1. Download Live2D Cubism models
2. Place model files in appropriate directories

**Resources:**
- [Live2D Cubism](https://www.live2d.com/)
- [Live2D SDK](https://www.live2d.com/sdk/)

### Step 6: Create Required Directories

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

### Step 7: Verify Installation

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
- `MCP_BROWSER_HEADLESS`: Run browser in headless mode (true/false)
- `MCP_RESEARCH_TOOL_SAVE_DIR`: Directory for research outputs (required)

#### Service Endpoints
- `WHISPER_ENDPOINT`: Whisper STT service endpoint
- `TTS_ENDPOINT`: TTS service endpoint
- `BRAVE_API_KEY`: Brave Search API key
- `NEWS_API_KEY`: News API key

#### Telegram Bot Configuration
- `TELEGRAM_BOT_TOKEN`: Telegram bot token from BotFather (required)
- `TELEGRAM_ADMIN_IDS`: Comma-separated list of allowed Telegram user IDs
- `TELEGRAM_ALLOW_ALL`: Set to "true" to allow all users (default: false)

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
- [AutoGen Documentation](https://microsoft.github.io/autogen/)
- [AutoGen Studio](https://github.com/microsoft/autogen-studio)

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

#### Option 2: Start Services Individually

```bash
# Start HTTP server
python -m http.server 8000

# Start proxy server
python proxy_server.py

# Start AutoGen Studio
autogenstudio serve --team team-config.json --port 8084

# Start MCP Browser-Use server
cd mcp-browser-use
uv run mcp-server-browser-use

# Start MCP Browser HTTP server
python start_mcp_browser_server.py
```

### Accessing the Application

#### Local Access (localhost)

1. **Web Interface**: Open `index-dev.html` in your browser (served on port 8000)
2. **AutoGen Studio**: Navigate to `http://localhost:8084`
3. **Proxy Server API**: `http://localhost:8002` (FastAPI with comprehensive endpoints)
4. **MCP Browser HTTP Server**: `http://localhost:5001` (Flask-based HTTP bridge)

#### Remote Network Access

All services are configured to accept connections from devices on your local network. To access from a remote device:

1. **Find your server's IP address:**
   - **Windows**: Run `ipconfig` in Command Prompt and look for "IPv4 Address" under your active network adapter
   - **Linux/Mac**: Run `ifconfig` or `ip addr` and look for your network interface IP
   - Example: `192.168.1.100`

2. **Access services from remote devices:**
   - **Web Interface**: `http://<server-ip>:8000` (e.g., `http://192.168.1.100:8000`)
   - **AutoGen Studio**: `http://<server-ip>:8084`
   - **Proxy Server API**: `http://<server-ip>:8002`
   - **MCP Browser HTTP Server**: `http://<server-ip>:5001`

3. **Frontend auto-detection:**
   - The web interface automatically detects if it's being accessed remotely and adjusts API endpoints accordingly
   - You can also manually specify the server IP using a URL parameter: `http://<server-ip>:8000?server=<server-ip>`

4. **Firewall configuration:**
   - Ensure your firewall allows incoming connections on ports: 8000, 8002, 5001, and 8084
   - **Windows Firewall**: Add inbound rules for these ports
   - **Linux**: Use `ufw` or `iptables` to allow the ports

**Security Note**: This configuration allows any device on your local network to access the services. For production use, consider adding authentication or restricting access via firewall rules.

### API Endpoints

#### Proxy Server Endpoints (Port 8002)

**Web Operations:**
- `GET /v1/proxy/fetch` - Fetch web content from a URL
- `GET /v1/proxy/search` - Perform web search (Brave Search or DuckDuckGo fallback)

**AI & Chat:**
- `POST /v1/proxy/autogen` - AutoGen team-based chat endpoint
- `POST /v1/telegram/chat` - Telegram bot chat endpoint
- `DELETE /v1/telegram/chat/{conversation_id}` - Clear Telegram conversation history

**Speech & Audio:**
- `POST /v1/audio/transcriptions` - Whisper STT proxy endpoint
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

- `POST /api/browser-agent` - Execute browser automation task
- `POST /api/deep-research` - Execute deep research task
- `GET /api/health` - Check server health and MCP availability
- `POST /api/disconnect` - Disconnect MCP client

### Using Browser Automation

```bash
# Via HTTP API (MCP Browser HTTP Server)
curl -X POST http://localhost:5001/api/browser-agent \
  -H "Content-Type: application/json" \
  -d '{"task": "Go to example.com and get the page title"}'

# Via Proxy Server MCP endpoints
curl -X POST http://localhost:8002/v1/mcp/servers/browser-use/tools/call \
  -H "Content-Type: application/json" \
  -d '{"toolName": "run_browser_agent", "parameters": {"task": "Your task here"}}'
```

### Using File Operations

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

### Using Telegram Bot

**Setup:**
1. Create a bot with [@BotFather](https://core.telegram.org/bots#botfather)
2. Set `TELEGRAM_BOT_TOKEN` in your `.env` file
3. Configure `TELEGRAM_ADMIN_IDS` or set `TELEGRAM_ALLOW_ALL=true`
4. Start the bot: `python telegram_bot.py`

**Bot Commands:**
- `/start` - Greet the user and register the conversation
- `/help` - Display available commands
- `/status` - Report backend status and message counts
- `/clear` - Clear the conversation history on the backend

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
├── memory/               # Memory system (embeddings, vector store)
├── scratch/              # File operations workspace
├── research_output/      # Research tool outputs
├── proxy_server.py       # FastAPI proxy server (port 8002)
├── telegram_bot.py       # Telegram bot integration
├── start_all.py         # Start all services script (Windows)
├── stop_all.py           # Stop all services script (Windows)
├── team-config.json      # AutoGen team configuration
├── mcp_servers.json      # MCP server configurations
├── mcp_config.env.example # Environment variables template
├── package.json          # Node.js dependencies
├── index-dev.html        # Web interface (development)
└── README.md             # This file
```

## Dependencies

### NPM Packages

| Package | Version | Purpose |
|---------|---------|----------|
| `@langchain/mcp-adapters` | ^0.6.0 | LangChain integration with Model Context Protocol |
| `@modelcontextprotocol/sdk` | ^1.0.0 | Model Context Protocol SDK for Node.js |
| `axios` | ^1.6.2 | HTTP client for API requests |
| `cors` | ^2.8.5 | Cross-Origin Resource Sharing middleware |
| `express` | ^4.18.2 | Web server framework |
| `ogg-opus-decoder` | ^1.7.3 | Audio decoder for Opus codec |

### Python Packages

See [Installation Guide](#step-3-install-python-dependencies) for complete list of Python dependencies.

## Additional Resources

### Official Documentation

- **[Microsoft AutoGen](https://microsoft.github.io/autogen/)** — Multi-agent collaboration framework
  - GitHub: https://github.com/microsoft/autogen
  - AutoGen Studio: https://github.com/microsoft/autogen-studio

- **[Browser-Use](https://docs.browser-use.com/)** — Autonomous browser automation
  - GitHub: https://github.com/browser-use/browser-use

- **[MCP Browser-Use Server](https://github.com/Saik0s/mcp-browser-use)** — MCP integration for browser-use

- **[Model Context Protocol (MCP)](https://modelcontextprotocol.io/)** — Protocol for AI tool integration
  - Python SDK: https://github.com/modelcontextprotocol/python-sdk
  - Node.js SDK: https://github.com/modelcontextprotocol/typescript-sdk

- **[UV Package Manager](https://github.com/astral-sh/uv)** — Fast Python package manager
  - Documentation: https://docs.astral.sh/uv/

- **[Playwright](https://playwright.dev/python/)** — Browser automation framework
  - GitHub: https://github.com/microsoft/playwright

- **[FastAPI](https://fastapi.tiangolo.com/)** — Modern web framework
  - GitHub: https://github.com/tiangolo/fastapi

### Avatar Resources

- **[VRoid Studio](https://vroid.com/studio)** — Create 3D avatars
- **[VRM Specification](https://github.com/vrm-c/vrm-specification)** — VRM format documentation
- **[VRM Animation](https://github.com/vrm-c/vrm-specification/tree/master/specification/VRMC_vrm_animation-1.0)** — Animation format
- **[Live2D Cubism](https://www.live2d.com/)** — 2D avatar platform

### API Services

- **[OpenAI API](https://platform.openai.com/docs)** — LLM and TTS services
- **[Brave Search API](https://brave.com/search/api/)** — Web search
- **[News API](https://newsapi.org/)** — News aggregation
- **[Telegram Bot API](https://core.telegram.org/bots/api)** — Telegram integration

## Troubleshooting

### Common Issues

1. **UV Command Not Found**
   ```bash
   pip install uv
   # Or use official installer (see Installation Guide)
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
