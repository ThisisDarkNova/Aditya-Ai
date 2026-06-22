from pywinauto.application import Application
import psutil
import time

class AppConductor:
    """
    ⚡ Silent Conductor: Exercises Absolute Authority to seamlessly manage PC applications.
    Uses pywinauto to control windows invisibly and psutil for process management.
    """
    def __init__(self):
        pass

    def launch_app(self, path: str, invisible: bool = False):
        try:
            app = Application(backend="uia").start(path)
            print(f"[AppConductor] Launched {path}")
            if invisible:
                # Give it a moment to appear
                time.sleep(1)
                app.top_window().minimize()
            return app
        except Exception as e:
            print(f"[AppConductor] Failed to launch {path}: {e}")
            return None

    def close_app(self, process_name: str):
        killed = 0
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
                    proc.kill()
                    killed += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        print(f"[AppConductor] Terminated {killed} instances of {process_name}")

app_conductor = AppConductor()
