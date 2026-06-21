# backend/core/paths.py
import os
import sys
from pathlib import Path

def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        # When running as compiled executable
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent

def get_data_dir() -> Path:
    """Returns the persistent data directory for Hinata AI."""
    appdata = os.getenv("APPDATA")
    if appdata:
        data_dir = Path(appdata) / "HinataAI" / "data"
    else:
        data_dir = get_base_dir() / "data"
    
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

def get_logs_dir() -> Path:
    """Returns the persistent logs directory for Hinata AI."""
    appdata = os.getenv("APPDATA")
    if appdata:
        logs_dir = Path(appdata) / "HinataAI" / "logs"
    else:
        logs_dir = get_base_dir() / "logs"
    
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir
