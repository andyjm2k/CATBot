import subprocess

# Define the different commands
commands = [
    'start cmd /k "%venv% && python -m http.server"',  # Start Http.server
    'start cmd /k "%venv% && cd ..\whisper-api-server && python main.py"',  # Start Whisper
    'start cmd /k "C:\\Users\\andyj\\AI_assistant\\venv312\\Scripts\\python C:\\Users\\andyj\\AI_assistant\\proxy_server.py"',  # Start Proxy server
    'start cmd /k "%venv% && autogenstudio ui"'  # Start executable with parameter
]

# Start all processes in separate command windows
processes = []
for cmd in commands:
    process = subprocess.Popen(cmd, shell=True)
    processes.append(process)

print("All processes have been started.")
