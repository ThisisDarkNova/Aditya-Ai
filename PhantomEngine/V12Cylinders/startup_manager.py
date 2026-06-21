# modules/startup_manager.py
"""
Startup Manager for Aditya.
Uses the Windows Registry (HKCU Run) to register Aditya for auto-start.
Supports startup delay and launch options (like minimized to system tray).
"""

from __future__ import annotations

import sys
import os
import time
import logging
import threading
from pathlib import Path
from V12Cylinders.settings_manager import settings

logger = logging.getLogger("aditya-startup")
logger.setLevel(logging.INFO)

# Set up logging handler
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[🚀 Startup] %(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
KEY_NAME = "Aditya"

def get_startup_command() -> str:
    """
    Get the command-line string to launch Aditya, prioritizing ADITYA.exe if packaged.
    """
    if getattr(sys, "frozen", False):
        # In production (PyInstaller frozen), AdityaCore.exe is inside 'resources/' of the NSIS install
        base_dir = Path(sys.executable).resolve().parent
        if base_dir.name == "resources":
            exe_path = base_dir.parent / "ADITYA.exe"
            if exe_path.exists():
                return f'"{exe_path.resolve()}" --startup'
        return f'"{sys.executable}" --no-ui --startup'
    else:
        # Development fallback
        project_root = Path(__file__).resolve().parent.parent.parent
        python_exe = sys.executable.replace("python.exe", "pythonw.exe")
        script_path = project_root / "backend" / "main.py"
        return f'"{python_exe}" "{script_path.resolve()}" --no-ui --startup'

def set_registry_run_key(enable: bool) -> bool:
    """
    Write or delete the HKCU Run registry value.
    """
    if os.name != "nt":
        logger.warning("Startup Manager is only supported on Windows.")
        return False
        
    import winreg
    cmd = get_startup_command()
    
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, KEY_PATH, 0, winreg.KEY_SET_VALUE)
        if enable:
            winreg.SetValueEx(key, KEY_NAME, 0, winreg.REG_SZ, cmd)
            logger.info(f"Registry entry set: {KEY_NAME} = {cmd}")
        else:
            try:
                winreg.DeleteValue(key, KEY_NAME)
                logger.info(f"Registry entry deleted: {KEY_NAME}")
            except FileNotFoundError:
                pass # Already deleted
        winreg.CloseKey(key)
        return True
    except Exception as e:
        logger.error(f"Failed to modify registry startup: {e}")
        return False

def enable_startup(enable: bool) -> bool:
    """
    Toggle startup state both in settings and the registry.
    """
    success = set_registry_run_key(enable)
    if success:
        settings.set("startup_enabled", enable)
    return success

def sync_startup_with_registry() -> None:
    """
    Ensure the Windows Registry matches the user settings configuration.
    """
    enabled = settings.get("startup_enabled", False)
    set_registry_run_key(enabled)

def handle_delayed_startup() -> None:
    """
    If '--startup' is passed, sleeps for the configured delay period.
    """
    if "--startup" in sys.argv:
        delay = settings.get("startup_delay_seconds", 15)
        logger.info(f"Aditya launched via Windows startup. Delaying boot by {delay} seconds...")
        time.sleep(delay)
        logger.info("Delay finished. Proceeding with boot sequence.")
