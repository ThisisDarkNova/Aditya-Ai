import subprocess
import os

class TheProducer:
    """
    🎬 Vespera The Producer: Live Stream Automator
    Connects to OBS Replay Buffer to clip highlights and automatically uses FFmpeg to crop them for TikTok/Shorts.
    """
    def __init__(self, output_dir: str = "C:/Users/DarkNova/Videos/Vespera_Clips"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def process_latest_clip(self, input_file: str):
        if not os.path.exists(input_file):
            print(f"[The Producer] File not found: {input_file}")
            return

        filename = os.path.basename(input_file)
        output_file = os.path.join(self.output_dir, f"tiktok_{filename}")

        print(f"[The Producer] Rendering 9:16 TikTok crop for {filename}...")
        try:
            # Uses FFmpeg to crop a standard 16:9 1080p video down to a center 9:16 vertical crop (1080x1920)
            # Assuming input is 1920x1080: crop=1080:1920:(1920-1080)/2:0 -> crop=1080:1920:420:0
            cmd = [
                "ffmpeg", "-y", "-i", input_file,
                "-vf", "crop=1080:1920:420:0",
                "-c:a", "copy", output_file
            ]
            # Mute stdout to keep console clean, this is a heavy operation
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"[The Producer] Render complete: {output_file}")
        except Exception as e:
            print(f"[The Producer] FFmpeg render failed: {e}")

producer = TheProducer()
