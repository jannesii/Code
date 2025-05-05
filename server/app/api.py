# app/api.py
import logging
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

@api_bp.route('/tmp/<path:filename>')
def serve_tmp_file(filename):
    """
    Serve any file under /tmp via HTTP.
    """
    # Log every request for debugging
    current_app.logger.info(f"Serving tmp file: {filename}")

    # In production, you may want to sanitize `filename`!
    return send_from_directory('/tmp', filename)