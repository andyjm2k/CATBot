#!/usr/bin/env python3
"""
Wrapper script to start the browser-use MCP server using the command line interface.
This should be more compatible with the MCP protocol.
"""
import os
import sys
import subprocess

def main():
    """Start the browser-use MCP server using the command line interface."""

    # Set environment variables
    env = os.environ.copy()

    # API Keys - check environment variables
    api_keys = {
        'GEMINI_API_KEY': env.get('GEMINI_API_KEY'),
        'OPENAI_API_KEY': env.get('OPENAI_API_KEY'),
        'ANTHROPIC_API_KEY': env.get('ANTHROPIC_API_KEY'),
    }

    # Set default API key if none provided
    if not any(api_keys.values()):
        print("Warning: No API key environment variables found")
        print("Please set one of: GEMINI_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY")
        print("Example: export GEMINI_API_KEY='your-key-here'")
    else:
        print(f"Using API keys: {[k for k, v in api_keys.items() if v]}")

    # Model configuration
    model = env.get('BROWSER_USE_MODEL', 'gpt-4o-mini')
    print(f"Using model: {model}")

    # Browser configuration
    env.setdefault('BROWSER_USE_HEADLESS', 'true')
    env.setdefault('BROWSER_USE_DISABLE_SECURITY', 'false')

    print(f"Browser config: headless={env['BROWSER_USE_HEADLESS']}, disable_security={env['BROWSER_USE_DISABLE_SECURITY']}")

    # Try to start the browser-use MCP server using uvx
    try:
        # Use uvx to run browser-use with MCP flag
        cmd = ['uvx', 'browser-use', '--mcp']
        print(f"Starting browser-use MCP server with command: {' '.join(cmd)}")

        # Start the subprocess
        process = subprocess.run(cmd, env=env, check=True)
        print("Browser-use MCP server exited successfully")

    except subprocess.CalledProcessError as e:
        print(f"Browser-use MCP server failed with exit code: {e.returncode}")
        sys.exit(e.returncode)
    except FileNotFoundError:
        print("Error: uvx not found. Trying alternative method...")
        # Fallback to python -m approach
        try:
            cmd = [sys.executable, '-m', 'browser_use.mcp']
            print(f"Trying with python -m: {' '.join(cmd)}")
            process = subprocess.run(cmd, env=env, check=True)
            print("Browser-use MCP server exited successfully")
        except subprocess.CalledProcessError as e:
            print(f"Browser-use MCP server failed with exit code: {e.returncode}")
            sys.exit(e.returncode)
        except FileNotFoundError:
            print("Error: browser_use.mcp module not found")
            print("Make sure browser-use is installed correctly")
            sys.exit(1)

if __name__ == "__main__":
    main()
