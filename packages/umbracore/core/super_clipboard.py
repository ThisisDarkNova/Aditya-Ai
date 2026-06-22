import time
import threading

class SuperClipboard:
    """
    📋 Vespera Super Clipboard & Cross-App Bridge
    Monitors the system clipboard and keeps a rolling memory of the last 100 items.
    Allows Vespera to fluidly pipe data between unrelated applications.
    """
    def __init__(self):
        self.history = []
        self.max_history = 100
        self.is_running = False
        self._thread = None
        self.pyperclip_available = False
        
        try:
            import pyperclip
            self.pyperclip_available = True
            self.pyperclip = pyperclip
        except ImportError:
            print("[SuperClipboard] pyperclip not installed. Clipboard monitoring disabled.")

    def start(self):
        if not self.pyperclip_available or self.is_running:
            return
        self.is_running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True, name="SuperClipboard")
        self._thread.start()
        print("[SuperClipboard] Monitoring active.")

    def stop(self):
        self.is_running = False

    def _monitor_loop(self):
        last_copied = ""
        while self.is_running:
            try:
                current = self.pyperclip.paste()
                # Basic check to avoid saving massive strings or duplicates
                if current and current != last_copied and len(current) < 50000:
                    last_copied = current
                    self.history.append(current)
                    if len(self.history) > self.max_history:
                        self.history.pop(0)
            except Exception:
                pass
            time.sleep(1.0)

    def get_recent(self, count: int = 5):
        return self.history[-count:]

super_clipboard = SuperClipboard()
