#!/usr/bin/env python3
"""
Simple test script to test the browser-use MCP server directly.
"""
import asyncio
import json
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_browser_use_mcp():
    """Test the browser-use MCP server."""
    try:
        # Start the browser-use MCP server as a subprocess
        server_params = StdioServerParameters(
            command=sys.executable,
            args=["browser_use_mcp_server.py"],
            env=None
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the session
                await session.initialize()

                # List available tools
                tools_result = await session.list_tools()
                print("Available tools:")
                for tool in tools_result.tools:
                    print(f"  - {tool.name}: {tool.description}")

                # Test calling a tool
                if tools_result.tools:
                    test_tool = tools_result.tools[0]
                    print(f"\nTesting tool: {test_tool.name}")
                    result = await session.call_tool(test_tool.name, {})
                    print(f"Result: {result}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_browser_use_mcp())
