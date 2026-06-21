import subprocess
import os

def launch_vscode(path: str = None) -> str:
    """
    Launches Visual Studio Code. Optionally opens a specific directory or file.
    """
    try:
        command = ["code"]
        if path and os.path.exists(path):
            command.append(path)
            
        # Using subprocess to open without blocking the python daemon
        subprocess.Popen(command, shell=True)
        
        target = f" at {path}" if path else ""
        return f"VSCode successfully launched{target}."
    except Exception as e:
        return f"Failed to launch VSCode. Ensure 'code' is in your system PATH. Error: {str(e)}"

def launch_terminal() -> str:
    """
    Launches a new Windows Terminal instance.
    """
    try:
        subprocess.Popen(["wt.exe"], shell=True)
        return "Windows Terminal launched."
    except Exception as e:
        return f"Failed to launch Windows Terminal. Error: {str(e)}"
