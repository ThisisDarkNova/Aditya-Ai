# core/db_doctor.py
"""
SQLite Integrity Doctor & Auto-Recovery utility.
Performs PRAGMA diagnostics on boot and recovers memory caches from backups if corrupted.
"""

import sqlite3
import shutil
import logging
from pathlib import Path

logger = logging.getLogger("aditya-db-doctor")
logger.setLevel(logging.INFO)

def check_and_repair_db(db_path: Path) -> bool:
    """
    Checks the integrity of the SQLite database or JSON database at `db_path`.
    If corrupt, attempts to restore the backup database.
    Returns True if the database is verified healthy (or repaired), False if rebuild is required.
    """
    if not db_path.exists():
        logger.info(f"Database {db_path.name} does not exist yet. Safe to initialize.")
        return True

    is_json = db_path.suffix.lower() == '.json'
    backup_path = db_path.with_name(db_path.name + ".bak") if is_json else db_path.with_suffix(".db.bak")
    is_healthy = False

    try:
        if is_json:
            import json
            with open(db_path, "r", encoding="utf-8") as f:
                json.load(f)
            is_healthy = True
            # Create a clean backup copy
            shutil.copy2(db_path, backup_path)
            logger.info(f"JSON database {db_path.name} passes integrity check. Clean backup saved.")
        else:
            # Run PRAGMA integrity check
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check;")
            result = cursor.fetchone()
            conn.close()

            if result and result[0] == "ok":
                is_healthy = True
                # Create a clean backup copy
                shutil.copy2(db_path, backup_path)
                logger.info(f"Database {db_path.name} passes integrity check. Clean backup saved.")
            else:
                logger.error(f"Database {db_path.name} failed integrity check: {result}")
    except Exception as e:
        logger.error(f"Error querying integrity for {db_path.name}: {e}")

    if not is_healthy:
        if backup_path.exists():
            logger.warning(f"Restoring {db_path.name} from backup copy...")
            try:
                if db_path.exists():
                    db_path.unlink()
                shutil.copy2(backup_path, db_path)
                logger.info(f"Successfully restored {db_path.name} from clean backup.")
                return True
            except Exception as backup_err:
                logger.critical(f"Failed to restore database from backup: {backup_err}")
        else:
            if is_json:
                logger.warning(f"No backup exists for {db_path.name}. Rebuilding empty JSON file.")
                try:
                    with open(db_path, "w", encoding="utf-8") as f:
                        f.write("{}")
                    logger.info(f"Successfully rebuilt empty JSON database: {db_path.name}")
                    return True
                except Exception as rebuild_err:
                    logger.critical(f"Failed to rebuild JSON database: {rebuild_err}")
                    return False
            else:
                logger.critical(f"No database backup exists for {db_path.name}. Database might need rebuilding.")
                return False

    return True
