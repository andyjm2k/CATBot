#!/usr/bin/env python3
import time
import requests
import json

def test_integration():
    print("🧪 Testing Complete MCP Browser Integration...")

    try:
        # Test basic connectivity first
        r = requests.get('http://localhost:8002/health')
        print(f'✅ Health check: {r.status_code}')

        # Test MCP servers list
        r = requests.get('http://localhost:8002/v1/mcp/servers')
        print(f'✅ Servers list: {r.status_code}')
        servers = r.json()
        print(f'📋 Available servers: {[s["name"] for s in servers["servers"]]}')

        # Test MCP connection
        if servers['servers']:
            server_id = servers['servers'][0]['id']
            print(f'🔌 Connecting to server: {server_id}')

            response = requests.post(f'http://localhost:8002/v1/mcp/servers/{server_id}/connect')
            print(f'🔌 MCP connection: {response.status_code}')

            if response.status_code == 200:
                print('✅ SUCCESS: MCP server connected!')

                # Test tools list
                tools_response = requests.post(f'http://localhost:8002/v1/mcp/servers/{server_id}/tools/list')
                print(f'🔧 Tools list: {tools_response.status_code}')

                if tools_response.status_code == 200:
                    tools = tools_response.json()
                    print(f'🛠️  Available tools: {[tool["name"] for tool in tools["result"]["tools"]]}')

                    # Test a simple tool call
                    if tools["result"]["tools"]:
                        tool_call_response = requests.post(
                            f'http://localhost:8002/v1/mcp/servers/{server_id}/tools/call',
                            json={
                                "toolName": "run_browser_agent",
                                "parameters": {
                                    "instruction": "Navigate to example.com and tell me what you see",
                                    "max_steps": 3,
                                    "use_vision": False
                                }
                            }
                        )
                        print(f'🔧 Tool call: {tool_call_response.status_code}')

                        if tool_call_response.status_code == 200:
                            result = tool_call_response.json()
                            print('✅ Tool execution successful!')
                            print(f'Result: {result["result"]["content"][0]["text"][:200]}...')
                        else:
                            print(f'❌ Tool call failed: {tool_call_response.text}')
                else:
                    print(f'❌ Tools list failed: {tools_response.text}')

            else:
                print(f'❌ Connection failed: {response.text}')

        print("✨ Integration test completed!")

    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == "__main__":
    test_integration()
