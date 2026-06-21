import ctypes
import math

# Using Windows multimedia keys to control volume without external heavy libraries
# Virtual-Key codes
VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF

def press_key(hexKeyCode):
    """Simulates a key press for Windows media keys."""
    # 0 is the mapType indicating that the keycode is a virtual key code
    ctypes.windll.user32.keybd_event(hexKeyCode, 0, 0, 0)
    ctypes.windll.user32.keybd_event(hexKeyCode, 0, 2, 0)

def set_volume_up(steps: int = 5) -> str:
    """Increases system volume."""
    try:
        for _ in range(steps):
            press_key(VK_VOLUME_UP)
        return f"Increased volume by {steps} steps."
    except Exception as e:
        return f"Failed to increase volume: {str(e)}"

def set_volume_down(steps: int = 5) -> str:
    """Decreases system volume."""
    try:
        for _ in range(steps):
            press_key(VK_VOLUME_DOWN)
        return f"Decreased volume by {steps} steps."
    except Exception as e:
        return f"Failed to decrease volume: {str(e)}"

def toggle_mute() -> str:
    """Toggles system mute."""
    try:
        press_key(VK_VOLUME_MUTE)
        return "Toggled system mute."
    except Exception as e:
        return f"Failed to toggle mute: {str(e)}"
