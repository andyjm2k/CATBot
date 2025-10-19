#!/usr/bin/env python3
"""
Test script to test the HTTP client for MCP server communication.
"""
import asyncio
import json
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_http_simulation():
    """Test MCP communication similar to how the HTTP client would work."""
    try:
        server_params = StdioServerParameters(
            command=sys.executable,
            args=["browser_use_mcp_server.py"],
            env=None
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Test tools/list
                print("Testing tools/list...")
                tools_result = await session.list_tools()
                print(f"Got {len(tools_result.tools)} tools")

                # Test tools/call
                print("Testing tools/call...")
                test_tool = tools_result.tools[0]
                call_result = await session.call_tool(test_tool.name, {"test": "parameter"})
                print(f"Call result type: {type(call_result)}")
                print(f"Call result has content: {hasattr(call_result, 'content')}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_http_simulation())
