#!/usr/bin/env python3
"""
Simple test to check MCP communication
"""
import asyncio
import json
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_mcp():
    """Test basic MCP communication"""
    try:
        # Create a simple test server that just echoes back
        test_server_code = '''
import sys
import json

def main():
    for line in sys.stdin:
        try:
            message = json.loads(line.strip())
            print(json.dumps({
                "jsonrpc": "2.0",
                "id": message.get("id"),
                "result": {"test": "echo"}
            }))
        except:
            pass

if __name__ == "__main__":
    main()
'''

        # Write test server to file
        with open('test_server.py', 'w') as f:
            f.write(test_server_code)

        server_params = StdioServerParameters(
            command=sys.executable,
            args=['test_server.py'],
            env=None
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Try tools/list
                try:
                    result = await session.list_tools()
                    print("Tools list result:", result)
                except Exception as e:
                    print(f"Tools list error: {e}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mcp())
