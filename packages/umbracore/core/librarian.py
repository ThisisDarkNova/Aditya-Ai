import os
import shutil
from pathlib import Path
from datetime import datetime

class TheLibrarian:
    """
    📚 Vespera The Librarian: Digital Organization
    Silently runs a nightly background task to categorize the Desktop and Downloads folders.
    """
    def __init__(self):
        self.extensions_map = {
            "Images": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
            "Documents": [".pdf", ".docx", ".xlsx", ".pptx", ".txt"],
            "Executables": [".exe", ".msi"],
            "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"]
        }

    def organize_directory(self, target_dir: str):
        print(f"[The Librarian] Organizing: {target_dir}")
        target = Path(target_dir)
        if not target.exists():
            return

        year_str = str(datetime.now().year)

        for item in target.iterdir():
            if item.is_file():
                ext = item.suffix.lower()
                category = "Others"
                
                for cat, exts in self.extensions_map.items():
                    if ext in exts:
                        category = cat
                        break
                
                # Build destination: e.g., Downloads/Images/2026/
                dest_dir = target / category / year_str
                dest_dir.mkdir(parents=True, exist_ok=True)
                
                dest_file = dest_dir / item.name
                # Avoid overwriting
                if not dest_file.exists():
                    try:
                        shutil.move(str(item), str(dest_file))
                        print(f"[The Librarian] Moved: {item.name} -> {category}/{year_str}")
                    except Exception as e:
                        pass

librarian = TheLibrarian()
