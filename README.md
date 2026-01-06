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

4. **Brave Search API Key** (Optional but recommended)
   - For web search functionality
   - Get your key: https://brave.com/search/api/
   - Environment variable: `BRAVE_API_KEY`

5. **News API Key** (Optional)
   - For news aggregation features
   - Get your key: https://newsapi.org/
   - Environment variable: `NEWS_API_KEY`

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
pip install json-repair MainContentExtractor==0.0.4 pydantic-settings typer python-telegram-bot

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
- `MCP_LLM_PROVIDER`: LLM provider (openai, google, anthropic, etc.)
- `MCP_LLM_MODEL_NAME`: Specific model name
- `MCP_BROWSER_HEADLESS`: Run browser in headless mode (true/false)
- `MCP_RESEARCH_TOOL_SAVE_DIR`: Directory for research outputs

#### Service Endpoints
- `WHISPER_ENDPOINT`: Whisper STT service endpoint
- `TTS_ENDPOINT`: TTS service endpoint
- `BRAVE_API_KEY`: Brave Search API key
- `NEWS_API_KEY`: News API key

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
```

### Accessing the Application

1. **Web Interface**: Open `index-stable.html` or `index-dev.html` in your browser
2. **AutoGen Studio**: Navigate to `http://localhost:8084`
3. **Proxy Server API**: `http://localhost:8002`
4. **MCP Browser Server**: `http://localhost:5001`

### Using Browser Automation

The browser automation features are accessible through the MCP Browser-Use integration:

```bash
# Via HTTP API
curl -X POST http://localhost:5001/api/browser-agent \
  -H "Content-Type: application/json" \
  -d '{"task": "Go to example.com and get the page title"}'

# Via MCP tools in the frontend
# Use the browser automation tool in the web interface
```

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
├── proxy_server.py       # FastAPI proxy server
├── telegram_bot.py        # Telegram bot integration
├── mcp_browser_client.py # MCP browser client wrapper
├── mcp_browser_server.py # MCP browser HTTP server
├── start_all.py          # Start all services script
├── team-config.json      # AutoGen team configuration
├── mcp_servers.json      # MCP server configurations
├── package.json          # Node.js dependencies
├── mcp_config.env.example # Environment variables template
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

5. **Port Already in Use**
   - Change port numbers in configuration files
   - Or stop the process using the port

### Getting Help

- Check the installation guide: `INSTALL_GUIDE.md`
- Review MCP Browser-Use README: `mcp-browser-use/README.md`
- Enable debug logging: Set `MCP_SERVER_LOGGING_LEVEL=DEBUG` in `.env`
- Check GitHub issues for related projects

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

