import threading
import time

class KeyboardDaemon:
    def __init__(self):
        self._thread = None

    def start(self):
        self._thread = threading.Thread(target=self._run, name="keyboard-listener-bg", daemon=True)
        self._thread.start()

    def _on_hotkey(self):
        from core.aditya_scheduler import reminder_system
        print("\n[🎯 HOTKEY] Aditya Global Action Triggered!")
        reminder_system.alerts.append("The user just pressed the Master Hotkey (Ctrl+Alt+J)! Ask them what emergency command or macro they want to execute.")

    def _run(self):
        try:
            import keyboard
            # Register a global hotkey that triggers an alert across the OS natively
            keyboard.add_hotkey('ctrl+alt+j', self._on_hotkey)
            keyboard.wait() # Block thread forever
        except ImportError:
            print("[⚠️ Keyboard Daemon] Python 'keyboard' module not installed. Hotkey listener disabled. Run 'pip install keyboard' to enable.")
        except Exception as e:
            print(f"[⚠️ Keyboard Daemon] Error starting listener: {e}")

global_hotkey_system = KeyboardDaemon()
