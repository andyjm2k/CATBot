#!/usr/bin/env python3
"""
Test script to check the exact format of tools/list response.
"""
import asyncio
import json
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_tools_list():
    """Test the tools/list response format."""
    try:
        server_params = StdioServerParameters(
            command=sys.executable,
            args=["browser_use_mcp_server.py"],
            env=None
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Get the tools list
                tools_result = await session.list_tools()
                print("Full tools response:")
                print(f"Type: {type(tools_result)}")
                print(f"Has tools: {hasattr(tools_result, 'tools')}")
                if hasattr(tools_result, 'tools'):
                    print(f"Number of tools: {len(tools_result.tools)}")
                print(f"Dir: {[attr for attr in dir(tools_result) if not attr.startswith('_')]}")

                print("\nTools array:")
                if hasattr(tools_result, 'tools'):
                    for i, tool in enumerate(tools_result.tools):
                        print(f"Tool {i}: {tool.name}")
                        print(f"  Description: {tool.description}")
                        print(f"  Input schema: {tool.inputSchema}")
                        print(f"  Type: {type(tool)}")
                        print(f"  Dir: {[attr for attr in dir(tool) if not attr.startswith('_')]}")
                        print()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_tools_list())
