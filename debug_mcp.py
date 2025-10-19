#!/usr/bin/env python3
"""
Debug script to check the MCP server response format.
"""
import asyncio
import sys
from browser_use.mcp.server import BrowserUseServer

async def debug_mcp():
    """Debug the MCP server response format."""
    server = BrowserUseServer()

    # Create a simple test to see what the server returns
    try:
        # Let's see what the server object has
        print("Server attributes:", dir(server))
        print("Server type:", type(server))

        # Try to run the server briefly to see what it does
        await asyncio.wait_for(server.run(), timeout=1.0)
    except asyncio.TimeoutError:
        print("Server started successfully (timed out as expected)")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_mcp())
