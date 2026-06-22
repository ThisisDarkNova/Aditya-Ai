import os
import psutil
import datetime
import requests
from google import genai
from dotenv import load_dotenv

class MorningBriefing:
    """
    Vespera Morning Briefing
    Connects to local system telemetry and uses Gemini to present a cinematic briefing.
    """
    def __init__(self):
        print("Initializing Morning Briefing...")
        load_dotenv()
        
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.weather_key = os.getenv("WEATHER_API_KEY")
        self.city = os.getenv("CITY", "New York")

        if not self.api_key or self.api_key == "paste_your_gemini_key_here":
            print("ERROR: Gemini API key missing in .env")
            self.client = None
        else:
            self.client = genai.Client(api_key=self.api_key)
            print("SUCCESS: Gemini API Connected.")

    def gather_telemetry(self):
        """Reads physical PC metrics."""
        cpu_usage = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        return {
            "cpu": f"{cpu_usage}%",
            "ram_used": f"{ram.used / (1024**3):.1f} GB",
            "ram_total": f"{ram.total / (1024**3):.1f} GB"
        }

    def fetch_weather(self):
        """Fetches real weather from OpenWeatherMap."""
        if not self.weather_key:
            return "Weather Data Unavailable"
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={self.city}&appid={self.weather_key}&units=metric"
            response = requests.get(url).json()
            if response.get("cod") == 200:
                desc = response["weather"][0]["description"]
                temp = response["main"]["temp"]
                return f"{temp}C, {desc} in {self.city}"
            return "Weather Data Unavailable"
        except Exception as e:
            return "Weather Data Unavailable"

    def generate_briefing(self):
        """Asks Gemini to create a personalized morning briefing."""
        if not self.client:
            return "Please configure the Gemini API key in umbracore/.env to enable AI briefings."
            
        telemetry = self.gather_telemetry()
        weather = self.fetch_weather()
        today = datetime.datetime.now().strftime("%A, %B %d")
        
        prompt = f"""
        You are Vespera, a highly advanced, luxurious Sentient Operating System. 
        It is morning on {today}. Give me a 3-sentence cinematic morning briefing.
        Mention that the system is running at optimal capacity.
        Current Telemetry: CPU at {telemetry['cpu']}, RAM using {telemetry['ram_used']} out of {telemetry['ram_total']}.
        Current Weather: {weather}.
        Keep it professional, slightly cold, and Rolls-Royce tier.
        """
        
        print("Connecting to Gemini Core...")
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            return response.text
        except Exception as e:
            return f"FAILED: Connection to Gemini failed: {e}"


if __name__ == "__main__":
    briefing = MorningBriefing()
    print("\n===============================")
    print(briefing.generate_briefing())
    print("===============================\n")
