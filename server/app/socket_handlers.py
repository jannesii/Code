# app/socket_handlers.py
import hmac
from flask import current_app
from flask_socketio import SocketIO

class SocketEventHandler:
    def __init__(self, socketio: SocketIO, ctrl):
        self.socketio = socketio
        self.ctrl = ctrl
        # Register event handlers (type ignores to satisfy stub signatures)
        self.socketio.on_event('connect', self.on_connect)    # type: ignore
        self.socketio.on_event('disconnect', self.on_disconnect)  # type: ignore
        self.socketio.on_event('image', self.on_image)        # type: ignore
        self.socketio.on_event('temphum', self.on_temphum)    # type: ignore
        self.socketio.on_event('status', self.on_status)      # type: ignore

    def _auth_ok(self, auth):
        api_key = (auth or {}).get('api_key')
        # Ensure API_KEY from config is a string
        api_key_config: str = current_app.config['SECRET_KEY']
        return bool(api_key and hmac.compare_digest(api_key, api_key_config))

    def on_connect(self, auth):
        if not self._auth_ok(auth):
            return False
        print("Client connected")

    def on_disconnect(self):
        print("Client disconnected")

    def on_image(self, data):
        if not data or 'image' not in data:
            self.socketio.emit('error', {'message': 'Invalid image data'})
            return
        saved = self.ctrl.record_image(data['image'])
        self.socketio.emit('image2v', {'image': saved.image})
        print("Broadcasting image.")

    def on_temphum(self, data):
        temp = data.get('temperature')
        hum = data.get('humidity')
        if temp is None or hum is None:
            self.socketio.emit('error', {'message': 'Invalid temphum data'})
            return
        saved = self.ctrl.record_temphum(temp, hum)
        self.socketio.emit('temphum2v', {'temperature': saved.temperature, 'humidity': saved.humidity})
        print(f"Broadcasting temphum: {saved.temperature}, {saved.humidity}")

    def on_status(self, data):
        status = data.get('status')
        if status is None:
            self.socketio.emit('error', {'message': 'Invalid status data'})
            return
        saved = self.ctrl.record_status(status)
        self.socketio.emit('status2v', {'status': saved.status})
        print(f"Broadcasting status: {saved.status}")
