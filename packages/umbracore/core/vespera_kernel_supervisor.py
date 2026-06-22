# core/process_supervisor.py
"""
Process & Thread Supervisor watchdog for Vespera.
Monitors critical sub-threads (such as UI servers, wake loops, cognitive loops)
and restarts them if they hang or exit unexpectedly.
"""

import threading
import time
import logging
from typing import Dict, Callable, Any

logger = logging.getLogger("vespera-supervisor")
logger.setLevel(logging.INFO)

class VesperaKernelSupervisor:
    def __init__(self):
        self._monitored_threads: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._running = False
        self._supervisor_thread = None

    def register_thread(self, name: str, start_fn: Callable[[], Any], thread_object: threading.Thread):
        """
        Register a thread to be supervised.
        """
        with self._lock:
            self._monitored_threads[name] = {
                "start_fn": start_fn,
                "thread": thread_object,
                "last_healthcheck": time.time(),
                "restart_count": 0
            }
            logger.info(f"Registered thread '{name}' under supervision.")

    def ping(self, name: str):
        """
        Sub-threads call this to report that they are healthy and running.
        """
        with self._lock:
            if name in self._monitored_threads:
                self._monitored_threads[name]["last_healthcheck"] = time.time()

    def start(self):
        """
        Start the supervisor thread.
        """
        if self._running:
            return
        self._running = True
        self._supervisor_thread = threading.Thread(target=self._run_loop, name="VesperaSupervisor", daemon=True)
        self._supervisor_thread.start()
        logger.info("Vespera Supervisor watchdog started.")

    def stop(self):
        self._running = False

    def _run_loop(self):
        while self._running:
            time.sleep(5)
            now = time.time()
            with self._lock:
                for name, info in list(self._monitored_threads.items()):
                    thread = info["thread"]
                    # If thread is dead or hasn't pinged in 60s, restart it
                    is_alive = thread.is_alive()
                    time_since_ping = now - info["last_healthcheck"]
                    
                    if not is_alive or time_since_ping > 60:
                        logger.warning(
                            f"Supervisor Alert: Thread '{name}' status: alive={is_alive}, last ping={time_since_ping:.1f}s ago. Restarting thread..."
                        )
                        try:
                            # Start new thread
                            new_thread = info["start_fn"]()
                            info["thread"] = new_thread
                            info["last_healthcheck"] = time.time()
                            info["restart_count"] += 1
                            logger.info(f"Successfully restarted thread '{name}' (Restart #{info['restart_count']})")
                        except Exception as e:
                            logger.error(f"Failed to restart thread '{name}': {e}")

# Global instance for monitoring backend process threads
supervisor = VesperaKernelSupervisor()
