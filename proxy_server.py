#!/usr/bin/env python3
"""
Python FastAPI replacement for the Node.js proxy server.
Provides the same functionality but in Python for better integration with the MCP ecosystem.
"""

import asyncio
import json
import os
import re
import time
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Import AutoGen components for team-based chat
try:
    from autogen_agentchat.teams import SelectorGroupChat
    from autogen_core import Component, FunctionCall, ComponentLoader
    AUTOGEN_AVAILABLE = True
    print("✅ AutoGen imports successful")
except ImportError as e:
    print(f"⚠️  AutoGen not available: {e}")
    AUTOGEN_AVAILABLE = False
    SelectorGroupChat = None
    Component = None
    ComponentLoader = None

# Import MCP SDK (with error handling)
try:
    from mcp import ClientSession, stdio_client, StdioServerParameters
    MCP_AVAILABLE = True
except ImportError as e:
    print(f"MCP import error: {e}")
    MCP_AVAILABLE = False
    ClientSession = None
    stdio_client = None
    StdioServerParameters = None

# Pydantic models for request/response validation
class ServerConfig(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    command: Optional[str] = None
    apiKey: Optional[str] = None
    model: Optional[str] = None
    url: Optional[str] = None
    wsUrl: Optional[str] = None
    status: Optional[str] = None
    enabled: Optional[bool] = None
    action: Optional[str] = None

class ToolCallRequest(BaseModel):
    toolName: str
    parameters: Optional[Dict[str, Any]] = None

# Global state (similar to the Node.js version)
mcp_clients = {}
mcp_servers = {}
SERVERS_FILE = Path(__file__).parent / "mcp_servers.json"
TEAM_CONFIG_FILE = Path(__file__).parent / "team-config.json"

# Global AutoGen team instance
autogen_team = None

# MCP Client Manager class to handle transport lifecycle
class MCPClientManager:
    """Manages MCP client and transport lifecycle."""

    def __init__(self, server_config: Dict[str, Any]):
        self.server_config = server_config
        self.client = None
        self.transport = None
        self.read = None
        self.write = None

    async def connect(self):
        """Connect to MCP server and initialize client."""
        if not MCP_AVAILABLE:
            raise Exception("MCP SDK not available")

        try:
            command_parts = self.server_config['command'].strip().split()
            if not command_parts:
                raise ValueError('Invalid command format')

            print(f"🔧 Creating MCP client with command: {command_parts[0]} and args: {command_parts[1:]}")

            # Prepare environment variables
            env = os.environ.copy()

            # Add API keys from server config if available
            if self.server_config.get('apiKey'):
                # Determine which API key to use based on the model
                model = self.server_config.get('model', '').lower()
                if 'gemini' in model:
                    env['GOOGLE_API_KEY'] = self.server_config['apiKey']
                    env['MCP_MODEL_PROVIDER'] = 'google'
                elif 'claude' in model:
                    env['ANTHROPIC_API_KEY'] = self.server_config['apiKey']
                    env['MCP_MODEL_PROVIDER'] = 'anthropic'
                else:
                    env['OPENAI_API_KEY'] = self.server_config['apiKey']
                    env['MCP_MODEL_PROVIDER'] = 'openai'

            # Add model configuration
            if self.server_config.get('model'):
                env['MCP_MODEL_NAME'] = self.server_config['model']

            # Set browser configuration for MCP server
            env.setdefault('BROWSER_USE_HEADLESS', 'true')
            env.setdefault('BROWSER_USE_DISABLE_SECURITY', 'false')

            print(f"🔐 Environment variables for MCP server: {list(env.keys())}")

            # Create server parameters
            server_params = StdioServerParameters(
                command=command_parts[0],
                args=command_parts[1:],
                env=env
            )

            # Create stdio client transport using async context manager
            try:
                transport_cm = stdio_client(server_params)
                async with transport_cm as (self.read, self.write):
                    # Create client session
                    self.client = ClientSession(self.read, self.write)

                    # Initialize the client
                    await self.client.initialize()

                    print("✅ MCP client setup complete")
                    return self.client
            except Exception as e:
                print(f"Failed to create stdio client: {e}")
                raise

        except Exception as e:
            print(f"MCP connection error: {e}")
            raise Exception(f"Failed to connect to MCP server: {str(e)}")

    async def disconnect(self):
        """Disconnect from MCP server."""
        if self.client:
            await self.client.close()
        if self.transport:
            # The transport context manager will handle cleanup
            pass

# FastAPI app
app = FastAPI(title="AI Assistant Proxy Server", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper function to clean HTML text (similar to Node.js version)
def clean_text(text: str) -> str:
    """Clean HTML text by removing tags and decoding entities."""
    if not text:
        return ""

    # Remove HTML tags
    text = re.sub(r'</?[^>]+(>|$)', '', text)

    # Decode HTML entities
    html_entities = {
        '&amp;': '&', '&lt;': '<', '&gt;': '>', '&quot;': '"', '&#039;': "'",
        '&rsquo;': "'", '&lsquo;': "'", '&rdquo;': '"', '&ldquo;': '"',
        '&ndash;': '-', '&mdash;': '—'
    }

    for entity, replacement in html_entities.items():
        text = text.replace(entity, replacement)

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# Helper function to parse dates (similar to Node.js version)
def parse_date(date_str: Optional[str]) -> Optional[float]:
    """Parse date string to timestamp."""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00')).timestamp()
    except (ValueError, AttributeError):
        return None

# Load servers from disk
def load_servers():
    """Load MCP servers from JSON file."""
    global mcp_servers
    try:
        if SERVERS_FILE.exists():
            with open(SERVERS_FILE, 'r', encoding='utf-8') as f:
                servers = json.load(f)
                mcp_servers = {server['id']: server for server in servers}
                print(f"Loaded {len(servers)} MCP servers from disk")
    except Exception as e:
        print(f"No existing servers file found, starting with empty state: {e}")

# Save servers to disk
def save_servers():
    """Save MCP servers to JSON file."""
    global mcp_servers
    try:
        servers = list(mcp_servers.values())
        with open(SERVERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(servers, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(servers)} MCP servers to disk")
    except Exception as e:
        print(f"Error saving servers to disk: {e}")

# Load AutoGen team from config
def load_autogen_team():
    """Load AutoGen team from team-config.json."""
    global autogen_team
    
    if not AUTOGEN_AVAILABLE:
        print("⚠️  AutoGen not available, skipping team load")
        return None
    
    try:
        if not TEAM_CONFIG_FILE.exists():
            print(f"⚠️  Team config file not found: {TEAM_CONFIG_FILE}")
            return None
            
        print(f"📂 Loading AutoGen team from {TEAM_CONFIG_FILE}...")
        
        with open(TEAM_CONFIG_FILE, 'r', encoding='utf-8') as f:
            team_config = json.load(f)
        
        # Load the team from the configuration using ComponentLoader
        loader = ComponentLoader()
        team = loader.load_component(team_config)
        
        print(f"✅ AutoGen team loaded successfully: {team_config.get('label', 'Unknown')}")
        return team
        
    except Exception as e:
        import traceback
        print(f"❌ Error loading AutoGen team: {e}")
        print(traceback.format_exc())
        return None

# Load servers on startup
try:
    load_servers()
    print(f"✅ Loaded {len(mcp_servers)} MCP servers from disk")
except Exception as e:
    print(f"Warning: Could not load servers on startup: {e}")

# Load AutoGen team on startup
try:
    autogen_team = load_autogen_team()
except Exception as e:
    print(f"Warning: Could not load AutoGen team on startup: {e}")

# Web proxy endpoint for fetching content
@app.get("/v1/proxy/fetch")
async def proxy_fetch(url: str):
    """Fetch web content through proxy."""
    if not url:
        raise HTTPException(status_code=400, detail="URL parameter is required")

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)

        return {"content": response.text}

    except Exception as e:
        print(f"Proxy error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch content: {str(e)}")

# Web search endpoint
@app.get("/v1/proxy/search")
async def proxy_search(query: str):
    """Search the web using Brave Search API or DuckDuckGo fallback."""
    if not query:
        raise HTTPException(status_code=400, detail="Search query is required")

    # Try Brave Search first
    try:
        brave_api_key = os.getenv('BRAVE_API_KEY', 'BSAu30gzJMxRgMIyw8HEO5CYU5bP_0R')

        async with httpx.AsyncClient() as client:
            response = await client.get(
                'https://api.search.brave.com/res/v1/web/search',
                headers={
                    'Accept': 'application/json',
                    'Accept-Encoding': 'gzip',
                    'X-Subscription-Token': brave_api_key
                },
                params={
                    'q': query,
                    'count': 10,
                    'search_lang': 'en',
                    'safesearch': 'moderate',
                    'freshness': 'past_month'
                }
            )

        if response.status_code == 200:
            data = response.json()
            if data.get('web', {}).get('results'):
                results = []
                for result in data['web']['results']:
                    # Parse date information
                    date_str = result.get('age') or result.get('published')
                    parsed_date = parse_date(date_str) if date_str else None

                    results.append({
                        'url': result['url'],
                        'title': clean_text(result.get('title', '')),
                        'snippet': clean_text(result.get('description', '')),
                        'date': parsed_date
                    })

                # Sort by date (newest first) and filter valid results
                results = [r for r in results if r['title'] and r['snippet']]
                results.sort(key=lambda x: parse_date(x.get('date')) or 0, reverse=True)

                return {"results": results[:5]}  # Return top 5 results

    except Exception as e:
        print(f"Brave Search failed, falling back to DuckDuckGo: {e}")

    # Fallback to DuckDuckGo
    try:
        search_url = f"https://html.duckduckgo.com/html/?q={query}"

        async with httpx.AsyncClient() as client:
            response = await client.get(
                search_url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5'
                },
                timeout=10.0
            )

        results = []
        html = response.text

        # Extract results using regex patterns
        patterns = [
            r'<div class="links_main links_deep result__body">.*?<a class="result__a" href="([^"]+)".*?>(.*?)</a>.*?<a class="result__snippet".*?>(.*?)</a>',
            r'<div class="result__body">.*?<a class="result__url" href="([^"]+)".*?>(.*?)</a>.*?<div class="result__snippet">(.*?)</div>',
            r'<div class="result__body">.*?<a class="result__a" href="([^"]+)".*?>(.*?)</a>.*?<div class="result__snippet">(.*?)</div>'
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, html, re.DOTALL)
            for match in matches:
                if len(results) >= 5:  # Limit to 5 results
                    break

                url, title, snippet = match.groups()
                url = url.replace('&amp;', '&')

                if 'duckduckgo.com' not in url:
                    results.append({
                        'url': url,
                        'title': clean_text(title),
                        'snippet': clean_text(snippet)
                    })

            if len(results) >= 5:
                break

        return {"results": results}

    except Exception as e:
        print(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to perform search: {str(e)}")

# AutoGen team chat endpoint (integrated directly)
@app.post("/v1/proxy/autogen")
async def autogen_chat(request: Request):
    """Run AutoGen team conversation directly (no separate service needed)."""
    global autogen_team
    
    try:
        body = await request.json()
        input_text = body.get('input')
        
        if not input_text:
            raise HTTPException(status_code=400, detail="Input parameter is required")

        print(f"🤖 AutoGen team request: {input_text[:100]}...")

        # Check if AutoGen is available and team is loaded
        if not AUTOGEN_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="AutoGen not available. Please install: pip install autogen-agentchat autogen-ext"
            )
        
        if autogen_team is None:
            # Try to load the team
            print("🔄 Loading AutoGen team for the first time...")
            autogen_team = load_autogen_team()
            if autogen_team is None:
                raise HTTPException(
                    status_code=503,
                    detail="AutoGen team not loaded. Check team-config.json exists and is valid."
                )
        else:
            # Check if the team config file has been modified and reload if needed
            try:
                config_mtime = TEAM_CONFIG_FILE.stat().st_mtime
                if not hasattr(autogen_team, '_config_mtime') or autogen_team._config_mtime != config_mtime:
                    print("🔄 Team config file changed, reloading AutoGen team...")
                    new_team = load_autogen_team()
                    if new_team is not None:
                        autogen_team = new_team
                        autogen_team._config_mtime = config_mtime
                    else:
                        print("⚠️  Failed to reload team, using existing team")
            except Exception as e:
                print(f"⚠️  Error checking team config modification time: {e}")

        try:
            # Run the team conversation
            print(f"🚀 Running AutoGen team with input: {input_text[:100]}...")
            result = await autogen_team.run(task=input_text)
            
            # Extract messages and final answer from result
            messages = []
            if hasattr(result, 'messages'):
                messages = [
                    {
                        "source": msg.source if hasattr(msg, 'source') else 'unknown',
                        "content": msg.content if hasattr(msg, 'content') else str(msg)
                    }
                    for msg in result.messages
                ]
            
            # Format all messages into a readable conversation summary
            conversation_summary = "=== AutoGen Team Workflow ===\n\n"
            
            if messages:
                for i, msg in enumerate(messages, 1):
                    source = msg.get('source', 'unknown')
                    content = msg.get('content', '')
                    conversation_summary += f"[{i}] {source}:\n{content}\n\n"
                
                conversation_summary += "=== End of Workflow ===\n\n"
                conversation_summary += "Please review the above conversation and provide a concise summary of the final result."
            else:
                conversation_summary = "No messages returned from AutoGen team."
            
            print(f"✅ AutoGen team completed with {len(messages)} messages")
            
            return {
                "output": conversation_summary,
                "response": conversation_summary,  # Alternative field name for compatibility
                "messages": messages,
                "message_count": len(messages)
            }
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"❌ AutoGen team execution error: {e}")
            print(f"   Traceback: {error_trace}")
            raise HTTPException(
                status_code=500,
                detail=f"AutoGen team execution failed: {str(e)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ AutoGen endpoint error: {e}")
        print(f"   Traceback: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process AutoGen request: {str(e)}"
        )

# MCP server management endpoints
@app.post("/v1/mcp/servers")
async def manage_servers(server_config: ServerConfig):
    """Manage MCP servers (create, update, clear)."""
    print(f"Received server config: {server_config.dict()}")

    global mcp_clients, mcp_servers

    try:
        # Handle clear action
        if server_config.action == 'clear':
            # Disconnect all connected servers
            for server_id, client in mcp_clients.items():
                try:
                    await client.close()
                except Exception as e:
                    print(f"Error closing client {server_id}: {e}")

            # Clear all servers and clients
            mcp_servers.clear()
            mcp_clients.clear()

            print("Cleared all MCP servers and clients")

            # Save to disk
            save_servers()

            return {"message": "All MCP servers cleared successfully"}

        # Validate required fields
        if not server_config.id or not server_config.name:
            raise HTTPException(status_code=400, detail="Missing required fields: id, name")

        # Update existing server or add new one
        existing_server = mcp_servers.get(server_config.id)
        if existing_server:
            # Update existing server
            mcp_servers[server_config.id] = {
                **existing_server,
                **server_config.dict(),
                'status': existing_server.get('status', 'disconnected')  # Preserve connection status
            }
            print(f"Updated MCP server: {server_config.name} ({server_config.id})")
        else:
            # Add new server
            mcp_servers[server_config.id] = {
                **server_config.dict(),
                'status': 'disconnected'
            }
            print(f"Added MCP server: {server_config.name} ({server_config.id})")

        # Save to disk
        save_servers()

        return {"message": "Server saved successfully"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error saving MCP server: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save MCP server: {str(e)}")

@app.get("/v1/mcp/servers")
async def get_servers():
    """Get all MCP servers."""
    try:
        servers = list(mcp_servers.values())
        return {"servers": servers}
    except Exception as e:
        print(f"Error getting MCP servers: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get MCP servers: {str(e)}")

def setup_browser_llm():
    """Set up the language model for browser automation."""
    model_provider = os.getenv("MCP_MODEL_PROVIDER", "google").lower()
    model_name = os.getenv("MCP_MODEL_NAME", "gemini-flash-latest")
    temperature = float(os.getenv("MCP_TEMPERATURE", "0.1"))

    if model_provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    elif model_provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=model_name,
            temperature=temperature,
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
    elif model_provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            api_key=os.getenv("GOOGLE_API_KEY")
        )
    else:
        # Default to Google/Gemini
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            api_key=os.getenv("GOOGLE_API_KEY", "dummy-key")
        )

async def create_mcp_client(server_config: Dict[str, Any]):
    """Create MCP client connection (similar to Node.js version)."""
    manager = MCPClientManager(server_config)
    client = await manager.connect()
    return client

@app.post("/v1/mcp/servers/{server_id}/connect")
async def connect_server(server_id: str):
    """Connect to an MCP server."""
    try:
        print(f"Attempting to connect to server: {server_id}")

        # Check if server exists
        server = mcp_servers.get(server_id)
        if not server:
            print(f"Server not found: {server_id}")
            raise HTTPException(status_code=404, detail="Server not found")

        print(f"Found server: {server['name']} ({server_id})")

        # For MCP Browser Use server, just mark as connected since we handle it directly
        if "mcp-browser-use" in server.get("name", "").lower():
            server['status'] = 'connected'
            mcp_servers[server_id] = server
            print(f"Successfully connected to MCP Browser Use server: {server['name']}")
            return {"message": "Server connected successfully"}

        if server_id in mcp_clients:
            print(f"Server already connected: {server_id}")
            raise HTTPException(status_code=409, detail="Server is already connected")

        if not MCP_AVAILABLE:
            raise HTTPException(status_code=503, detail="MCP SDK not available")

        print(f"Creating MCP client for server: {server['name']}")
        client = await create_mcp_client(server)
        mcp_clients[server_id] = client

        server['status'] = 'connected'
        mcp_servers[server_id] = server

        print(f"Successfully connected to MCP server: {server['name']}")
        return {"message": "Server connected successfully"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error connecting to MCP server: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to connect to MCP server: {str(e)}")

@app.post("/v1/mcp/servers/{server_id}/disconnect")
async def disconnect_server(server_id: str):
    """Disconnect from an MCP server."""
    try:
        global mcp_clients, mcp_servers

        # Check if this is the MCP Browser Use server
        server = mcp_servers.get(server_id)
        if server and "mcp-browser-use" in server.get("name", "").lower():
            # Just mark as disconnected since we don't have a real connection
            server['status'] = 'disconnected'
            mcp_servers[server_id] = server
            return {"message": "Server disconnected successfully"}

        if not MCP_AVAILABLE:
            raise HTTPException(status_code=503, detail="MCP SDK not available")

        client = mcp_clients.get(server_id)
        if not client:
            raise HTTPException(status_code=404, detail="Server is not connected")

        # Create a temporary manager to handle disconnect
        if server:
            manager = MCPClientManager(server)
            await manager.disconnect()

        del mcp_clients[server_id]

        server = mcp_servers.get(server_id)
        if server:
            server['status'] = 'disconnected'
            mcp_servers[server_id] = server

        return {"message": "Server disconnected successfully"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error disconnecting MCP server: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to disconnect MCP server: {str(e)}")

# Browser automation tool endpoint (integrated directly)
@app.post("/v1/mcp/servers/{server_id}/tools/call")
async def call_tool(server_id: str, request: ToolCallRequest):
    """Call a tool on an MCP server - now handles browser automation directly."""
    if not MCP_AVAILABLE:
        raise HTTPException(status_code=503, detail="MCP SDK not available")

    try:
        print(f"🔧 [TOOLS/CALL] Server: {server_id}")

        client = mcp_clients.get(server_id)
        if not client:
            print(f"❌ [TOOLS/CALL] Server {server_id} not found or not connected")
            raise HTTPException(status_code=404, detail="Server is not connected")

        tool_name = request.toolName
        parameters = request.parameters or {}

        print(f"🔍 [TOOLS/CALL] Tool name: {tool_name}")
        print(f"🔍 [TOOLS/CALL] Parameters: {parameters}")

        if tool_name == "run_browser_agent":
            # Handle browser automation directly
            instruction = parameters.get("instruction", "")
            max_steps = parameters.get("max_steps", 10)
            use_vision = parameters.get("use_vision", True)

            try:
                # Import browser-use components (lazy imports)
                Agent = __import__('browser_use', fromlist=['Agent']).Agent
                BrowserSession = __import__('browser_use', fromlist=['BrowserSession']).BrowserSession

                # Set up browser configuration
                headless = os.getenv("BROWSER_USE_HEADLESS", "true").lower() == "true"
                disable_security = os.getenv("BROWSER_USE_DISABLE_SECURITY", "false").lower() == "true"

                # Create browser session
                browser = BrowserSession(
                    headless=headless,
                    disable_security=disable_security
                )

                # Set up LLM based on environment configuration
                llm = setup_browser_llm()

                # Create and run the agent
                agent = Agent(
                    task=instruction,
                    llm=llm,
                    browser=browser,
                    max_steps=max_steps,
                    use_vision=use_vision
                )

                # Run the agent
                result = await agent.run()

                # Close browser
                await browser.close()

                return {
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Browser automation completed successfully.\n\nResult: {result}"
                            }
                        ]
                    }
                }

            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                return {
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Browser automation failed: {str(e)}\n\nDetails: {error_details}"
                            }
                        ]
                    }
                }
        else:
            # Handle other tools through the MCP client
            if not tool_name:
                print("❌ [TOOLS/CALL] toolName is required but missing")
                raise HTTPException(status_code=400, detail="toolName is required")

            # Make MCP request to call tool
            result = await client.request(
                method="tools/call",
                params={
                    "name": tool_name,
                    "arguments": parameters
                }
            )

            return {"result": result}

    except HTTPException:
        raise
    except Exception as e:
        print(f"💥 [TOOLS/CALL] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to call tool on MCP server: {str(e)}")

@app.post("/v1/mcp/servers/{server_id}/tools/list")
async def list_tools(server_id: str):
    """List tools available on an MCP server."""
    if not MCP_AVAILABLE:
        raise HTTPException(status_code=503, detail="MCP SDK not available")

    try:
        print(f"🔍 [TOOLS/LIST] Server: {server_id}")

        # Check if this is the MCP Browser Use server
        server = mcp_servers.get(server_id)
        if server and "mcp-browser-use" in server.get("name", "").lower():
            # Return the browser automation tool directly
            return {
                "result": {
                    "tools": [
                        {
                            "name": "run_browser_agent",
                            "description": "Control a web browser using natural language commands. Executes browser automation tasks and returns results.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "instruction": {
                                        "type": "string",
                                        "description": "Natural language instruction for browser automation (e.g., 'Navigate to Google and search for cats')",
                                    },
                                    "max_steps": {
                                        "type": "integer",
                                        "description": "Maximum number of steps the agent should take",
                                        "default": 10
                                    },
                                    "use_vision": {
                                        "type": "boolean",
                                        "description": "Whether to use vision for understanding page content",
                                        "default": True
                                    }
                                },
                                "required": ["instruction"]
                            }
                        }
                    ]
                }
            }

        global mcp_clients

        client = mcp_clients.get(server_id)
        if not client:
            print(f"❌ [TOOLS/LIST] Server {server_id} not found or not connected")
            raise HTTPException(status_code=404, detail="Server is not connected")

        # Make MCP request to list tools
        result = await client.request(
            method="tools/list",
            params={}
        )

        print(f"📨 [TOOLS/LIST] Raw response from MCP server: {result}")

        # Validate response structure
        if not result:
            print("❌ [TOOLS/LIST] No result returned from MCP server")
        elif 'tools' not in result:
            print(f"❌ [TOOLS/LIST] Missing 'tools' field in response: {list(result.keys())}")
        elif not isinstance(result['tools'], list):
            print(f"❌ [TOOLS/LIST] 'tools' field is not an array: {type(result['tools'])}")
        else:
            print(f"✅ [TOOLS/LIST] Found {len(result['tools'])} tools in response")
            for i, tool in enumerate(result['tools']):
                print(f"  Tool {i}: {tool.get('name', 'unnamed')}")
                if 'name' not in tool:
                    print(f"    ❌ Missing name for tool {i}")
                if 'description' not in tool:
                    print(f"    ⚠️  Missing description for tool {i}")
                if 'inputSchema' not in tool:
                    print(f"    ⚠️  Missing inputSchema for tool {i}")
                else:
                    schema = tool['inputSchema']
                    print(f"    ✅ inputSchema type: {schema.get('type')}")
                    if 'properties' in schema:
                        print(f"    ✅ Has {len(schema['properties'])} properties")
                    else:
                        print("    ⚠️  No properties in inputSchema")

        return {"result": result}

    except HTTPException:
        raise
    except Exception as e:
        print(f"💥 [TOOLS/LIST] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list tools on MCP server: {str(e)}")

@app.post("/v1/mcp/servers/{server_id}/tools/call")
async def call_tool(server_id: str, request: ToolCallRequest):
    """Call a tool on an MCP server."""
    if not MCP_AVAILABLE:
        raise HTTPException(status_code=503, detail="MCP SDK not available")

    try:
        print(f"🔧 [TOOLS/CALL] Server: {server_id}")

        global mcp_clients

        client = mcp_clients.get(server_id)
        if not client:
            print(f"❌ [TOOLS/CALL] Server {server_id} not found or not connected")
            raise HTTPException(status_code=404, detail="Server is not connected")

        tool_name = request.toolName
        parameters = request.parameters or {}

        print(f"🔍 [TOOLS/CALL] Tool name: {tool_name}")
        print(f"🔍 [TOOLS/CALL] Parameters: {parameters}")

        if not tool_name:
            print("❌ [TOOLS/CALL] toolName is required but missing")
            raise HTTPException(status_code=400, detail="toolName is required")

        # Make MCP request to call tool
        result = await client.request(
            method="tools/call",
            params={
                "name": tool_name,
                "arguments": parameters
            }
        )

        print(f"📨 [TOOLS/CALL] Raw response from MCP server: {result}")

        # Validate response structure
        if not result:
            print("❌ [TOOLS/CALL] No result returned from MCP server")
        elif 'content' not in result:
            print(f"❌ [TOOLS/CALL] Missing 'content' field in response: {list(result.keys())}")
        elif not isinstance(result['content'], list):
            print(f"❌ [TOOLS/CALL] 'content' field is not an array: {type(result['content'])}")
        else:
            print(f"✅ [TOOLS/CALL] Found {len(result['content'])} content items in response")
            for i, content_item in enumerate(result['content']):
                content_type = content_item.get('type', 'unknown type')
                print(f"  Content {i}: {content_type}")
                if content_type == 'text' and 'text' in content_item:
                    text_content = content_item['text'][:100] + ('...' if len(content_item['text']) > 100 else '')
                    print(f"    ✅ Text content: '{text_content}'")
                else:
                    print(f"    ⚠️  Non-text content: {content_item}")

        return {"result": result}

    except HTTPException:
        raise
    except Exception as e:
        print(f"💥 [TOOLS/CALL] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to call tool on MCP server: {str(e)}")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "AI Assistant Proxy Server", "version": "2.0.0"}

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": time.time()}

if __name__ == "__main__":
    # Start the server
    uvicorn.run(
        "proxy_server:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
