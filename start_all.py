import subprocess

# Define the different commands
commands = [
    'start cmd /k "%venv% && python -m http.server"',  # Start Http.server
    'start cmd /k "%venv% && cd ..\whisper-api-server && python main.py"',  # Start Whisper
    'start cmd /k "%venv% && autogenstudio serve --team team-config.json --port 8084"',  # Start executable with parameter
    'start cmd /k "cd mcp-browser-use && uv --directory . run mcp-server-browser-use"',  # Start MCP Browser Use Server
    'start cmd /k "C:\\Users\\andyj\\AI_assistant\\venv312\\Scripts\\python start_mcp_browser_server.py"',  # Start Browser Server Flask APIs
    'start cmd /k "C:\\Users\\andyj\\AI_assistant\\venv312\\Scripts\\python C:\\Users\\andyj\\AI_assistant\\proxy_server.py"'  # Start Proxy server
]

# Start all processes in separate command windows
processes = []
for cmd in commands:
    process = subprocess.Popen(cmd, shell=True)
    processes.append(process)

print("All processes have been started.")
