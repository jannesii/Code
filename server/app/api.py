# app/api.py
import logging
from datetime import datetime
import pytz
from flask import Blueprint, request, jsonify, current_app
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
