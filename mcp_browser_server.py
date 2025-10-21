#!/usr/bin/env python3
"""
HTTP Server for MCP Browser-Use Integration
Provides REST API endpoints for the frontend to interact with MCP browser tools.
This server acts as a bridge between HTTP requests and the MCP protocol.
"""
import asyncio
import json
import logging
import os
from typing import Optional
from pathlib import Path

# Import Flask for creating HTTP server endpoints
from flask import Flask, request, jsonify
from flask_cors import CORS

# Import our MCP browser client wrapper
from mcp_browser_client import MCPBrowserClient

# Configure logging for the HTTP server
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask application instance
app = Flask(__name__)
# Enable CORS for all routes to allow frontend access
CORS(app)

# Global client instance to maintain persistent connection
mcp_client: Optional[MCPBrowserClient] = None


def get_env_config():
    """
    Load environment configuration for the MCP server.
    Reads from environment variables or .env file.
    
    Returns:
        Dictionary of configuration values for MCP server.
    """
    config = {
        # LLM Provider Configuration - specify which AI model to use
        "MCP_LLM_PROVIDER": os.environ.get("MCP_LLM_PROVIDER", "google"),
        "MCP_LLM_MODEL_NAME": os.environ.get("MCP_LLM_MODEL_NAME", "gemini-2.0-flash-exp"),
        
        # API Keys - credentials for AI providers
        "MCP_LLM_GOOGLE_API_KEY": os.environ.get("GOOGLE_API_KEY", ""),
        "MCP_LLM_OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY", ""),
        "MCP_LLM_ANTHROPIC_API_KEY": os.environ.get("ANTHROPIC_API_KEY", ""),
        
        # Browser Configuration - how the browser should behave
        "MCP_BROWSER_HEADLESS": os.environ.get("MCP_BROWSER_HEADLESS", "true"),
        "MCP_BROWSER_DISABLE_SECURITY": os.environ.get("MCP_BROWSER_DISABLE_SECURITY", "false"),
        "MCP_BROWSER_KEEP_OPEN": os.environ.get("MCP_BROWSER_KEEP_OPEN", "false"),
        
        # Research Tool Configuration - where to save research outputs
        "MCP_RESEARCH_TOOL_SAVE_DIR": os.environ.get("MCP_RESEARCH_TOOL_SAVE_DIR", "./research_output"),
        
        # Agent Tool Configuration - control agent behavior
        "MCP_AGENT_TOOL_MAX_STEPS": os.environ.get("MCP_AGENT_TOOL_MAX_STEPS", "100"),
        "MCP_AGENT_TOOL_USE_VISION": os.environ.get("MCP_AGENT_TOOL_USE_VISION", "true"),
        
        # Server Configuration - logging and telemetry settings
        "MCP_SERVER_LOGGING_LEVEL": os.environ.get("MCP_SERVER_LOGGING_LEVEL", "INFO"),
    }
    
    # Log which provider and model are being used
    logger.info(f"Using LLM Provider: {config['MCP_LLM_PROVIDER']}, Model: {config['MCP_LLM_MODEL_NAME']}")
    return config


async def get_or_create_client():
    """
    Get or create the global MCP client instance.
    Maintains a persistent connection to improve performance.
    
    Returns:
        MCPBrowserClient instance.
    """
    global mcp_client
    
    # Check if client exists and is connected
    if mcp_client is None or mcp_client.session is None:
        logger.info("Creating new MCP client connection...")
        # Load environment configuration
        env_config = get_env_config()
        
        # Determine mcp-browser-use directory
        mcp_browser_use_dir = os.environ.get(
            'MCP_BROWSER_USE_DIR',
            str(Path(__file__).parent / "mcp-browser-use")
        )
        
        # Create new client instance with configuration
        # use_uv=True is the default and recommended approach
        mcp_client = MCPBrowserClient(
            env_vars=env_config,
            use_uv=True,
            mcp_browser_use_dir=mcp_browser_use_dir
        )
        # Establish connection to MCP server
        await mcp_client.connect()
    
    return mcp_client


@app.route('/api/browser-agent', methods=['POST'])
def browser_agent_endpoint():
    """
    HTTP endpoint for run_browser_agent tool.
    
    Request body:
        {
            "task": "Natural language description of task"
        }
    
    Response:
        {
            "success": true/false,
            "result": "Result text from agent",
            "error": "Error message if failed"
        }
    """
    try:
        # Parse JSON request body
        data = request.get_json()
        
        # Validate required parameters
        if not data or 'task' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required parameter: task'
            }), 400
        
        # Extract task from request
        task = data['task']
        logger.info(f"Received browser-agent request: {task[:100]}...")
        
        # Run async function in event loop
        async def run_task():
            client = await get_or_create_client()
            return await client.run_browser_agent(task)
        
        # Execute the task and get result
        result = asyncio.run(run_task())
        
        # Return success response
        return jsonify({
            'success': True,
            'result': result
        })
    
    except Exception as e:
        # Log and return error response
        logger.error(f"Error in browser-agent endpoint: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/deep-research', methods=['POST'])
def deep_research_endpoint():
    """
    HTTP endpoint for run_deep_research tool.
    
    Request body:
        {
            "research_task": "Research topic description",
            "max_parallel_browsers": 3  // optional
        }
    
    Response:
        {
            "success": true/false,
            "result": "Research report content",
            "error": "Error message if failed"
        }
    """
    try:
        # Parse JSON request body
        data = request.get_json()
        
        # Validate required parameters
        if not data or 'research_task' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required parameter: research_task'
            }), 400
        
        # Extract parameters from request
        research_task = data['research_task']
        max_parallel_browsers = data.get('max_parallel_browsers', None)
        
        logger.info(f"Received deep-research request: {research_task[:100]}...")
        
        # Run async function in event loop
        async def run_research():
            client = await get_or_create_client()
            return await client.run_deep_research(
                research_task, 
                max_parallel_browsers
            )
        
        # Execute the research and get result
        result = asyncio.run(run_research())
        
        # Return success response
        return jsonify({
            'success': True,
            'result': result
        })
    
    except Exception as e:
        # Log and return error response
        logger.error(f"Error in deep-research endpoint: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify server status.
    
    Response:
        {
            "status": "healthy",
            "mcp_connected": true/false
        }
    """
    # Check if MCP client is connected
    is_connected = mcp_client is not None and mcp_client.session is not None
    
    return jsonify({
        'status': 'healthy',
        'mcp_connected': is_connected
    })


@app.route('/api/disconnect', methods=['POST'])
def disconnect_endpoint():
    """
    Endpoint to manually disconnect the MCP client.
    Useful for cleanup or reconnecting with new configuration.
    
    Response:
        {
            "success": true,
            "message": "Disconnected successfully"
        }
    """
    global mcp_client
    
    try:
        # Disconnect client if it exists
        if mcp_client:
            async def disconnect():
                await mcp_client.disconnect()
            
            asyncio.run(disconnect())
            mcp_client = None
        
        return jsonify({
            'success': True,
            'message': 'Disconnected successfully'
        })
    
    except Exception as e:
        logger.error(f"Error disconnecting: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def main():
    """
    Main entry point for the HTTP server.
    Starts the Flask application on specified host and port.
    """
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5001))
    host = os.environ.get('HOST', '127.0.0.1')
    
    logger.info(f"Starting MCP Browser HTTP Server on {host}:{port}")
    logger.info("Available endpoints:")
    logger.info("  POST /api/browser-agent - Execute browser automation task")
    logger.info("  POST /api/deep-research - Execute deep research task")
    logger.info("  GET  /api/health - Check server health")
    logger.info("  POST /api/disconnect - Disconnect MCP client")
    
    # Create research output directory if it doesn't exist
    research_dir = os.environ.get("MCP_RESEARCH_TOOL_SAVE_DIR", "./research_output")
    Path(research_dir).mkdir(parents=True, exist_ok=True)
    logger.info(f"Research output directory: {research_dir}")
    
    # Start the Flask server
    app.run(host=host, port=port, debug=False)


if __name__ == '__main__':
    main()

