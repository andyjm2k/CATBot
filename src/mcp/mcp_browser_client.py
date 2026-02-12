#!/usr/bin/env python3
"""
MCP Browser-Use Client Wrapper (HTTP transport).
Provides a client to interact with the mcp-server-browser-use HTTP server tools.
Requires the HTTP server to be running: uv run mcp-server-browser-use server (in mcp-browser-use directory).
"""
import asyncio
import logging
import os
from typing import Any, Dict, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging for this module
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Default URL for the browser-use HTTP MCP server (must be started separately)
DEFAULT_BROWSER_USE_HTTP_URL = "http://127.0.0.1:8383/mcp"


def _get_browser_use_http_url() -> str:
    """Return the browser-use HTTP MCP endpoint URL from env or default."""
    return os.environ.get("MCP_BROWSER_USE_HTTP_URL", DEFAULT_BROWSER_USE_HTTP_URL).strip()


def _content_to_text(result: Any) -> str:
    """Extract text from FastMCP call_tool result.content (list of content items)."""
    if not result or not getattr(result, "content", None):
        return "Browser agent completed but returned no content."
    content = result.content
    if not content:
        return "Browser agent completed but returned no content."
    parts = []
    for item in content:
        if hasattr(item, "text"):
            parts.append(item.text)
        else:
            parts.append(str(item))
    return "\n".join(parts) if parts else "Browser agent completed but returned no content."


class MCPBrowserClient:
    """
    Client to interact with the MCP browser-use HTTP server.
    Uses FastMCP Client to call run_browser_agent and run_deep_research tools.
    """

    def __init__(
        self,
        server_script_path: Optional[str] = None,
        env_vars: Optional[Dict[str, str]] = None,
        use_uv: bool = True,
        mcp_browser_use_dir: Optional[str] = None,
        http_url: Optional[str] = None,
    ):
        """
        Initialize the MCP Browser Client (HTTP mode).

        Args:
            server_script_path: Unused; kept for API compatibility.
            env_vars: Unused for HTTP; server uses its own config. Kept for compatibility.
            use_uv: Unused; kept for API compatibility.
            mcp_browser_use_dir: Unused; kept for API compatibility.
            http_url: Override URL for the browser-use HTTP server (default: MCP_BROWSER_USE_HTTP_URL env or 127.0.0.1:8383/mcp).
        """
        self._http_url = (http_url or _get_browser_use_http_url()).strip()
        logger.info("MCPBrowserClient initialized (HTTP) for %s", self._http_url)

    async def connect(self) -> bool:
        """
        Verify the HTTP server is reachable by listing tools.
        No persistent connection; each tool call uses a new HTTP request.
        """
        try:
            from fastmcp import Client

            async with Client(self._http_url) as client:
                tools = await client.list_tools()
                names = [t.name for t in tools]
                logger.info("Successfully connected to MCP server; tools: %s", names)
            return True
        except Exception as e:
            logger.error("Failed to connect to MCP server: %s", e)
            logger.error(
                "Hint: Start the HTTP server with: uv run mcp-server-browser-use server (in mcp-browser-use directory)"
            )
            raise

    async def disconnect(self) -> None:
        """
        No-op for HTTP mode; no persistent connection to close.
        """
        logger.debug("Disconnect (no-op for HTTP mode)")

    async def run_browser_agent(self, task: str) -> str:
        """
        Execute a browser automation task using natural language.

        Args:
            task: Natural language description of the task to perform.

        Returns:
            Result of the browser automation task as a string.
        """
        from fastmcp import Client

        try:
            logger.info("Calling run_browser_agent with task: %s...", task[:100])
            async with Client(self._http_url) as client:
                result = await client.call_tool("run_browser_agent", {"task": task})
            if getattr(result, "is_error", False):
                return "Error: " + _content_to_text(result)
            logger.info("Browser agent completed successfully")
            return _content_to_text(result)
        except Exception as e:
            logger.error("Error in run_browser_agent: %s", e)
            return "Error: " + str(e)

    async def run_deep_research(
        self,
        research_task: str,
        max_parallel_browsers: Optional[int] = None,
    ) -> str:
        """
        Execute a deep research task with multi-step web research.

        Args:
            research_task: Description of the research topic.
            max_parallel_browsers: Optional override (reserved; upstream MCP uses 'topic' only).

        Returns:
            Research report content as a string.
        """
        from fastmcp import Client

        # Upstream MCP server (mcp-server-browser-use) expects 'topic', not 'research_task'
        args: Dict[str, Any] = {"topic": research_task}
        # Do not send max_parallel_browsers_override; upstream tool schema does not include it

        try:
            logger.info("Calling run_deep_research with task: %s...", research_task[:100])
            async with Client(self._http_url) as client:
                result = await client.call_tool("run_deep_research", args)
            if getattr(result, "is_error", False):
                return "Error: " + _content_to_text(result)
            logger.info("Deep research completed successfully")
            return _content_to_text(result)
        except Exception as e:
            logger.error("Error in run_deep_research: %s", e)
            return "Error: " + str(e)

    async def __aenter__(self) -> "MCPBrowserClient":
        """Context manager entry - verify server is reachable."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit - no-op for HTTP."""
        await self.disconnect()


async def test_client() -> None:
    """
    Test the MCP browser client (HTTP).
    Ensure mcp-server-browser-use server is running first.
    """
    async with MCPBrowserClient() as client:
        print("\n=== Testing Browser Agent ===")
        agent_result = await client.run_browser_agent(
            "Navigate to example.com and tell me the page title"
        )
        print("Agent Result:", agent_result[:500] if len(agent_result) > 500 else agent_result)

        print("\n=== Testing Deep Research ===")
        research_result = await client.run_deep_research(
            "What are the latest developments in AI in 2024?"
        )
        print(
            "Research Result:",
            research_result[:500] + "..." if len(research_result) > 500 else research_result,
        )


if __name__ == "__main__":
    asyncio.run(test_client())
