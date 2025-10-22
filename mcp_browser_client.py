#!/usr/bin/env python3
"""
MCP Browser-Use Client Wrapper
Provides HTTP endpoints to interact with the MCP browser-use server tools.
This module acts as a bridge between the frontend and the MCP server.
"""
import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging for this module
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import MCP client libraries for communication with the server
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPBrowserClient:
    """
    Client class to interact with the MCP browser-use server.
    Provides methods to call run_browser_agent and run_deep_research tools.
    """
    
    def __init__(
        self, 
        server_script_path: str = None, 
        env_vars: Dict[str, str] = None,
        use_uv: bool = True,
        mcp_browser_use_dir: str = None
    ):
        """
        Initialize the MCP Browser Client.
        
        Args:
            server_script_path: Path to the MCP server script. Defaults to mcp-browser-use server.
            env_vars: Dictionary of environment variables to pass to the server process.
            use_uv: Whether to use uv package manager (default: True, recommended)
            mcp_browser_use_dir: Directory containing mcp-browser-use installation
        """
        # Set default mcp-browser-use directory
        if mcp_browser_use_dir is None:
            mcp_browser_use_dir = str(Path(__file__).parent / "mcp-browser-use")
        
        self.mcp_browser_use_dir = mcp_browser_use_dir
        self.use_uv = use_uv
        self.server_script_path = server_script_path
        
        # Merge provided env vars with current environment
        self.env_vars = os.environ.copy()
        if env_vars:
            self.env_vars.update(env_vars)
        
        # Client session will be created when needed
        self.session: Optional[ClientSession] = None
        self.read_stream = None
        self.write_stream = None
        self._client_context = None
        
        if self.use_uv:
            logger.info(f"MCPBrowserClient initialized using uv in directory: {self.mcp_browser_use_dir}")
        else:
            logger.info(f"MCPBrowserClient initialized with server script: {self.server_script_path}")
    
    async def connect(self):
        """
        Establish connection to the MCP server.
        Creates a stdio client session for communication.
        """
        try:
            # Configure server parameters for the MCP browser-use server
            if self.use_uv:
                # Use uv to run the mcp-server-browser-use command (recommended)
                # This matches the official mcp-browser-use project setup
                server_params = StdioServerParameters(
                    command="uv",
                    args=["--directory", self.mcp_browser_use_dir, "run", "mcp-server-browser-use"],
                    env=self.env_vars
                )
                logger.info("Connecting to MCP browser-use server using uv...")
            else:
                # Fallback: Use standard Python module execution
                server_params = StdioServerParameters(
                    command=sys.executable,
                    args=["-m", "mcp_server_browser_use"],  # Run as module
                    env=self.env_vars
                )
                logger.info("Connecting to MCP browser-use server using Python module...")
            
            # Create stdio client and establish session
            self._client_context = stdio_client(server_params)
            self.read_stream, self.write_stream = await self._client_context.__aenter__()
            
            # Create and initialize the client session
            self.session = ClientSession(self.read_stream, self.write_stream)
            await self.session.__aenter__()
            await self.session.initialize()
            
            logger.info("Successfully connected to MCP server")
            
            # List available tools to verify connection
            tools_result = await self.session.list_tools()
            available_tools = [tool.name for tool in tools_result.tools]
            logger.info(f"Available tools: {available_tools}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            if self.use_uv:
                logger.error("Hint: Make sure 'uv' is installed and available in PATH")
                logger.error("Install with: pip install uv")
            raise
    
    async def disconnect(self):
        """
        Close the connection to the MCP server.
        Properly cleanup resources.
        """
        try:
            # Close the session and client context
            if self.session:
                await self.session.__aexit__(None, None, None)
                self.session = None
            
            if self._client_context:
                await self._client_context.__aexit__(None, None, None)
                self._client_context = None
            
            logger.info("Disconnected from MCP server")
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
    
    async def run_browser_agent(self, task: str) -> str:
        """
        Execute a browser automation task using natural language.
        
        Args:
            task: Natural language description of the task to perform.
        
        Returns:
            Result of the browser automation task as a string.
        """
        # Ensure connection is established
        if not self.session:
            await self.connect()
        
        try:
            logger.info(f"Calling run_browser_agent with task: {task[:100]}...")
            # Call the run_browser_agent tool via MCP protocol
            result = await self.session.call_tool("run_browser_agent", {"task": task})
            
            # Extract text content from the result
            if result and hasattr(result, 'content') and len(result.content) > 0:
                response_text = result.content[0].text if hasattr(result.content[0], 'text') else str(result.content[0])
                logger.info(f"Browser agent completed successfully")
                return response_text
            else:
                logger.warning("Browser agent returned empty result")
                return "Browser agent completed but returned no content."
        
        except Exception as e:
            logger.error(f"Error in run_browser_agent: {e}")
            return f"Error: {str(e)}"
    
    async def run_deep_research(
        self, 
        research_task: str, 
        max_parallel_browsers: Optional[int] = None
    ) -> str:
        """
        Execute a deep research task with multi-step web research.
        
        Args:
            research_task: Description of the research topic.
            max_parallel_browsers: Optional override for max parallel browser instances.
        
        Returns:
            Research report content as a string.
        """
        # Ensure connection is established
        if not self.session:
            await self.connect()
        
        try:
            logger.info(f"Calling run_deep_research with task: {research_task[:100]}...")
            
            # Prepare arguments for the tool call
            args = {"research_task": research_task}
            if max_parallel_browsers is not None:
                args["max_parallel_browsers_override"] = max_parallel_browsers
            
            # Call the run_deep_research tool via MCP protocol
            result = await self.session.call_tool("run_deep_research", args)
            
            # Extract text content from the result
            if result and hasattr(result, 'content') and len(result.content) > 0:
                response_text = result.content[0].text if hasattr(result.content[0], 'text') else str(result.content[0])
                logger.info(f"Deep research completed successfully")
                return response_text
            else:
                logger.warning("Deep research returned empty result")
                return "Deep research completed but returned no content."
        
        except Exception as e:
            logger.error(f"Error in run_deep_research: {e}")
            return f"Error: {str(e)}"
    
    async def __aenter__(self):
        """Context manager entry - establish connection."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup connection."""
        await self.disconnect()


async def test_client():
    """
    Test function to verify the MCP browser client functionality.
    Demonstrates usage of both browser agent and deep research tools.
    """
    # Example environment configuration
    env_config = {
        "MCP_LLM_PROVIDER": "google",
        "MCP_LLM_MODEL_NAME": "gemini-2.0-flash-exp",
        "MCP_LLM_GOOGLE_API_KEY": os.environ.get("GOOGLE_API_KEY", ""),
        "MCP_BROWSER_HEADLESS": "true",
        "MCP_RESEARCH_TOOL_SAVE_DIR": "./research_output"
    }
    
    # Use async context manager for automatic cleanup
    # use_uv=True is the default and recommended approach
    async with MCPBrowserClient(env_vars=env_config, use_uv=True) as client:
        # Test browser agent
        print("\n=== Testing Browser Agent ===")
        agent_result = await client.run_browser_agent(
            "Navigate to example.com and tell me the page title"
        )
        print(f"Agent Result: {agent_result}")
        
        # Test deep research
        print("\n=== Testing Deep Research ===")
        research_result = await client.run_deep_research(
            "What are the latest developments in AI in 2024?"
        )
        print(f"Research Result: {research_result[:500]}...")


if __name__ == "__main__":
    # Run the test when executed directly
    asyncio.run(test_client())

