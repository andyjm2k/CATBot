# MCP Browser Integration - Setup Checklist

Use this checklist to ensure your integration is properly configured and working.

## ✅ Pre-Installation Checklist

- [ ] Python 3.10 or higher is installed
  - Check: `python --version`
- [ ] Chrome or Chromium browser is available
- [ ] You have an API key for Google AI, OpenAI, or Anthropic
- [ ] At least 4GB RAM available
- [ ] Internet connection is active

## ✅ Installation Checklist

- [ ] Install Python dependencies
  ```bash
  pip install -r requirements_mcp_browser.txt
  ```
  
- [ ] Install Playwright browsers
  ```bash
  playwright install
  ```
  
- [ ] Verify installations
  ```bash
  python -c "import mcp; print('MCP installed')"
  python -c "import flask; print('Flask installed')"
  python -c "from playwright.sync_api import sync_playwright; print('Playwright installed')"
  ```

## ✅ Configuration Checklist

- [ ] Copy configuration template
  ```bash
  copy mcp_config.env.example .env
  ```
  
- [ ] Edit `.env` file with your settings
  - [ ] Add your API key (GOOGLE_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY)
  - [ ] Set MCP_LLM_PROVIDER (google, openai, or anthropic)
  - [ ] Set MCP_LLM_MODEL_NAME
  - [ ] Set MCP_RESEARCH_TOOL_SAVE_DIR (e.g., ./research_output)
  
- [ ] Verify critical variables are set
  ```bash
  # Windows PowerShell
  $env:GOOGLE_API_KEY
  $env:MCP_RESEARCH_TOOL_SAVE_DIR
  
  # Linux/Mac
  echo $GOOGLE_API_KEY
  echo $MCP_RESEARCH_TOOL_SAVE_DIR
  ```

- [ ] Create research output directory
  ```bash
  mkdir research_output
  ```

## ✅ File Verification Checklist

Ensure these files exist in your project:

- [ ] `mcp_browser_client.py` - MCP client wrapper
- [ ] `mcp_browser_server.py` - HTTP server
- [ ] `start_mcp_browser_server.py` - Startup script
- [ ] `test_mcp_browser_integration.py` - Unit tests
- [ ] `requirements_mcp_browser.txt` - Dependencies
- [ ] `mcp_config.env.example` - Config template
- [ ] `.env` - Your configuration (created from example)
- [ ] `index-dev.html` - Updated with new tools
- [ ] `QUICK_START.md` - Quick start guide
- [ ] `MCP_BROWSER_INTEGRATION.md` - Full documentation
- [ ] `MCP_INTEGRATION_README.md` - Package overview
- [ ] `INTEGRATION_CHECKLIST.md` - This checklist

## ✅ Server Startup Checklist

- [ ] Start the HTTP server
  ```bash
  python start_mcp_browser_server.py
  ```
  
- [ ] Verify server starts without errors
  - [ ] See "Starting MCP Browser HTTP Server" message
  - [ ] No error messages in console
  - [ ] Server displays configuration summary
  
- [ ] Check server endpoints are listed
  - [ ] POST /api/browser-agent
  - [ ] POST /api/deep-research
  - [ ] GET /api/health
  - [ ] POST /api/disconnect

## ✅ Basic Testing Checklist

- [ ] Test health endpoint
  ```bash
  curl http://127.0.0.1:5001/api/health
  ```
  Expected: `{"status": "healthy", "mcp_connected": false}`
  
- [ ] Test browser agent with simple task
  ```bash
  curl -X POST http://127.0.0.1:5001/api/browser-agent \
    -H "Content-Type: application/json" \
    -d "{\"task\": \"Go to example.com and get the page title\"}"
  ```
  Expected: Success response with page title
  
- [ ] Test deep research with simple query
  ```bash
  curl -X POST http://127.0.0.1:5001/api/deep-research \
    -H "Content-Type: application/json" \
    -d "{\"research_task\": \"What is Python?\"}"
  ```
  Expected: Success response with research report

- [ ] Run unit tests
  ```bash
  python test_mcp_browser_integration.py -v
  ```
  Expected: All tests pass

## ✅ Frontend Integration Checklist

- [ ] Open `index-dev.html` in browser
- [ ] Verify no JavaScript errors in console
- [ ] Test browser agent tool with assistant
  - [ ] Ask: "Go to example.com and tell me about the page"
  - [ ] Wait for response
  - [ ] Verify result is displayed
  
- [ ] Test deep research tool with assistant
  - [ ] Ask: "Research the benefits of exercise"
  - [ ] Wait for research to complete (may take 1-2 minutes)
  - [ ] Verify report is displayed
  
- [ ] Check research output directory
  ```bash
  dir research_output\*  # Windows
  ls research_output/    # Linux/Mac
  ```
  - [ ] Verify research reports are created
  - [ ] Open a report to verify contents

## ✅ Tool Verification Checklist

In your browser console, verify tools are registered:

```javascript
// Check if tools exist in the tools array
console.log(tools.find(t => t.function.name === 'runBrowserAgent'));
console.log(tools.find(t => t.function.name === 'runDeepResearch'));
```

Both should return tool definition objects (not undefined).

## ✅ Advanced Testing Checklist

- [ ] Test with headless mode disabled
  - Set `MCP_BROWSER_HEADLESS=false` in `.env`
  - Restart server
  - Run a browser task
  - Verify browser window opens
  
- [ ] Test with different LLM providers
  - [ ] Google AI (gemini)
  - [ ] OpenAI (gpt-4)
  - [ ] Anthropic (claude)
  
- [ ] Test with vision enabled
  - Ensure `MCP_AGENT_TOOL_USE_VISION=true`
  - Ask assistant to describe visual elements
  
- [ ] Test with multiple parallel browsers
  - Set `max_parallel_browsers: 5` in research task
  - Verify faster research completion

## ✅ Production Readiness Checklist

- [ ] API keys are stored securely (not in code)
- [ ] `.env` file is added to `.gitignore`
- [ ] CORS is configured appropriately for your domain
- [ ] Browser security settings are appropriate (`MCP_BROWSER_DISABLE_SECURITY=false`)
- [ ] Resource limits are set appropriately
  - [ ] `MCP_AGENT_TOOL_MAX_STEPS` (default: 100)
  - [ ] `MCP_RESEARCH_TOOL_MAX_PARALLEL_BROWSERS` (default: 3)
- [ ] Logging level is appropriate (`MCP_SERVER_LOGGING_LEVEL=INFO`)
- [ ] Server is accessible from your frontend
- [ ] Health check endpoint works
- [ ] Error handling is properly configured

## ✅ Documentation Review Checklist

- [ ] Read [QUICK_START.md](QUICK_START.md)
- [ ] Review [MCP_BROWSER_INTEGRATION.md](MCP_BROWSER_INTEGRATION.md)
- [ ] Understand architecture diagram
- [ ] Familiarize with API endpoints
- [ ] Review troubleshooting section
- [ ] Understand best practices
- [ ] Review security considerations

## ✅ Common Issues Resolution

If you encounter issues, check these:

### Server Won't Start
- [ ] All dependencies installed? `pip list | grep -E "mcp|flask|playwright"`
- [ ] Python version correct? `python --version` (need 3.10+)
- [ ] `.env` file exists and has required variables?
- [ ] Port 5001 available? `netstat -an | findstr 5001`

### Browser Tasks Fail
- [ ] Playwright installed? `playwright install`
- [ ] Browser binary accessible?
- [ ] Sufficient system resources?
- [ ] Network connection active?

### Research Not Working
- [ ] `MCP_RESEARCH_TOOL_SAVE_DIR` set and directory exists?
- [ ] Write permissions on directory?
- [ ] Sufficient disk space?

### Frontend Connection Issues
- [ ] Server running? Check with health endpoint
- [ ] Correct port in frontend (5001)?
- [ ] CORS configured correctly?
- [ ] No firewall blocking localhost?

## ✅ Maintenance Checklist

Regular maintenance tasks:

### Daily (If Using Frequently)
- [ ] Check server logs for errors
- [ ] Monitor disk space for research outputs
- [ ] Verify API quota usage

### Weekly
- [ ] Clean old research reports
  ```bash
  # Windows
  forfiles /P research_output /D -7 /C "cmd /c del @path"
  # Linux/Mac
  find research_output -mtime +7 -delete
  ```
- [ ] Review and update configuration if needed
- [ ] Check for MCP browser-use updates

### Monthly
- [ ] Update dependencies
  ```bash
  pip install --upgrade -r requirements_mcp_browser.txt
  playwright install
  ```
- [ ] Review security settings
- [ ] Optimize configuration based on usage

## 🎉 Success Criteria

Your integration is successfully set up when:

✅ Server starts without errors
✅ Health check returns "healthy" status
✅ Browser agent completes a simple task
✅ Deep research generates a report
✅ Frontend can communicate with server
✅ Research reports are saved correctly
✅ No linting errors in code
✅ Unit tests all pass

## 📝 Notes

### Configuration File Location
Your `.env` file should be in the project root:
```
C:\Users\andyj\AI_assistant\.env
```

### Default Ports
- HTTP Server: 5001
- MCP Server: stdio (no port)

### Research Output
Reports are saved as:
```
research_output/
  <task-id>/
    <task-id>.md        # Main report
    sources.json        # Source tracking
    findings.json       # Research findings
```

### Log Files
If `MCP_SERVER_LOG_FILE` is set, logs are written to that file.
Otherwise, logs appear in console output.

## 🆘 Getting Help

If you're stuck:

1. ✅ Check this checklist again
2. 📖 Review [QUICK_START.md](QUICK_START.md)
3. 📚 Read [MCP_BROWSER_INTEGRATION.md](MCP_BROWSER_INTEGRATION.md)
4. 🐛 Check server logs (`MCP_SERVER_LOGGING_LEVEL=DEBUG`)
5. 🔍 Test endpoints individually with curl
6. 💬 Review GitHub issues: https://github.com/Saik0s/mcp-browser-use/issues

---

**Last Updated**: 2024
**Version**: 1.0.0

