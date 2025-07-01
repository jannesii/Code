# app/api.py
import logging
import os
import tempfile
from datetime import datetime
import pytz
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_login import login_required, current_user

api_bp = Blueprint('api', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)

@api_bp.route('/temphum')
@login_required
def get_temphum():
    ctrl = current_app.ctrl
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

@api_bp.route('/timelapse_config')
@login_required
def get_timelapse_config():
    ctrl = current_app.ctrl
    conf = ctrl.get_timelapse_conf()
    vals = {
        'image_delay':   conf.image_delay,
        'temphum_delay': conf.temphum_delay,
        'status_delay':  conf.status_delay
    }
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
    ctrl = current_app.ctrl
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
    logger.info("Serving tmp file: preview.jpg")

    # In production, you may want to sanitize `path`!
    temp_dir = tempfile.gettempdir()
    return send_from_directory(temp_dir, 'preview.jpg')
