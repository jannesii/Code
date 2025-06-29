import logging
from flask import request, flash
from flask_socketio import SocketIO

from .controller import Controller


class SocketEventHandler:
    _instance: "SocketEventHandler | None" = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, socketio: SocketIO = None, ctrl: Controller = None):
        if self._initialized:
            return
        self.socketio = socketio
        self.ctrl = ctrl
        self.logger = logging.getLogger(__name__)
        self._initialized = True
        socketio.on_event('connect',    self.handle_connect)
        socketio.on_event('disconnect', self.handle_disconnect)
        # socketio.on_event('image',      self.handle_image)
        socketio.on_event('temphum',    self.handle_temphum)
        socketio.on_event('status',     self.handle_status)
        socketio.on_event('printerAction', self.handle_printer_action)

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

    def flash(self, message, category):
        """Emit a flash message to the client."""
        self.socketio.emit('flash', {'category': category, 'message': message})
        self.logger.info("Flash message: %s (%s)", category, message)

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
            self.socketio.emit(
                'error', {'message': 'Invalid temperature/humidity data'})
            self.logger.warning("Bad temphum payload: %s", data)
            return
        saved = self.ctrl.record_temphum(temp, hum)
        self.socketio.emit('temphum2v', {
            'temperature': saved.temperature,
            'humidity':    saved.humidity
        })
        self.logger.info("Broadcasted temphum: %s", data)

    def handle_status(self, data):
        if data is None:
            self.socketio.emit('error', {'message': 'Invalid status data'})
            self.logger.warning("Bad status payload: %s", data)
            return
        # saved = self.ctrl.update_status(data)
        self.socketio.emit('status2v', data)
        self.logger.info("Broadcasted status: %s", data)
        
    def handler_printer_result(self, result, action):
        if result is None:
            self.socketio.emit('error', {'message': 'Invalid printer result'})
            self.logger.warning("Bad printer result: %s", result)
            return
        elif result == '':
            return
        
        if result:
            self.flash(
                f"Printer action '{action}' completed successfully.",
                'success'
            )
        else:
            self.flash(
                f"Printer action '{action}' failed.",
                'error'
            )

    def handle_printer_action(self, data):
        action = data.get('action', '')
        result = data.get('result', '')
        if result != '':
            self.handler_printer_result(result, action)
            return
        if action not in ['pause', 'resume', 'stop', 'home']:
            self.socketio.emit(
                'error', {'message': f'Invalid printer action: {action}'})
            self.logger.warning("Bad printer action: %s", action)
            return
        
        self.socketio.emit('printerAction', {'action': action})
        self.logger.info("Handled printer action: %s", action)
