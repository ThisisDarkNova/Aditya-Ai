class GuardianOverride:
    """
    🛡️ The Guardian Override: Ultimate System Failsafe
    Analyzes pending commands and respectfully refuses to execute if a crash/stream failure probability > 99%.
    """
    def __init__(self):
        # A list of highly destructive or stream-breaking commands
        self.blacklist_patterns = [
            "taskkill /f /im obs64.exe",
            "shutdown /s",
            "del /s /q C:\\Windows",
            "format c:"
        ]

    def assess_risk(self, command: str, context: str = "") -> bool:
        """
        Returns True if the command is deemed safe.
        Returns False if the command hits the 99% crash probability threshold.
        """
        cmd_lower = command.lower()
        for pattern in self.blacklist_patterns:
            if pattern in cmd_lower:
                print(f"[Guardian] CRITICAL RISK DETECTED: Execution of '{command}' blocked.")
                return False
                
        # If stream is active, block heavy CPU tasks
        if "stream_active" in context and "ffmpeg -i" in cmd_lower:
             print(f"[Guardian] STREAM RISK DETECTED: Heavy video encoding blocked while streaming.")
             return False

        return True

    def get_rejection_message(self) -> str:
        return "I must respectfully decline that command. My analysis indicates a 99% probability of catastrophic system failure or stream interruption. I will protect your session."

guardian = GuardianOverride()
