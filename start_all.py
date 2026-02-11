import subprocess

# Define the different commands
commands = [
    'start cmd /k "C:\\Users\\andyj\\AI_assistant\\venv312\\Scripts\\python C:\\Users\\andyj\\AI_assistant\\https_server.py"',  # Start HTTPS server (port 8000)
    'start cmd /k "%venv% && cd ..\whisper-api-server && python main.py"',  # Start Whisper
    'start cmd /k "C:\\Users\\andyj\\AI_assistant\\venv312\\Scripts\\python C:\\Users\\andyj\\AI_assistant\\proxy_server.py"',  # Start Proxy server (port 8002 with HTTPS)
    'start cmd /k "%venv% && autogenstudio serve --team team-config.json --host 0.0.0.0 --port 8084"',  # Start executable with parameter
    'start cmd /k "C:\\Users\\andyj\\AI_assistant\\venv312\\Scripts\\python C:\\Users\\andyj\\AI_assistant\\start_mcp_browser_use_http_server.py"',  # Start MCP Browser Use HTTP server (port 8383) with project .env so model matches
    'start cmd /k "C:\\Users\\andyj\\AI_assistant\\venv312\\Scripts\\python start_mcp_browser_server.py"'  # Start Browser Server Flask APIs
]

# Start all processes in separate command windows
processes = []
for cmd in commands:
    process = subprocess.Popen(cmd, shell=True)
    processes.append(process)

print("All processes have been started.")
