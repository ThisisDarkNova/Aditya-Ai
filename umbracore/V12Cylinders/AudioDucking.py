import time

class AudioDucking:
    """
    🔈 Vespera Audio Ducking: The Contextual Auto-Mute
    Analyzes voice input context. If you are talking to someone else (e.g., Discord or human in the room),
    Vespera silently mutes its TTS engine so it doesn't interrupt.
    """
    def __init__(self):
        self.is_human_detected = False

    def analyze_audio_context(self, transcribed_text: str):
        # NLP heuristics to detect conversational tangents not directed at Vespera
        lower_text = transcribed_text.lower()
        human_triggers = [
            "what do you think guys", 
            "hang on a second", 
            "hold on bro", 
            "brb", 
            "can you hear me", 
            "dude"
        ]
        
        if any(trigger in lower_text for trigger in human_triggers):
            print(f"[AudioDucking] Human conversation detected ('{transcribed_text}'). Engaging Silent Mute.")
            self.is_human_detected = True
            return True
            
        self.is_human_detected = False
        return False

    def should_speak(self) -> bool:
        return not self.is_human_detected

audio_ducker = AudioDucking()
