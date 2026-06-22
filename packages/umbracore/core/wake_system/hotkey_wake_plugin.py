# core/wake_system/hotkey_wake_plugin.py
"""
Hotkey wake plugin. Listens for a global hotkey sequence (e.g. Ctrl+Alt+J)
using the keyboard library.
"""

from __future__ import annotations

import logging
import threading
from typing import Callable
from core.wake_system.base_wake_plugin import BaseWakePlugin
from core.settings_manager import settings

logger = logging.getLogger("vespera-wake-hotkey")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[🎯 Hotkey Listener] %(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class HotkeyWakePlugin(BaseWakePlugin):
    """
    Modular keyboard hotkey wake plugin.
    """
    def __init__(self, on_wake_callback: Callable[[], None]) -> None:
        super().__init__("Hotkey Trigger", on_wake_callback)
        self._lock = threading.Lock()
        self._keyboard_module = None

    def start(self) -> None:
        with self._lock:
            if self.is_active:
                return
            
            # Check settings toggle
            if not settings.get("hotkey_enabled", True):
                return
                
            try:
                import keyboard
                self._keyboard_module = keyboard
                
                hotkey = settings.get("hotkey_sequence", "ctrl+alt+j")
                keyboard.add_hotkey(hotkey, self._on_hotkey_pressed)
                
                self.is_active = True
                logger.info(f"Hotkey wake plugin registered for shortcut: {hotkey}")
            except ImportError:
                logger.warning("Python 'keyboard' module not installed. Hotkey listener disabled.")
            except Exception as e:
                logger.error(f"Error registering hotkey listener: {e}")

    def stop(self) -> None:
        with self._lock:
            if not self.is_active:
                return
                
            try:
                if self._keyboard_module:
                    self._keyboard_module.clear_all_hotkeys()
                self.is_active = False
                logger.info("Hotkey wake plugin stopped.")
            except Exception as e:
                logger.error(f"Error unregistering hotkey: {e}")

    def _on_hotkey_pressed(self) -> None:
        """
        Triggered when the system hotkey combination is pressed.
        """
        logger.info("System hotkey sequence detected. Triggering wake event...")
        self.on_wake_callback()
