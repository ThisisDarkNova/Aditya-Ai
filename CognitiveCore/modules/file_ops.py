import os
import shutil
import glob
from typing import List, Dict
try:
    import pypdf
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

def search_files(query: str, start_dir: str = "") -> str:
    """
    Search for files matching the query in the specified start_dir.
    Defaults to the current working directory if start_dir is empty.
    """
    if not start_dir:
        start_dir = os.getcwd()
        
    if not os.path.exists(start_dir):
        return f"Error: Search directory '{start_dir}' does not exist."
        
    print(f"[AI] Searching files for query '{query}' starting from '{start_dir}'...")
    matches = []
    
    # Standard walk search
    for root, dirs, files in os.walk(start_dir):
        # Skip hidden/node_modules/venv dirs to optimize speed
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'venv', '.git', '__pycache__']]
        
        for file in files:
            if query.lower() in file.lower():
                full_path = os.path.join(root, file)
                matches.append(full_path)
                if len(matches) >= 30: # Limit to avoid massive results
                    break
        if len(matches) >= 30:
            break
            
    if not matches:
        return f"No files found matching '{query}' in '{start_dir}'."
        
    result_lines = [f"- {os.path.basename(m)}: {m}" for m in matches]
    return f"Found {len(matches)} files matching '{query}':\n" + "\n".join(result_lines)

def organize_directory(dir_path: str) -> str:
    """
    Organizes files in the given directory path into categorized subfolders.
    """
    if not os.path.exists(dir_path):
        return f"Error: Directory '{dir_path}' does not exist."
        
    categories = {
        "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".xls", ".pptx", ".csv", ".md"],
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".ico"],
        "Media": [".mp3", ".wav", ".mp4", ".mkv", ".avi", ".mov", ".flac"],
        "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
        "Executables": [".exe", ".msi", ".bat", ".sh"],
        "Coding": [".py", ".js", ".ts", ".html", ".css", ".json", ".xml", ".java", ".cpp", ".c", ".go"]
    }
    
    # Create category dirs if files exist for them
    moved_count = 0
    errors = []
    
    try:
        files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
        
        for file in files:
            file_path = os.path.join(dir_path, file)
            _, ext = os.path.splitext(file).lower()
            
            # Find category
            target_cat = "Others"
            for cat, extensions in categories.items():
                if ext in extensions:
                    target_cat = cat
                    break
            
            # Create target folder
            target_dir = os.path.join(dir_path, target_cat)
            os.makedirs(target_dir, exist_ok=True)
            
            # Move file safely
            dest_path = os.path.join(target_dir, file)
            try:
                shutil.move(file_path, dest_path)
                moved_count += 1
            except Exception as e:
                errors.append(f"Could not move {file}: {e}")
                
        status_msg = f"Successfully organized {moved_count} files into categorized folders."
        if errors:
            status_msg += f"\nErrors occurred for some files:\n" + "\n".join(errors)
        return status_msg
        
    except Exception as e:
        return f"Error organizing directory '{dir_path}': {e}"

def read_pdf_text(file_path: str, max_pages: int = 10) -> str:
    """
    Extracts and returns text content from a PDF file.
    Limits reading to max_pages to prevent massive token usage.
    """
    if not os.path.exists(file_path):
        return f"Error: PDF file '{file_path}' does not exist."
    
    if not HAS_PYPDF:
        return "Error: PDF text extraction requires pypdf. Install with: pip install pypdf"
    
    try:
        print(f"[AI] Reading PDF file: {file_path}")
        reader = pypdf.PdfReader(file_path)
        num_pages = len(reader.pages)
        pages_to_read = min(num_pages, max_pages)
        
        text_content = []
        for i in range(pages_to_read):
            page_text = reader.pages[i].extract_text()
            if page_text:
                text_content.append(f"--- Page {i+1} ---\n{page_text}")
            
        extracted_text = "\n\n".join(text_content)
        
        # Limit total characters to 8000
        if len(extracted_text) > 8000:
            extracted_text = extracted_text[:8000] + "\n\n[... Truncated due to size constraints ...]"
            
        summary_info = f"Extracted text from {pages_to_read} of {num_pages} pages in '{os.path.basename(file_path)}':\n\n"
        return summary_info + extracted_text
        
    except Exception as e:
        return f"Error extracting text from PDF '{file_path}': {e}"
