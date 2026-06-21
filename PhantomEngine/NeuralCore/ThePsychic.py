import time
import subprocess

class ThePsychic:
    """
    🔮 Aditya The Psychic: Proactive Intelligence
    Detects when you sit down (via camera/mouse wake) and automatically pre-warms your workspace.
    """
    def __init__(self):
        self.workspace_prepared = False

    def on_user_arrival(self, project_path: str):
        if self.workspace_prepared:
            return
            
        print("[The Psychic] User arrival detected. Pre-warming workspace...")
        try:
            # Silently pull latest git branch
            subprocess.run(["git", "pull"], cwd=project_path, capture_output=True)
            print(f"[The Psychic] Git pull complete on {project_path}.")
            
            # Open IDE (e.g., code .)
            subprocess.run(["code", "."], cwd=project_path, shell=True)
            print("[The Psychic] VS Code launched.")
            
            self.workspace_prepared = True
        except Exception as e:
            print(f"[The Psychic] Failed to prep workspace: {e}")

    def reset_for_next_session(self):
        self.workspace_prepared = False

psychic = ThePsychic()
