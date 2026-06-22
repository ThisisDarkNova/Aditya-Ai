"""
ui_server.py — Lightweight HTTP server that serves the UI widget
and exposes /api/status for the 3D orb to poll.
Runs in a background thread so it doesn't block asyncio.
"""

import json
import os
import threading
import urllib.parse
import logging
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

# Structured logger for UI Server
ui_logger = logging.getLogger("vespera-ui-server")
ui_logger.setLevel(logging.INFO)
if not ui_logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[🌐 UI Server] %(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    ui_logger.addHandler(handler)

from V12Cylinders.settings_manager import settings
from V12Cylinders.file_indexer import workspace_indexer
from V12Cylinders.research_worker import start_research, get_research_job, get_all_research_jobs

# Shared state — main.py updates this, UI reads it
_current_status = {
    "status": "connecting",
    "custom_color": None,
    "particle_count": None,
    "message": None,
    "rgb_mode": None,
    "speed": None,
    "particle_size": None,
    "chat_history": [],  # List of dicts: {"role": "user"|"ai", "text": "..."}
    "active_workspace": "general",
    "metrics": {
        "cpu": 0,
        "ram": 0,
        "gpu": "N/A"
    }
}
_pending_inputs = []
_interrupt_requested = False
_lock = threading.Lock()

def check_and_clear_interrupt() -> bool:
    global _interrupt_requested
    with _lock:
        if _interrupt_requested:
            _interrupt_requested = False
            return True
        return False

import sys

def _resolve_ui_dir() -> str:
    """Locate the React UI build directory (client/dist/) regardless of run mode.

    Search order:
      1. Frozen (EXE) — look for `client/dist/` next to the EXE and in known
         electron-builder resource roots. Also walk up the tree in case the EXE
         sits at e.g. `<project>/backend/dist/VesperaCore.exe`.
      2. Dev (running main.py directly) — walk up from this file to the project
         root and pick `client/dist/`.
    """
    here = Path(__file__).resolve()

    candidates: list[Path] = []

    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent
        # PyInstaller may set _MEIPASS to a temp extraction dir
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            candidates.append(Path(meipass) / "client" / "dist")

        candidates.extend([
            exe_dir / "client" / "dist",            # packaged next to VesperaCore.exe
            exe_dir / "dist",                        # flattened layout
            exe_dir.parent / "client" / "dist",      # e.g. resources/../
            exe_dir / "app.asar.unpacked" / "client" / "dist",
        ])
        # Walk up the tree looking for `client/dist/index.html`
        walker = exe_dir
        for _ in range(6):
            walker = walker.parent
            candidates.append(walker / "client" / "dist")
    else:
        # __file__ is .../<project>/backend/ui_server.py
        project_root = here.parent.parent
        candidates.extend([
            project_root / "client" / "dist",
            project_root.parent / "client" / "dist",
        ])
        walker = project_root
        for _ in range(4):
            walker = walker.parent
            candidates.append(walker / "client" / "dist")

    for candidate in candidates:
        if candidate.is_dir() and (candidate / "index.html").is_file():
            ui_logger.info(f"Serving UI from: {candidate}")
            return str(candidate)

    fallback = candidates[0]
    ui_logger.warning(
        f"UI directory not found. Tried: {[str(c) for c in candidates]}. "
        f"Falling back to: {fallback}"
    )
    return str(fallback)


UI_DIR = _resolve_ui_dir()
PORT = 7865


def set_status(status: str) -> None:
    """Called by main.py to update AI status (listening, speaking, thinking, tool, offline)."""
    with _lock:
        _current_status["status"] = status

def set_ui_control(color: str = None, particles: int = None, message: str = None, rgb_mode: bool = None, speed: float = None, particle_size: float = None) -> None:
    """Called to configure custom orb appearance or show a message."""
    with _lock:
        if color is not None:
            _current_status["custom_color"] = color
        if particles is not None:
            _current_status["particle_count"] = particles
        if message is not None:
            _current_status["message"] = message
        if rgb_mode is not None:
            _current_status["rgb_mode"] = rgb_mode
        if speed is not None:
            _current_status["speed"] = speed
        if particle_size is not None:
            _current_status["particle_size"] = particle_size

def get_status() -> str:
    with _lock:
        return _current_status["status"]

def add_chat_message(role: str, text: str) -> None:
    """Append a chat message to history."""
    with _lock:
        if not text.strip():
            return
        
        # Save previous completed user-ai turn to memory when a new turn starts
        if role == "user" and _current_status["chat_history"]:
            try:
                if _current_status["chat_history"][-1]["role"] == "ai":
                    last_ai = _current_status["chat_history"][-1]["text"]
                    last_user = ""
                    for msg in reversed(_current_status["chat_history"][:-1]):
                        if msg["role"] == "user":
                            last_user = msg["text"]
                            break
                    if last_user and last_ai:
                        import NeuralCore.vespera_memory
                        core.vespera_memory.memory_system.add_chat(last_user, last_ai)
            except Exception as e:
                ui_logger.error(f"Failed to sync conversation turn to memory: {e}")

        # If the last message is from the same role (especially AI), append to it
        if role == "ai" and _current_status["chat_history"] and _current_status["chat_history"][-1]["role"] == "ai":
            _current_status["chat_history"][-1]["text"] += text
        else:
            _current_status["chat_history"].append({"role": role, "text": text})
            
        # Keep history short (last 20 messages)
        if len(_current_status["chat_history"]) > 20:
            _current_status["chat_history"] = _current_status["chat_history"][-20:]

def pop_pending_input() -> str | None:
    """Get the next typed user message, if any."""
    with _lock:
        if _pending_inputs:
            return _pending_inputs.pop(0)
        return None


class _Handler(SimpleHTTPRequestHandler):
    """Serves static UI files + /api/status JSON endpoint."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=UI_DIR, **kwargs)

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)

        # CORS Headers for all GET requests
        def send_json_response(data, status_code=200):
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode('utf-8'))

        try:
            if path == "/api/status":
                try:
                    from NeuralCore.system_monitor import sys_monitor
                    sys_monitor.start()
                    cpu, ram_p, ram_free, bat_pct, bat_plugged = sys_monitor.get_health()
                    with _lock:
                        _current_status["metrics"]["cpu"] = round(cpu, 1)
                        _current_status["metrics"]["ram"] = round(ram_p, 1)
                        _current_status["metrics"]["gpu"] = sys_monitor._gpu_status
                except Exception as e:
                    ui_logger.error(f"Failed to update metrics: {e}")
                with _lock:
                    send_json_response(_current_status)
                return

            if path == "/api/realtime":
                try:
                    from NeuralCore.vespera_voice import realtime
                    data = realtime.get_status()
                except Exception as e:
                    ui_logger.error(f"Failed to fetch realtime status: {e}")
                    data = {"error": str(e)}
                send_json_response(data)
                return
                
            if path == "/api/memory":
                try:
                    import NeuralCore.vespera_memory
                    mem_data = {
                        "profile": core.vespera_memory.memory_system.get_profile(),
                        "history": core.vespera_memory.memory_system.get_history(),
                        "goals": core.vespera_memory.memory_system.get_goals(),
                        "preferences": core.vespera_memory.memory_system.get_preferences(),
                        "learned_facts": core.vespera_memory.memory_system.get_learned_facts(),
                        "workflows": core.vespera_memory.memory_system.get_workflows(),
                        "long_term_memories": core.vespera_memory.memory_system.get_long_term_memories()
                    }
                    send_json_response(mem_data)
                except Exception as e:
                    ui_logger.error(f"Failed to fetch memory state: {e}")
                    send_json_response({"error": str(e)}, 500)
                return

            if path == "/api/resolve-app":
                try:
                    name = query_params.get("name", [""])[0]
                    from V12Cylinders.vespera_app_resolver import app_resolver
                    resolved = app_resolver.resolve_app(name)
                    if resolved:
                        send_json_response(resolved)
                    else:
                        send_json_response({"error": "App not resolved"}, 404)
                except Exception as e:
                    ui_logger.error(f"Failed to resolve app: {e}")
                    send_json_response({"error": str(e)}, 500)
                return

            if path == "/api/focus-app":
                try:
                    name = query_params.get("name", [""])[0]
                    from V12Cylinders.vespera_app_resolver import app_resolver
                    from pathlib import Path
                    app = app_resolver.resolve_app(name)
                    if app:
                        focused = app_resolver._focus_window(app["name"], Path(app["path"]).stem)
                        send_json_response({"focused": focused, "path": app["path"], "name": app["name"]})
                    else:
                        send_json_response({"error": "App not resolved"}, 404)
                except Exception as e:
                    ui_logger.error(f"Failed to focus app: {e}")
                    send_json_response({"error": str(e)}, 500)
                return

            if path == "/api/settings":
                try:
                    send_json_response(settings.get_all())
                except Exception as e:
                    ui_logger.error(f"Failed to fetch settings: {e}")
                    send_json_response({"error": str(e)}, 500)
                return

            if path == "/api/files":
                try:
                    query = query_params.get("query", [""])[0]
                    sort_by = query_params.get("sort_by", ["name"])[0]
                    descending = query_params.get("descending", ["false"])[0].lower() == "true"
                    files_list = workspace_indexer.search_and_sort(query, sort_by, descending)
                    send_json_response(files_list)
                except Exception as e:
                    ui_logger.error(f"Failed to search files: {e}")
                    send_json_response({"error": str(e)}, 500)
                return

            if path == "/api/files/preview":
                try:
                    file_path = query_params.get("path", [""])[0]
                    if not file_path:
                        send_json_response({"error": "Path parameter is required"}, 400)
                        return
                    content = workspace_indexer.get_safe_content(file_path)
                    send_json_response(content)
                except Exception as e:
                    ui_logger.error(f"Failed to preview file {file_path}: {e}")
                    send_json_response({"error": str(e)}, 500)
                return

            if path == "/api/research":
                try:
                    job_id = query_params.get("job_id", [""])[0]
                    if job_id:
                        job = get_research_job(job_id)
                        if job:
                            send_json_response(job)
                        else:
                            send_json_response({"error": f"Research job {job_id} not found"}, 404)
                    else:
                        send_json_response(get_all_research_jobs())
                except Exception as e:
                    ui_logger.error(f"Failed to fetch research status: {e}")
                    send_json_response({"error": str(e)}, 500)
                return
                
            if path == "/api/expand":
                self.send_response(200)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                try:
                    import webview
                    if webview.windows:
                        webview.windows[0].resize(600, 500)
                except Exception as e:
                    ui_logger.warning(f"Failed to expand window: {e}")
                return
                
            if path == "/api/shrink":
                self.send_response(200)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                try:
                    import webview
                    if webview.windows:
                        webview.windows[0].resize(180, 320)
                except Exception as e:
                    ui_logger.warning(f"Failed to shrink window: {e}")
                return

            super().do_GET()
        except Exception as e:
            ui_logger.error(f"Error handling GET request {self.path}: {e}")
            send_json_response({"error": "Internal Server Error"}, 500)

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        def send_json_response(data, status_code=200):
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode('utf-8'))

        # Enforce payload size limit (max 1MB)
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 1024 * 1024:
            ui_logger.warning(f"Payload too large: {content_length} bytes")
            send_json_response({"error": "Payload too large. Maximum size is 1MB."}, 413)
            return

        post_data = self.rfile.read(content_length)
        
        # Parse JSON payload
        try:
            data = json.loads(post_data.decode('utf-8')) if post_data else {}
        except Exception as e:
            ui_logger.error(f"Malformed JSON payload: {e}")
            send_json_response({"error": f"Invalid JSON payload: {str(e)}"}, 400)
            return

        try:
            if path == "/api/open-anything":
                query = data.get("query", "").strip()
                if not query:
                    send_json_response({"error": "Query cannot be empty"}, 400)
                    return
                
                try:
                    import re
                    from V12Cylinders.vespera_app_resolver import app_resolver
                    from V12Cylinders.vespera_silent_launcher import silent_launcher
                    from NeuralCore.event_bus import event_bus

                    # Remove prefixes like "open", "launch"
                    clean_query = re.sub(r'^(open|launch|run|start)\s+', '', query, flags=re.IGNORECASE).strip()
                    query_lower = clean_query.lower()
                    
                    event_bus.publish("open_anything", {"query": query, "clean_query": clean_query})

                    result = None
                    # 1. URL Check
                    if clean_query.startswith(("http://", "https://", "www.")) or re.search(r'\.[a-z]{2,6}(/|$)', query_lower):
                        url = clean_query if clean_query.startswith("http") else "https://" + clean_query
                        res = silent_launcher.open_url(url)
                        result = {"type": "url", "status": res, "target": url}
                    
                    if not result:
                        # 2. Folder Check
                        common_folders = {
                            "downloads": Path(os.path.expanduser("~/Downloads")),
                            "documents": Path(os.path.expanduser("~/Documents")),
                            "desktop": Path(os.path.expanduser("~/Desktop")),
                            "pictures": Path(os.path.expanduser("~/Pictures")),
                            "videos": Path(os.path.expanduser("~/Videos")),
                            "music": Path(os.path.expanduser("~/Music")),
                        }
                        for key, folder_path in common_folders.items():
                            if key in query_lower:
                                if folder_path.exists():
                                    res = silent_launcher.open_folder(str(folder_path))
                                    result = {"type": "folder", "status": res, "target": str(folder_path)}
                                    break
                    
                    if not result:
                        # 3. Check App Resolver
                        resolved_app = app_resolver.resolve_app(clean_query)
                        if resolved_app:
                            res = app_resolver.open_app(resolved_app["name"])
                            result = {"type": "app", "status": res, "target": resolved_app["path"]}

                    if not result:
                        # 4. Check workspace indexer
                        workspace_files = workspace_indexer.search_and_sort(clean_query)
                        if workspace_files:
                            best_match = workspace_files[0]
                            full_path = workspace_indexer.root_dir / best_match["path"]
                            res = silent_launcher.open_file(str(full_path))
                            result = {"type": "file", "status": res, "target": str(full_path)}

                    if not result:
                        # Fallback
                        res = silent_launcher.open(clean_query)
                        result = {"type": "shell", "status": res, "target": clean_query}

                    send_json_response(result)
                except Exception as e:
                    ui_logger.error(f"Failed in open-anything: {e}")
                    send_json_response({"error": str(e)}, 500)
                return

            if path == "/api/chat":
                text = data.get("text", "").strip()
                if text:
                    with _lock:
                        _pending_inputs.append(text)
                    add_chat_message("user", text)
                    ui_logger.info(f"Received user chat message: {text[:60]}")
                send_json_response({"status": "queued"})
                return

            if path == "/api/settings":
                if not isinstance(data, dict):
                    send_json_response({"error": "Settings payload must be a JSON object"}, 400)
                    return
                
                # Input validation and sanitization bounds
                for key, val in data.items():
                    try:
                        if key == "startup_delay_seconds":
                            data[key] = max(10, min(30, int(val)))
                        elif key == "temperature":
                            data[key] = max(0.0, min(2.0, float(val)))
                        elif key == "font_size":
                            data[key] = max(8, min(32, int(val)))
                        elif key == "max_agent_loops":
                            data[key] = max(1, min(100, int(val)))
                    except (ValueError, TypeError) as e:
                        ui_logger.warning(f"Invalid type or bounds for setting {key}: {e}")
                        send_json_response({"error": f"Invalid bounds/type for key '{key}'"}, 400)
                        return

                # Write values to settings_manager
                for key, val in data.items():
                    settings.set(key, val)
                    if key == "startup_enabled" or key == "launch_on_startup":
                        try:
                            from V12Cylinders.startup_manager import set_registry_run_key
                            set_registry_run_key(bool(val))
                        except Exception as e:
                            ui_logger.error(f"Failed to sync registry auto-start: {e}")
                
                ui_logger.info("Settings updated dynamically.")
                send_json_response({"status": "success", "settings": settings.get_all()})
                return

            if path == "/api/research":
                query = data.get("query", "").strip()
                if not query:
                    send_json_response({"error": "Search query cannot be empty"}, 400)
                    return
                if len(query) > 200:
                    send_json_response({"error": "Search query too long (max 200 characters)"}, 400)
                    return
                
                # Spawn background research job
                job_id = start_research(query)
                ui_logger.info(f"Started research job {job_id} for query '{query}'")
                send_json_response({"status": "running", "job_id": job_id})
                return

            if path == "/api/memory":
                if not isinstance(data, dict):
                    send_json_response({"error": "VesperaMemoryEngine payload must be a JSON object"}, 400)
                    return
                
                try:
                    import NeuralCore.vespera_memory
                    core.vespera_memory.memory_system.update_all_memory(data)
                    ui_logger.info("VesperaMemoryEngine collections updated.")
                    send_json_response({"status": "success"})
                except Exception as e:
                    ui_logger.error(f"Failed to update memory: {e}")
                    send_json_response({"error": str(e)}, 500)
                return

            if path == "/api/chat/clear":
                ui_logger.info("Clearing chat history.")
                with _lock:
                    _current_status["chat_history"] = []
                send_json_response({"status": "success", "message": "Chat history cleared."})
                return

            if path == "/api/close":
                ui_logger.info("Shutdown request received. Terminating GUI and exiting.")
                self.send_response(200)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                
                def _kill():
                    import time
                    time.sleep(0.2)
                    try:
                        import webview
                        if webview.windows:
                            webview.windows[0].destroy()
                    except Exception:
                        pass
                    os._exit(0)
                threading.Thread(target=_kill, daemon=True).start()
                return

            if path == "/api/interrupt":
                ui_logger.info("Interrupt requested from UI.")
                global _interrupt_requested
                with _lock:
                    _interrupt_requested = True
                send_json_response({"status": "interrupted"})
                return

            if path == "/api/mute":
                is_muted = bool(data.get("muted", False))
                settings.set("mic_muted", is_muted)
                ui_logger.info(f"Microphone mute state set to: {is_muted}")
                if is_muted:
                    try:
                        from NeuralCore.wake_system import wake_system
                        wake_system.reset_trigger()
                    except Exception:
                        pass
                send_json_response({"status": "success", "muted": is_muted})
                return

            if path == "/api/vision":
                is_active = bool(data.get("active", False))
                settings.set("vision_active", is_active)
                ui_logger.info(f"Vision state set to: {is_active}")
                if is_active:
                    with _lock:
                        _pending_inputs.append("[System: User has enabled Vision Camera Mode. You can now see their screen via tools if needed.]")
                send_json_response({"status": "success", "vision_active": is_active})
                return

            send_json_response({"error": "Endpoint not found"}, 404)
        except Exception as e:
            ui_logger.error(f"Error handling POST request {self.path}: {e}")
            send_json_response({"error": "Internal Server Error"}, 500)

    def do_OPTIONS(self):
        """Handle CORS preflight requests from Electron UI."""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, DELETE")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def log_message(self, format, *args):
        pass


from socketserver import ThreadingMixIn

class ReusableHTTPServer(ThreadingMixIn, HTTPServer):
    allow_reuse_address = 1
    daemon_threads = True  # All handler threads are daemon — won't block shutdown

def start_ui_server() -> None:
    """Start the UI server in a daemon thread. Non-blocking."""
    # Restore previous chat session history if enabled
    try:
        restore = settings.get("restore_last_session", True)
        if restore:
            import NeuralCore.vespera_memory
            hist = core.vespera_memory.memory_system.get_history()
            with _lock:
                mapped = []
                for entry in hist:
                    if "user" in entry:
                        mapped.append({"role": "user", "text": entry["user"]})
                    if "ai" in entry:
                        mapped.append({"role": "ai", "text": entry["ai"]})
                _current_status["chat_history"] = mapped[-20:]
            ui_logger.info(f"Restored last session: {len(_current_status['chat_history'])} messages loaded.")
    except Exception as e:
        ui_logger.error(f"Failed to restore last session on startup: {e}")

    bind_host = os.environ.get("VESPERA_UI_BIND", "0.0.0.0")

    def _run():
        try:
            # Bind to 0.0.0.0 so both IPv4 (127.0.0.1) and IPv6 (::1) clients work.
            # We still only serve on localhost — no external exposure.
            server = ReusableHTTPServer((bind_host, PORT), _Handler)
            ui_logger.info(
                f"HTTP server bound to {bind_host}:{PORT} (serving UI from: {UI_DIR})"
            )
            server.serve_forever()
        except OSError as e:
            ui_logger.error(
                f"Port {PORT} bind error on {bind_host}: {e}. "
                f"Is another VesperaCore already holding the port?"
            )
        except Exception as e:
            ui_logger.error(f"UI server crashed: {e}", exc_info=True)

    t = threading.Thread(target=_run, name="ui-server", daemon=True)
    t.start()

    def _watchdog():
        import time as _t
        while True:
            _t.sleep(5)
            if not t.is_alive():
                ui_logger.error("UI server thread is no longer alive.")
                break
    threading.Thread(target=_watchdog, name="ui-server-watchdog", daemon=True).start()

    print(f"[UI] Vespera widget running at http://127.0.0.1:{PORT} (bound on {bind_host})")
