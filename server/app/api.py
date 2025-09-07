# app/api.py
import logging
import os
import tempfile
from datetime import datetime
import pytz
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_login import login_required, current_user
from .controller import Controller
from typing import Any, Dict

api_bp = Blueprint('api', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)

@api_bp.route('/temphum')
@login_required
def get_temphum():
    ctrl: Controller = current_app.ctrl # type: ignore
    finland_tz = pytz.timezone('Europe/Helsinki')
    date_str = request.args.get('date', datetime.now(finland_tz).date().isoformat())
    logger.info(
        "API /temphum for %s by %s",
        date_str, current_user.get_id()
    )
    data = ctrl.get_temphum_for_date(date_str)
    return jsonify([
        {'timestamp': d.timestamp, 'temperature': d.temperature, 'humidity': d.humidity}
        for d in data
    ])
    
@api_bp.route('/esp32_temphum')
@login_required
def get_esp32_temphum():
    ctrl: Controller = current_app.ctrl # type: ignore
    finland_tz = pytz.timezone('Europe/Helsinki')
    date_str = request.args.get('date', datetime.now(finland_tz).date().isoformat())
    location = request.args.get('location', 'default').strip()
    logger.info(
        "API /esp32_temphum for %s by %s",
        date_str, current_user.get_id()
    )
    data = ctrl.get_esp32_temphum_for_date(date_str, location)
    return jsonify([
        {'timestamp': d.timestamp, 'temperature': d.temperature, 'humidity': d.humidity}
        for d in data
    ])


@api_bp.route('/timelapse_config')
@login_required
def get_timelapse_config():
    ctrl: Controller = current_app.ctrl # type: ignore
    conf = ctrl.get_timelapse_conf()
    vals = {
        'image_delay':   conf.image_delay,
        'temphum_delay': conf.temphum_delay,
        'status_delay':  conf.status_delay
    } if conf else {}
    logger.info(
        "API /timelapse_config by %s",
        current_user.get_id()
    )
    return jsonify(vals)

@api_bp.route('/gcode')
@login_required
def get_gcode_commands():
    """
    Get all G-code commands from the database.
    """
    ctrl: Controller = current_app.ctrl # type: ignore
    commands = ctrl.get_all_gcode_commands()
    return jsonify({
        'gcode_list': commands
    })

@api_bp.route('/previewJpg')
@login_required
def serve_tmp_file():
    """
    Serve any file under /tmp via HTTP.
    """
    # Log every request for debugging
    logger.debug("Serving tmp file: preview.jpg")

    # In production, you may want to sanitize `path`!
    temp_dir = tempfile.gettempdir()
    return send_from_directory(temp_dir, 'preview.jpg')


@api_bp.route('/ac/status')
@login_required
def get_ac_status():
    """Return current AC on/off status from the running thermostat."""
    ac_thermo = getattr(current_app, 'ac_thermostat', None)  # type: ignore
    if ac_thermo is None:
        logger.warning("API /ac/status requested but thermostat not initialized")
        return jsonify({
            "is_on": None,
            "thermostat_enabled": None,
            "thermo_active": None,
            "mode": None,
            "fan_speed": None,
            "sleep_enabled": None,
            "sleep_start": None,
            "sleep_stop": None,
        }), 503
    try:
        enabled = getattr(ac_thermo, '_enabled', True)
        try:
            st = ac_thermo.ac.get_status()
            mode = st.get('mode') if isinstance(st, dict) else None
            fan  = st.get('fan_speed_enum') if isinstance(st, dict) else None
        except Exception:
            mode = None
            fan = None
        return jsonify({
            "is_on": bool(ac_thermo.is_on),
            "thermostat_enabled": bool(enabled),
            "thermo_active": bool(enabled),
            "mode": mode,
            "fan_speed": fan,
            "sleep_enabled": bool(getattr(ac_thermo.cfg, 'sleep_enabled', True)),
            "sleep_start": getattr(ac_thermo.cfg, 'sleep_start', None),
            "sleep_stop": getattr(ac_thermo.cfg, 'sleep_stop', None),
            "setpoint_c": float(getattr(ac_thermo.cfg, 'setpoint_c', 0.0)),
            "pos_hysteresis": float(getattr(ac_thermo.cfg, 'pos_hysteresis', 0.0)),
            "neg_hysteresis": float(getattr(ac_thermo.cfg, 'neg_hysteresis', 0.0)),
        })
    except Exception as e:
        logger.exception("Error reading AC status: %s", e)
        return jsonify({
            "is_on": None,
            "thermostat_enabled": None,
            "thermo_active": None,
            "mode": None,
            "fan_speed": None,
            "sleep_enabled": None,
            "sleep_start": None,
            "sleep_stop": None,
        }), 500
