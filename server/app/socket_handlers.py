import logging
from flask import request, flash, current_app
from flask_socketio import SocketIO
from typing import Set, Any
from flask_login import current_user

from .controller import Controller
from .tuya import ACThermostat


class SocketEventHandler:
    _instance: "SocketEventHandler | None" = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, socketio: SocketIO, ctrl: Controller):
        if self._initialized:
            return
        self.socketio = socketio
        self.ctrl = ctrl
        self.logger = logging.getLogger(__name__)
        # Track currently connected sids by role
        self.view_sids: Set[str] = set()
        self.client_sids: Set[str] = set()
        self.esp32_sids: Set[str] = set()
        self._initialized = True
        socketio.on_event('connect',    self.handle_connect)
        socketio.on_event('disconnect', self.handle_disconnect)
        socketio.on_event('image',      self.handle_image)
        socketio.on_event('temphum',    self.handle_temphum)
        socketio.on_event('esp32_temphum', self.handle_esp32_temphum)
        socketio.on_event('status',     self.handle_status)
        socketio.on_event('printerAction', self.handle_printer_action)
        socketio.on_event('ac_control',   self.handle_ac_control)

    def handle_connect(self, auth):
        # Use Flask-Login session cookie for auth instead of API key
        if not current_user.is_authenticated:
            self.logger.warning("Socket connect refused: unauthenticated user")
            return False
        sid = request.sid  # type: ignore
        # Classify this connection
        role = None
        try:
            if isinstance(auth, dict):
                role = (auth.get('role') or auth.get('type') or auth.get('client'))
        except Exception:
            pass
        # Heuristic: consider browsers as view when UA looks like one
        is_view = False
        if role is None:
            ua = str(request.headers.get('User-Agent', '')).lower()
            # Very rough heuristic: browsers include 'mozilla' in UA
            if 'mozilla' in ua:
                is_view = True
        # Normalize role
        role_l = str(role).lower() if role is not None else None
        if sid:
            if role_l == 'view' or is_view:
                self.view_sids.add(sid)
                self.logger.info("View connected: %s (tracked)", sid)
            elif role_l in {'client', 'raspi', 'pi', 'printer', 'timelapse'}:
                self.client_sids.add(sid)
                self.logger.info("Client connected: %s (tracked)", sid)
            elif role_l == 'esp32':
                self.esp32_sids.add(sid)
                self.logger.info("ESP32 server connected: %s (tracked)", sid)
            else:
                self.logger.info("Client connected (unclassified): %s", sid)
        else:
            self.logger.info("Client connected: %s", sid)

    def handle_disconnect(self, *args):
        """Allow any positional args to avoid signature mismatch."""
        sid = request.sid  # type: ignore
        removed = False
        if sid in self.view_sids:
            self.view_sids.discard(sid); removed = True
            self.logger.info("View disconnected: %s (untracked)", sid)
        if sid in self.client_sids:
            self.client_sids.discard(sid); removed = True
            self.logger.info("Client disconnected: %s (untracked)", sid)
        if sid in self.esp32_sids:
            self.esp32_sids.discard(sid); removed = True
            self.logger.info("ESP32 server disconnected: %s (untracked)", sid)
        if not removed:
            self.logger.info("Client disconnected: %s", sid)

    def emit_to_views(self, event: str, payload: Any = None) -> None:
        """Emit event only to currently connected browser views (by sid)."""
        # Iterate over a copy to avoid mutation during iteration
        for sid in list(self.view_sids):
            try:
                self.socketio.emit(event, payload, to=sid)
            except Exception:
                # If emit fails (e.g., stale sid), drop it
                self.view_sids.discard(sid)
                self.logger.debug("Removed stale view sid: %s", sid)

    def emit_to_clients(self, event: str, payload: Any = None) -> None:
        """Emit event only to timelapse/pi clients (not views or esp32)."""
        for sid in list(self.client_sids):
            try:
                self.socketio.emit(event, payload, to=sid)
            except Exception:
                self.client_sids.discard(sid)
                self.logger.debug("Removed stale client sid: %s", sid)

    def emit_to_esp32(self, event: str, payload: Any = None) -> None:
        """Emit event only to esp32_server connections."""
        for sid in list(self.esp32_sids):
            try:
                self.socketio.emit(event, payload, to=sid)
            except Exception:
                self.esp32_sids.discard(sid)
                self.logger.debug("Removed stale esp32 sid: %s", sid)

    def flash(self, message, category):
        """Emit a flash message to the client."""
        self.emit_to_views('flash', {'category': category, 'message': message})
        self.logger.info("Flash message: %s (%s)", category, message)

    def handle_image(self, *args):
        self.emit_to_views('image')
        self.logger.debug("Emitted 'image' event")

    def handle_temphum(self, data):
        temp, hum = data.get('temperature'), data.get('humidity')
        if temp is None or hum is None:
            self.socketio.emit(
                'error', {'message': 'Invalid temperature/humidity data'})
            self.logger.warning("Bad temphum payload: %s", data)
            return
        saved = self.ctrl.record_temphum(temp, hum)
        self.emit_to_views('temphum2v', {
            'temperature': saved.temperature,
            'humidity':    saved.humidity
        })
        self.logger.debug("Broadcasted temphum: %s", data)
        
    def handle_esp32_temphum(self, data):
        location, temp, hum = data.get('location'), data.get('temperature_c'), data.get('humidity_pct')
        if location is None or temp is None or hum is None:
            self.socketio.emit(
                'error', {'message': 'Invalid location/temperature/humidity data'})
            self.logger.warning("Bad esp32 temphum payload: %s", data)
            return
        saved = self.ctrl.record_esp32_temphum(location, temp-1, hum)
        self.emit_to_views('esp32_temphum', {
            'location': saved.location,
            'temperature': saved.temperature,
            'humidity':    saved.humidity
        })
        
        self.logger.debug("Broadcasted esp32 temphum: %s", data)

    def handle_status(self, data):
        if data is None:
            self.socketio.emit('error', {'message': 'Invalid status data'})
            self.logger.warning("Bad status payload: %s", data)
            return
        # saved = self.ctrl.update_status(data)
        self.emit_to_views('status2v', data)
        self.logger.debug("Broadcasted status: %s", data)
        
    def handle_client_response(self, result, action):
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
        result = data.get('result', '')
        if not current_user.is_admin and result == '':
            self.flash(
                "You do not have permission to perform printer actions.",
                'error'
            )
            return
        self.logger.info("Received printer action data: %s", data)
        action = data.get('action', '')
        if result != '':
            self.handle_client_response(result, action)
            return
        if action not in ['pause', 'resume', 'stop', 'home', 
                          'timelapse_start', 'timelapse_stop',
                          'run_gcode'
                          ]:
            self.socketio.emit(
                'error', {'message': f'Invalid printer action: {action}'})
            self.logger.warning("Bad printer action: %s", action)
            return
        
        if action == 'run_gcode':
            gcode = data.get('gcode', '')
            if not gcode:
                self.flash(
                    "No G-code provided for run_gcode action",
                    'error'
                )
                self.logger.error("No G-code provided for run_gcode action")
                return
            try:
                result = self.ctrl.record_gcode_command(gcode=gcode)
            except ValueError as e:
                self.logger.exception("Error recording G-code: %s", e)
                return

        # Send printer action only to registered clients (Pi/Raspi)
        self.emit_to_clients('printerAction', data)
        self.logger.info("Handled printer action: %s", action)

    def handle_ac_control(self, data):
        if data is None or not isinstance(data, dict):
            self.socketio.emit('error', {'message': 'Invalid AC control payload'})
            self.logger.warning("Bad ac_control payload: %s", data)
            return
        action = (data.get('action') or '').strip()
        self.logger.info("Received ac_control: %s", action)
        ac_thermo: ACThermostat | None = getattr(current_app, 'ac_thermostat', None)  # type: ignore
        if ac_thermo is None:
            self.socketio.emit('error', {'message': 'AC thermostat not initialized'})
            self.logger.error("ac_control: thermostat missing")
            return
        try:
            if action == 'power_on':
                ac_thermo.set_power(True)
                return
            if action == 'power_off':
                ac_thermo.set_power(False)
                return
            if action == 'thermostat_enable':
                ac_thermo.enable()
                return
            if action == 'thermostat_disable':
                ac_thermo.disable()
                return
            if action == 'set_mode':
                val = (data.get('value') or '').strip().lower()
                # User reports 'hot' unsupported
                if val not in {'cold', 'wet', 'wind'}:
                    self.socketio.emit('error', {'message': f'Unsupported mode: {val}'})
                    return
                ac_thermo.set_mode(val)
                return
            if action == 'set_fan_speed':
                val = (data.get('value') or '').strip().lower()
                # User reports 'mid' and 'auto' unsupported
                if val not in {'low', 'high'}:
                    self.socketio.emit('error', {'message': f'Unsupported fan speed: {val}'})
                    return
                ac_thermo.set_fan_speed(val)
                return
            if action == 'set_setpoint':
                try:
                    val = float(data.get('value'))
                except Exception:
                    self.socketio.emit('error', {'message': 'Invalid setpoint'})
                    return
                ac_thermo.set_setpoint(val)
                return
            if action == 'set_hysteresis':
                try:
                    val = float(data.get('value'))
                except Exception:
                    self.socketio.emit('error', {'message': 'Invalid hysteresis'})
                    return
                # Backward-compatible single value: split evenly
                ac_thermo.set_hysteresis(val)
                return
            if action == 'set_hysteresis_split':
                try:
                    pos = float(data.get('pos'))
                    neg = float(data.get('neg'))
                except Exception:
                    self.socketio.emit('error', {'message': 'Invalid hysteresis values'})
                    return
                ac_thermo.set_hysteresis_split(pos, neg)
                return
            if action == 'status':
                # Re-emit current statuses to requester(s)
                self.emit_to_views('ac_status', { 'is_on': bool(ac_thermo.is_on) })
                self.emit_to_views('thermostat_status', {
                    'enabled': getattr(ac_thermo, '_enabled', True),
                    'thermo_active': getattr(ac_thermo, '_enabled', True),
                })
                # Also emit current mode/fan
                try:
                    st = ac_thermo.ac.get_status()
                    mode = st.get('mode') if isinstance(st, dict) else None
                    fan  = st.get('fan_speed_enum') if isinstance(st, dict) else None
                except Exception:
                    mode = None
                    fan = None
                self.emit_to_views('ac_state', { 'mode': mode, 'fan_speed': fan })
                # Emit current sleep configuration as well
                self.emit_to_views('sleep_status', {
                    'sleep_enabled': bool(getattr(ac_thermo.cfg, 'sleep_active', True)),
                    'sleep_start': ac_thermo.cfg.sleep_start,
                    'sleep_stop': ac_thermo.cfg.sleep_stop,
                })
                # Emit thermostat configuration
                self.emit_to_views('thermo_config', {
                    'setpoint_c': float(getattr(ac_thermo.cfg, 'target_temp', 0.0)),
                    'pos_hysteresis': float(getattr(ac_thermo.cfg, 'pos_hysteresis', 0.0)),
                    'neg_hysteresis': float(getattr(ac_thermo.cfg, 'neg_hysteresis', 0.0)),
                })
                return
            if action == 'set_sleep_enabled':
                en = bool(data.get('value'))
                ac_thermo.set_sleep_enabled(en)
                return
            if action == 'set_sleep_times':
                start = (data.get('start') or '').strip() or None
                stop  = (data.get('stop') or '').strip() or None
                ac_thermo.set_sleep_times(start, stop)
                return
            self.socketio.emit('error', {'message': f'Invalid AC control action: {action}'})
            self.logger.warning("Bad ac_control action: %s", action)
        except Exception as e:
            self.logger.exception("ac_control error: %s", e)
            self.socketio.emit('error', {'message': 'AC control error'})
