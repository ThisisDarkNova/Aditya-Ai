# core/wake_system/__init__.py
"""
Event-driven Wake System Orchestrator.
Manages wake plugins, routes audio frames, handles wake detections,
plays activation sounds, and restores Aditya user interfaces.
"""

from __future__ import annotations

import os
import logging
import threading
from typing import Any
import pygetwindow as gw
from NeuralCore.wake_system.base_wake_plugin import BaseWakePlugin
from NeuralCore.wake_system.hotkey_wake_plugin import HotkeyWakePlugin
from NeuralCore.wake_system.keyword_wake_plugin import KeywordWakePlugin
from V12Cylinders.settings_manager import settings

logger = logging.getLogger("aditya-wake-orchestrator")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[⚡ Wake System] %(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class WakeSystemOrchestrator:
    """
    Main manager for discovering, loading, and routing events to wake plugins.
    """
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self.triggered = False
        self.plugins: list[BaseWakePlugin] = []
        
        # Load and register default plugins
        self._register_plugins()

    def _register_plugins(self) -> None:
        """
        Instantiate and register all modular wake detection plugins.
        """
        # Register keyboard hotkeys
        self.plugins.append(HotkeyWakePlugin(on_wake_callback=self.wake))
        
        # Register Wake word listener
        self.plugins.append(KeywordWakePlugin(on_wake_callback=self.wake))

    def start(self) -> None:
        """
        Activate all registered wake plugins.
        """
        with self._lock:
            # Sync with local permission settings
            if not settings.get("mic_permission_granted", False):
                logger.warning("Microphone access permission not yet granted by user. Standby mic checks disabled.")
            
            logger.info("Initializing wake plugins...")
            for plugin in self.plugins:
                try:
                    plugin.start()
                except Exception as e:
                    logger.error(f"Failed to start wake plugin '{plugin.name}': {e}")

    def stop(self) -> None:
        """
        Deactivate all registered wake plugins.
        """
        with self._lock:
            logger.info("Stopping wake plugins...")
            for plugin in self.plugins:
                try:
                    plugin.stop()
                except Exception as e:
                    logger.error(f"Failed to stop wake plugin '{plugin.name}': {e}")

    def process_audio(self, data: bytes) -> None:
        """
        Route raw mic PCM bytes to all active wake plugins.
        """
        with self._lock:
            # Check if mic permission is granted
            if not settings.get("mic_permission_granted", False):
                return
                
            for plugin in self.plugins:
                if plugin.is_active:
                    try:
                        plugin.process_audio(data)
                    except Exception as e:
                        logger.error(f"Error routing audio to plugin '{plugin.name}': {e}")

    def is_triggered(self) -> bool:
        """
        Return whether the system has been awakened.
        """
        with self._lock:
            # If wake word activation is disabled, the system is always considered triggered (active listening)
            if not settings.get("wake_word_enabled", False):
                return True
            return self.triggered

    def reset_trigger(self) -> None:
        """
        Return the system to muted/standby mode.
        """
        with self._lock:
            self.triggered = False
            logger.info("System returned to standby mode.")

    def request_microphone_permission(self) -> bool:
        """
        Request mic permission transparently and store configuration locally.
        """
        with self._lock:
            if settings.get("mic_permission_granted", False):
                return True
                
            print("\n" + "!"*50)
            print("🎙️ ADITYA Microphone Access Authorization Request")
            print("!"*50)
            print("Aditya requires microphone access to support:")
            print(" - Offline wake word listening")
            print(" - Live real-time voice conversations")
            print("\nAll wake detection audio is processed locally on this computer.")
            print("No audio data is sent to the cloud until you activate Aditya.")
            print("!"*50)
            
            # Non-blocking console prompt or automatic grant for terminal runs
            import sys
            if not sys.stdin.isatty():
                logger.info("Non-interactive session detected. Automatically granting microphone permission to prevent hanging.")
                settings.set("mic_permission_granted", True)
                self.start()
                return True

            response = input("Grant microphone permission to Aditya? (y/n): ").strip().lower()
            granted = response in ["y", "yes"]
            settings.set("mic_permission_granted", granted)
            
            if granted:
                logger.info("Microphone access authorized by user.")
                # Restart plugins now that permission is granted
                self.start()
            else:
                logger.warning("Microphone access denied. Voice capabilities will remain disabled.")
            
            return granted

    def wake(self) -> None:
        """
        Trigger a wake event: notify interfaces, restore windows, play activation sounds,
        and alert the Gemini Live loop.
        """
        with self._lock:
            # If a game is active, prevent waking up (DarkNova Mode constraint)
            try:
                from V12Cylinders.gaming_monitor import gaming_monitor
                if gaming_monitor.is_gaming_active():
                    logger.info("Wake event ignored: DarkNova Mode is active.")
                    return
            except Exception:
                pass

            if self.triggered:
                return
            self.triggered = True
            logger.info("Aditya has been awakened! Executing wake sequence...")

            # 1. Play activation sound asynchronously
            self._play_activation_sound()

            # 2. Restore/focus UI Windows
            self._restore_aditya_windows()

            # 3. Notify UI Server
            try:
                from ui_server import set_status, set_ui_control, add_chat_message
                set_status("listening")
                set_ui_control(message="Awake & Listening")
                add_chat_message("ai", "[System: Woken up by wake trigger]")
            except Exception as e:
                logger.error(f"Failed to update UI server status: {e}")

            # 4. Inject alert to prompt Aditya to speak immediately
            try:
                from NeuralCore.aditya_scheduler import reminder_system
                reminder_system.alerts.append(
                    "The user just triggered the wake system to activate you! "
                    "Instantly say a brief, warm greeting (e.g. 'I am listening!', 'Aditya online.') "
                    "and ask how you can help them."
                )
            except Exception as e:
                logger.error(f"Failed to inject wake alert into reminder system: {e}")

    def _play_activation_sound(self) -> None:
        """
        Play a local sound file or generate fallback beep.
        """
        import winsound
        import sys
        from pathlib import Path
        if getattr(sys, "frozen", False):
            project_root = Path(sys.executable).resolve().parent
        else:
            project_root = Path(__file__).resolve().parent.parent.parent
        sound_path = os.path.abspath(project_root / "sounds/hack.wav")
        if os.path.exists(sound_path):
            try:
                winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            except Exception as e:
                logger.error(f"Failed to play hack.wav: {e}")
        else:
            try:
                winsound.Beep(880, 100)
                winsound.Beep(1200, 150)
            except Exception:
                pass

    def _restore_aditya_windows(self) -> None:
        """
        Search for and bring Aditya windows to the foreground.
        """
        try:
            windows = gw.getAllWindows()
            found = False
            for w in windows:
                if w.title and "ADITYA" in w.title.upper():
                    try:
                        w.restore()
                        w.activate()
                        found = True
                        logger.info(f"Restored Aditya interface window: '{w.title}'")
                    except Exception as e:
                        logger.debug(f"Could not restore window '{w.title}': {e}")
            if not found:
                logger.debug("No Aditya windows found to restore.")
        except Exception as e:
            logger.error(f"Failed during window restoration scan: {e}")

# Global instance for seamless usage
wake_system = WakeSystemOrchestrator()
