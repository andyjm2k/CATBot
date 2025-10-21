# MCP Browser-Use Integration - Complete Package

This integration adds powerful browser automation and web research capabilities to your AI assistant using the Model Context Protocol (MCP).

## 📦 What's Included

### Core Files
- **`mcp_browser_client.py`** - Python client wrapper for MCP browser-use server
- **`mcp_browser_server.py`** - HTTP bridge server (Flask) for frontend integration
- **`start_mcp_browser_server.py`** - Convenient startup script with configuration validation
- **`index-dev.html`** - Updated with new tool definitions and handlers

### Configuration
- **`mcp_config.env.example`** - Complete configuration template
- **`.env`** - Your local configuration (create from example)

### Documentation
- **`QUICK_START.md`** - 5-minute setup guide
- **`MCP_BROWSER_INTEGRATION.md`** - Complete integration documentation
- **`MCP_INTEGRATION_README.md`** - This file

### Testing
- **`test_mcp_browser_integration.py`** - Comprehensive unit tests
- **`requirements_mcp_browser.txt`** - Python dependencies

## 🚀 Quick Start

### 1. Install
```bash
pip install -r requirements_mcp_browser.txt
playwright install
```

### 2. Configure
```bash
copy mcp_config.env.example .env
# Edit .env and add your API key
```

### 3. Run
```bash
python start_mcp_browser_server.py
```

### 4. Use
Open your AI assistant and ask it to browse the web or conduct research!

## 🎯 Features

### Browser Agent (`runBrowserAgent`)
Execute browser tasks with natural language:
- Navigate websites
- Fill forms and click buttons
- Extract information
- Multi-step web interactions

**Example prompts:**
- "Go to github.com and find trending repositories"
- "Search Amazon for wireless headphones and show me top results"
- "Extract all links from example.com"

### Deep Research (`runDeepResearch`)
Comprehensive multi-source research:
- Parallel browser instances
- Automatic source tracking
- Markdown report generation
- Configurable depth

**Example prompts:**
- "Research AI developments in 2024"
- "Compare top 5 electric vehicles"
- "What are the health benefits of exercise?"

## 📋 Requirements

- Python 3.10+
- Chrome/Chromium browser
- API key for: Google AI, OpenAI, or Anthropic
- 4GB+ RAM recommended
- Internet connection

## 🏗️ Architecture

```
┌─────────────────┐
│  AI Assistant   │  ← User interface (HTML/JS)
│  (Frontend)     │
└────────┬────────┘
         │ HTTP POST (port 5001)
         ↓
┌─────────────────┐
│  HTTP Bridge    │  ← Flask REST API
│  Server         │
└────────┬────────┘
         │ MCP Protocol (stdio)
         ↓
┌─────────────────┐
│  MCP Browser    │  ← Browser automation engine
│  Use Server     │
└────────┬────────┘
         │ Playwright
         ↓
┌─────────────────┐
│  Browser        │  ← Chrome/Chromium
│  (Headless/GUI) │
└─────────────────┘
```

## 📖 Documentation

- **Getting Started**: Read [QUICK_START.md](QUICK_START.md)
- **Full Guide**: See [MCP_BROWSER_INTEGRATION.md](MCP_BROWSER_INTEGRATION.md)
- **Configuration**: Check `mcp_config.env.example`
- **API Reference**: In full documentation

## 🧪 Testing

### Run Tests
```bash
python test_mcp_browser_integration.py -v
```

### Manual Testing
```bash
# Health check
curl http://127.0.0.1:5001/api/health

# Browser agent
curl -X POST http://127.0.0.1:5001/api/browser-agent \
  -H "Content-Type: application/json" \
  -d '{"task": "Go to example.com"}'

# Deep research
curl -X POST http://127.0.0.1:5001/api/deep-research \
  -H "Content-Type: application/json" \
  -d '{"research_task": "AI trends 2024"}'
```

## 🔧 Configuration Overview

### Minimal Configuration (.env)
```bash
# API Key (choose one)
GOOGLE_API_KEY=your_key_here
# or OPENAI_API_KEY=your_key_here

# Research output directory (required)
MCP_RESEARCH_TOOL_SAVE_DIR=./research_output

# LLM provider
MCP_LLM_PROVIDER=google
MCP_LLM_MODEL_NAME=gemini-2.0-flash-exp
```

### Advanced Options
- Browser settings (headless, security, size)
- Agent configuration (max steps, vision)
- Research settings (parallel browsers)
- Server settings (logging, port)

See `mcp_config.env.example` for all options.

## 🎨 Usage Examples

### From AI Assistant (Natural Language)

Just talk to your assistant naturally:

**Browser Tasks:**
- "Find the latest news about AI"
- "Go to Wikipedia and search for quantum computing"
- "Check the weather forecast for New York"

**Research Tasks:**
- "I need a comprehensive report on renewable energy"
- "Research the best laptops for programming in 2024"
- "What are the latest trends in web development?"

### From Code (Direct API)

```javascript
// Browser automation
fetch('http://127.0.0.1:5001/api/browser-agent', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        task: 'Go to github.com and find trending repos'
    })
});

// Deep research
fetch('http://127.0.0.1:5001/api/deep-research', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        research_task: 'Latest AI developments',
        max_parallel_browsers: 3
    })
});
```

## 🐛 Troubleshooting

### Server won't start
1. Check if Python 3.10+ is installed
2. Verify all dependencies are installed
3. Check `.env` file exists and has required variables

### Browser tasks fail
1. Ensure Playwright is installed: `playwright install`
2. Try non-headless mode: `MCP_BROWSER_HEADLESS=false`
3. Check if port 5001 is available

### Research not working
1. Verify `MCP_RESEARCH_TOOL_SAVE_DIR` is set
2. Check directory permissions
3. Ensure API key has sufficient quota

### Connection errors
1. Confirm server is running: `curl http://127.0.0.1:5001/api/health`
2. Check firewall settings
3. Verify correct port (default: 5001)

## 📁 Project Structure

```
AI_assistant/
├── mcp_browser_client.py          # MCP client wrapper
├── mcp_browser_server.py          # HTTP server
├── start_mcp_browser_server.py    # Startup script
├── test_mcp_browser_integration.py # Unit tests
├── requirements_mcp_browser.txt   # Dependencies
├── mcp_config.env.example         # Config template
├── .env                           # Your config (gitignored)
├── index-dev.html                 # Updated frontend
├── QUICK_START.md                 # Quick guide
├── MCP_BROWSER_INTEGRATION.md     # Full docs
├── MCP_INTEGRATION_README.md      # This file
├── research_output/               # Research reports
└── mcp-browser-use/               # MCP server
    └── src/mcp_server_browser_use/
```

## 🔒 Security Notes

1. **API Keys**: Never commit `.env` file to version control
2. **CORS**: Default allows all origins - restrict in production
3. **Browser Security**: Keep `MCP_BROWSER_DISABLE_SECURITY=false` unless testing
4. **Resource Limits**: Set appropriate limits on parallel browsers
5. **Input Validation**: All inputs are validated before processing

## 🎯 Best Practices

1. **Start with headless mode** for better performance
2. **Limit parallel browsers** to 3-5 to avoid resource issues
3. **Monitor server logs** for troubleshooting
4. **Test simple tasks first** before complex automation
5. **Clean research outputs** periodically
6. **Use vision selectively** to reduce costs
7. **Set appropriate max steps** for your tasks

## 📊 Performance Tips

- **Keep browser open**: `MCP_BROWSER_KEEP_OPEN=true` for repeated tasks
- **Parallel research**: Use `maxParallelBrowsers: 5` for speed
- **Optimize steps**: Reduce `MCP_AGENT_TOOL_MAX_STEPS` for simple tasks
- **Disable vision**: Turn off for text-only tasks
- **Use faster models**: Try `gemini-2.0-flash-exp` for speed

## 🆘 Support

### Resources
- **Full Documentation**: [MCP_BROWSER_INTEGRATION.md](MCP_BROWSER_INTEGRATION.md)
- **Quick Start**: [QUICK_START.md](QUICK_START.md)
- **MCP Browser-Use**: https://github.com/Saik0s/mcp-browser-use

### Debug Steps
1. Check server logs (`MCP_SERVER_LOGGING_LEVEL=DEBUG`)
2. Verify environment configuration
3. Test endpoints with curl
4. Review browser console errors
5. Check GitHub issues

## 📝 License

This integration uses the MCP browser-use project (MIT License).
See https://github.com/Saik0s/mcp-browser-use for details.

## 🎉 What's Next?

1. **Test the integration** with simple browser tasks
2. **Try deep research** on a topic you're interested in
3. **Customize configuration** for your needs
4. **Explore advanced features** (vision, CDP connection, etc.)
5. **Share your feedback** and use cases!

---

## File Descriptions

### Core Implementation

**mcp_browser_client.py** (305 lines)
- Async MCP client wrapper
- Handles stdio communication
- Tool execution methods
- Connection management
- Error handling and logging

**mcp_browser_server.py** (248 lines)
- Flask HTTP server
- REST API endpoints
- Request/response handling
- Environment configuration
- Health check and diagnostics

**start_mcp_browser_server.py** (77 lines)
- Startup script with validation
- Environment variable loading
- Configuration display
- Error checking and reporting

### Frontend Integration

**index-dev.html** (Updated sections)
- Tool definitions for AI model (lines 2424-2462)
- Handler functions (lines 7487-7605)
- HTTP fetch requests to server
- Error handling and user feedback

### Testing

**test_mcp_browser_integration.py** (388 lines)
- Unit tests for MCPBrowserClient
- HTTP endpoint tests
- Mock-based testing
- 70%+ code coverage
- Async test support

### Documentation

**QUICK_START.md**
- 5-minute setup guide
- Minimal configuration
- Common issues and solutions

**MCP_BROWSER_INTEGRATION.md** (Comprehensive)
- Complete architecture overview
- Detailed configuration guide
- Usage examples and API reference
- Troubleshooting guide
- Best practices and security

**MCP_INTEGRATION_README.md** (This file)
- Package overview
- Quick reference
- Project structure

---

## Summary

✅ **Browser automation** with natural language
✅ **Deep research** capabilities
✅ **HTTP REST API** for easy integration
✅ **Comprehensive documentation**
✅ **Unit tests** included
✅ **Easy configuration** with `.env` file
✅ **Production-ready** architecture

**Ready to use!** Start the server and begin automating web tasks with your AI assistant.

For detailed instructions, see [QUICK_START.md](QUICK_START.md) or [MCP_BROWSER_INTEGRATION.md](MCP_BROWSER_INTEGRATION.md).

