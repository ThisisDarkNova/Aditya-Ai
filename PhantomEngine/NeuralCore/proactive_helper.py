import threading
import time
from NeuralCore.system_monitor import sys_monitor
from ui_server import add_chat_message

class ProactiveHelper:
    """
    Background daemon that monitors hardware health (CPU, RAM, Battery) 
    and raises proactive warnings in the Chat UI and System Status.
    """
    def __init__(self):
        self._stop_event = threading.Event()
        self._thread = None
        # Track last warning timestamps to prevent spamming
        self._last_alert_times = {}
        
    def start(self):
        if self._thread is None or not self._thread.is_alive():
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._loop, daemon=True, name="ProactiveHelperThread")
            self._thread.start()
            print("[AI] Proactive background assistant started.")
            
    def stop(self):
        self._stop_event.set()
        
    def _should_alert(self, key: str, cooldown: float = 300.0) -> bool:
        """Helper to ensure we only send the same alert once every `cooldown` seconds."""
        now = time.time()
        last_time = self._last_alert_times.get(key, 0.0)
        if now - last_time > cooldown:
            self._last_alert_times[key] = now
            return True
        return False
        
    def _loop(self):
        # Wait for system monitor to warm up
        time.sleep(3.0)
        
        while not self._stop_event.is_set():
            try:
                # get_health returns (cpu, ram_percent, ram_free_gb, bat_percent, bat_plugged)
                cpu, ram, ram_free, bat_pct, bat_plugged = sys_monitor.get_health()
                
                # Check CPU
                if cpu > 90.0:
                    alert_text = f"CPU usage is critically high: {cpu}%!"
                    sys_monitor.add_alert(alert_text)
                    if self._should_alert("cpu"):
                        add_chat_message("ai", f"[SYSTEM WARNING] {alert_text}")
                else:
                    # Clean alert if resolved
                    with sys_monitor._lock:
                        sys_monitor._alerts = [a for a in sys_monitor._alerts if "CPU usage" not in a]
                
                # Check RAM
                if ram > 90.0:
                    alert_text = f"System RAM is nearly exhausted: {ram}% used ({ram_free:.1f} GB free)!"
                    sys_monitor.add_alert(alert_text)
                    if self._should_alert("ram"):
                        add_chat_message("ai", f"[SYSTEM WARNING] {alert_text}")
                else:
                    with sys_monitor._lock:
                        sys_monitor._alerts = [a for a in sys_monitor._alerts if "RAM is nearly exhausted" not in a]
                        
                # Check Battery
                if bat_pct is not None and bat_pct < 20.0 and not bat_plugged:
                    alert_text = f"Battery is critically low: {bat_pct}% remaining!"
                    sys_monitor.add_alert(alert_text)
                    if self._should_alert("battery"):
                        add_chat_message("ai", f"[SYSTEM WARNING] {alert_text}")
                else:
                    with sys_monitor._lock:
                        sys_monitor._alerts = [a for a in sys_monitor._alerts if "Battery is critically low" not in a]
                        
            except Exception as e:
                print(f"[ProactiveHelper] Error checking system stats: {e}")
                
            time.sleep(10.0) # Check every 10 seconds

# Global singleton
proactive_helper = ProactiveHelper()
