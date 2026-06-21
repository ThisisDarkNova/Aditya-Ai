import obsws_python as obs
import time
import threading

class OBSDirector:
    """
    🎥 Aditya OBS Director: Directly controls OBS Studio via websockets.
    """
    def __init__(self, host="localhost", port=4455, password=""):
        self.host = host
        self.port = port
        self.password = password
        self.client = None
        self.is_connected = False

    def connect(self):
        try:
            self.client = obs.ReqClient(host=self.host, port=self.port, password=self.password, timeout=3)
            self.is_connected = True
            print("[OBS_Director] Connected to OBS Studio.")
        except Exception as e:
            print(f"[OBS_Director] Failed to connect: {e}")
            self.is_connected = False

    def change_scene(self, scene_name: str):
        if not self.is_connected:
            self.connect()
        if self.is_connected:
            try:
                self.client.set_current_program_scene(scene_name)
                print(f"[OBS_Director] Switched to scene: {scene_name}")
            except Exception as e:
                print(f"[OBS_Director] Scene switch failed: {e}")

obs_director = OBSDirector()
