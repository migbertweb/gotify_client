import websocket
import threading
import json
import time
from PyQt6.QtCore import QObject, pyqtSignal

class GotifyClient(QObject):
    message_received = pyqtSignal(dict)
    connection_status = pyqtSignal(bool)

    def __init__(self, url, token):
        super().__init__()
        self.url = url
        self.token = token
        self.ws = None
        self.running = False
        self.thread = None

    def connect(self):
        if self.running:
            return

        if not self.url or not self.token:
            return

        # Prepare URL
        ws_url = self.url.replace("http://", "ws://").replace("https://", "wss://")
        if not ws_url.endswith("/"):
            ws_url += "/"
        ws_url += f"stream?token={self.token}"

        self.running = True
        self.thread = threading.Thread(target=self._run_ws, args=(ws_url,), daemon=True)
        self.thread.start()

    def disconnect(self):
        self.running = False
        if self.ws:
            self.ws.close()
        if self.thread:
            self.thread.join(timeout=1)

    def _run_ws(self, url):
        while self.running:
            try:
                self.ws = websocket.WebSocketApp(
                    url,
                    on_open=self._on_open,
                    on_message=self._on_message,
                    on_error=self._on_error,
                    on_close=self._on_close
                )
                self.ws.run_forever()
            except Exception as e:
                print(f"WebSocket error: {e}")
            
            if self.running:
                print("Reconnecting in 5 seconds...")
                time.sleep(5)

    def _on_open(self, ws):
        print("Connected to Gotify")
        self.connection_status.emit(True)

    def _on_message(self, ws, message):
        try:
            data = json.loads(message)
            self.message_received.emit(data)
        except json.JSONDecodeError:
            pass

    def _on_error(self, ws, error):
        print(f"Gotify Error: {error}")

    def _on_close(self, ws, close_status_code, close_msg):
        print("Disconnected from Gotify")
        self.connection_status.emit(False)
