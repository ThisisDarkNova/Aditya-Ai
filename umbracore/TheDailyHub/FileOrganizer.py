import os
import shutil
import time
import threading
from pathlib import Path

class TheSilentButler:
    """
    🧹 Vespera The Silent Butler (File Organizer)
    Silently watches the Downloads folder and automatically organizes files into 
    Images, Documents, Installers, and Archives based on extensions.
    """
    def __init__(self):
        self.downloads_dir = Path.home() / "Downloads"
        self.is_cleaning = False
        self._thread = None
        
        self.categories = {
            "Images": ['.png', '.jpg', '.jpeg', '.gif', '.webp'],
            "Documents": ['.pdf', '.docx', '.txt', '.xlsx'],
            "Installers": ['.exe', '.msi'],
            "Archives": ['.zip', '.rar', '.7z', '.tar.gz']
        }

    def start(self):
        if self.is_cleaning:
            return
        self.is_cleaning = True
        self._thread = threading.Thread(target=self._butler_loop, daemon=True, name="TheSilentButler")
        self._thread.start()
        print("[The Silent Butler] Now maintaining the estate (Downloads).")

    def stop(self):
        self.is_cleaning = False

    def _butler_loop(self):
        while self.is_cleaning:
            if self.downloads_dir.exists():
                for item in self.downloads_dir.iterdir():
                    if item.is_file():
                        self._categorize_file(item)
            # Sweep every 10 minutes
            time.sleep(600)
            
    def _categorize_file(self, file_path: Path):
        ext = file_path.suffix.lower()
        for category, extensions in self.categories.items():
            if ext in extensions:
                cat_dir = self.downloads_dir / category
                cat_dir.mkdir(exist_ok=True)
                try:
                    # Silently move
                    shutil.move(str(file_path), str(cat_dir / file_path.name))
                    print(f"[The Silent Butler] Organized: {file_path.name} -> {category}")
                except Exception:
                    pass
                break

if __name__ == "__main__":
    butler = TheSilentButler()
    # butler.start()
