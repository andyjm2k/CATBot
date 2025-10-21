#!/usr/bin/env python3
"""
Unit Tests for MCP Browser Client Integration
Tests the MCPBrowserClient wrapper and HTTP server endpoints.
Provides comprehensive test coverage for browser automation and research tools.
"""
import unittest
import asyncio
import os
import sys
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import modules to test
from mcp_browser_client import MCPBrowserClient


class TestMCPBrowserClient(unittest.TestCase):
    """
    Unit tests for MCPBrowserClient class.
    Tests initialization, connection, and tool execution.
    """
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create test environment configuration
        self.test_env = {
            "MCP_LLM_PROVIDER": "google",
            "MCP_LLM_MODEL_NAME": "gemini-2.0-flash-exp",
            "MCP_LLM_GOOGLE_API_KEY": "test_api_key",
            "MCP_BROWSER_HEADLESS": "true",
            "MCP_RESEARCH_TOOL_SAVE_DIR": "./test_research_output"
        }
        
        # Create client instance for testing
        self.client = MCPBrowserClient(env_vars=self.test_env)
    
    def test_initialization(self):
        """Test that MCPBrowserClient initializes correctly with environment variables."""
        # Verify client is created
        self.assertIsNotNone(self.client)
        
        # Verify environment variables are set correctly
        self.assertIn("MCP_LLM_PROVIDER", self.client.env_vars)
        self.assertEqual(self.client.env_vars["MCP_LLM_PROVIDER"], "google")
        
        # Verify session starts as None
        self.assertIsNone(self.client.session)
    
    @patch('mcp_browser_client.stdio_client')
    async def test_connect_success(self, mock_stdio):
        """Test successful connection to MCP server."""
        # Mock the stdio client context manager
        mock_read = AsyncMock()
        mock_write = AsyncMock()
        mock_context = AsyncMock()
        mock_context.__aenter__ = AsyncMock(return_value=(mock_read, mock_write))
        mock_context.__aexit__ = AsyncMock()
        mock_stdio.return_value = mock_context
        
        # Mock the session initialization
        with patch('mcp_browser_client.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock()
            mock_session.initialize = AsyncMock()
            
            # Mock tools list response
            mock_tools_result = Mock()
            mock_tool1 = Mock()
            mock_tool1.name = "run_browser_agent"
            mock_tool2 = Mock()
            mock_tool2.name = "run_deep_research"
            mock_tools_result.tools = [mock_tool1, mock_tool2]
            mock_session.list_tools = AsyncMock(return_value=mock_tools_result)
            
            mock_session_class.return_value = mock_session
            
            # Test connection
            result = await self.client.connect()
            
            # Verify connection was successful
            self.assertTrue(result)
            self.assertIsNotNone(self.client.session)
            mock_session.initialize.assert_called_once()
            mock_session.list_tools.assert_called_once()
    
    @patch('mcp_browser_client.stdio_client')
    async def test_run_browser_agent(self, mock_stdio):
        """Test execution of run_browser_agent tool."""
        # Set up mock connection
        mock_read = AsyncMock()
        mock_write = AsyncMock()
        mock_context = AsyncMock()
        mock_context.__aenter__ = AsyncMock(return_value=(mock_read, mock_write))
        mock_context.__aexit__ = AsyncMock()
        mock_stdio.return_value = mock_context
        
        # Mock the session and tool call
        with patch('mcp_browser_client.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock()
            mock_session.initialize = AsyncMock()
            
            # Mock tools list
            mock_tools_result = Mock()
            mock_tool = Mock()
            mock_tool.name = "run_browser_agent"
            mock_tools_result.tools = [mock_tool]
            mock_session.list_tools = AsyncMock(return_value=mock_tools_result)
            
            # Mock tool call result
            mock_result = Mock()
            mock_content = Mock()
            mock_content.text = "Successfully navigated to example.com. Page title: Example Domain"
            mock_result.content = [mock_content]
            mock_session.call_tool = AsyncMock(return_value=mock_result)
            
            mock_session_class.return_value = mock_session
            
            # Connect and run browser agent
            await self.client.connect()
            result = await self.client.run_browser_agent("Go to example.com and get the title")
            
            # Verify the call was made correctly
            mock_session.call_tool.assert_called_once_with(
                "run_browser_agent", 
                {"task": "Go to example.com and get the title"}
            )
            
            # Verify result is correct
            self.assertIn("Example Domain", result)
    
    @patch('mcp_browser_client.stdio_client')
    async def test_run_deep_research(self, mock_stdio):
        """Test execution of run_deep_research tool."""
        # Set up mock connection
        mock_read = AsyncMock()
        mock_write = AsyncMock()
        mock_context = AsyncMock()
        mock_context.__aenter__ = AsyncMock(return_value=(mock_read, mock_write))
        mock_context.__aexit__ = AsyncMock()
        mock_stdio.return_value = mock_context
        
        # Mock the session and tool call
        with patch('mcp_browser_client.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock()
            mock_session.initialize = AsyncMock()
            
            # Mock tools list
            mock_tools_result = Mock()
            mock_tool = Mock()
            mock_tool.name = "run_deep_research"
            mock_tools_result.tools = [mock_tool]
            mock_session.list_tools = AsyncMock(return_value=mock_tools_result)
            
            # Mock tool call result
            mock_result = Mock()
            mock_content = Mock()
            mock_content.text = "# Research Report\n\nFindings about AI developments in 2024..."
            mock_result.content = [mock_content]
            mock_session.call_tool = AsyncMock(return_value=mock_result)
            
            mock_session_class.return_value = mock_session
            
            # Connect and run deep research
            await self.client.connect()
            result = await self.client.run_deep_research(
                "What are the latest AI developments in 2024?",
                max_parallel_browsers=3
            )
            
            # Verify the call was made correctly with parameters
            mock_session.call_tool.assert_called_once_with(
                "run_deep_research",
                {
                    "research_task": "What are the latest AI developments in 2024?",
                    "max_parallel_browsers_override": 3
                }
            )
            
            # Verify result contains research report
            self.assertIn("Research Report", result)
    
    async def test_disconnect(self):
        """Test disconnection cleanup."""
        # Mock session
        mock_session = AsyncMock()
        mock_session.__aexit__ = AsyncMock()
        self.client.session = mock_session
        
        # Mock context
        mock_context = AsyncMock()
        mock_context.__aexit__ = AsyncMock()
        self.client._client_context = mock_context
        
        # Test disconnection
        await self.client.disconnect()
        
        # Verify cleanup was performed
        mock_session.__aexit__.assert_called_once()
        mock_context.__aexit__.assert_called_once()
        self.assertIsNone(self.client.session)
    
    def test_context_manager_protocol(self):
        """Test that client can be used as async context manager."""
        # Verify context manager methods exist
        self.assertTrue(hasattr(self.client, '__aenter__'))
        self.assertTrue(hasattr(self.client, '__aexit__'))


class TestMCPBrowserServerEndpoints(unittest.TestCase):
    """
    Unit tests for HTTP server endpoints.
    Tests Flask routes and request handling.
    """
    
    @patch('mcp_browser_server.MCPBrowserClient')
    @patch('mcp_browser_server.get_or_create_client')
    def test_browser_agent_endpoint_success(self, mock_get_client, mock_client_class):
        """Test successful browser agent endpoint call."""
        # Import Flask app
        from mcp_browser_server import app
        
        # Mock client and response
        mock_client = AsyncMock()
        mock_client.run_browser_agent = AsyncMock(
            return_value="Page title: Example Domain"
        )
        mock_get_client.return_value = mock_client
        
        # Create test client
        with app.test_client() as client:
            # Mock asyncio.run to execute async function
            with patch('mcp_browser_server.asyncio.run') as mock_run:
                mock_run.return_value = "Page title: Example Domain"
                
                # Make POST request to endpoint
                response = client.post(
                    '/api/browser-agent',
                    json={'task': 'Go to example.com and get title'},
                    content_type='application/json'
                )
                
                # Verify response is successful
                self.assertEqual(response.status_code, 200)
                data = response.get_json()
                self.assertTrue(data['success'])
                self.assertIn('Example Domain', data['result'])
    
    @patch('mcp_browser_server.MCPBrowserClient')
    @patch('mcp_browser_server.get_or_create_client')
    def test_deep_research_endpoint_success(self, mock_get_client, mock_client_class):
        """Test successful deep research endpoint call."""
        # Import Flask app
        from mcp_browser_server import app
        
        # Mock client and response
        mock_client = AsyncMock()
        mock_client.run_deep_research = AsyncMock(
            return_value="# Research Report\n\nFindings..."
        )
        mock_get_client.return_value = mock_client
        
        # Create test client
        with app.test_client() as client:
            # Mock asyncio.run
            with patch('mcp_browser_server.asyncio.run') as mock_run:
                mock_run.return_value = "# Research Report\n\nFindings..."
                
                # Make POST request to endpoint
                response = client.post(
                    '/api/deep-research',
                    json={
                        'research_task': 'AI developments 2024',
                        'max_parallel_browsers': 3
                    },
                    content_type='application/json'
                )
                
                # Verify response is successful
                self.assertEqual(response.status_code, 200)
                data = response.get_json()
                self.assertTrue(data['success'])
                self.assertIn('Research Report', data['result'])
    
    def test_browser_agent_endpoint_missing_task(self):
        """Test browser agent endpoint with missing task parameter."""
        # Import Flask app
        from mcp_browser_server import app
        
        # Create test client
        with app.test_client() as client:
            # Make POST request without task
            response = client.post(
                '/api/browser-agent',
                json={},
                content_type='application/json'
            )
            
            # Verify error response
            self.assertEqual(response.status_code, 400)
            data = response.get_json()
            self.assertFalse(data['success'])
            self.assertIn('Missing required parameter', data['error'])
    
    def test_health_check_endpoint(self):
        """Test health check endpoint returns status."""
        # Import Flask app
        from mcp_browser_server import app
        
        # Create test client
        with app.test_client() as client:
            # Make GET request to health endpoint
            response = client.get('/api/health')
            
            # Verify response
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertIn('status', data)
            self.assertIn('mcp_connected', data)


def run_async_test(coro):
    """Helper function to run async tests."""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)

