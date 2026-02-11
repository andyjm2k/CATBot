#!/usr/bin/env python3
"""
Start the mcp-server-browser-use HTTP server with this project's .env so that
the background MCP server uses the same LLM provider/model as the Flask HTTP bridge.
Run from project root. Press Ctrl+C to stop the server.
"""
import os
import subprocess
import sys
from pathlib import Path

# Project root = directory containing this script
PROJECT_ROOT = Path(__file__).resolve().parent
MCP_BROWSER_USE_DIR = PROJECT_ROOT / "mcp-browser-use"

# Load project .env so MCP_LLM_* match the Flask server / proxy
try:
    from dotenv import load_dotenv
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"Loaded env from: {env_file}")
except ImportError:
    pass

# Ensure the MCP server process sees the same env (provider/model)
provider = os.environ.get("MCP_LLM_PROVIDER", "google")
model = os.environ.get("MCP_LLM_MODEL_NAME", "")
print(f"Starting MCP server with LLM: provider={provider}, model={model or '(default)'}")
print(f"URL: http://127.0.0.1:8383/mcp")
print("Press Ctrl+C to stop.\n")

if not MCP_BROWSER_USE_DIR.is_dir():
    print(f"Error: mcp-browser-use directory not found: {MCP_BROWSER_USE_DIR}")
    sys.exit(1)

# Run the HTTP MCP server; it will read MCP_LLM_* from env (inherited from our .env)
try:
    subprocess.run(
        ["uv", "run", "mcp-server-browser-use", "server"],
        cwd=str(MCP_BROWSER_USE_DIR),
        env=os.environ.copy(),
    )
except KeyboardInterrupt:
    print("\nStopped.")
except FileNotFoundError:
    print("Error: 'uv' not found. Install uv or run from mcp-browser-use: uv run mcp-server-browser-use server")
    sys.exit(1)
