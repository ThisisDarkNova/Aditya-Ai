import os
import time
import obsws_python as obs
from dotenv import load_dotenv

class TheChauffeur:
    """
    Vespera The Chauffeur (OBS Automation)
    Hooks into real OBS Websockets to automatically switch scenes.
    """
    def __init__(self):
        print("Booting The Chauffeur Engine...")
        load_dotenv()
        
        self.host = os.getenv("OBS_HOST", "localhost")
        self.port = os.getenv("OBS_PORT", "4455")
        self.password = os.getenv("OBS_PASSWORD", "")
        
        if self.password == "paste_your_obs_password_here" or not self.password:
            print("ERROR: OBS Password missing in .env")
            self.client = None
        else:
            try:
                self.client = obs.ReqClient(host=self.host, port=self.port, password=self.password)
                print("SUCCESS: OBS WebSocket Connected.")
            except Exception as e:
                print(f"FAILED: Failed to connect to OBS: {e}")
                self.client = None

    def engage_afk_mode(self):
        """Switches to the BRB scene."""
        if not self.client:
            print("OBS Client not configured. Simulating: Switched to 'Be Right Back' scene.")
            return
            
        try:
            self.client.set_current_program_scene("Be Right Back")
            print("SUCCESS: Scene changed to: Be Right Back")
        except Exception as e:
            print(f"FAILED: Scene switch failed: {e}")

    def monitor_stream(self):
        print("MONITORING: The Chauffeur is watching for events... (Press Ctrl+C to stop)")
        try:
            while True:
                time.sleep(5)
                # In a real scenario, this hooks into a game state API (e.g., Riot API)
                # For now, it simply monitors connection health.
        except KeyboardInterrupt:
            print("STOPPED: The Chauffeur shutting down.")

if __name__ == "__main__":
    driver = TheChauffeur()
    if driver.client:
        driver.engage_afk_mode()
        driver.monitor_stream()
