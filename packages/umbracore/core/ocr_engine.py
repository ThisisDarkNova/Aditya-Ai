# backend/core/ocr_engine.py
import os
import sys

def get_tesseract_path() -> str:
    """
    Dynamically resolves the path to tesseract.exe across Windows environments.
    Checks bundled directories, standard Program Files, and AppData.
    """
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
    bundled_path = os.path.join(base_dir, "tesseract", "tesseract.exe")
    if os.path.exists(bundled_path):
        return bundled_path
        
    prog_files = os.environ.get("ProgramFiles", "C:\\Program Files")
    prog_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    
    paths = [
        os.path.join(prog_files, "Tesseract-OCR", "tesseract.exe"),
        os.path.join(prog_files_x86, "Tesseract-OCR", "tesseract.exe"),
        os.path.join(local_app_data, "Tesseract-OCR", "tesseract.exe"),
        os.path.join(local_app_data, "Programs", "Tesseract-OCR", "tesseract.exe")
    ]
    
    for p in paths:
        if os.path.exists(p):
            return p
            
    return ""
