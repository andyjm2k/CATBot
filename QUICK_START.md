# Quick Start Guide - MCP Browser Integration

Get up and running with MCP browser tools in 5 minutes!

## Prerequisites

- Python 3.10+
- Chrome/Chromium browser
- API key for Google AI, OpenAI, or Anthropic

## Installation (One-Time Setup)

### Step 1: Install UV and Dependencies

```bash
# Install uv package manager (REQUIRED)
pip install uv

# Install Python packages
pip install -r requirements_mcp_browser.txt

# Install MCP browser-use server dependencies
cd mcp-browser-use
uv sync
uv run playwright install
cd ..

# Install Playwright browsers for your environment
playwright install
```

### Step 2: Configure Environment

```bash
# Copy the example configuration
copy mcp_config.env.example .env

# Edit .env and add your API key
notepad .env
```

**Minimal .env configuration:**
```bash
# Add your API key
GOOGLE_API_KEY=your_api_key_here

# Or for OpenAI
# OPENAI_API_KEY=your_api_key_here

# Required: Research output directory
MCP_RESEARCH_TOOL_SAVE_DIR=./research_output
```

## Running the Server

### Method 1: Using Startup Script (Recommended)

```bash
python start_mcp_browser_server.py
```

### Method 2: Direct Server Launch

```bash
python mcp_browser_server.py
```

You should see:
```
Starting MCP Browser HTTP Server on 127.0.0.1:5001
Available endpoints:
  POST /api/browser-agent - Execute browser automation task
  POST /api/deep-research - Execute deep research task
  GET  /api/health - Check server health
```

## Using with Your AI Assistant

1. **Open your AI assistant** (`index-dev.html`)
2. **Talk naturally** - the assistant will use the tools automatically!

### Example Prompts

**Browser Automation:**
- "Go to github.com and tell me about trending repositories"
- "Search Google for 'best coffee shops near me' and summarize results"
- "Navigate to example.com and extract all the links"

**Deep Research:**
- "Research the latest AI developments in 2024"
- "Compare the top 5 electric vehicles available"
- "What are the health benefits of meditation? Give me a detailed report"

## Verification

### Test 1: Health Check
```bash
curl http://127.0.0.1:5001/api/health
```

Expected: `{"status": "healthy", "mcp_connected": false}`

### Test 2: Simple Browser Task
```bash
curl -X POST http://127.0.0.1:5001/api/browser-agent \
  -H "Content-Type: application/json" \
  -d "{\"task\": \"Go to example.com and get the page title\"}"
```

## Common Issues

### "Connection refused"
→ Server is not running. Start it with `python start_mcp_browser_server.py`

### "API key not found"
→ Add your API key to `.env` file

### "Missing MCP_RESEARCH_TOOL_SAVE_DIR"
→ Add `MCP_RESEARCH_TOOL_SAVE_DIR=./research_output` to `.env`

### "Playwright browser not found"
→ Run `playwright install`

## Next Steps

- Read full documentation: [MCP_BROWSER_INTEGRATION.md](MCP_BROWSER_INTEGRATION.md)
- Customize configuration in `.env`
- Try advanced features (vision, parallel browsers, etc.)
- Check research reports in `./research_output/`

## Getting Help

1. Check server logs for errors
2. Verify `.env` configuration
3. Review [MCP_BROWSER_INTEGRATION.md](MCP_BROWSER_INTEGRATION.md)
4. Test endpoints with curl commands above

## Architecture Quick Reference

```
Your AI Assistant (HTML)
    ↓ HTTP
MCP Browser Server (Python) - Port 5001
    ↓ MCP Protocol
Browser-Use MCP Server
    ↓
Playwright/Chrome Browser
```

---

**Ready to automate!** 🚀

Start the server and ask your assistant to browse the web or conduct research!

