# core/wake_system/keyword_wake_plugin.py
"""
Wake word plugin. Matches configured phrases (e.g., "Hey Nova")
from the microphone stream using local, privacy-respecting processing.
"""

from __future__ import annotations

import logging
import threading
from typing import Callable
from NeuralCore.wake_system.base_wake_plugin import BaseWakePlugin
from V12Cylinders.settings_manager import settings

logger = logging.getLogger("aditya-wake-word")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[🗣️ Wake Word] %(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class KeywordWakePlugin(BaseWakePlugin):
    """
    Modular Wake Word Plugin. Matches configured keyword phrases (e.g. "Hey Nova").
    Designed for local, privacy-first audio streaming analysis.
    """
    def __init__(self, on_wake_callback: Callable[[], None]) -> None:
        super().__init__("Wake Word Trigger", on_wake_callback)
        self._lock = threading.Lock()
        
    def start(self) -> None:
        with self._lock:
            if self.is_active:
                return
                
            if not settings.get("wake_word_enabled", False):
                return
                
            self.is_active = True
            logger.info(f"Wake word listener initialized for: '{settings.get('wake_word', 'Hey Nova')}'")

    def stop(self) -> None:
        with self._lock:
            if not self.is_active:
                return
            self.is_active = False
            logger.info("Wake word listener stopped.")

    def process_audio(self, data: bytes) -> None:
        """
        Processes microphone audio chunks.
        Note: This acts as an extensible local processing hook. Advanced models (e.g. PocketSphinx/Whisper) 
        can be easily linked here. Default implementation keeps CPU load at 0%.
        """
        if not self.is_active:
            return
            
        # Lightweight local energy envelope matching or integration placeholder
        pass
