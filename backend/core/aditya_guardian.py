# core/resource_guard.py
"""
Disk space and system memory leak prevention guard for Aditya.
Periodically checks environment health (Disk space, RAM usage) and cleans local caches if limits are breached.
"""

import os
import shutil
import psutil
import logging
import threading
import time
from pathlib import Path
from core.paths import get_data_dir

logger = logging.getLogger("aditya-resource-guard")
logger.setLevel(logging.INFO)

class AdityaGuardian:
    def __init__(self, check_interval_secs: int = 60):
        self.check_interval = check_interval_secs
        self.data_dir = get_data_dir()
        self._running = False

    def start(self):
        self._running = True
        t = threading.Thread(target=self._run_guard, name="AdityaGuardianThread", daemon=True)
        t.start()
        logger.info("Resource usage protection guard active.")

    def stop(self):
        self._running = False

    def _run_guard(self):
        while self._running:
            time.sleep(self.check_interval)
            try:
                # 1. Disk Space check
                usage = shutil.disk_usage(self.data_dir)
                free_gb = usage.free / (1024 ** 3)
                if free_gb < 1.0: # Less than 1GB free
                    logger.warning(f"Disk space low! Only {free_gb:.2f}GB left. Running temp-file purging...")
                    self._purge_cache()

                # 2. Python RAM leak check
                process = psutil.Process(os.getpid())
                mem_mb = process.memory_info().rss / (1024 ** 2)
                if mem_mb > 500: # Python engine shouldn't consume > 500MB RAM typically
                    logger.warning(f"Aditya memory consumption high ({mem_mb:.1f}MB). Triggering garbage collection.")
                    import gc
                    gc.collect()
            except Exception as e:
                logger.error(f"Error executing resource metrics inspection: {e}")

    def _purge_cache(self):
        """Purges old non-critical files like logs or exports to free storage."""
        log_dir = self.data_dir / "logs"
        if log_dir.exists():
            for file in log_dir.glob("*.log.*"): # Old rotated log files
                try:
                    file.unlink()
                except Exception:
                    pass
        logger.info("Completed cache log purging.")

resource_guard = AdityaGuardian()
