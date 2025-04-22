import logging
import hmac
from flask import current_app, request
from flask_socketio import SocketIO

class SocketEventHandler:
    def __init__(self, socketio: SocketIO, ctrl):
        self.socketio = socketio
        self.ctrl     = ctrl
        self.logger   = logging.getLogger(__name__)

        socketio.on_event('connect',    self.handle_connect)
        socketio.on_event('disconnect', self.handle_disconnect)
        socketio.on_event('image',      self.handle_image)
        socketio.on_event('temphum',    self.handle_temphum)
        socketio.on_event('status',     self.handle_status)

    def handle_connect(self, auth):
        # Use Flask-Login session cookie for auth instead of API key
        from flask_login import current_user
        if not current_user.is_authenticated:
            self.logger.warning("Socket connect refused: unauthenticated user")
            return False
        self.logger.info("Client connected: %s", request.sid)

    def handle_disconnect(self, *args):
        """Allow any positional args to avoid signature mismatch."""
        self.logger.info("Client disconnected: %s", request.sid)

    def handle_image(self, data):
        if not data or 'image' not in data:
            self.socketio.emit('error', {'message': 'Invalid image data'})
            self.logger.warning("Bad image payload: %s", data)
            return
        saved = self.ctrl.record_image(data['image'])
        self.socketio.emit('image2v', {'image': saved.image})
        self.logger.info("Broadcasted image")

    def handle_temphum(self, data):
        temp, hum = data.get('temperature'), data.get('humidity')
        if temp is None or hum is None:
            self.socketio.emit('error', {'message': 'Invalid temperature/humidity data'})
            self.logger.warning("Bad temphum payload: %s", data)
            return
        saved = self.ctrl.record_temphum(temp, hum)
        self.socketio.emit('temphum2v', {
            'temperature': saved.temperature,
            'humidity':    saved.humidity
        })
        self.logger.info("Broadcasted temphum: %s", data)

    def handle_status(self, data):
        status = data.get('status')
        if status is None:
            self.socketio.emit('error', {'message': 'Invalid status data'})
            self.logger.warning("Bad status payload: %s", data)
            return
        saved = self.ctrl.record_status(status)
        self.socketio.emit('status2v', {'status': saved.status})
        self.logger.info("Broadcasted status: %s", saved.status)
