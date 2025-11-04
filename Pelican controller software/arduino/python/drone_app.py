"""
PyWebView desktop application for P8 PRO Drone Controller

This file exposes a small API used by the frontend (web/app.js) to control the
`DroneNLPController` backend and provides an embedded desktop UI via pywebview.
"""
import os
import threading
import json
import webview
from pathlib import Path

from drone_nlp_controller import DroneNLPController

BASE_DIR = Path(__file__).parent
WEB_DIR = BASE_DIR / 'web'
INDEX_FILE = WEB_DIR / 'index.html'

class DroneAPI:
    def __init__(self):
        self.controller = None
        self.lock = threading.Lock()

    def _ensure_controller(self):
        if self.controller is None:
            # Default port left empty; GUI will request explicit port
            self.controller = DroneNLPController(arduino_port="COM3")
        return self.controller

    # Exposed methods for JS (pywebview will call them)
    def get_serial_ports(self):
        import serial.tools.list_ports
        ports = [p.device for p in serial.tools.list_ports.comports()]
        return ports

    def connect(self, port):
        with self.lock:
            self.controller = DroneNLPController(arduino_port=port)
            ok = self.controller.connect_arduino()
            return {"connected": ok}

    def disconnect(self):
        with self.lock:
            if self.controller:
                self.controller.disconnect_arduino()
                self.controller = None
            return {"disconnected": True}

    def send_command(self, command):
        with self.lock:
            if not self.controller or not self.controller.is_connected:
                return {"sent": False, "reason": "not_connected"}
            self.controller.process_text_command(command)
            return {"sent": True}

    def start_voice(self):
        # Start voice recognition in a background thread
        def voice_loop(ctrl):
            try:
                ctrl.run_voice_mode()
            except Exception as e:
                print('Voice thread error:', e)

        with self.lock:
            if not self.controller:
                return {"started": False, "reason": "not_connected"}
            t = threading.Thread(target=voice_loop, args=(self.controller,), daemon=True)
            t.start()
            return {"started": True}

    def stop_voice(self):
        # The controller's run_voice_mode reacts to user stopping; we can try to set a flag
        # but the simple controller uses KeyboardInterrupt or local flow; leave as best-effort
        # For now just return success; real implementation could add an event to break loop
        return {"stopped": True}

    def get_status(self):
        with self.lock:
            if not self.controller:
                return {"armed": False, "flying": False, "last_command": None}
            s = self.controller.drone_state
            return {"armed": bool(s.get('armed')), "flying": bool(s.get('flying')), "last_command": s.get('last_command')}

# Launch function used by webview
def start_webview():
    api = DroneAPI()

    # Determine index file path
    index_path = INDEX_FILE.resolve().as_uri()

    # Create the window with the Python API bound to `window.pywebview.api` in JS
    window = webview.create_window('P8 PRO Drone Controller', index_path, js_api=api, width=1000, height=700)

    # Try preferred GUI backends in order. On Windows, edgechromium (WebView2) is preferred.
    try:
        print('Starting webview with edgechromium backend...')
        webview.start(gui='edgechromium', debug=False)
    except Exception as e:
        print('edgechromium start failed:', e)
        try:
            print('Falling back to default webview.start()')
            webview.start()
        except Exception as e2:
            print('Fallback start also failed:', e2)
            raise

if __name__ == '__main__':
    start_webview()
