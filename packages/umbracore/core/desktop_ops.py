import pygetwindow as gw
import pyautogui
import time
from typing import List

def list_windows() -> List[str]:
    """Returns a list of all active visible window titles."""
    titles = gw.getAllTitles()
    # Filter out empty titles and system shell stuff
    clean_titles = [
        t.strip() for t in titles 
        if t and t.strip() and t not in ["Program Manager", "Settings", "Start"]
    ]
    return clean_titles

def organize_windows(action: str, window_title: str) -> str:
    """
    Minimizes, maximizes, restores, or snaps windows to left/right side of screen.
    Actions: 'minimize', 'maximize', 'restore', 'snap_left', 'snap_right'
    """
    action = action.lower()
    windows = gw.getWindowsWithTitle(window_title)
    if not windows:
        # Try a case-insensitive search through all titles
        all_wins = gw.getAllWindows()
        matched_wins = [w for w in all_wins if w.title and window_title.lower() in w.title.lower()]
        if matched_wins:
            windows = matched_wins
        else:
            return f"No window found matching '{window_title}'."
            
    win = windows[0]
    
    try:
        # Bring to focus first
        if win.isMinimized and action != 'minimize':
            win.restore()
        win.activate()
        time.sleep(0.1)
        
        sw, sh = pyautogui.size()
        # Leave some space at the bottom for the taskbar (approx 40px)
        usable_height = sh - 40
        
        if action == "minimize":
            win.minimize()
            return f"Minimized window '{win.title}'."
        elif action == "maximize":
            win.maximize()
            return f"Maximized window '{win.title}'."
        elif action == "restore":
            win.restore()
            return f"Restored window '{win.title}'."
        elif action == "snap_left":
            win.restore()
            win.resizeTo(sw // 2, usable_height)
            win.moveTo(0, 0)
            return f"Snapped window '{win.title}' to the left."
        elif action == "snap_right":
            win.restore()
            win.resizeTo(sw // 2, usable_height)
            win.moveTo(sw // 2, 0)
            return f"Snapped window '{win.title}' to the right."
        else:
            return f"Unknown action '{action}'. Use minimize, maximize, restore, snap_left, or snap_right."
            
    except Exception as e:
        return f"Error executing window operation '{action}' on '{window_title}': {e}"

def set_system_mode(mode: str) -> str:
    """
    Launches and arranges windows for specific workflows: 'coding', 'gaming', 'streaming'.
    """
    mode = mode.lower()
    sw, sh = pyautogui.size()
    usable_height = sh - 40
    
    if mode == "coding":
        # Arrange workspace for coding: open/restore VS Code on left, Browser on right
        from core.app_opener import open_app_human
        open_app_human("visual studio code")
        time.sleep(1.0)
        
        # Try to find VS Code and snap left
        vs_wins = [w for w in gw.getAllWindows() if w.title and "visual studio code" in w.title.lower() or "vscode" in w.title.lower() or " - code" in w.title.lower()]
        if vs_wins:
            try:
                vs_wins[0].restore()
                vs_wins[0].activate()
                vs_wins[0].resizeTo(sw // 2, usable_height)
                vs_wins[0].moveTo(0, 0)
            except Exception:
                pass
                
        return "Workspace optimized for CODING. VS Code opened and snapped to the left."
        
    elif mode == "gaming":
        # Minimize everything non-gaming related to free resources and clean screen
        all_wins = gw.getAllWindows()
        minimized_count = 0
        for w in all_wins:
            if w.title and w.visible and not w.isMinimized:
                title_lower = w.title.lower()
                # Keep game-related launchers/tools open
                if not any(g in title_lower for g in ["steam", "epic", "gog", "discord", "spotify", "nvidia", "amd"]):
                    if "vespera" not in title_lower and "dashboard" not in title_lower:
                        try:
                            w.minimize()
                            minimized_count += 1
                        except Exception:
                            pass
        return f"Workspace optimized for GAMING. Minimized {minimized_count} background apps to free system focus and resources."
        
    elif mode == "streaming":
        # Open OBS, snap left. Prepare browser or chat.
        from core.app_opener import open_app_human
        open_app_human("obs studio")
        time.sleep(1.0)
        
        obs_wins = [w for w in gw.getAllWindows() if w.title and "obs" in w.title.lower()]
        if obs_wins:
            try:
                obs_wins[0].restore()
                obs_wins[0].activate()
                obs_wins[0].resizeTo(sw // 2, usable_height)
                obs_wins[0].moveTo(0, 0)
            except Exception:
                pass
        return "Workspace optimized for STREAMING. OBS Studio launched and snapped left."
        
    else:
        return f"Unknown workspace mode: {mode}. Supported modes: coding, gaming, streaming."
