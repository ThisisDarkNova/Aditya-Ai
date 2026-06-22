# modules/settings_manager.py
"""
Thread-safe settings manager for Vespera.
Saves settings to data/settings.json, maintaining a backup settings.json.bak
and automatically recovering from corrupted configurations.
"""

from __future__ import annotations

import json
import os
import shutil
import logging
import threading
from pathlib import Path
from typing import Any

logger = logging.getLogger("vespera-settings")
logger.setLevel(logging.INFO)

# Set up standard logging handler if not already present
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[⚙️ Settings] %(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

from NeuralCore.paths import get_data_dir

_DATA_DIR = get_data_dir()
_SETTINGS_PATH = _DATA_DIR / "settings.json"
_BACKUP_PATH = _DATA_DIR / "settings.json.bak"

DEFAULT_SETTINGS: dict[str, Any] = {
    "startup_enabled": False,
    "startup_delay_seconds": 15,
    "start_minimized": True,
    "launch_directly_voice": True,
    "restore_last_session": True,
    "wake_word_enabled": False,
    "wake_word": "Hey Nova",
    "hotkey_enabled": True,
    "hotkey_sequence": "ctrl+alt+j",
    "mic_permission_granted": False,
    "gaming_mode": {
        "enabled": True,
        "auto_detect_games": True,
        "suppress_notifications": True,
        "valorant_priority": True,
    },
    # Models
    "model_name": "gemini-2.0-flash-exp",
    "temperature": 0.7,
    "api_key": "",
    # VesperaMemoryEngine
    "memory_enabled": True,
    "memory_depth": 100,
    # Agents
    "agent_swarm_enabled": False,
    "max_agent_loops": 10,
    # Automation
    "allow_macros": True,
    "auto_backup": True,
    # Appearance
    "theme": "glass",
    "font_size": 14,
    "reduce_motion": False,
    "high_contrast": False,
    # Developer
    "debug_mode": False,
    "port": 7865,
    "clap_sensitivity": 0.5,
    "launch_on_startup": False,
    "notifications_enabled": True,
    "mic_muted": False,
    "vision_active": False,
}

class SettingsManager:
    """
    Centralized, thread-safe, and crash-resilient manager for Vespera's settings.
    """
    def __init__(self, path: Path = _SETTINGS_PATH, backup_path: Path = _BACKUP_PATH) -> None:
        self.path = path
        self.backup_path = backup_path
        self._lock = threading.RLock()
        
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        
        self._settings = {}
        self.load()

    def load(self) -> None:
        """
        Load settings from disk. Gracefully falls back to backup if corrupted,
        and uses defaults if backup fails or is missing.
        """
        with self._lock:
            loaded_ok = False
            
            # 1. Try loading main settings file
            if self.path.exists():
                try:
                    with open(self.path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if isinstance(data, dict):
                        self._settings = data
                        loaded_ok = True
                        logger.info("Settings loaded successfully.")
                except Exception as e:
                    logger.error(f"Error loading settings file: {e}. Attempting recovery from backup.")

            # 2. Try loading backup if main failed
            if not loaded_ok and self.backup_path.exists():
                try:
                    with open(self.backup_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if isinstance(data, dict):
                        self._settings = data
                        loaded_ok = True
                        logger.info("Settings recovered successfully from backup.")
                        # Attempt to heal main file
                        self.save()
                except Exception as e:
                    logger.critical(f"Backup settings file corrupted: {e}")

            # 3. Fallback to defaults if both failed
            if not loaded_ok:
                logger.warning("Initializing settings to default values.")
                self._settings = dict(DEFAULT_SETTINGS)
                self.save()

            # Clean and validate settings against the schema
            from V12Cylinders.vespera_safety import validate_settings_dict
            self._settings = validate_settings_dict(self._settings, DEFAULT_SETTINGS)
            self.save()


    def save(self) -> None:
        """
        Save settings to disk and maintain a backup copy.
        """
        import time
        with self._lock:
            temp_path = self.path.with_suffix(f".tmp_{threading.get_ident()}")
            for attempt in range(5):
                try:
                    # Write to temp file first to prevent corruption on sudden power failure
                    with open(temp_path, "w", encoding="utf-8") as f:
                        json.dump(self._settings, f, indent=4, ensure_ascii=False)
                    
                    # Atomically replace main settings file
                    if os.path.exists(self.path):
                        try:
                            os.remove(self.path)
                        except FileNotFoundError:
                            pass
                    os.rename(temp_path, self.path)
                    
                    # Clone the latest settings to backup
                    shutil.copy2(self.path, self.backup_path)
                    
                    # Success, exit retry loop
                    return
                except PermissionError as e:
                    if attempt < 4:
                        time.sleep(0.01 * (attempt + 1))
                    else:
                        logger.error(f"Failed to save settings after retries: {e}")
                except Exception as e:
                    logger.error(f"Failed to save settings: {e}")
                    break
                finally:
                    if os.path.exists(temp_path):
                        try:
                            os.remove(temp_path)
                        except Exception:
                            pass

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a settings value.
        """
        with self._lock:
            return self._settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set a settings value and save immediately.
        """
        with self._lock:
            # Enforce validation bounds for numeric entries
            if key == "startup_delay_seconds":
                value = max(10, min(30, int(value)))
                
            self._settings[key] = value
            self.save()
            logger.info(f"Setting updated: {key} = {value}")

    def get_all(self) -> dict[str, Any]:
        """
        Get a copy of all settings.
        """
        with self._lock:
            return dict(self._settings)

# Global instance for seamless usage
settings = SettingsManager()
