import os

class AutoInjector:
    """
    💉 Vespera Auto-Injector: Absolute Authority File Editor
    Silently writes and edits code files directly, triggering hot-reloads instantly.
    """
    def __init__(self):
        pass

    def inject_code(self, file_path: str, new_content: str, overwrite: bool = True):
        try:
            mode = "w" if overwrite else "a"
            with open(file_path, mode, encoding="utf-8") as f:
                f.write(new_content)
            print(f"[AutoInjector] Successfully injected code into {file_path}")
            return True
        except Exception as e:
            print(f"[AutoInjector] Injection failed on {file_path}: {e}")
            return False

auto_injector = AutoInjector()
