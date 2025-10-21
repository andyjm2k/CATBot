# MCP Browser-Use Integration Guide

Complete guide for integrating MCP browser-use tools (`run_browser_agent` and `run_deep_research`) into your AI assistant.

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)
8. [API Reference](#api-reference)

---

## Overview

This integration adds powerful browser automation and deep research capabilities to your AI assistant using the MCP (Model Context Protocol) browser-use server.

### Features

- **Browser Automation** (`runBrowserAgent`): Execute complex web tasks using natural language
  - Navigate websites, fill forms, click buttons
  - Extract information from web pages
  - Multi-step web interactions with AI guidance
  
- **Deep Research** (`runDeepResearch`): Comprehensive multi-source research
  - Parallel browser instances for faster research
  - Automatic citation and source tracking
  - Markdown report generation with findings

---

## Architecture

The integration consists of three main components:

```
┌─────────────────┐
│  Frontend HTML  │ ← User interacts with assistant
│  (index-dev.html)│
└────────┬────────┘
         │ HTTP POST
         ↓
┌─────────────────┐
│  HTTP Server    │ ← Flask server bridges HTTP to MCP
│  (port 5001)    │
└────────┬────────┘
         │ MCP Protocol (stdio)
         ↓
┌─────────────────┐
│  MCP Browser    │ ← Browser-use MCP server
│  Server         │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Browser        │ ← Playwright/Chrome automation
│  (Headless/GUI) │
└─────────────────┘
```

### Component Details

1. **Frontend (index-dev.html)**
   - Tool definitions for AI model
   - Handler functions for HTTP requests
   - User interface integration

2. **HTTP Bridge Server (mcp_browser_server.py)**
   - Flask REST API endpoints
   - MCP protocol communication
   - Request/response translation

3. **MCP Client Wrapper (mcp_browser_client.py)**
   - Async MCP client implementation
   - Tool execution methods
   - Connection management

4. **MCP Browser-Use Server**
   - Browser automation engine
   - Deep research orchestration
   - LLM integration for decision-making

---

## Installation

### Prerequisites

- Python 3.10 or higher
- Node.js (for MCP inspector, optional)
- Chrome/Chromium browser
- Existing AI assistant setup

### Step 1: Install Python Dependencies

```bash
# Navigate to your AI assistant directory
cd C:\Users\andyj\AI_assistant

# Install required packages
pip install flask flask-cors mcp anthropic openai google-generativeai playwright

# Install Playwright browsers
playwright install
```

### Step 2: Install MCP Browser-Use Server

The server is already included in your `mcp-browser-use/` directory. To verify:

```bash
# Test the installation
cd mcp-browser-use
python -m mcp_server_browser_use --help
```

### Step 3: Verify File Structure

Ensure these files are in your project root:

```
AI_assistant/
├── mcp_browser_client.py          # MCP client wrapper
├── mcp_browser_server.py          # HTTP server
├── mcp_config.env.example         # Configuration template
├── test_mcp_browser_integration.py # Unit tests
├── index-dev.html                 # Updated with new tools
└── mcp-browser-use/               # MCP server directory
```

---

## Configuration

### Step 1: Create Configuration File

Copy the example configuration:

```bash
# Create your .env file from the example
copy mcp_config.env.example .env
```

### Step 2: Configure Environment Variables

Edit `.env` file with your settings:

```bash
# Required: API Key for your LLM provider
GOOGLE_API_KEY=your_actual_google_api_key_here

# Or for OpenAI
# OPENAI_API_KEY=your_openai_key_here

# LLM Configuration
MCP_LLM_PROVIDER=google
MCP_LLM_MODEL_NAME=gemini-2.0-flash-exp

# Browser Settings
MCP_BROWSER_HEADLESS=true
MCP_BROWSER_KEEP_OPEN=false

# Research Output Directory (REQUIRED for deep research)
MCP_RESEARCH_TOOL_SAVE_DIR=./research_output

# Agent Configuration
MCP_AGENT_TOOL_MAX_STEPS=100
MCP_AGENT_TOOL_USE_VISION=true

# HTTP Server
PORT=5001
HOST=127.0.0.1
```

### Step 3: Load Environment Variables

The server automatically loads environment variables. To manually load:

```bash
# Windows PowerShell
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
    }
}

# Linux/Mac
export $(cat .env | xargs)
```

---

## Usage

### Starting the Integration

#### 1. Start the HTTP Bridge Server

Open a terminal and run:

```bash
# From your AI_assistant directory
python mcp_browser_server.py
```

You should see:

```
INFO:mcp_browser_server:Starting MCP Browser HTTP Server on 127.0.0.1:5001
INFO:mcp_browser_server:Available endpoints:
INFO:mcp_browser_server:  POST /api/browser-agent - Execute browser automation task
INFO:mcp_browser_server:  POST /api/deep-research - Execute deep research task
INFO:mcp_browser_server:  GET  /api/health - Check server health
```

#### 2. Open Your AI Assistant

Open `index-dev.html` in your web browser.

### Using the Tools

#### Browser Agent Examples

Ask your assistant:

- "Go to github.com and find the trending repositories"
- "Navigate to amazon.com and search for wireless headphones, then tell me the top 3 results"
- "Visit example.com and extract all the links on the page"
- "Fill out the contact form on example.com with name 'Test User' and email 'test@example.com'"

The assistant will automatically use the `runBrowserAgent` tool to execute these tasks.

#### Deep Research Examples

Ask your assistant:

- "Research the latest developments in quantum computing"
- "What are the best electric vehicles available in 2024? Give me a comprehensive comparison."
- "Research the health benefits of Mediterranean diet with scientific sources"
- "Compare the top 5 project management tools for small teams"

The assistant will use the `runDeepResearch` tool to:
1. Break down the research into subtasks
2. Execute parallel web searches
3. Gather information from multiple sources
4. Generate a comprehensive markdown report

### Advanced Usage

#### Controlling Research Depth

You can specify the number of parallel browsers:

```javascript
// In your custom code
await handleDeepResearch({
    researchTask: "Your research topic",
    maxParallelBrowsers: 5  // Use more browsers for faster research
});
```

#### Viewing Research Reports

Research reports are saved to the directory specified in `MCP_RESEARCH_TOOL_SAVE_DIR`:

```bash
# View latest research report
cd research_output
ls -lt  # List by most recent
```

---

## Testing

### Running Unit Tests

```bash
# Run all tests
python test_mcp_browser_integration.py

# Run with verbose output
python test_mcp_browser_integration.py -v

# Run specific test class
python -m unittest test_mcp_browser_integration.TestMCPBrowserClient

# Run specific test method
python -m unittest test_mcp_browser_integration.TestMCPBrowserClient.test_connect_success
```

### Manual Testing

#### Test 1: Health Check

```bash
curl http://127.0.0.1:5001/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "mcp_connected": false
}
```

#### Test 2: Browser Agent

```bash
curl -X POST http://127.0.0.1:5001/api/browser-agent \
  -H "Content-Type: application/json" \
  -d '{"task": "Go to example.com and get the page title"}'
```

#### Test 3: Deep Research

```bash
curl -X POST http://127.0.0.1:5001/api/deep-research \
  -H "Content-Type: application/json" \
  -d '{
    "research_task": "What are the benefits of TypeScript?",
    "max_parallel_browsers": 2
  }'
```

### Testing from Frontend

Open browser console in your AI assistant and run:

```javascript
// Test browser agent
fetch('http://127.0.0.1:5001/api/browser-agent', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({task: 'Go to example.com'})
}).then(r => r.json()).then(console.log);

// Test deep research
fetch('http://127.0.0.1:5001/api/deep-research', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({research_task: 'AI trends 2024'})
}).then(r => r.json()).then(console.log);
```

---

## Troubleshooting

### Common Issues

#### 1. "Connection refused" Error

**Problem**: HTTP server is not running.

**Solution**:
```bash
# Start the server
python mcp_browser_server.py

# Check if port is in use
netstat -an | findstr 5001  # Windows
lsof -i :5001              # Linux/Mac
```

#### 2. "MCP server failed to start"

**Problem**: Environment variables not configured or MCP server issues.

**Solutions**:
- Verify API key is set: `echo %GOOGLE_API_KEY%` (Windows) or `echo $GOOGLE_API_KEY` (Linux/Mac)
- Check MCP server installation: `python -m mcp_server_browser_use`
- Review server logs for specific errors

#### 3. "Research tool save directory not configured"

**Problem**: `MCP_RESEARCH_TOOL_SAVE_DIR` not set.

**Solution**:
```bash
# Set the environment variable
export MCP_RESEARCH_TOOL_SAVE_DIR=./research_output

# Or add to .env file
echo "MCP_RESEARCH_TOOL_SAVE_DIR=./research_output" >> .env
```

#### 4. Browser Automation Fails

**Problem**: Browser not launching or tasks timing out.

**Solutions**:
- Ensure Playwright is installed: `playwright install`
- Try non-headless mode: Set `MCP_BROWSER_HEADLESS=false`
- Increase max steps: `MCP_AGENT_TOOL_MAX_STEPS=200`
- Check browser binary path: `MCP_BROWSER_BINARY_PATH=/path/to/chrome`

#### 5. "Unknown tool" Error

**Problem**: Tool names don't match between frontend and handlers.

**Solution**: Verify tool names in `index-dev.html`:
- Tool definition: `name: "runBrowserAgent"`
- Case statement: `case "runBrowserAgent":`
- Handler function: `async function handleBrowserAgent`

### Debug Mode

Enable detailed logging:

```bash
# Set debug level
export MCP_SERVER_LOGGING_LEVEL=DEBUG

# Run server with output
python mcp_browser_server.py
```

### Getting Help

1. Check server logs
2. Review browser console for frontend errors
3. Test endpoints with curl
4. Verify environment configuration
5. Check GitHub issues: https://github.com/Saik0s/mcp-browser-use/issues

---

## API Reference

### HTTP Endpoints

#### POST /api/browser-agent

Execute a browser automation task.

**Request Body**:
```json
{
  "task": "string (required) - Natural language task description"
}
```

**Response**:
```json
{
  "success": true,
  "result": "Task result text"
}
```

**Example**:
```bash
curl -X POST http://127.0.0.1:5001/api/browser-agent \
  -H "Content-Type: application/json" \
  -d '{"task": "Go to github.com and list trending repos"}'
```

---

#### POST /api/deep-research

Execute a deep research task.

**Request Body**:
```json
{
  "research_task": "string (required) - Research topic",
  "max_parallel_browsers": 3  // optional, default: 3, max: 5
}
```

**Response**:
```json
{
  "success": true,
  "result": "Markdown formatted research report"
}
```

**Example**:
```bash
curl -X POST http://127.0.0.1:5001/api/deep-research \
  -H "Content-Type: application/json" \
  -d '{
    "research_task": "Compare React vs Vue.js",
    "max_parallel_browsers": 4
  }'
```

---

#### GET /api/health

Check server health status.

**Response**:
```json
{
  "status": "healthy",
  "mcp_connected": true
}
```

---

#### POST /api/disconnect

Manually disconnect MCP client (useful for reconnecting with new config).

**Response**:
```json
{
  "success": true,
  "message": "Disconnected successfully"
}
```

---

### Frontend Tool Definitions

#### runBrowserAgent

```javascript
{
    type: "function",
    function: {
        name: "runBrowserAgent",
        description: "Executes browser automation tasks using natural language",
        parameters: {
            type: "object",
            properties: {
                task: {
                    type: "string",
                    description: "Natural language description of the browser task"
                }
            },
            required: ["task"]
        }
    }
}
```

#### runDeepResearch

```javascript
{
    type: "function",
    function: {
        name: "runDeepResearch",
        description: "Performs comprehensive multi-step web research",
        parameters: {
            type: "object",
            properties: {
                researchTask: {
                    type: "string",
                    description: "The research topic or question"
                },
                maxParallelBrowsers: {
                    type: "number",
                    description: "Optional: Max parallel browser instances (1-5)"
                }
            },
            required: ["researchTask"]
        }
    }
}
```

---

## Environment Variables Reference

### LLM Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_LLM_PROVIDER` | LLM provider (google, openai, anthropic, etc.) | google |
| `MCP_LLM_MODEL_NAME` | Model name to use | gemini-2.0-flash-exp |
| `MCP_LLM_GOOGLE_API_KEY` | Google AI API key | - |
| `MCP_LLM_OPENAI_API_KEY` | OpenAI API key | - |
| `MCP_LLM_ANTHROPIC_API_KEY` | Anthropic API key | - |

### Browser Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_BROWSER_HEADLESS` | Run browser in headless mode | true |
| `MCP_BROWSER_KEEP_OPEN` | Keep browser open between requests | false |
| `MCP_BROWSER_DISABLE_SECURITY` | Disable browser security features | false |
| `MCP_BROWSER_WINDOW_WIDTH` | Browser window width | 1280 |
| `MCP_BROWSER_WINDOW_HEIGHT` | Browser window height | 1100 |

### Agent Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_AGENT_TOOL_MAX_STEPS` | Max steps per task | 100 |
| `MCP_AGENT_TOOL_MAX_ACTIONS_PER_STEP` | Max actions per step | 5 |
| `MCP_AGENT_TOOL_USE_VISION` | Enable screenshot analysis | true |

### Research Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_RESEARCH_TOOL_MAX_PARALLEL_BROWSERS` | Max parallel browsers | 3 |
| `MCP_RESEARCH_TOOL_SAVE_DIR` | Research output directory | (required) |

### Server Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_SERVER_LOGGING_LEVEL` | Logging level | INFO |
| `PORT` | HTTP server port | 5001 |
| `HOST` | HTTP server host | 127.0.0.1 |

---

## Best Practices

1. **Keep Browser Headless**: Set `MCP_BROWSER_HEADLESS=true` in production for better performance
2. **Limit Parallel Browsers**: Use 3-5 max to avoid resource exhaustion
3. **Monitor Logs**: Check server logs regularly for issues
4. **Secure API Keys**: Never commit API keys to version control
5. **Test Incrementally**: Test browser automation with simple tasks first
6. **Clean Up Research**: Periodically clean old research reports
7. **Use Vision Sparingly**: Vision analysis increases token usage and costs

---

## Performance Tips

1. **Persistent Connection**: Set `MCP_BROWSER_KEEP_OPEN=true` for repeated tasks
2. **Parallel Research**: Use `maxParallelBrowsers: 5` for faster research
3. **Optimize Steps**: Reduce `MCP_AGENT_TOOL_MAX_STEPS` for simpler tasks
4. **Cache Results**: Store frequently accessed research results
5. **Selective Vision**: Disable vision for text-only tasks

---

## Security Considerations

1. **API Key Protection**: Store API keys in `.env`, never in code
2. **CORS Configuration**: Restrict CORS in production
3. **Input Validation**: All inputs are validated before processing
4. **Browser Security**: Keep `MCP_BROWSER_DISABLE_SECURITY=false` unless testing
5. **Resource Limits**: Set appropriate limits on parallel browsers and steps
6. **Network Isolation**: Consider running in isolated environment

---

## License

This integration uses the MCP browser-use project which is licensed under MIT License.
See https://github.com/Saik0s/mcp-browser-use for details.

---

## Support

For issues and questions:
- MCP Browser-Use: https://github.com/Saik0s/mcp-browser-use/issues
- Check logs: `MCP_SERVER_LOGGING_LEVEL=DEBUG`
- Review this documentation
- Test with minimal configuration first

---

## Changelog

### Version 1.0.0 (2024)
- Initial integration
- Browser agent tool support
- Deep research tool support
- HTTP bridge server
- Comprehensive testing suite
- Full documentation

