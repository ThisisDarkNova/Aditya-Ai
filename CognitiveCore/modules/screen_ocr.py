
def read_screen_text() -> str:
    """
    Takes a screenshot of the primary monitor and runs OCR via Tesseract 
    to extract and return all visible text.
    """
    import os
    import gc
    import numpy as np
    import cv2
    import mss
    import pytesseract
    try:
        from core.ocr_engine import get_tesseract_path
        tess_path = get_tesseract_path()
        if tess_path and os.path.exists(tess_path):
            pytesseract.pytesseract.tesseract_cmd = tess_path
            
        print("[AI] Capturing screen for OCR text extraction...")
        with mss.mss() as sct:
            sct_img = sct.grab(sct.monitors[1])
            img = np.array(sct_img)
            
        # Convert and preprocess image
        img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        
        # Extract text using Tesseract
        try:
            text = pytesseract.image_to_string(gray, timeout=10)
        except Exception as e:
            text = f"[OCR Timeout or Error]: {e}"
        
        # Force memory cleanup of heavy arrays
        del sct_img, img, img_bgr, gray
        gc.collect()
        
        cleaned_lines = [line.strip() for line in text.split('\n') if line.strip()]
        cleaned_text = "\n".join(cleaned_lines)
        
        if not cleaned_text:
            return "Screen captured, but no visible text could be read via OCR."
            
        # Prevent context window overflow
        if len(cleaned_text) > 4000:
            cleaned_text = cleaned_text[:4000] + "\n\n[... Remaining screen text truncated ...]"
            
        return f"--- Current Screen Text Output ---\n{cleaned_text}\n---------------------------------"
        
    except Exception as e:
        return f"Error running screen OCR: {e}. Ensure Tesseract OCR is installed at C:\\Program Files\\Tesseract-OCR."
