# core/aditya_core.py
"""
╔══════════════════════════════════════════════════════════════╗
║              ADITYA Core — Command Router                    ║
║  Central brain that routes every spoken/typed command to     ║
║  the correct skill, module, or OS function.                  ║
║                                                              ║
║  Every OS-level action uses AdityaSilentLauncher:            ║
║  → Zero terminal flashes. Zero CMD popups. Pure magic.       ║
╚══════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import re
import os
import logging

# ── Standard module imports ───────────────────────────────────────────────────
from V12Cylinders.app_opener import (
    type_text, press_hotkey, paste_text,
    clear_active_window_text, media_control,
    set_system_volume, set_system_brightness,
    send_whatsapp_message,
)
from V12Cylinders.youtube_player import play_song_on_youtube

# ── Silent Launcher (NEW — replaces old open_app_human) ───────────────────────
from V12Cylinders.aditya_silent_launcher import (
    open_silently,
    open_file_silently,
    open_folder_silently,
    open_url_silently,
    run_tool_silently,
)

logger = logging.getLogger("aditya-core")

# ── Allowed raw system commands (allowlist for security) ──────────────────────
# Aditya will NOT execute raw shell strings unless they start with one of these.
_SAFE_CMD_PREFIXES = (
    "taskkill",
    "explorer",
    "ipconfig",
    "ping",
    "netstat",
    "sfc",
    "chkdsk",
    "robocopy",
    "xcopy",
    "del ",
    "mkdir",
    "rmdir",
    "cls",
    "ver",
    "systeminfo",
    "shutdown",
    "restart",
    "sc ",
    "net ",
)


# ═══════════════════════════════════════════════════════════════════════════════
# COMMAND CLASSIFIER — determines what TYPE of target the user gave
# ═══════════════════════════════════════════════════════════════════════════════

def _classify_open_target(target: str) -> str:
    """
    Classifies the open target so we call the right launcher method.
    Returns: 'url' | 'file' | 'folder' | 'app'
    """
    # URL patterns
    if re.match(r'^https?://', target) or re.match(r'^www\.', target):
        return 'url'
    # Windows URI schemes (ms-settings:, ms-store:, etc.)
    if re.match(r'^ms-\w+:', target):
        return 'app'
    # Absolute path to a folder
    if os.path.isdir(target):
        return 'folder'
    # Absolute path to a file
    if os.path.isfile(target):
        return 'file'
    # Has a file extension that isn't .exe → treat as file path
    if re.search(r'\.\w{2,5}$', target) and not target.endswith('.exe'):
        return 'file'
    # Default → app name
    return 'app'


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLE COMMAND PROCESSOR
# ═══════════════════════════════════════════════════════════════════════════════

def _process_single_command(command: str) -> str:
    """
    Process a single, atomic command string.
    All OS-level launches go through AdityaSilentLauncher.
    Returns a human-readable result string for Aditya to speak.
    """
    import time

    original_command = command.strip()
    command_lower    = command.lower().strip()

    # Small delay for non-text commands (prevents voice/UI race conditions)
    if not any(command_lower.startswith(k) for k in ("reply", "type", "paste")):
        time.sleep(0.4)

    # ── 1. OPEN — apps, files, folders, URLs ─────────────────────────────────
    if command_lower.startswith("open "):
        target = original_command[5:].strip()   # preserve casing for paths/URLs
        target_lower = target.lower()

        kind = _classify_open_target(target)
        logger.info(f"Open command | target='{target}' | classified as '{kind}'")

        if kind == 'url':
            return open_url_silently(target)
        elif kind == 'file':
            return open_file_silently(target)
        elif kind == 'folder':
            return open_folder_silently(target)
        else:
            # App — use the silent launcher (handles aliases + PATH search + ShellExecuteW)
            return open_silently(target_lower)

    # ── 2. LAUNCH — explicit "launch" keyword (same as open) ─────────────────
    elif command_lower.startswith("launch "):
        target = original_command[7:].strip()
        return open_silently(target.lower())

    # ── 3. START — explicit "start" keyword ───────────────────────────────────
    elif command_lower.startswith("start ") and len(command_lower) > 6:
        target = original_command[6:].strip()
        # Security: block raw dangerous commands via this path
        if target.lower().startswith(("cmd", "powershell", "wscript", "cscript")):
            return "⚠️ Direct shell execution is restricted for security."
        return open_silently(target.lower())

    # ── 4. PLAY — YouTube / Media ────────────────────────────────────────────
    elif command_lower.startswith("play "):
        song_name = original_command[5:].strip()
        if song_name.lower().endswith(" on youtube"):
            song_name = song_name[:-11].strip()
        return play_song_on_youtube(song_name)

    # ── 5. TYPING / CLIPBOARD ────────────────────────────────────────────────
    elif command_lower.startswith("type "):
        return type_text(original_command[5:].strip())

    elif command_lower.startswith("reply "):
        import pyautogui
        text = original_command[6:].strip()
        result = type_text(text)
        time.sleep(0.05)
        pyautogui.press('enter')
        return result + " — pressed Enter to send."

    elif command_lower.startswith("paste "):
        return paste_text(original_command[6:].strip())

    elif command_lower in ("clear_text", "delete_all", "clear text"):
        return clear_active_window_text()

    # ── 6. MOUSE ─────────────────────────────────────────────────────────────
    elif command_lower.startswith("mouse "):
        parts = original_command[6:].strip().split(" ", 1)
        action = parts[0]
        text   = parts[1].strip(" '\"") if len(parts) > 1 else ""
        from V12Cylinders.app_opener import mouse_control
        return mouse_control(action=action, text_to_click=text)

    # ── 7. SCROLL ────────────────────────────────────────────────────────────
    elif command_lower == "scroll down":
        import pyautogui
        pyautogui.scroll(-800)
        return "Scrolled down."

    elif command_lower == "scroll up":
        import pyautogui
        pyautogui.scroll(800)
        return "Scrolled up."

    # ── 8. KEYBOARD SHORTCUTS ────────────────────────────────────────────────
    elif command_lower.startswith(("press ", "shortcut ")):
        clean = (command_lower
                 .replace("shortcut", "").replace("press", "")
                 .replace("+", " ").replace(",", " ").replace(" and ", " "))
        keys = clean.strip().split()
        if not keys:
            return "No keys specified."
        return press_hotkey(keys)

    # ── 9. WHATSAPP ───────────────────────────────────────────────────────────
    elif command_lower.startswith("whatsapp "):
        content = command_lower.replace("whatsapp ", "", 1).strip()
        if " " in content:
            number, msg = content.split(" ", 1)
            return send_whatsapp_message(number.strip(), msg.strip())
        return "Please say: whatsapp [number] [message]"

    # ── 10. VOLUME / BRIGHTNESS ───────────────────────────────────────────────
    elif command_lower.startswith("volume "):
        return set_system_volume(command_lower.replace("volume", "").strip())

    elif command_lower.startswith("brightness "):
        return set_system_brightness(command_lower.replace("brightness", "").strip())

    # ── 11. MEDIA CONTROLS ────────────────────────────────────────────────────
    elif command_lower.startswith("media "):
        return media_control(command_lower.replace("media ", "").strip())

    # ── 12. SYSTEM POWER ──────────────────────────────────────────────────────
    elif command_lower in ("lock", "lock pc", "lock screen", "lock computer"):
        import ctypes
        ctypes.windll.user32.LockWorkStation()
        return "PC locked."

    elif command_lower in ("sleep pc", "sleep computer"):
        # Silent sleep — no visible cmd window
        run_tool_silently("powercfg.exe", ["-h", "off"])
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        return "PC going to sleep."

    elif command_lower in ("shutdown", "shutdown pc", "turn off pc"):
        run_tool_silently("shutdown.exe", ["/s", "/t", "5", "/c", "Aditya initiated shutdown."])
        return "PC will shut down in 5 seconds."

    elif command_lower in ("restart", "restart pc"):
        run_tool_silently("shutdown.exe", ["/r", "/t", "5", "/c", "Aditya initiated restart."])
        return "PC will restart in 5 seconds."

    elif command_lower in ("cancel shutdown", "abort shutdown"):
        run_tool_silently("shutdown.exe", ["/a"])
        return "Shutdown cancelled."

    # ── 13. ADITYA STANDBY ────────────────────────────────────────────────────
    elif command_lower in ("standby", "aditya sleep", "sleep aditya", "go to sleep", "deactivate wake"):
        try:
            from NeuralCore.wake_system import wake_system
            wake_system.reset_trigger()
            return "Aditya entering standby mode."
        except Exception:
            return "Standby initiated."

    # ── 14. PC OPTIMIZATION ───────────────────────────────────────────────────
    elif any(k in command_lower for k in ("optimize my pc", "optimize pc", "optimize system")):
        from skills.pc_optimizer import clean_system_temp, optimize_gaming_mode
        return f"{clean_system_temp()} | {optimize_gaming_mode()}"

    elif any(k in command_lower for k in ("clean temp", "clear cache", "clean junk")):
        from skills.pc_optimizer import clean_system_temp
        return clean_system_temp()

    elif any(k in command_lower for k in ("system health", "pc health", "pc diagnostic")):
        from skills.pc_optimizer import get_system_health
        h = get_system_health()
        return (f"CPU: {h['cpu_percent']}% | RAM: {h['ram_percent']}% "
                f"({h['ram_free_gb']:.1f} GB free) | Disk free: {h['disk_free_gb']:.1f} GB")

    # ── 15. STUDY SKILLS ──────────────────────────────────────────────────────
    elif "generate notes" in command_lower:
        from skills.study_helper import generate_notes_file
        return generate_notes_file(
            "Mathematics", "Trigonometry",
            "Trigonometric ratios:\n1. sin(A) = Opposite/Hypotenuse\n"
            "2. cos(A) = Adjacent/Hypotenuse\n3. tan(A) = Opposite/Adjacent"
        )

    elif "create a quiz" in command_lower:
        from skills.study_helper import generate_quiz_file
        return generate_quiz_file(
            "Science", "Chemical Reactions",
            [
                {"question": "Product of H₂ + O₂?", "options": ["Water", "CO₂", "Salt"], "answer": "Water"},
                {"question": "Reaction that absorbs heat?", "options": ["Endothermic", "Exothermic", "Combustion"], "answer": "Endothermic"},
            ]
        )

    # ── 16. SAFE SYSTEM COMMANDS (allowlisted only) ───────────────────────────
    elif command_lower.startswith("taskkill "):
        # Extract and validate the process name being killed
        parts = command_lower.split()
        # Must follow pattern: taskkill /f /im <process.exe>
        if "/im" in parts:
            proc_idx = parts.index("/im") + 1
            if proc_idx < len(parts):
                proc_name = parts[proc_idx]
                # Validate: only alphanumeric + dots/underscores allowed
                if re.match(r'^[\w\.\-]+\.exe$', proc_name):
                    result = run_tool_silently(
                        "taskkill.exe",
                        ["/f", "/im", proc_name]
                    )
                    return f"Killed process '{proc_name}': {result}"
                return f"⚠️ Invalid process name format: '{proc_name}'"
        return "⚠️ Use format: taskkill /f /im processname.exe"

    # ── 17. UNRECOGNIZED ──────────────────────────────────────────────────────
    return f"Command not recognized: '{command}'"


# ═══════════════════════════════════════════════════════════════════════════════
# PUBLIC ENTRY POINT — process_command()
# ═══════════════════════════════════════════════════════════════════════════════

def process_command(command: str) -> str:
    """
    Central command entry point.
    Handles compound commands (comma/and-separated) by dispatching each part.

    Examples:
        process_command("open chrome")
        process_command("open C:\\notes.txt")
        process_command("open https://youtube.com")
        process_command("volume 50 and brightness 80")
        process_command("open notepad, type Hello World, press ctrl s")
    """
    command = command.strip()
    command_lower = command.lower()

    # Never split typing/pasting commands — they may contain commas
    _no_split_prefixes = ("type ", "paste ", "reply ", "whatsapp ")
    if any(command_lower.startswith(p) for p in _no_split_prefixes):
        return _process_single_command(command)

    # Split compound commands on ", " or " and "
    if ", " in command or re.search(r'\band\b', command_lower):
        parts = []
        if ", " in command:
            for sp in command.split(", "):
                if re.search(r'\band\b', sp.lower()):
                    parts.extend(re.split(r'\s+and\s+', sp, flags=re.IGNORECASE))
                else:
                    parts.append(sp)
        else:
            parts = re.split(r'\s+and\s+', command, flags=re.IGNORECASE)

        results = [_process_single_command(p.strip()) for p in parts if p.strip()]
        return " | ".join(results)

    return _process_single_command(command)
