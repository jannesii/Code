# app/api.py
import logging
import os
import tempfile
from datetime import datetime
import pytz
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_login import login_required, current_user
from .controller import Controller

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

@api_bp.route('/temperature', methods=["POST"])
@login_required
def temperature():
    data = request.get_json(force=True, silent=True) or {}
    logger.debug(
        "API /temperature test=%s", data
    )
    return jsonify({"ok": True}), 200

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
