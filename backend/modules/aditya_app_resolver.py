# modules/aditya_app_resolver.py
"""
╔══════════════════════════════════════════════════════════════╗
║           ADITYA Direct Application Resolver Engine          ║
║  Scans Start Menu, Registry, and Program Files to build a    ║
║  local database and resolve apps by exact/alias/fuzzy match.  ║
║  Switches to running apps (focus/restore) or spawns directly.║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import logging
import winreg
import fnmatch  
from pathlib import Path
from typing import List, Dict, Optional, Any
import difflib
import subprocess
import psutil
import pygetwindow as gw
import ctypes

logger = logging.getLogger("aditya-app-resolver")
if not logger.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter("[🔍 Resolver] %(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(_h)
logger.setLevel(logging.INFO)

from core.paths import get_data_dir
DB_PATH = get_data_dir() / "app_database.json"

# Common app aliases
ALIASES = {
    "vscode": "visual studio code",
    "vs code": "visual studio code",
    "chrome": "google chrome",
    "edge": "microsoft edge",
    "cmd": "command prompt",
    "powershell": "windows powershell",
    "calc": "calculator",
    "paint": "mspaint",
}

def parse_lnk_binary(lnk_path: Path) -> Optional[str]:
    """Lightweight binary parser for shell link (.lnk) target path."""
    try:
        with open(lnk_path, "rb") as f:
            data = f.read()
        if len(data) < 76 or data[0:4] != b'L\x00\x00\x00':
            return None
        flags = data[20]
        # LinkInfo structure flag is 0x02
        if flags & 0x02:
            link_info_offset = int.from_bytes(data[76:80], byteorder="little")
            local_base_path_offset = int.from_bytes(data[link_info_offset + 16:link_info_offset + 20], byteorder="little")
            path_start = link_info_offset + local_base_path_offset
            path_end = data.find(b"\x00", path_start)
            if path_end != -1:
                target_path = data[path_start:path_end].decode("utf-8", errors="ignore")
                if os.path.exists(target_path) and target_path.lower().endswith(".exe"):
                    return target_path
    except Exception:
        pass
    return None

class AppResolver:
    def __init__(self):
        self.apps: List[Dict[str, Any]] = []
        self.load_database()

    def load_database(self):
        if DB_PATH.exists():
            try:
                with open(DB_PATH, "r", encoding="utf-8") as f:
                    self.apps = json.load(f)
                logger.info(f"Loaded {len(self.apps)} apps from database.")
                return
            except Exception as e:
                logger.error(f"Error loading apps database: {e}")
        self.scan_and_rebuild()

    def save_database(self):
        try:
            with open(DB_PATH, "w", encoding="utf-8") as f:
                json.dump(self.apps, f, indent=4, ensure_ascii=False)
            logger.info(f"Saved {len(self.apps)} apps to database.")
        except Exception as e:
            logger.error(f"Error saving apps database: {e}")

    def scan_and_rebuild(self):
        logger.info("Scanning for installed applications...")
        found_apps = {}

        # Helper to add app safely
        def add_app(name: str, exe_path: str):
            if not exe_path or not os.path.exists(exe_path):
                return
            exe_path_norm = os.path.normpath(exe_path).lower()
            name_clean = name.strip().lower()
            if not name_clean:
                return
            # Deduplicate by path
            if exe_path_norm not in found_apps:
                found_apps[exe_path_norm] = {
                    "name": name.strip(),
                    "path": exe_path,
                    "aliases": [name_clean]
                }
            else:
                if name_clean not in found_apps[exe_path_norm]["aliases"]:
                    found_apps[exe_path_norm]["aliases"].append(name_clean)

        # 1. Scan Start Menu Shortcuts (.lnk)
        start_menu_paths = [
            Path(os.environ.get("ProgramData", r"C:\ProgramData")) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
            Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
        ]
        for menu_path in start_menu_paths:
            if menu_path.exists():
                for root, _, files in os.walk(menu_path):
                    for file in files:
                        if file.lower().endswith(".lnk"):
                            lnk = Path(root) / file
                            target = parse_lnk_binary(lnk)
                            if target:
                                name = lnk.stem
                                add_app(name, target)

        # 2. Scan Registry Uninstall Entries
        reg_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        ]
        for hive, subkey in reg_paths:
            try:
                with winreg.OpenKey(hive, subkey) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            name_subkey = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, name_subkey) as app_key:
                                try:
                                    disp_name, _ = winreg.QueryValueEx(app_key, "DisplayName")
                                    # Try to find executable path
                                    try:
                                        install_loc, _ = winreg.QueryValueEx(app_key, "InstallLocation")
                                    except FileNotFoundError:
                                        install_loc = ""
                                    
                                    try:
                                        disp_icon, _ = winreg.QueryValueEx(app_key, "DisplayIcon")
                                    except FileNotFoundError:
                                        disp_icon = ""

                                    exe_target = None
                                    if disp_icon:
                                        icon_path = disp_icon.split(",")[0].strip('" ')
                                        if icon_path.lower().endswith(".exe") and os.path.exists(icon_path):
                                            exe_target = icon_path

                                    if not exe_target and install_loc:
                                        # Scan install loc for executable matching app name
                                        loc_path = Path(install_loc.strip('" '))
                                        if loc_path.exists():
                                            for f in loc_path.iterdir():
                                                if f.is_file() and f.suffix.lower() == ".exe":
                                                    # best guess
                                                    exe_target = str(f)
                                                    break

                                    if exe_target:
                                        add_app(disp_name, exe_target)
                                except Exception:
                                    pass
                        except OSError:
                            break
            except Exception:
                pass

        # 3. Scan Program Files & Program Files (x86) (depth 2)
        prog_dirs = [
            Path(os.environ.get("ProgramFiles", r"C:\Program Files")),
            Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")),
            Path(os.environ.get("LOCALAPPDATA", "")) / "Programs",
        ]
        for p_dir in prog_dirs:
            if p_dir.exists():
                try:
                    for item in p_dir.iterdir():
                        if item.is_dir():
                            try:
                                for sub_item in item.iterdir():
                                    if sub_item.is_case_sensitive() or True: # safety
                                        if sub_item.is_file() and sub_item.suffix.lower() == ".exe":
                                            # Filter out uninstallers/helper exes
                                            stem = sub_item.stem.lower()
                                            if "uninstall" not in stem and "setup" not in stem:
                                                add_app(sub_item.stem, str(sub_item))
                            except Exception:
                                pass
                except Exception:
                    pass

        # 4. WindowsApps (best effort scan of common user paths or system defaults)
        win_apps_path = Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "WindowsApps"
        # Since WindowsApps has high security/permissions, we do a quick check
        # and also include system32 apps
        sys32 = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32"
        if sys32.exists():
            for name in ["calc.exe", "mspaint.exe", "notepad.exe", "cmd.exe", "powershell.exe", "taskmgr.exe"]:
                p = sys32 / name
                if p.exists():
                    add_app(name.replace(".exe", ""), str(p))

        self.apps = list(found_apps.values())
        # Inject standard aliases
        for app in self.apps:
            aliases_lower = [a.lower() for a in app["aliases"]]
            for alias_key, actual_val in ALIASES.items():
                if actual_val in aliases_lower and alias_key not in aliases_lower:
                    app["aliases"].append(alias_key)

        self.save_database()

    def resolve_app(self, name: str) -> Optional[Dict[str, Any]]:
        name_lower = name.lower().strip()
        
        # 1. Exact Match on name or aliases
        for app in self.apps:
            if app["name"].lower() == name_lower:
                return app
            if name_lower in app["aliases"]:
                return app

        # 2. Alias mapping lookup
        if name_lower in ALIASES:
            mapped_name = ALIASES[name_lower]
            for app in self.apps:
                if app["name"].lower() == mapped_name or mapped_name in app["aliases"]:
                    return app

        # 3. Fuzzy Match
        candidates = []
        for app in self.apps:
            # Check all aliases & names
            score = 0.0
            for alias in app["aliases"]:
                ratio = difflib.SequenceMatcher(None, name_lower, alias.lower()).ratio()
                if ratio > score:
                    score = ratio
            if score > 0.65:
                candidates.append((score, app))

        if candidates:
            candidates.sort(key=lambda x: x[0], reverse=True)
            return candidates[0][1]

        return None

    def open_app(self, name: str) -> str:
        """Main interface to resolve, focus or launch an app."""
        app = self.resolve_app(name)
        if not app:
            # Fallback to direct name execute if we couldn't resolve
            return self._launch_directly(name, name)

        exe_path = app["path"]
        app_name = app["name"]

        # Step 1: Check if already running
        focused = self._focus_window(app_name, Path(exe_path).stem)
        if focused:
            return f"✅ Switched to already-running '{app_name}'."

        # Step 2: Spawn new instance directly
        return self._launch_directly(exe_path, app_name)

    def _focus_window(self, app_name: str, exe_stem: str) -> bool:
        try:
            # Try finding window by exe title or process stem
            all_windows = gw.getAllWindows()
            target_win = None
            for w in all_windows:
                if w.title and w.visible:
                    w_title = w.title.lower()
                    if app_name.lower() in w_title or exe_stem.lower() in w_title:
                        target_win = w
                        break

            if target_win:
                if target_win.isMinimized:
                    target_win.restore()
                hwnd = target_win._hWnd
                ctypes.windll.user32.ShowWindow(hwnd, 1) # SW_SHOWNORMAL
                ctypes.windll.user32.SetForegroundWindow(hwnd)
                return True
        except Exception as e:
            logger.debug(f"Failed to focus window: {e}")
        return False

    def _launch_directly(self, exe_path: str, app_name: str) -> str:
        try:
            # Launch without console wrapper, completely detached
            subprocess.Popen(
                f'"{exe_path}"',
                shell=True,
                creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
            )
            return f"✅ Opened '{app_name}' successfully."
        except Exception as e:
            logger.error(f"Failed to launch '{app_name}' directly: {e}")
            return f"❌ Failed to launch '{app_name}': {e}"

app_resolver = AppResolver()
