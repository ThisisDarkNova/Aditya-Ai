# core/signal_handler.py
"""
Signal interceptor wrapper for Vespera.
Intercepts OS-level termination requests (like SIGINT, SIGTERM, ctrl+c, or Windows taskkill)
to flush logs, close open files/sockets, and release process resources cleanly.
"""

import signal
import sys
import logging
from typing import Callable, List

logger = logging.getLogger("vespera-signals")
logger.setLevel(logging.INFO)

class CleanShutdownHandler:
    def __init__(self):
        self._callbacks: List[Callable[[], None]] = []
        self._installed = False

    def register_cleanup(self, fn: Callable[[], None]):
        """
        Register a function to be executed during graceful shutdown.
        """
        self._callbacks.append(fn)

    def install(self):
        if self._installed:
            return
        
        # Intercept INT (ctrl+c) and TERM (kill)
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
        
        # Windows-specific break signals
        if sys.platform == "win32":
            try:
                signal.signal(signal.SIGBREAK, self._handle_signal)
            except AttributeError:
                pass
                
        self._installed = True
        logger.info("Signal interceptor installed.")

    def _handle_signal(self, signum, frame):
        logger.info(f"Interception signal received: {signum}. Starting graceful termination sequence...")
        
        for callback in self._callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error during cleanup handler execution: {e}")
                
        logger.info("Termination sequence complete. Exiting process.")
        sys.exit(0)

# Global shutdown coordinator
shutdown_coordinator = CleanShutdownHandler()
