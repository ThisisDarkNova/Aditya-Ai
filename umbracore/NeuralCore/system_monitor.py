import psutil
import threading
import time
from datetime import datetime
import pygetwindow as gw

class SystemMonitor:
    """
    Background Threaded Metric Monitoring (Legacy Vespera v3.0 Feature).
    Runs psutil checks continuously in a daemon thread so it never blocks the main asyncio loop.
    """
    def __init__(self):
        self._cpu = 0.0
        self._ram_percent = 0.0
        self._ram_free_gb = 0.0
        self._ram_total_gb = 0
        self._bat_percent = None
        self._bat_plugged = False
        self._disk_percent = 0.0
        self._active_windows = []
        self._gpu_status = "N/A"
        self._net_sent_kbps = 0.0
        self._net_recv_kbps = 0.0
        self._alerts = []
        
        self._ip_timezone_name = None
        self._cached_timezone = None
        
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True, name="SystemMonitorThread")
        
        # Fetch timezone based on IP address in background
        threading.Thread(target=self._fetch_ip_timezone, daemon=True).start()

    def _fetch_ip_timezone(self):
        try:
            import urllib.request, json
            req = urllib.request.urlopen("http://ip-api.com/json/", timeout=5)
            data = json.loads(req.read().decode())
            tz_name = data.get("timezone")
            if tz_name:
                from zoneinfo import ZoneInfo
                self._ip_timezone_name = tz_name
                self._cached_timezone = ZoneInfo(tz_name)
        except Exception:
            pass  # Silently fallback to local system time if API is blocked or times out
            
    def start(self):
        if not self._thread.is_alive():
            self._thread.start()
            
    def stop(self):
        self._stop_event.set()
        
    def _get_gpu_status_internal(self) -> str:
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                return f"{gpus[0].name} ({gpus[0].load * 100:.1f}% load)"
        except Exception:
            pass
            
        try:
            import subprocess
            out = subprocess.check_output(
                "powershell -Command \"Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name\"", 
                shell=True
            ).decode("utf-8", errors="ignore").strip()
            lines = [line.strip() for line in out.split('\n') if line.strip()]
            if lines:
                return f"{lines[0]} (Load: N/A)"
        except Exception:
            pass
        return "N/A"
        
    def _monitor_loop(self):
        last_net = psutil.net_io_counters()
        last_time = time.time()
        
        while not self._stop_event.is_set():
            try:
                # Get metrics
                cpu = psutil.cpu_percent(interval=None)
                ram = psutil.virtual_memory()
                disk = psutil.disk_usage("/")
                bat = psutil.sensors_battery()
                
                # Get active windows safely
                titles = gw.getAllTitles()
                clean_windows = [t for t in titles if t and t.strip() and t not in ["Program Manager", "Settings"]]
                
                # GPU status
                gpu_status = self._get_gpu_status_internal()
                
                # Network bandwidth calculation
                current_net = psutil.net_io_counters()
                current_time = time.time()
                dt = current_time - last_time
                sent_speed = 0.0
                recv_speed = 0.0
                if dt > 0:
                    sent_speed = (current_net.bytes_sent - last_net.bytes_sent) / 1024 / dt
                    recv_speed = (current_net.bytes_recv - last_net.bytes_recv) / 1024 / dt
                last_net = current_net
                last_time = current_time
                
                # Update shared state
                with self._lock:
                    self._cpu = cpu
                    self._ram_percent = ram.percent
                    self._ram_free_gb = ram.available / (1024**3)
                    self._ram_total_gb = ram.total // (1024**3)
                    self._disk_percent = disk.percent
                    self._active_windows = clean_windows
                    self._gpu_status = gpu_status
                    self._net_sent_kbps = sent_speed
                    self._net_recv_kbps = recv_speed
                    if bat:
                        self._bat_percent = bat.percent
                        self._bat_plugged = bat.power_plugged
                    else:
                        self._bat_percent = None
                        self._bat_plugged = False
                    
            except Exception as e:
                print(f"[SystemMonitor] Error reading metrics: {e}")
                
            time.sleep(5.0) # Update every 5 seconds smoothly
            
    def get_health(self):
        with self._lock:
            return self._cpu, self._ram_percent, self._ram_free_gb, self._bat_percent, self._bat_plugged

    def get_windows(self):
        with self._lock:
            return list(self._active_windows)

    def add_alert(self, alert_text: str):
        with self._lock:
            if alert_text not in self._alerts:
                self._alerts.append(alert_text)
                
    def clear_alerts(self):
        with self._lock:
            self._alerts.clear()

    def get_status_string(self) -> str:
        """Returns the cached system status as a formatted string for the AI context."""
        with self._lock:
            cpu = self._cpu
            ram_p = self._ram_percent
            ram_t = self._ram_total_gb
            disk_p = self._disk_percent
            gpu = self._gpu_status
            net_sent = self._net_sent_kbps
            net_recv = self._net_recv_kbps
            apps = ", ".join(self._active_windows) if self._active_windows else "None visible"
            alerts = list(self._alerts)
            
        if self._cached_timezone:
            current_time = datetime.now(self._cached_timezone).strftime("%Y-%m-%d %I:%M %p") + f" ({self._ip_timezone_name})"
        else:
            current_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")
        
        status = (
            "\n\n=== CURRENT PC STATUS ===\n"
            f"Time: {current_time}\n"
            f"CPU: {cpu}%  |  GPU: {gpu}  |  RAM: {ram_p}% (Total: {ram_t} GB)  |  Storage C: {disk_p}% used\n"
            f"Network: Up: {net_sent:.1f} KB/s, Down: {net_recv:.1f} KB/s\n"
            f"Currently Active Windows: {apps}\n"
        )
        if alerts:
            status += "=== ACTIVE SYSTEM ALERTS ===\n"
            for alert in alerts:
                status += f"[ALERT] {alert}\n"
        status += "========================="
        return status

# Global singleton
sys_monitor = SystemMonitor()
