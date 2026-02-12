import os
import subprocess

# List of process names to terminate
process_names = [
    "python.exe",         # Kills all Python scripts (including http.server and Whisper)
    "node.exe",           # Kills the npm process
    "autogenstudio.exe"   # Kills the Autogen Studio UI process
]

# Kill all specified processes
for process in process_names:
    os.system(f"taskkill /IM {process} /F")

# Ensure no lingering `cmd.exe` windows remain open
os.system('taskkill /IM cmd.exe /F')

print("All processes have been stopped.")
