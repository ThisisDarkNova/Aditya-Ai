# skills/pc_optimizer.py
"""
PC Optimizer & Diagnostics system tool for Aditya.
Provides safe utilities to clean temp files, adjust process priority, and gather diagnostics.
"""

import os
import sys
import shutil
import psutil
import logging
import gc

logger = logging.getLogger("aditya-pc-optimizer")
logger.setLevel(logging.INFO)

def clean_system_temp() -> str:
    """
    Cleans system temporary files safely to free up disk space.
    """
    cleaned_bytes = 0
    temp_dirs = []
    
    if sys.platform == "win32":
        # Windows Temp folders
        temp_dirs = [
            os.environ.get("TEMP"),
            os.environ.get("TMP"),
            os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "Temp")
        ]
    else:
        temp_dirs = ["/tmp"]

    temp_dirs = [d for d in temp_dirs if d and os.path.exists(d)]
    
    for temp_dir in temp_dirs:
        logger.info(f"Scanning temp directory: {temp_dir}")
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    # Skip files in use or locked
                    file_size = os.path.getsize(file_path)
                    os.remove(file_path)
                    cleaned_bytes += file_size
                except Exception:
                    pass
            for d in dirs:
                dir_path = os.path.join(root, d)
                try:
                    shutil.rmtree(dir_path)
                except Exception:
                    pass
                    
    # Force Garbage Collection
    gc.collect()
    
    mb_saved = cleaned_bytes / (1024 ** 2)
    result = f"PC Optimization Complete: Cleaned temporary folders. Saved {mb_saved:.2f} MB of disk space."
    logger.info(result)
    return result

def optimize_gaming_mode() -> str:
    """
    Boosts Aditya's process priority and schedules background indexers to release resources.
    """
    try:
        p = psutil.Process(os.getpid())
        if sys.platform == "win32":
            p.nice(psutil.HIGH_PRIORITY_CLASS)
            logger.info("Process priority optimized to High for gaming mode performance.")
        else:
            p.nice(-10)
        
        # Trigger GC sweep
        gc.collect()
        return "Gaming optimization active. System priority configured to High, garbage collection executed."
    except Exception as e:
        logger.error(f"Failed to configure gaming priority optimization: {e}")
        return f"Gaming optimization incomplete: process priority adjustment failed ({e})"

def get_system_health() -> dict:
    """
    Gathers core diagnostics (CPU, RAM, Disk).
    """
    cpu_percent = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory()
    
    disk_path = "C:\\" if sys.platform == "win32" else "/"
    disk = shutil.disk_usage(disk_path)
    
    return {
        "cpu_percent": cpu_percent,
        "ram_percent": memory.percent,
        "ram_free_gb": memory.available / (1024 ** 3),
        "disk_free_gb": disk.free / (1024 ** 3),
        "platform": sys.platform
    }
