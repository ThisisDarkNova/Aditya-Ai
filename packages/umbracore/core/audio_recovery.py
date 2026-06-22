# core/audio_recovery.py
"""
Audio Pipeline Device Recovery Monitor for Vespera.
Intercepts device change notifications and handles graceful recovery/hotswapping of
PyAudio streams to prevent crashes when headphones or mics are disconnected on Windows.
"""

import time
import logging
import pyaudio
import threading
from typing import Optional, Callable

logger = logging.getLogger("vespera-audio-recovery")
logger.setLevel(logging.INFO)

class AudioRecoveryMonitor:
    def __init__(self, check_interval: int = 5):
        self.check_interval = check_interval
        self._pyaudio_instance: Optional[pyaudio.PyAudio] = None
        self._last_device_count = 0
        self._on_device_change_callback: Optional[Callable[[], None]] = None
        self._running = False

    def start(self, p_instance: pyaudio.PyAudio, on_change_callback: Callable[[], None]):
        """
        Start the audio hardware connection watcher.
        """
        self._pyaudio_instance = p_instance
        self._on_device_change_callback = on_change_callback
        
        try:
            self._last_device_count = self._pyaudio_instance.get_device_count()
        except Exception:
            self._last_device_count = 0

        self._running = True
        watcher = threading.Thread(target=self._watch_loop, name="AudioDeviceWatcher", daemon=True)
        watcher.start()
        logger.info("Audio Hardware Recovery Monitor started.")

    def stop(self):
        self._running = False

    def _watch_loop(self):
        import threading
        while self._running:
            time.sleep(self.check_interval)
            if not self._pyaudio_instance:
                continue
                
            try:
                current_count = self._pyaudio_instance.get_device_count()
                if current_count != self._last_device_count:
                    logger.warning(
                        f"Audio hardware change detected! Devices: {self._last_device_count} -> {current_count}. Triggering pipeline swap..."
                    )
                    self._last_device_count = current_count
                    if self._on_device_change_callback:
                        self._on_device_change_callback()
            except Exception as e:
                logger.error(f"Error checking audio hardware status: {e}")

# Global audio monitor instance
audio_monitor = AudioRecoveryMonitor()
