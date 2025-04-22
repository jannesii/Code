# app/api.py
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required
from datetime import datetime
import pytz

api_bp = Blueprint('api', __name__)

@api_bp.route('/temphum')
@login_required
def temphum():
    finland_tz = pytz.timezone('Europe/Helsinki')
    date_str = request.args.get('date', datetime.now(finland_tz).date().isoformat())
    ctrl = current_app.ctrl
    data = ctrl.get_temphum_for_date(date_str)
    return jsonify([
        {'timestamp': d.timestamp, 'temperature': d.temperature, 'humidity': d.humidity}
        for d in data
    ])
