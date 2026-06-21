import pyautogui
import subprocess
import time
import random
import pygetwindow as gw
import psutil
import ctypes
from typing import Tuple

try:
    import pywhatkit
except ImportError:
    pywhatkit = None

# Safety (mouse corner le jao to stop ho jaye) - Disabled to prevent fail-safe crashes during background tasks
pyautogui.FAILSAFE = False


def _wait_for_window(app_name: str, timeout=0.0) -> bool:
    """Blocks until a window matching app_name becomes strictly active/focused."""
    print(f"[AI] Waiting for '{app_name}' to come to screen focus...")
    waited = 0.0
    while waited <= timeout:
        active = gw.getActiveWindow()
        if active and active.title:
            # Simple check if app_name exists in the title (e.g. 'notepad' in 'Untitled - Notepad')
            if app_name.lower() in active.title.lower():
                return True
        if timeout <= 0:
            break
        time.sleep(0.1)
        waited += 0.1
    return False

def open_app_human(app_name: str) -> str:
    """
    Smart App Opener:
    1. Checks if app is running -> Switches to it (no duplicate copies).
    2. If not running -> Uses Win key to naturally launch.
    3. Execution lock -> Waits until the app is confirmed active before proceeding.
    """
    try:
        print(f"[AI] Request to handle app: {app_name}")
        
        # 1. Smart Switch (Check running windows)
        windows = gw.getWindowsWithTitle(app_name)
        active_candidates = [w for w in windows if w.title and w.visible]
        
        if active_candidates:
            target = active_candidates[-1] # Favor last instance ("lastince" fix)
            print(f"[AI] Found existing app '{target.title}'. Switching to it.")
            if target.isMinimized:
                target.restore()
            try:
                target.activate()
            except Exception:
                pass # Fallback to focus lock if standard activate fails
                
            if _wait_for_window(app_name, timeout=1.0):
                print(f"[✓] Switched to running {app_name} successfully")
                return f"Switched to running app: {app_name}"

        # 2. Open Natural via Win+S Key
        print(f"[AI] Opening new instance of: {app_name}")
        time.sleep(0.3)
        pyautogui.hotkey('win', 's')
        time.sleep(random.uniform(0.5, 0.8))
        pyautogui.write(app_name, interval=random.uniform(0.01, 0.03))
        time.sleep(random.uniform(0.5, 0.8))
        pyautogui.press('enter')

        # 3. Final Verification Lock (0 delay check)
        if _wait_for_window(app_name, timeout=2.0):
            print(f"[✓] {app_name} is definitively active on screen")
            return f"{app_name} opened and focused successfully"
        else:
            print(f"[WARNING] Timeout waiting for {app_name}. Proceeding anyway.")
            return f"{app_name} launched but could not verify focus."
            
    except Exception as e:
        print(f"[ERROR] Failed to open/switch app: {e}")
        return f"Error opening app: {e}"


def open_app_detached(app_name: str) -> str:
    """
    Open an app using subprocess in a fully detached process.
    The app runs independently — no blocking.
    """
    try:
        print(f"[AI] Opening app (detached): {app_name}")

        # Use Windows 'start' command for detached launch
        subprocess.Popen(
            f'start "" "{app_name}"',
            shell=True,
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        )

        print(f"[✓] {app_name} launched (detached)")
        return f"{app_name} launched successfully"

    except Exception as e:
        print(f"[ERROR] Failed to open app: {e}")
        return f"Error opening app: {e}"


from NeuralCore.aditya_memory import memory_system

def is_ascii(s):
    return all(ord(c) < 128 for c in s)

def type_text(text: str) -> str:
    """
    Type text character by character so the user can see it typing.
    Smart Logic: Stops typing if the active window changes.
    """
    try:
        import pygetwindow as gw
        total_len = len(text)
        print(f"[AI] Typing like human ({total_len} chars): {text[:60]}...")

        def is_ascii(s):
            return all(ord(c) < 128 for c in s)

        active = gw.getActiveWindow()
        initial_title = active.title if active else None

        if is_ascii(text):
            for char in text:
                current_active = gw.getActiveWindow()
                current_title = current_active.title if current_active else None
                
                # Check if user switched apps mid-typing!
                if current_title != initial_title:
                    print(f"\n[WARNING] Active window changed from '{initial_title}' to '{current_title}'! Aborting typing to prevent accidents.")
                    return "Aborted typing because the user switched the active window."
                
                pyautogui.write(char)
                time.sleep(0.005)
        else:
            time.sleep(0.05)
            _copy_to_clipboard(text)
            time.sleep(0.05)
            pyautogui.hotkey('ctrl', 'v')
                
        print(f"[✓] Text typed successfully")
        return "Text typed successfully"

    except Exception as e:
        print(f"[ERROR] Failed to type text: {e}")
        return f"Error typing text: {e}"


def _copy_to_clipboard(text: str):
    """Safely copy text to Windows clipboard using pyperclip."""
    import pyperclip
    pyperclip.copy(text)


def paste_text(text: str) -> str:
    """
    Paste text into the currently active window using the clipboard.
    Much faster for large code blocks or documents.
    """
    try:
        print(f"[AI] Pasting text ({len(text)} chars)...")
        _copy_to_clipboard(text)
        time.sleep(0.2)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.1)
        return "Text pasted successfully"
    except Exception as e:
        print(f"[ERROR] Failed to paste text: {e}")
        return f"Error pasting text: {e}"


def press_hotkey(keys: list[str]) -> str:
    """
    Press a combination of keys (hotkey).
    Example: ['ctrl', 'c'], ['alt', 'f4'], ['win', 'r']
    """
    try:
        print(f"[AI] Pressing hotkey: {keys}")
        pyautogui.hotkey(*keys)
        return f"Pressed {'+'.join(keys)}"
    except Exception as e:
        print(f"[ERROR] Failed to press hotkey: {e}")
        return f"Error pressing hotkey: {e}"


def clear_active_window_text() -> str:
    """
    Clears all text in the active window.
    Performs exactly: Ctrl+A -> Delete -> Enter.
    """
    try:
        print(f"[AI] Clearing text in active window (Ctrl+a -> Del -> Enter)...")
        time.sleep(0.3)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        pyautogui.press('delete')
        time.sleep(0.1)
        pyautogui.press('enter')
        return "Cleared active window successfully"
    except Exception as e:
        print(f"[ERROR] Failed to clear text: {e}")
        return f"Error clearing text: {e}"


def media_control(action: str) -> str:
    """Controls media playback natively."""
    try:
        print(f"[AI] Executing media command: {action}")
        if action in ["play", "pause", "playpause"]:
            pyautogui.press("playpause")
            return f"Toggled play/pause"
        elif action == "next":
            pyautogui.press("nexttrack")
            return f"Skipped to next track"
        elif action in ["prev", "previous"]:
            pyautogui.press("prevtrack")
            return f"Went to previous track"
        elif action == "mute":
            pyautogui.press("volumemute")
            return f"Toggled mute"
        else:
            return f"Unknown media command: {action}"
        return f"Error executing media macro: {e}"

def set_system_volume(percent_str: str) -> str:
    """Sets system Master Volume natively on Windows, macOS, and Linux."""
    import sys
    import subprocess
    try:
        val_str = percent_str.replace('%', '').strip()
        val = int(val_str)
        val = max(0, min(100, val))
        
        if sys.platform == "win32":
            from pycaw.pycaw import AudioUtilities
            devices = AudioUtilities.GetSpeakers()
            devices.EndpointVolume.SetMasterVolumeLevelScalar(val / 100.0, None)
            return f"System volume set to {val}%"
        elif sys.platform == "darwin":
            # macOS volume control
            subprocess.run(["osascript", "-e", f"set volume output volume {val}"], check=True)
            return f"macOS system volume set to {val}%"
        else:
            # Linux volume control using amixer
            subprocess.run(["amixer", "-D", "pulse", "sset", "Master", f"{val}%"], check=True)
            return f"Linux system volume set to {val}%"
    except Exception as e:
        error_msg = f"Error setting volume: {e}"
        print(f"[ERROR] {error_msg}")
        return error_msg

def set_system_brightness(percent_str: str) -> str:
    """Sets system brightness natively on Windows, macOS, and Linux."""
    import sys
    import subprocess
    try:
        val_str = percent_str.replace('%', '').strip()
        val = int(val_str)
        val = max(0, min(100, val))
        
        if sys.platform == "win32":
            import screen_brightness_control as sbc
            sbc.set_brightness(val)
            return f"Screen brightness set to {val}%"
        elif sys.platform == "darwin":
            # macOS brightness control via osascript
            subprocess.run(["osascript", "-e", f"tell application \"System Events\" to set value of variable \"brightness\" to {val / 100.0}"], check=True)
            return f"macOS screen brightness set to {val}%"
        else:
            # Linux brightness control via brightnessctl
            subprocess.run(["brightnessctl", "set", f"{val}%"], check=True)
            return f"Linux screen brightness set to {val}%"
    except Exception as e:
        return f"Error setting brightness: {e}"

def send_whatsapp_message(contact: str, message: str) -> str:
    """Sends a WhatsApp message using pywhatkit. Contact must include country code if possible."""
    if not pywhatkit:
        return "Error: pywhatkit is not installed. Run 'pip install pywhatkit'"
    try:
        print(f"[AI] Sending WhatsApp message to: {contact} | Content: {message}")
        if not contact.startswith("+"):
            contact = "+91" + contact # Default to Indian code
        
        # Send instantly via PyWhatKit
        pywhatkit.sendwhatmsg_instantly(contact, message, wait_time=15, tab_close=True, close_time=5)
        return f"Successfully queued WhatsApp message to {contact}"
    except Exception as e:
        return f"Error sending WhatsApp message: {e}"

def get_monitor_scaling() -> float:
    """Returns the Windows display scaling factor (e.g. 1.25 for 125%)."""
    try:
        # Query Windows for the scaling factor
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        logical_width = user32.GetSystemMetrics(0)
        
        # Get physical width via GDI
        h_dc = ctypes.windll.user32.GetDC(0)
        physical_width = ctypes.windll.gdi32.GetDeviceCaps(h_dc, 118) # 118 = DESKTOPHORZRES
        ctypes.windll.user32.ReleaseDC(0, h_dc)
        
        scale = physical_width / logical_width
        return scale
    except:
        return 1.0 # Fallback to 100%

def mouse_control(action: str, x: int = 0, y: int = 0, clicks: int = 1, button: str = 'left', text_to_click: str = "") -> str:
    """
    Advanced mouse controller for Aditya.
    Supported actions: 'click', 'double_click', 'right_click', 'move_to', 'drag_to', 'click_text', 'scroll_up', 'scroll_down'
    Coordinates are normalized [0-1000].
    """
    try:
        if action == 'click_text' and text_to_click:
            import pytesseract
            import os
            import numpy as np
            import cv2
            from pytesseract import Output
            from NeuralCore.ocr_engine import get_tesseract_path
            
            tess_path = get_tesseract_path()
            if tess_path and os.path.exists(tess_path):
                pytesseract.pytesseract.tesseract_cmd = tess_path
            
            print(f"[AI] OCR searching for text: '{text_to_click}' to click...")
            import mss
            with mss.mss() as sct:
                sct_img = sct.grab(sct.monitors[1])
                img = np.array(sct_img)
            img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
            
            # Generate different preprocessed views of the image to handle low contrast and various font weights
            preprocessed_images = [
                ("gray", gray),
                ("adaptive_thresh", cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)),
                ("upscaled", cv2.resize(gray, (0, 0), fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC))
            ]
            
            found_coords = None
            matched_method = None
            
            for method_name, processed_img in preprocessed_images:
                try:
                    data = pytesseract.image_to_data(processed_img, output_type=Output.DICT, timeout=10)
                except Exception as e:
                    print(f"[AI] OCR method '{method_name}' failed or timed out: {e}")
                    continue
                
                target_words = [w.lower().strip() for w in text_to_click.split() if w.lower().strip()]
                if not target_words:
                    break
                    
                n_words = len(data['text'])
                
                # Helper to map coordinates back if the image was upscaled
                scale_factor = 1.5 if method_name == "upscaled" else 1.0
                
                # Pass 1: Consecutive matching
                for start_idx in range(n_words - len(target_words) + 1):
                    match_count = 0
                    seq_left = None
                    seq_top = None
                    seq_right = None
                    seq_bottom = None
                    
                    for w_offset in range(len(target_words)):
                        curr_idx = start_idx + w_offset
                        ocr_word = data['text'][curr_idx].strip().lower()
                        target_word = target_words[w_offset]
                        
                        ocr_clean = "".join(c for c in ocr_word if c.isalnum())
                        target_clean = "".join(c for c in target_word if c.isalnum())
                        
                        if not target_clean:
                            match_count += 1
                            continue
                            
                        if not ocr_clean:
                            break
                            
                        if ocr_clean == target_clean or target_clean in ocr_clean or ocr_clean in target_clean:
                            l = int(data['left'][curr_idx] / scale_factor)
                            t = int(data['top'][curr_idx] / scale_factor)
                            w = int(data['width'][curr_idx] / scale_factor)
                            h = int(data['height'][curr_idx] / scale_factor)
                            
                            if seq_left is None or l < seq_left: seq_left = l
                            if seq_top is None or t < seq_top: seq_top = t
                            if seq_right is None or (l + w) > seq_right: seq_right = l + w
                            if seq_bottom is None or (t + h) > seq_bottom: seq_bottom = t + h
                            
                            match_count += 1
                        else:
                            break
                            
                    if match_count == len(target_words) and seq_left is not None:
                        found_coords = (seq_left, seq_top, seq_right - seq_left, seq_bottom - seq_top)
                        matched_method = method_name
                        break
                
                if found_coords:
                    break
                    
                # Pass 2: Reconstruct string list and substring search
                joined_list = []
                for i in range(n_words):
                    w_text = data['text'][i].strip().lower()
                    if w_text:
                        joined_list.append((w_text, i))
                        
                joined_str = " ".join([item[0] for item in joined_list])
                clean_target = " ".join(target_words)
                
                if clean_target in joined_str or joined_str in clean_target:
                    target_len = len(target_words)
                    for start_idx in range(len(joined_list) - target_len + 1):
                        sub_phrase = " ".join([joined_list[start_idx + k][0] for k in range(target_len)])
                        if clean_target in sub_phrase or sub_phrase in clean_target:
                            seq_left = None
                            seq_top = None
                            seq_right = None
                            seq_bottom = None
                            for k in range(target_len):
                                orig_idx = joined_list[start_idx + k][1]
                                l = int(data['left'][orig_idx] / scale_factor)
                                t = int(data['top'][orig_idx] / scale_factor)
                                w = int(data['width'][orig_idx] / scale_factor)
                                h = int(data['height'][orig_idx] / scale_factor)
                                
                                if seq_left is None or l < seq_left: seq_left = l
                                if seq_top is None or t < seq_top: seq_top = t
                                if seq_right is None or (l + w) > seq_right: seq_right = l + w
                                if seq_bottom is None or (t + h) > seq_bottom: seq_bottom = t + h
                            if seq_left is not None:
                                found_coords = (seq_left, seq_top, seq_right - seq_left, seq_bottom - seq_top)
                                matched_method = method_name
                                break
                if found_coords:
                    break
            
            # Clean up OpenCV/OCR matrices
            del sct_img, img, img_bgr, gray
            import gc
            gc.collect()
            
            if found_coords:
                bx, by, bw, bh = found_coords
                center_x = bx + bw // 2
                center_y = by + bh // 2
                
                # Adjust for monitor scale factor (PyAutoGUI uses logical coordinates)
                scale = get_monitor_scaling()
                logical_x = int(center_x / scale)
                logical_y = int(center_y / scale)
                
                print(f"[AI] Target found via OCR ({matched_method}): physical center ({center_x}, {center_y}), logical center ({logical_x}, {logical_y}) at scale {scale:.2f}x")
                pyautogui.moveTo(logical_x, logical_y, duration=0.4)
                if clicks > 0:
                    pyautogui.click(clicks=clicks, button=button, interval=0.1)
                
                return f"Successfully OCR-clicked on text '{text_to_click}' at physical ({center_x}, {center_y}) -> logical ({logical_x}, {logical_y}) using preprocessing method '{matched_method}'"
            else:
                return f"Error: Could not find text '{text_to_click}' on screen via any OCR preprocessing methods."

        screen_w, screen_h = pyautogui.size()
        scale = get_monitor_scaling()
        
        real_x = int((x / 1000.0) * screen_w)
        real_y = int((y / 1000.0) * screen_h)
        
        # Ensure coordinates are within screen bounds
        real_x = max(0, min(screen_w - 1, real_x))
        real_y = max(0, min(screen_h - 1, real_y))

        print(f"[AI] Action: {action} | Scale: {scale:.2f}x | Target Logical: ({real_x}, {real_y})")
        
        if action == 'move_to':
            pyautogui.moveTo(real_x, real_y, duration=0.4)
        elif action == 'click':
            pyautogui.click(real_x, real_y, clicks=clicks, button=button, interval=0.1)
        elif action == 'double_click':
            pyautogui.doubleClick(real_x, real_y, button=button, interval=0.1)
        elif action == 'right_click':
            pyautogui.click(real_x, real_y, button='right')
        elif action == 'drag_to':
            pyautogui.dragTo(real_x, real_y, duration=0.8, button=button)
        elif action == 'scroll_up':
            pyautogui.scroll(500)
            return "Successfully scrolled up."
        elif action == 'scroll_down':
            pyautogui.scroll(-500)
            return "Successfully scrolled down."
        else:
            return f"Error: Unknown mouse action '{action}'"
            
        return f"Successfully performed {action} at {real_x}, {real_y} (Scaling {scale:.2f}x detected)"
    except Exception as e:
        return f"Error performing {action} at {x}, {y}: {e}"

def calibrate_mouse() -> str:
    """Moves mouse to corners of screen for calibration feedback."""
    try:
        w, h = pyautogui.size()
        points = [(0, 0), (w-1, 0), (0, h-1), (w-1, h-1), (w//2, h//2)]
        print("[AI] Starting visual mouse calibration...")
        for p in points:
            pyautogui.moveTo(p[0], p[1], duration=1.0)
            time.sleep(0.5)
        return f"Calibration complete. Monitor logical resolution: {w}x{h}"
    except Exception as e:
        return f"Calibration error: {e}"
