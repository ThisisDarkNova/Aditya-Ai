import time
import threading
from mss import mss
from PIL import Image
import pytesseract

class OmniScreenContext:
    """
    💎 Dynamic Context Window: Constantly analyzes what is currently on your screen 
    via fast OCR to proactively predict needs.
    """
    def __init__(self):
        self.latest_text = ""
        self.is_running = False
        self._thread = None
        self.sct = mss()
    
    def start(self):
        if self.is_running: return
        self.is_running = True
        self._thread = threading.Thread(target=self._scan_loop, daemon=True, name="OmniScreen_Scanner")
        self._thread.start()
        print("[OmniScreen] Dynamic Context Window active.")

    def stop(self):
        self.is_running = False

    def _scan_loop(self):
        # We use a slow loop to save Compute Reserve, but enough to provide context
        while self.is_running:
            try:
                # Capture the primary monitor
                monitor = self.sct.monitors[1]
                sct_img = self.sct.grab(monitor)
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                
                # Perform OCR (ensure Tesseract-OCR is installed on the system)
                # This will silently fail or return empty if Tesseract is not installed
                text = pytesseract.image_to_string(img)
                self.latest_text = text.strip()
            except Exception as e:
                # Silently catch OCR failures to prevent UI crashing
                pass
            
            time.sleep(5)  # Scan every 5 seconds to conserve CPU

omni_screen = OmniScreenContext()
