import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

class OBSGlassServer:
    """
    💎 OBS Glass Server: Serves transparent HTML5/WebGL widgets directly to OBS Studio.
    """
    def __init__(self, port=7866):
        self.port = port
        self.host = "127.0.0.1"
        self._server = None
        self._thread = None
        self.web_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "wraithglass", "obs_widgets"))
        
        # Ensure the directory exists
        os.makedirs(self.web_root, exist_ok=True)
        self._create_default_widget()

    def _create_default_widget(self):
        index_path = os.path.join(self.web_root, "index.html")
        if not os.path.exists(index_path):
            with open(index_path, "w", encoding="utf-8") as f:
                f.write('''<!DOCTYPE html>
<html>
<head>
    <style>
        body { 
            margin: 0; overflow: hidden; 
            background-color: transparent !important; 
            font-family: 'Inter', sans-serif;
            color: white;
        }
        .widget {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 20px;
            width: 300px;
        }
    </style>
</head>
<body>
    <div class="widget">
        <h3>Vespera Stream Info</h3>
        <p>Awaiting data...</p>
    </div>
</body>
</html>''')

    def _run_server(self):
        class Handler(SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=self.web_root, **kwargs)

        self._server = HTTPServer((self.host, self.port), Handler)
        print(f"[OBS_GlassServer] Serving Bespoke Widgets on http://{self.host}:{self.port}")
        self._server.serve_forever()

    def start(self):
        self._thread = threading.Thread(target=self._run_server, daemon=True, name="OBSGlassServer")
        self._thread.start()

obs_glass_server = OBSGlassServer()
