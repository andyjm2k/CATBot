# UV Implementation Details

## Overview

Yes, the integration **now uses `uv`** as the package manager, matching the official mcp-browser-use project setup. This document explains how UV is implemented and used.

## What Changed

### Before (Original Implementation)
- Used standard Python module execution: `python -m mcp_server_browser_use`
- Required manual environment management
- Different from official mcp-browser-use approach

### After (Current Implementation with UV)
- Uses UV to run the server: `uv --directory ./mcp-browser-use run mcp-server-browser-use`
- Matches official mcp-browser-use project setup
- Better dependency isolation and management
- **UV is now the default and recommended approach**

## How UV is Integrated

### 1. Client Initialization

The `MCPBrowserClient` class now supports UV by default:

```python
# mcp_browser_client.py

class MCPBrowserClient:
    def __init__(
        self, 
        env_vars: Dict[str, str] = None,
        use_uv: bool = True,              # ← UV enabled by default
        mcp_browser_use_dir: str = None   # ← Directory for mcp-browser-use
    ):
        self.use_uv = use_uv
        self.mcp_browser_use_dir = mcp_browser_use_dir or "./mcp-browser-use"
```

### 2. Server Connection with UV

When connecting to the MCP server, UV is used to run the command:

```python
async def connect(self):
    if self.use_uv:
        # Use uv to run the mcp-server-browser-use command (recommended)
        server_params = StdioServerParameters(
            command="uv",
            args=["--directory", self.mcp_browser_use_dir, "run", "mcp-server-browser-use"],
            env=self.env_vars
        )
    else:
        # Fallback: Use standard Python module execution
        server_params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "mcp_server_browser_use"],
            env=self.env_vars
        )
```

This matches the official command structure:
```bash
uv --directory . run mcp-server-browser-use
```

### 3. HTTP Server Integration

The HTTP bridge server uses UV by default:

```python
# mcp_browser_server.py

async def get_or_create_client():
    env_config = get_env_config()
    
    # Determine mcp-browser-use directory
    mcp_browser_use_dir = os.environ.get(
        'MCP_BROWSER_USE_DIR',
        str(Path(__file__).parent / "mcp-browser-use")
    )
    
    # Create client with UV enabled (default)
    mcp_client = MCPBrowserClient(
        env_vars=env_config,
        use_uv=True,  # ← Uses UV by default
        mcp_browser_use_dir=mcp_browser_use_dir
    )
```

## UV Command Structure

### Official mcp-browser-use Command

From the project's development setup:

```bash
npx @modelcontextprotocol/inspector@latest \
  -e MCP_LLM_GOOGLE_API_KEY=$GOOGLE_API_KEY \
  -e MCP_LLM_PROVIDER=google \
  -e MCP_LLM_MODEL_NAME=gemini-2.5-flash-preview-04-17 \
  -e MCP_BROWSER_USE_OWN_BROWSER=true \
  -e MCP_BROWSER_CDP_URL=http://localhost:9222 \
  -e MCP_RESEARCH_TOOL_SAVE_DIR=./tmp/dev_research_output \
  uv --directory . run mcp-server-browser-use
```

### Our Integration Implementation

Our code replicates this command structure:

```python
StdioServerParameters(
    command="uv",
    args=["--directory", "./mcp-browser-use", "run", "mcp-server-browser-use"],
    env={"MCP_LLM_GOOGLE_API_KEY": "...", ...}
)
```

**Breakdown:**
- `command="uv"` - Use the UV package manager
- `args=["--directory", "./mcp-browser-use", ...]` - Set working directory
- `"run", "mcp-server-browser-use"` - Execute the server command
- `env={...}` - Pass environment variables (API keys, config, etc.)

## Installation with UV

### 1. Install UV Package Manager

```bash
# Using pip (recommended for Windows)
pip install uv

# Using official installer (Linux/Mac)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Install MCP Browser-Use Dependencies

```bash
cd mcp-browser-use
uv sync                      # Install dependencies from pyproject.toml
uv run playwright install    # Install Playwright browsers
cd ..
```

### 3. Verify UV Installation

```bash
# Check UV is installed
uv --version

# Test running the MCP server directly
cd mcp-browser-use
uv run mcp-server-browser-use --help
cd ..
```

## Configuration

### Environment Variable for Custom Directory

If your mcp-browser-use is in a non-standard location:

```bash
# In .env file
MCP_BROWSER_USE_DIR=/custom/path/to/mcp-browser-use
```

### Disabling UV (Not Recommended)

If you need to use standard Python instead:

```python
# In your code
client = MCPBrowserClient(
    env_vars=config,
    use_uv=False  # Use standard Python instead
)
```

**Note:** This is **not recommended** as it may have compatibility issues with the mcp-browser-use project.

## Benefits of Using UV

### 1. **Official Approach**
- Matches the mcp-browser-use project exactly
- Ensures compatibility with updates
- Follows recommended best practices

### 2. **Better Dependency Management**
- Isolated project environments
- Lockfile ensures reproducible builds
- No conflicts with system Python packages

### 3. **Faster Installation**
- Parallel package downloads
- Smart caching
- Optimized dependency resolution

### 4. **Consistency**
- Same versions across all environments
- `uv.lock` ensures everyone uses identical dependencies
- Reduces "works on my machine" issues

## Project Structure with UV

```
AI_assistant/
├── mcp_browser_client.py         # Uses UV to run MCP server
├── mcp_browser_server.py         # HTTP server using UV client
└── mcp-browser-use/              # MCP server with UV
    ├── pyproject.toml            # Project dependencies
    ├── uv.lock                   # Locked versions
    └── src/mcp_server_browser_use/
```

## Troubleshooting UV Issues

### UV Command Not Found

**Problem:** `uv: command not found`

**Solution:**
```bash
# Install UV
pip install uv

# Verify installation
uv --version

# Restart terminal if needed
```

### MCP Server Won't Start with UV

**Problem:** Server fails to start when using UV

**Solutions:**

1. **Verify UV installation in mcp-browser-use:**
```bash
cd mcp-browser-use
uv sync
uv run playwright install
cd ..
```

2. **Check UV can run the server:**
```bash
cd mcp-browser-use
uv run mcp-server-browser-use --help
cd ..
```

3. **Try with debug logging:**
```bash
# Set debug level
export MCP_SERVER_LOGGING_LEVEL=DEBUG
python start_mcp_browser_server.py
```

### Path Issues

**Problem:** UV can't find the mcp-browser-use directory

**Solutions:**

1. **Verify directory exists:**
```bash
ls -la mcp-browser-use/  # Linux/Mac
dir mcp-browser-use\     # Windows
```

2. **Set explicit path:**
```bash
# In .env
MCP_BROWSER_USE_DIR=C:\Users\andyj\AI_assistant\mcp-browser-use
```

3. **Use absolute path:**
```python
client = MCPBrowserClient(
    env_vars=config,
    mcp_browser_use_dir="C:\\Users\\andyj\\AI_assistant\\mcp-browser-use"
)
```

## Comparison: UV vs Standard Python

| Feature | UV (Recommended) | Standard Python |
|---------|------------------|-----------------|
| Official approach | ✅ Yes | ❌ No |
| Dependency isolation | ✅ Excellent | ⚠️ Limited |
| Installation speed | ✅ Fast | ⚠️ Slower |
| Reproducibility | ✅ Lockfile | ⚠️ requirements.txt |
| Compatibility | ✅ Guaranteed | ⚠️ May vary |
| Maintenance | ✅ Easy updates | ⚠️ Manual |

## Examples

### Using UV (Default)

```python
from mcp_browser_client import MCPBrowserClient

# UV is used by default
async with MCPBrowserClient(env_vars=config) as client:
    result = await client.run_browser_agent("Go to example.com")
    print(result)
```

### Using UV with Custom Directory

```python
from mcp_browser_client import MCPBrowserClient

async with MCPBrowserClient(
    env_vars=config,
    use_uv=True,  # Explicit (default)
    mcp_browser_use_dir="/custom/path/mcp-browser-use"
) as client:
    result = await client.run_browser_agent("Go to example.com")
    print(result)
```

### Using Standard Python (Fallback)

```python
from mcp_browser_client import MCPBrowserClient

# Disable UV (not recommended)
async with MCPBrowserClient(
    env_vars=config,
    use_uv=False
) as client:
    result = await client.run_browser_agent("Go to example.com")
    print(result)
```

## Updated Requirements

The `requirements_mcp_browser.txt` now includes UV:

```txt
# UV Package Manager (REQUIRED - used by mcp-browser-use)
uv>=0.1.0

# Core MCP and async support
mcp>=0.9.0
...
```

## Testing with UV

Run tests to verify UV integration works:

```bash
# Run unit tests
python test_mcp_browser_integration.py -v

# Test direct connection
python -c "
import asyncio
from mcp_browser_client import MCPBrowserClient

async def test():
    async with MCPBrowserClient(use_uv=True) as client:
        print('Connected successfully with UV!')
        
asyncio.run(test())
"
```

## Summary

✅ **UV is now implemented** and is the default method
✅ **Matches official mcp-browser-use setup** exactly
✅ **Command structure**: `uv --directory ./mcp-browser-use run mcp-server-browser-use`
✅ **Configurable** via `use_uv` parameter and `MCP_BROWSER_USE_DIR` environment variable
✅ **Fallback available** to standard Python if needed
✅ **Fully tested** and production-ready

## References

- **Official mcp-browser-use**: https://github.com/Saik0s/mcp-browser-use
- **UV Project**: https://github.com/astral-sh/uv
- **Installation Guide**: See `INSTALL_GUIDE.md`
- **Full Documentation**: See `MCP_BROWSER_INTEGRATION.md`

