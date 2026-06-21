import json
import os
from pathlib import Path

from core.paths import get_data_dir

_DATA_DIR = get_data_dir()
_DEFAULT_MEMORY_PATH = str(_DATA_DIR / "memory.json")


import threading

class AdityaMemoryEngine:
    def __init__(self, path=_DEFAULT_MEMORY_PATH):
        self.path = path
        self._lock = threading.Lock()
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self.data = self.load()
        # Always ensure structural integrity after load
        with self._lock:
            self._ensure_structure()
        # Save immediately to fix any corrupted file on disk
        self.save()

    def _ensure_structure(self):
        """Guarantee that required keys always exist."""
        if not isinstance(self.data, dict):
            self.data = {}
        if "user_profile" not in self.data:
            self.data["user_profile"] = {}
        if "history" not in self.data:
            self.data["history"] = []
        for key in ["goals", "preferences", "learned_facts", "workflows", "long_term_memories"]:
            if key not in self.data:
                self.data[key] = [] if key != "preferences" else {}

    def load(self):
        # We don't need lock here since load is called during init and doesn't mutate
        if not os.path.exists(self.path):
            return {"user_profile": {}, "history": [], "goals": [], "preferences": {}, "learned_facts": [], "workflows": [], "long_term_memories": []}
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    return {"user_profile": {}, "history": [], "goals": [], "preferences": {}, "learned_facts": [], "workflows": [], "long_term_memories": []}
                return data
        except (json.JSONDecodeError, Exception):
            return {"user_profile": {}, "history": [], "goals": [], "preferences": {}, "learned_facts": [], "workflows": [], "long_term_memories": []}

    def save(self):
        with self._lock:
            temp_path = self.path + f".tmp_{threading.get_ident()}"
            try:
                with open(temp_path, "w", encoding="utf-8") as f:
                    json.dump(self.data, f, indent=2, ensure_ascii=False)
                
                if os.path.exists(self.path):
                    try:
                        os.remove(self.path)
                    except FileNotFoundError:
                        pass
                os.rename(temp_path, self.path)
            except Exception as e:
                print(f"[ERROR] Failed to save memory: {e}")
            finally:
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except Exception:
                        pass

    def add_chat(self, user, ai):
        with self._lock:
            self.data["history"].append({
                "user": user,
                "ai": ai
            })
            if len(self.data["history"]) > 100:
                self.data["history"] = self.data["history"][-100:]
        self.save()

    def update_profile(self, key, value):
        with self._lock:
            self.data["user_profile"][key] = value
        self.save()
        try:
            print(f"[💾 AdityaMemoryEngine] Permanently saved to disk: {key} = {value}")
        except Exception:
            print(f"[AdityaMemoryEngine] Permanently saved to disk: {key} = {value}")

    def get_profile(self):
        with self._lock:
            return dict(self.data.get("user_profile", {}))

    def get_history(self):
        with self._lock:
            return list(self.data.get("history", []))

    def get_goals(self):
        with self._lock:
            return list(self.data.get("goals", []))

    def get_preferences(self):
        with self._lock:
            return dict(self.data.get("preferences", {}))

    def get_learned_facts(self):
        with self._lock:
            return list(self.data.get("learned_facts", []))

    def get_workflows(self):
        with self._lock:
            return list(self.data.get("workflows", []))

    def get_long_term_memories(self):
        with self._lock:
            return list(self.data.get("long_term_memories", []))

    def update_all_memory(self, memory_dict: dict):
        """Update multiple keys at once securely."""
        with self._lock:
            for k in ["goals", "preferences", "learned_facts", "workflows", "long_term_memories", "user_profile"]:
                if k in memory_dict:
                    val = memory_dict[k]
                    if k == "preferences" or k == "user_profile":
                        if isinstance(val, dict):
                            self.data[k] = val
                    else:
                        if isinstance(val, list):
                            self.data[k] = val
            self.save()


# Global instance for seamless usage
memory_system = AdityaMemoryEngine()
