# modules/vespera_silent_launcher.py
"""
╔══════════════════════════════════════════════════════════════╗
║           VESPERA Silent Launcher Engine                      ║
║  Opens anything on Windows with zero visible terminal flash. ║
║  No CMD windows. No popups. Pure magic.                      ║
╚══════════════════════════════════════════════════════════════╝

HOW IT WORKS:
  Windows API exposes subprocess creation flags that control process
  visibility at the kernel level — before any window is even drawn.

  Key flags used:
    • CREATE_NO_WINDOW     (0x08000000) — Suppresses any console/cmd window
    • DETACHED_PROCESS     (0x00000008) — Process is independent; not attached to our terminal
    • CREATE_NEW_PROCESS_GROUP            — Isolated signal group; Ctrl+C won't kill child
    • SW_HIDE (via STARTUPINFO.wShowWindow = 0) — Hides the initial window frame

  For GUI apps (.exe), we use ctypes ShellExecuteW — the same API
  Windows Explorer uses internally, so the app opens exactly as if
  the user double-clicked it from the desktop.

USAGE:
    from core.vespera_silent_launcher import VesperaSilentLauncher
    launcher = VesperaSilentLauncher()

    launcher.open("chrome")
    launcher.open("notepad")
    launcher.open(r"C:\\Users\\DarkNova\\Documents\\notes.txt")
    launcher.open("https://youtube.com")
    launcher.open(r"C:\\Games\\Valorant\\VALORANT.exe")
    launcher.open("ms-settings:display")    # Windows Settings URI
    launcher.open("calc")
"""

from __future__ import annotations

import os
import sys
import subprocess
import ctypes
import logging
import winreg
from pathlib import Path
from typing import Optional

import psutil
import pygetwindow as gw

# ── Logger ────────────────────────────────────────────────────────────────────
logger = logging.getLogger("vespera-silent-launcher")
if not logger.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter("[🚀 Launcher] %(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(_h)
logger.setLevel(logging.INFO)

# ── Windows API constants ─────────────────────────────────────────────────────
CREATE_NO_WINDOW       = 0x08000000
DETACHED_PROCESS       = 0x00000008
CREATE_NEW_PROC_GROUP  = 0x00000200
SW_HIDE                = 0
SW_SHOWMINIMIZED       = 2
SW_SHOWNORMAL          = 1

# ── Known app aliases → their actual executable or shell command ───────────────
# Add/extend this as Vespera learns new apps.
APP_ALIASES: dict[str, str] = {
    # Browsers
    "chrome":          "chrome.exe",
    "google chrome":   "chrome.exe",
    "firefox":         "firefox.exe",
    "edge":            "msedge.exe",
    "microsoft edge":  "msedge.exe",
    "brave":           "brave.exe",
    # Development
    "vs code":         "code.exe",
    "vscode":          "code.exe",
    "visual studio code": "code.exe",
    "notepad":         "notepad.exe",
    "notepad++":       "notepad++.exe",
    # System
    "task manager":    "taskmgr.exe",
    "file explorer":   "explorer.exe",
    "explorer":        "explorer.exe",
    "control panel":   "control.exe",
    "calculator":      "calc.exe",
    "calc":            "calc.exe",
    "paint":           "mspaint.exe",
    "cmd":             "cmd.exe",
    "powershell":      "powershell.exe",
    "terminal":        "wt.exe",
    "windows terminal":"wt.exe",
    "registry editor": "regedit.exe",
    "regedit":         "regedit.exe",
    # Media
    "vlc":             "vlc.exe",
    "spotify":         "spotify.exe",
    "discord":         "discord.exe",
    # Games / Gaming
    "valorant":        "VALORANT.exe",
    "steam":           "steam.exe",
    # Productivity
    "word":            "winword.exe",
    "excel":           "excel.exe",
    "powerpoint":      "powerpnt.exe",
    "outlook":         "outlook.exe",
    "teams":           "teams.exe",
    "zoom":            "zoom.exe",
    "obs":             "obs64.exe",
    # Settings URI shortcuts
    "settings":        "ms-settings:",
    "display settings":"ms-settings:display",
    "sound settings":  "ms-settings:sound",
    "wifi settings":   "ms-settings:network-wifi",
    "bluetooth":       "ms-settings:bluetooth",
    "apps settings":   "ms-settings:appsfeatures",
    "update settings": "ms-settings:windowsupdate",
}


class VesperaSilentLauncher:
    """
    The core silent launcher engine for Vespera OS.

    Strategy (in priority order):
      1. If already running → focus/restore window (no duplicate processes)
      2. If it's a URL or ms-* URI → ShellExecuteW (system default handler)
      3. If it's an absolute file path → ShellExecuteW (open with default app)
      4. If it's a known alias → resolve to exe, then ShellExecuteW
      5. If it's a bare name → search PATH + common install dirs → ShellExecuteW
      6. Final fallback → Win+R style shell.execute with the raw name
    """

    def __init__(self) -> None:
        self._shell32 = ctypes.windll.shell32
        self._user32  = ctypes.windll.user32

    # ── Public API ─────────────────────────────────────────────────────────────

    def open(self, target: str, background: bool = False) -> str:
        """
        Open anything silently.

        Args:
            target:     App name, file path, folder path, URL, or ms-URI.
            background: If True, don't bring the app to front (minimized launch).

        Returns:
            A human-readable status string (fed back to AI for verbal response).
        """
        target = target.strip()
        logger.info(f"Launch request: '{target}' | background={background}")

        # Check if it's a URL, absolute path, or settings URI
        is_path_or_url = target.startswith(("http://", "https://", "ms-settings:", "ms-", "ftp://")) or os.path.isabs(target)
        
        if not is_path_or_url:
            from core.vespera_app_resolver import app_resolver
            return app_resolver.open_app(target)

        # Step 1 — Check if already running; switch focus instead of re-launching
        focused = self._try_focus_existing(target)
        if focused:
            return focused

        # Step 2 — Resolve the target to something launchable
        resolved = self._resolve(target)
        logger.info(f"Resolved '{target}' → '{resolved}'")

        # Step 3 — Launch via the right strategy
        return self._launch(resolved, original_name=target, background=background)

    def open_file(self, path: str) -> str:
        """Open a specific file with its default Windows application."""
        return self.open(path)

    def open_folder(self, path: str) -> str:
        """Open a folder in Windows Explorer."""
        p = Path(path)
        if not p.exists():
            return f"❌ Folder not found: {path}"
        return self._shell_execute(str(p))

    def open_url(self, url: str) -> str:
        """Open a URL in the default browser."""
        if not url.startswith(("http://", "https://", "ftp://")):
            url = "https://" + url
        return self._shell_execute(url)

    def run_silent(self, exe_path: str, args: list[str] = None) -> str:
        """
        Run an executable completely silently with CREATE_NO_WINDOW.
        Use this for CLI tools that Vespera runs internally (e.g., ffmpeg, yt-dlp).

        Args:
            exe_path: Full path to executable.
            args:     Command-line arguments list.
        """
        cmd = [exe_path] + (args or [])
        try:
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = SW_HIDE

            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                startupinfo=si,
                creationflags=CREATE_NO_WINDOW | DETACHED_PROCESS | CREATE_NEW_PROC_GROUP,
            )
            stdout, stderr = proc.communicate(timeout=30)
            if proc.returncode == 0:
                return f"✅ Command executed successfully."
            else:
                err = stderr.decode(errors="replace").strip()
                return f"⚠️ Command exited with code {proc.returncode}: {err}"

        except subprocess.TimeoutExpired:
            proc.kill()
            return "⚠️ Command timed out after 30 seconds."
        except FileNotFoundError:
            return f"❌ Executable not found: {exe_path}"
        except Exception as e:
            logger.error(f"run_silent failed: {e}")
            return f"❌ Error running command: {e}"

    # ── Internal Resolution ────────────────────────────────────────────────────

    def _resolve(self, target: str) -> str:
        """Resolve a human name or path to a launchable string."""

        # Already an absolute path?
        p = Path(target)
        if p.is_absolute() and p.exists():
            return str(p)

        # URL?
        if target.startswith(("http://", "https://", "ms-settings:", "ms-", "ftp://")):
            return target

        # Known alias?
        alias_key = target.lower().strip()
        if alias_key in APP_ALIASES:
            return APP_ALIASES[alias_key]

        # Search PATH for the exe
        exe = self._find_in_path(target)
        if exe:
            return exe

        # Search common Windows install directories
        exe = self._search_common_dirs(target)
        if exe:
            return exe

        # Return as-is; let ShellExecuteW / Win32 figure it out
        return target

    def _find_in_path(self, name: str) -> Optional[str]:
        """Check if name (or name.exe) exists anywhere in the system PATH."""
        candidates = [name, name + ".exe"] if not name.endswith(".exe") else [name]
        for path_dir in os.environ.get("PATH", "").split(os.pathsep):
            for c in candidates:
                full = Path(path_dir) / c
                if full.is_file():
                    return str(full)
        return None

    def _search_common_dirs(self, name: str) -> Optional[str]:
        """Search common Windows app install locations for the exe."""
        search_dirs = [
            Path(os.environ.get("ProgramFiles", r"C:\Program Files")),
            Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")),
            Path(os.environ.get("LOCALAPPDATA", r"C:\Users\Default\AppData\Local")),
            Path(os.environ.get("APPDATA", r"C:\Users\Default\AppData\Roaming")),
            Path(r"C:\Windows"),
            Path(r"C:\Windows\System32"),
        ]
        candidates = [name, name + ".exe"] if not name.endswith(".exe") else [name]
        for d in search_dirs:
            if not d.exists():
                continue
            for c in candidates:
                # Direct match
                direct = d / c
                if direct.is_file():
                    return str(direct)
                # One level deep (e.g., C:\Program Files\Chrome\chrome.exe)
                for subdir in d.iterdir() if d.exists() else []:
                    try:
                        candidate = subdir / c
                        if candidate.is_file():
                            return str(candidate)
                    except (PermissionError, OSError):
                        continue
        return None

    # ── Launch Strategies ──────────────────────────────────────────────────────

    def _launch(self, resolved: str, original_name: str, background: bool) -> str:
        """Choose the right launch method based on what we resolved to."""

        # ShellExecuteW handles: .exe, files, URLs, ms-* URIs, folders
        result = self._shell_execute(resolved, background=background)

        if "✅" in result or "launched" in result.lower():
            return result

        # Fallback: subprocess with full silent flags
        logger.warning(f"ShellExecuteW failed for '{resolved}'. Trying subprocess fallback.")
        return self._subprocess_launch(resolved, original_name)

    def _shell_execute(self, target: str, background: bool = False) -> str:
        """
        Use Windows ShellExecuteW — the gold standard for opening anything.
        This is what Explorer.exe uses when you double-click a file.

        ShellExecuteW(hwnd, operation, file, params, dir, show_cmd)
          • hwnd=0        → No parent window
          • operation="open" → Standard open verb
          • show_cmd=1    → SW_SHOWNORMAL (visible) | SW_SHOWMINIMIZED (background)
        """
        show_cmd = SW_SHOWMINIMIZED if background else SW_SHOWNORMAL
        try:
            ret = ctypes.windll.shell32.ShellExecuteW(
                None,       # hwnd
                "open",     # lpOperation
                target,     # lpFile
                None,       # lpParameters
                None,       # lpDirectory
                show_cmd,   # nShowCmd
            )

            # ShellExecuteW returns > 32 on success
            if ret > 32:
                app_label = Path(target).stem if Path(target).suffix else target
                logger.info(f"✅ Launched '{app_label}' via ShellExecuteW (ret={ret})")
                return f"✅ Opened '{app_label}' successfully."
            else:
                error_map = {
                    0:  "Out of memory or resources.",
                    2:  "File not found.",
                    3:  "Path not found.",
                    5:  "Access denied.",
                    8:  "Insufficient memory.",
                    32: "DLL not found.",
                }
                err = error_map.get(ret, f"Unknown error (code {ret})")
                logger.warning(f"ShellExecuteW returned {ret}: {err}")
                return f"⚠️ Could not open '{target}': {err}"

        except Exception as e:
            logger.error(f"ShellExecuteW exception: {e}")
            return f"❌ Launch error: {e}"

    def _subprocess_launch(self, target: str, original_name: str) -> str:
        """
        Subprocess fallback — uses the Windows 'start' shell command,
        which is the same as clicking Run in the Start Menu.
        CREATE_NO_WINDOW ensures zero terminal flash.
        """
        try:
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = SW_HIDE

            subprocess.Popen(
                f'start "" "{target}"',
                shell=True,
                startupinfo=si,
                creationflags=CREATE_NO_WINDOW | DETACHED_PROCESS | CREATE_NEW_PROC_GROUP,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            logger.info(f"✅ Launched '{original_name}' via subprocess fallback")
            return f"✅ Opened '{original_name}' successfully."

        except Exception as e:
            logger.error(f"Subprocess fallback failed: {e}")
            return f"❌ All launch methods failed for '{original_name}': {e}"

    # ── Focus Existing Window ──────────────────────────────────────────────────

    def _try_focus_existing(self, target: str) -> Optional[str]:
        """
        If the app is already running, bring its window to front instead
        of spawning a duplicate process. Returns result string or None.
        """
        try:
            # Normalize: resolve alias first
            resolved_name = APP_ALIASES.get(target.lower(), target)
            exe_name = Path(resolved_name).stem.lower()  # e.g. "chrome" from "chrome.exe"

            # Search all open windows for a title match
            all_windows = gw.getAllWindows()
            candidates = [
                w for w in all_windows
                if w.title and w.visible and (
                    exe_name in w.title.lower() or
                    target.lower() in w.title.lower()
                )
            ]

            if candidates:
                win = candidates[-1]  # most recent instance
                logger.info(f"Found existing window: '{win.title}'. Focusing it.")

                if win.isMinimized:
                    win.restore()

                # Use Win32 SetForegroundWindow for reliable focus
                hwnd = win._hWnd
                self._user32.ShowWindow(hwnd, SW_SHOWNORMAL)
                self._user32.SetForegroundWindow(hwnd)

                return f"✅ Switched to already-running '{win.title}'."

        except Exception as e:
            logger.debug(f"Focus check failed (non-critical): {e}")

        return None


# ── Module-level singleton ─────────────────────────────────────────────────────
# Import and use this instance everywhere:
#   from core.vespera_silent_launcher import silent_launcher
#   silent_launcher.open("chrome")
silent_launcher = VesperaSilentLauncher()


# ── Convenience wrappers (used by vespera_core.py command router) ──────────────

def open_silently(target: str) -> str:
    """Open anything silently. Main entry point for AI tool calls."""
    return silent_launcher.open(target)

def open_file_silently(path: str) -> str:
    """Open a file with its default application, invisibly."""
    return silent_launcher.open_file(path)

def open_folder_silently(path: str) -> str:
    """Open a folder in Windows Explorer, invisibly."""
    return silent_launcher.open_folder(path)

def open_url_silently(url: str) -> str:
    """Open a URL in the default browser, invisibly."""
    return silent_launcher.open_url(url)

def run_tool_silently(exe_path: str, args: list[str] = None) -> str:
    """Run a CLI tool completely invisibly and return its output."""
    return silent_launcher.run_silent(exe_path, args)
