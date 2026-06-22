# modules/file_indexer.py
"""
Thread-safe background file indexer for the Vespera workspace.
Caches file lists and metadata to avoid re-scanning drives on every refresh.
Provides search, sort, and secure preview features.
"""

import os
import time
import threading
import logging
from pathlib import Path
from typing import List, Dict, Any
from V12Cylinders.settings_manager import settings

logger = logging.getLogger("vespera-file-indexer")
logger.setLevel(logging.INFO)

# Set up logging handler if not present
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[📂 FileIndexer] %(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class FileIndexer:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir.resolve()
        self.files_cache: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
        self._thread = None
        self._running = False
        
        self.ignored_dirs = {
            ".git", "node_modules", "__pycache__", "build", "dist",
            ".kilocode", ".vscode", ".venv", ".venv_mj", "venv",
            "AppData", "LocalSettings", "Temp"
        }
        self.ignored_extensions = {".pyc", ".pyo", ".pyd", ".exe", ".dll", ".so", ".png", ".jpg", ".jpeg", ".gif", ".ico"}

    def start(self):
        """Start the background indexing thread."""
        with self._lock:
            if self._running:
                return
            self._running = True
            self._thread = threading.Thread(target=self._index_loop, name="file-indexer", daemon=True)
            self._thread.start()
            logger.info("File Indexer started in background.")

    def _index_loop(self):
        """Periodically scans the workspace in the background (every 30 seconds)."""
        while self._running:
            try:
                self.reindex()
            except Exception as e:
                logger.error(f"Error during indexing scan: {e}")
            # Sleep for 30 seconds before checking again
            for _ in range(30):
                if not self._running:
                    break
                time.sleep(1)

    def stop(self):
        self._running = False

    def reindex(self):
        """Perform a single full scan of the root directory and user directories."""
        logger.info(f"Scanning workspace root: {self.root_dir}")
        temp_files = []
        start_time = time.time()
        
        # Scan workspace
        for root, dirs, files in os.walk(self.root_dir):
            # Prune ignored directories in-place to prevent os.walk from descending into them
            dirs[:] = [d for d in dirs if d not in self.ignored_dirs]
            
            for file in files:
                file_path = Path(root) / file
                ext = file_path.suffix.lower()
                if ext in self.ignored_extensions:
                    continue
                
                try:
                    stat = file_path.stat()
                    rel_path = file_path.relative_to(self.root_dir).as_posix()
                    temp_files.append({
                        "name": file,
                        "path": rel_path,
                        "size": stat.st_size,
                        "mtime": stat.st_mtime,
                        "extension": ext,
                        "is_workspace": True
                    })
                except Exception:
                    # Ignore files we can't stat (permissions etc)
                    pass

        # Scan user directories (Documents, Downloads, Desktop)
        user_dirs = [
            Path(os.path.expanduser("~/Documents")),
            Path(os.path.expanduser("~/Downloads")),
            Path(os.path.expanduser("~/Desktop"))
        ]
        for u_dir in user_dirs:
            if u_dir.exists():
                logger.info(f"Scanning user directory: {u_dir}")
                for root, dirs, files in os.walk(u_dir):
                    dirs[:] = [d for d in dirs if d not in self.ignored_dirs]
                    for file in files:
                        file_path = Path(root) / file
                        ext = file_path.suffix.lower()
                        if ext in self.ignored_extensions:
                            continue
                        try:
                            stat = file_path.stat()
                            temp_files.append({
                                "name": file,
                                "path": file_path.as_posix(),
                                "size": stat.st_size,
                                "mtime": stat.st_mtime,
                                "extension": ext,
                                "is_workspace": False
                            })
                        except Exception:
                            pass

        with self._lock:
            self.files_cache = temp_files
        
        elapsed = time.time() - start_time
        logger.info(f"Scan complete. Indexed {len(temp_files)} files in {elapsed:.3f}s")

    def get_files(self) -> List[Dict[str, Any]]:
        """Returns a copy of the cached file list."""
        with self._lock:
            return list(self.files_cache)

    def search_and_sort(self, query: str = "", sort_by: str = "name", descending: bool = False) -> List[Dict[str, Any]]:
        """Search and sort files from cache."""
        files = self.get_files()
        
        if query:
            q = query.lower()
            files = [f for f in files if q in f["name"].lower() or q in f["path"].lower()]

        # Sorting logic
        if sort_by == "size":
            files.sort(key=lambda x: x["size"], reverse=descending)
        elif sort_by == "mtime":
            files.sort(key=lambda x: x["mtime"], reverse=descending)
        elif sort_by == "extension":
            files.sort(key=lambda x: x["extension"], reverse=descending)
        else:
            files.sort(key=lambda x: x["name"].lower(), reverse=descending)

        return files

    def get_safe_content(self, rel_path: str) -> Dict[str, Any]:
        """Safely read content for previewing, ensuring no path traversal."""
        try:
            # Resolve to prevent traversal (e.g. "../")
            target_path = (self.root_dir / rel_path).resolve()
            if not target_path.is_relative_to(self.root_dir):
                return {"error": "Access Denied: Path traversal detected."}
            
            if not target_path.exists():
                return {"error": "File not found."}
            
            if target_path.is_dir():
                return {"error": "Cannot preview directories."}

            # Check file size before loading (limit preview to 100KB)
            stat = target_path.stat()
            if stat.st_size > 100 * 1024:
                return {
                    "path": rel_path,
                    "truncated": True,
                    "content": f"[File is too large ({stat.st_size} bytes). Preview truncated.]"
                }

            with open(target_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            return {
                "path": rel_path,
                "content": content,
                "truncated": False
            }
        except Exception as e:
            return {"error": f"Failed to read file: {str(e)}"}

# Global instances can be initialized with project root
def get_project_root() -> Path:
    import sys
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent.parent

workspace_indexer = FileIndexer(get_project_root())
workspace_indexer.start()
