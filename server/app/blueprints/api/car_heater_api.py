"""Car Heater API routes."""
from datetime import datetime, date
from typing import Any, Dict, List
import logging
import json
from flask import Blueprint, request, jsonify, current_app
from ...core import Controller
from ...core.models import CarHeaterStatus
from ...extensions import csrf
from ...security import require_api_key

car_bp = Blueprint('car_bp', __name__, url_prefix='/car_heater')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@car_bp.route('/status', methods=['POST'])
@csrf.exempt
@require_api_key
def update_car_heater_status():
    """Update the car heater status and return queued commands."""
    ctrl: Controller = getattr(current_app, "ctrl", None)
    if ctrl is None:
        return jsonify({"error": "Controller not initialized"}), 500

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    # Raw Shelly JSON payload from the ESP
    shelly_raw = data.get("shelly")
    timestamp = data.get("timestamp")

    shelly = None
    if shelly_raw:
        try:
            shelly = json.loads(shelly_raw)
        except json.JSONDecodeError:
            logger.warning("Failed to decode shelly JSON: %r", shelly_raw)
    if shelly is None:
        shelly = {}

    aenergy = shelly.get("aenergy") or {}
    temp = shelly.get("temperature") or {}
    car = CarHeaterStatus(
        id=None,
        # Core status
        timestamp=timestamp,
        is_heater_on=bool(shelly.get("output")),        # True / False
        instant_power_w=shelly.get("apower", 0.0),       # e.g. 35.1
        voltage_v=shelly.get("voltage"),          # e.g. 229.7
        current_a=shelly.get("current"),          # e.g. 0.187

        # Energy (Wh)
        energy_total_wh=aenergy.get("total"),     # lifetime energy
        energy_last_min_wh=(aenergy.get("by_minute") or [None])[0],
        energy_ts=aenergy.get("minute_ts"),         # UNIX ts

        # Device temperature

        device_temp_c=temp.get("tC"),             # 37.9
        device_temp_f=temp.get("tF"),             # 100.1
        ambient_temp=data.get("temperature"),    # in Celsius

        # Optional/meta
        source=shelly.get("source")                # 'button', 'HTTP_in', ...
    )

    # Persist status in DB
    try:
        recorded = ctrl.record_car_heater_status(car)
        logger.debug("Recorded car heater status: %s", recorded)
    except Exception as e:
        logger.exception("Failed to record car heater status: %s", e)

    # Fetch any queued commands from the shared CarHeaterService
    commands: List[Dict[str, Any]] = []
    try:
        service = current_app.config.get("CAR_HEATER_SERVICE")
        if service is None:
            logger.warning("CAR_HEATER_SERVICE not found in app.config")
        else:
            commands = service.get_queued_commands()
    except Exception as e:
        logger.exception("Failed to fetch queued car heater commands: %s", e)

    # Return commands as a plain JSON list so ESP can act on them
    return jsonify(commands), 200
