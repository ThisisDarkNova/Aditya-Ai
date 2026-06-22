# modules/gaming_monitor.py
"""
Gaming Monitor for Vespera's DarkNova Mode.
Detects when high-performance games (like Valorant) are running,
lowers process CPU priority, suppresses UI alerts, and disables voice speech.
"""

from __future__ import annotations

import os
import time
import logging
import threading
import psutil
from core.settings_manager import settings

logger = logging.getLogger("vespera-gaming")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[🎮 Gaming Monitor] %(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

GAME_PROCESSES = [
    "VALORANT-Win64-Shipping.exe",
    "Valorant.exe",
    "csgo.exe",
    "cs2.exe",
    "League of Legends.exe",
    "Overwatch.exe",
    "Gta5.exe",
    "r5apex.exe",
    "javaw.exe",
    "minecraft.exe",
    "FortniteClient-Win64-Shipping.exe",
    "obs64.exe",
    "obs.exe",
]

class GamingMonitor:
    """
    Background monitor process executing DarkNova Mode resource constraints and notification suppression.
    """
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self.gaming_active = False
        self.original_priority = None

    def start(self) -> None:
        with self._lock:
            if self._thread is not None:
                return
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run, name="gaming-monitor-bg", daemon=True)
            self._thread.start()
            logger.info("Gaming Monitor started.")

    def stop(self) -> None:
        with self._lock:
            if self._thread is None:
                return
            self._stop_event.set()
            self._thread.join(timeout=1.0)
            self._thread = None
            logger.info("Gaming Monitor stopped.")

    def is_gaming_active(self) -> bool:
        with self._lock:
            return self.gaming_active

    def _run(self) -> None:
        """
        Periodically scan process registry list for matches.
        """
        while not self._stop_event.is_set():
            config = settings.get("gaming_mode", {})
            if not config.get("enabled", True) or not config.get("auto_detect_games", True):
                # Reset if disabled
                if self.gaming_active:
                    self._deactivate_gaming_mode()
                time.sleep(5)
                continue

            game_running = False
            try:
                for proc in psutil.process_iter(["name"]):
                    name = proc.info["name"]
                    if name in GAME_PROCESSES:
                        game_running = True
                        break
            except Exception as e:
                logger.error(f"Error scanning processes: {e}")

            if game_running:
                if not self.gaming_active:
                    self._activate_gaming_mode()
            else:
                if self.gaming_active:
                    self._deactivate_gaming_mode()

            time.sleep(5)

    def _activate_gaming_mode(self) -> None:
        with self._lock:
            self.gaming_active = True
            logger.info("🎮 High-priority game detected. Entering DarkNova Mode...")
            
            # 1. Lower process priority class to IDLE
            try:
                p = psutil.Process(os.getpid())
                self.original_priority = p.nice()
                p.nice(psutil.IDLE_PRIORITY_CLASS)
                logger.info("Process priority successfully set to IDLE.")
            except Exception as e:
                logger.warning(f"Unable to adjust process priority: {e}")
                
            # 2. Reset status to sleeping and disable UI messages
            try:
                from api.ui_server import set_ui_control, set_status
                set_ui_control(message="DarkNova Mode Enabled")
                set_status("sleeping")
            except Exception:
                pass

    def _deactivate_gaming_mode(self) -> None:
        with self._lock:
            self.gaming_active = False
            logger.info("🎮 Game closed. Exiting DarkNova Mode...")
            
            # Restore process priority class
            try:
                p = psutil.Process(os.getpid())
                p.nice(self.original_priority or psutil.BELOW_NORMAL_PRIORITY_CLASS)
                logger.info("Process priority class restored to normal levels.")
            except Exception as e:
                logger.warning(f"Unable to restore process priority class: {e}")
                
            try:
                from api.ui_server import set_ui_control
                set_ui_control(message="Vespera Active")
            except Exception:
                pass

# Global instance for seamless usage
gaming_monitor = GamingMonitor()
