#!/usr/bin/env python3
"""
Simple test script for the browser-use MCP HTTP server.
Requires the HTTP server to be running: in mcp-browser-use directory run:
  uv run mcp-server-browser-use server
Then run this script from the project root. It uses the FastMCP client to list tools.
For running browser tasks, use MCPBrowserClient (mcp_browser_client.py) which also uses HTTP.
"""
import asyncio
import os


async def test_browser_use_http():
    """Connect to the browser-use HTTP MCP server and list tools."""
    from fastmcp import Client

    url = os.environ.get("MCP_BROWSER_USE_HTTP_URL", "http://127.0.0.1:8383/mcp").strip()
    print(f"Connecting to {url} ...")
    try:
        async with Client(url) as client:
            tools = await client.list_tools()
        print("Available tools:")
        for t in tools:
            name = getattr(t, "name", "?")
            desc = (getattr(t, "description", None) or "")[:70]
            print(f"  - {name}: {desc}")
        print("Test completed successfully.")
    except Exception as e:
        print(f"Error: {e}")
        print(
            "Ensure the browser-use HTTP server is running: "
            "in mcp-browser-use directory run: uv run mcp-server-browser-use server"
        )
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_browser_use_http())
