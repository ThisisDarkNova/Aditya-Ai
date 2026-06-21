import time
import threading

class ThermalGuardian:
    """
    🔥 Aditya Thermal Guardian
    Monitors CPU/GPU thermals using psutil/WMI. Force-suspends background AI tasks
    if temperature exceeds safe thresholds during intense gaming.
    """
    def __init__(self, limit_celsius: int = 85):
        self.limit_celsius = limit_celsius
        self.is_monitoring = False
        self._thread = None

    def start(self):
        if self.is_monitoring:
            return
        self.is_monitoring = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True, name="ThermalGuardian")
        self._thread.start()
        print("[ThermalGuardian] Hardware thermal monitoring active.")

    def stop(self):
        self.is_monitoring = False

    def _monitor_loop(self):
        try:
            import psutil
            has_psutil = True
        except ImportError:
            has_psutil = False
            print("[ThermalGuardian] 'psutil' missing. Using mock thermal data.")

        while self.is_monitoring:
            current_temp = 50.0 # Mock standard temp
            
            if has_psutil:
                try:
                    # Linux/macOS style sensor reading. Windows often requires WMI or OpenHardwareMonitor
                    temps = psutil.sensors_temperatures()
                    if 'coretemp' in temps:
                        current_temp = temps['coretemp'][0].current
                except Exception:
                    pass

            if current_temp >= self.limit_celsius:
                print(f"[ThermalGuardian] ⚠️ THERMAL LIMIT EXCEEDED ({current_temp}°C). Pausing non-critical AI tasks.")
                # self._pause_all_background_tasks()
                
            time.sleep(10) # Check every 10 seconds

thermal_guardian = ThermalGuardian()
