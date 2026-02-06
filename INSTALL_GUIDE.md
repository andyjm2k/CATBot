# Installation Guide - MCP Browser-Use Integration

Complete installation instructions following the official mcp-browser-use project setup.

## Prerequisites

- **Python 3.10+** - Check with `python --version`
- **Node.js 16+** (optional, for MCP inspector) - Check with `node --version`
- **Chrome/Chromium browser**
- **API Key** - For Google AI, OpenAI, or Anthropic

## Step 1: Install UV Package Manager

The mcp-browser-use project uses `uv` as its package manager. Install it first:

### Option A: Using pip (Recommended)
```bash
pip install uv
```

### Option B: Using official installer
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Verify installation
```bash
uv --version
```

## Step 2: Install MCP Browser-Use Server

The server is already cloned in your `mcp-browser-use/` directory. Install its dependencies:

```bash
# Navigate to the mcp-browser-use directory
cd mcp-browser-use

# Sync dependencies using uv
uv sync

# Install Playwright browsers
uv run playwright install
```

### Verify MCP server installation
```bash
# Test the server directly
uv run mcp-server-browser-use --help
```

You should see the help output for the mcp-server-browser-use command.

## Step 3: Install Integration Dependencies

Return to your project root and install the HTTP bridge server dependencies:

```bash
# Return to project root
cd ..

# Install Python dependencies (includes uv if not already installed)
pip install -r requirements_mcp_browser.txt

# Install Playwright browsers for your Python environment
playwright install
```

## Step 4: Configure Environment

### Create configuration file
```bash
# Copy the example configuration
copy mcp_config.env.example .env    # Windows
# or
cp mcp_config.env.example .env      # Linux/Mac
```

### Edit .env file

Open `.env` in a text editor and configure:

**Required settings:**
```bash
# Your API key (choose one provider)
GOOGLE_API_KEY=your_actual_api_key_here
# or
# OPENAI_API_KEY=your_actual_api_key_here
# or
# ANTHROPIC_API_KEY=your_actual_api_key_here

# LLM Configuration
MCP_LLM_PROVIDER=google
MCP_LLM_MODEL_NAME=gemini-2.0-flash-exp

# Research output directory (REQUIRED)
MCP_RESEARCH_TOOL_SAVE_DIR=./research_output

# Browser settings
MCP_BROWSER_HEADLESS=true
```

**Optional settings:**
```bash
# MCP Browser-Use directory (auto-detected if in default location)
MCP_BROWSER_USE_DIR=./mcp-browser-use

# HTTP Server settings
PORT=5001
HOST=127.0.0.1

# Agent configuration
MCP_AGENT_TOOL_MAX_STEPS=100
MCP_AGENT_TOOL_USE_VISION=true

# Research configuration
MCP_RESEARCH_TOOL_MAX_PARALLEL_BROWSERS=3
```

### Load environment variables

**Windows PowerShell:**
```powershell
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
    }
}
```

**Linux/Mac:**
```bash
export $(cat .env | xargs)
```

## Step 5: Create Required Directories

```bash
# Create research output directory
mkdir research_output

# Create directories for optional features (if enabled)
# mkdir recordings       # If MCP_AGENT_TOOL_ENABLE_RECORDING=true
# mkdir agent_history    # If MCP_AGENT_TOOL_HISTORY_PATH is set
# mkdir traces          # If MCP_BROWSER_TRACE_PATH is set
```

## Step 6: Verify Installation

### Test 1: UV Command
```bash
uv --version
```
Should display uv version number.

### Test 2: MCP Server
```bash
cd mcp-browser-use
uv run mcp-server-browser-use --help
cd ..
```
Should display help text without errors.

### Test 3: Python Dependencies
```bash
python -c "import mcp; print('MCP OK')"
python -c "import flask; print('Flask OK')"
python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
```
All should print "OK" messages.

### Test 4: Start HTTP Server
```bash
python start_mcp_browser_server.py
```

Expected output:
```
Loading environment from: .env
Using LLM Provider: google, Model: gemini-2.0-flash-exp
Research output directory: ./research_output

==================================================
MCP Browser HTTP Server Configuration
==================================================
LLM Provider: google
Model: gemini-2.0-flash-exp
Browser Headless: true
Keep Browser Open: false
Max Parallel Browsers: 3
Server Port: 5001
Server Host: 127.0.0.1
==================================================

Starting MCP Browser HTTP Server on 127.0.0.1:5001
Available endpoints:
  POST /api/browser-agent - Execute browser automation task
  POST /api/deep-research - Execute deep research task
  GET  /api/health - Check server health
  POST /api/disconnect - Disconnect MCP client
```

### Test 5: Health Check

In a new terminal:
```bash
curl http://127.0.0.1:5001/api/health
```

Expected response:
```json
{"status": "healthy", "mcp_connected": false}
```

### Test 6: Simple Browser Task

```bash
curl -X POST http://127.0.0.1:5001/api/browser-agent \
  -H "Content-Type: application/json" \
  -d "{\"task\": \"Go to example.com and get the page title\"}"
```

Expected: Success response with page title information.

## Step 7: Frontend Integration

1. **Open CATBot**: Open `index-dev.html` in a web browser
2. **Check console**: Open browser DevTools (F12) and check for errors
3. **Test with assistant**: Ask "Go to example.com and tell me about the page"

## Troubleshooting Installation Issues

### UV Not Found

**Problem**: `uv: command not found`

**Solutions**:
- Install uv: `pip install uv`
- Verify PATH includes Python scripts directory
- Restart terminal after installation

### MCP Server Won't Start

**Problem**: `mcp-server-browser-use: command not found`

**Solutions**:
```bash
# Navigate to mcp-browser-use directory
cd mcp-browser-use

# Sync dependencies
uv sync

# Try running directly
uv run python -m mcp_server_browser_use
```

### Playwright Installation Issues

**Problem**: Browser binaries not found

**Solutions**:
```bash
# Install Playwright browsers for uv environment
cd mcp-browser-use
uv run playwright install

# Install Playwright browsers for system Python
cd ..
playwright install

# Install specific browser
playwright install chromium
```

### Environment Variables Not Loading

**Problem**: Server reports missing API key

**Solutions**:
- Verify `.env` file exists in project root
- Check file has correct format (KEY=value, no quotes needed)
- Manually set environment variable:
  ```bash
  # Windows
  set GOOGLE_API_KEY=your_key_here
  
  # Linux/Mac
  export GOOGLE_API_KEY=your_key_here
  ```

### Port Already in Use

**Problem**: `Address already in use: 5001`

**Solutions**:
```bash
# Windows - Find process using port
netstat -ano | findstr :5001
# Kill process (replace PID)
taskkill /PID <pid> /F

# Linux/Mac - Find and kill process
lsof -ti:5001 | xargs kill -9

# Or change port in .env
echo "PORT=5002" >> .env
```

### Permission Denied

**Problem**: Cannot create directories or write files

**Solutions**:
- Run terminal as administrator (Windows) or use sudo (Linux/Mac)
- Check directory permissions
- Choose different output directory with write access

## Architecture Overview

After installation, your setup looks like this:

```
Project Root/
├── .env                          ← Your configuration
├── mcp_browser_client.py         ← MCP client wrapper (uses uv)
├── mcp_browser_server.py         ← HTTP bridge server
├── start_mcp_browser_server.py   ← Startup script
├── index-dev.html                ← Frontend with tools
└── mcp-browser-use/              ← MCP server (uses uv)
    ├── pyproject.toml            ← UV project file
    ├── uv.lock                   ← UV lockfile
    └── src/mcp_server_browser_use/
```

## UV vs Traditional Python

This integration uses **uv** because:

1. ✅ **Official approach** - Matches mcp-browser-use project
2. ✅ **Better dependency management** - Isolated environments
3. ✅ **Faster installation** - Parallel downloads
4. ✅ **Reproducible builds** - Lockfile ensures consistency

### How UV is Used

The integration runs the MCP server with:
```bash
uv --directory ./mcp-browser-use run mcp-server-browser-use
```

This tells uv to:
- Use the project in `./mcp-browser-use` directory
- Run the `mcp-server-browser-use` command
- Use dependencies from `pyproject.toml` and `uv.lock`

### Fallback to Standard Python

If you prefer not to use uv, you can disable it:

```python
# In your code
client = MCPBrowserClient(
    env_vars=config,
    use_uv=False  # Use standard Python instead
)
```

However, this is **not recommended** as it may have compatibility issues.

## Post-Installation

### Next Steps

1. ✅ **Run tests**: `python test_mcp_browser_integration.py -v`
2. ✅ **Try browser task**: Ask assistant to navigate a website
3. ✅ **Try research**: Ask assistant to research a topic
4. ✅ **Read full docs**: See `MCP_BROWSER_INTEGRATION.md`
5. ✅ **Customize config**: Edit `.env` for your needs

### Updating Dependencies

```bash
# Update uv itself
pip install --upgrade uv

# Update mcp-browser-use dependencies
cd mcp-browser-use
uv sync --upgrade

# Update integration dependencies
cd ..
pip install --upgrade -r requirements_mcp_browser.txt
```

### Verifying Everything Works

Run this checklist:
- [ ] `uv --version` works
- [ ] `python start_mcp_browser_server.py` starts without errors
- [ ] `curl http://127.0.0.1:5001/api/health` returns healthy
- [ ] Browser task completes successfully
- [ ] Research generates a report
- [ ] Frontend can communicate with server

## Support

If you encounter issues:

1. Check `INTEGRATION_CHECKLIST.md` for verification steps
2. Review `TROUBLESHOOTING.md` (if available)
3. Enable debug logging: `MCP_SERVER_LOGGING_LEVEL=DEBUG`
4. Check GitHub issues: https://github.com/Saik0s/mcp-browser-use/issues

## Summary

✅ **Installed uv package manager**
✅ **Installed mcp-browser-use server with uv**
✅ **Installed integration dependencies**
✅ **Configured environment variables**
✅ **Created required directories**
✅ **Verified all components work**

Your MCP browser integration is now ready to use! 🚀

