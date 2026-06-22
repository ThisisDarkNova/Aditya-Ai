import subprocess

class TheBouncer:
    """
    🚷 Vespera The Bouncer: Total Focus Protection
    Intercepts and blocks Windows notifications during coding/streaming.
    Allows only VIP messages through via custom Rolls-Royce acoustic chimes.
    """
    def __init__(self):
        self.focus_mode_active = False

    def engage_focus_mode(self):
        if self.focus_mode_active:
            return
        
        print("[The Bouncer] Engaging Focus Mode. Silencing all Windows notifications.")
        self.focus_mode_active = True
        
        # Mocks turning on Windows 11 Focus Assist via PowerShell registry edit
        # In a real environment, this usually requires an elevated PowerShell script:
        # Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Notifications\\Settings" -Name "NOC_GLOBAL_SETTING_TOASTS_ENABLED" -Value 0
        try:
            # Mocking the execution
            pass
        except Exception as e:
            print(f"[The Bouncer] Failed to engage Focus Assist: {e}")

    def disengage_focus_mode(self):
        print("[The Bouncer] Focus Mode deactivated. Notifications restored.")
        self.focus_mode_active = False

    def play_vip_chime(self, sender_name: str):
        """
        Plays a bespoke, bass-heavy acoustic thud for VIPs, bypassing Windows completely.
        """
        print(f"[The Bouncer] VIP Message received from {sender_name}. Playing Rolls-Royce acoustic chime.")
        # Mocks playing a .wav file:
        # import winsound
        # winsound.PlaySound("sounds/rolls_royce_thud.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)

the_bouncer = TheBouncer()
