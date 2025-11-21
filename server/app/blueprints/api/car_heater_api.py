"""Car Heater API routes."""
from datetime import datetime, date, timezone
from typing import Any, Dict, List
import logging
import json
from zoneinfo import ZoneInfo
from flask import Blueprint, request, jsonify, current_app
from ...core import Controller
from ...core.models import CarHeaterStatus
from ...extensions import csrf
from ...security import require_api_key

car_bp = Blueprint('car_bp', __name__, url_prefix='/car_heater')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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
    
    action_results = data.get("action_results", {})
    if action_results:
        logger.info("Received action results from car heater ESP: \n\n%r", action_results)
        # Here you could process action_results if needed
        
    shelly_connected = bool(data.get("shelly_connected", True))

    # Raw Shelly JSON payload from the ESP
    shelly_raw = data.get("shelly")
    
    raw_ts = data.get("timestamp")  # '2025-11-21 19:44:10'

    # Interpret the string as UTC
    dt_utc = datetime.strptime(raw_ts, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)

    # Convert to Helsinki time (or whatever you use)
    dt_local = dt_utc.astimezone(ZoneInfo("Europe/Helsinki"))

    timestamp = dt_local

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
    
    if shelly:
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
            
        # Notify any connected browser views of the latest status
        try:
            handler = getattr(current_app, "sio_handler", None)
            if handler is not None:
                handler.emit_to_views("car_heater_status", {
                    "status": {
                        "id": recorded.id if 'recorded' in locals() else None,
                        "timestamp": car.timestamp,
                        "is_heater_on": car.is_heater_on,
                        "instant_power_w": car.instant_power_w,
                        "voltage_v": car.voltage_v,
                        "current_a": car.current_a,
                        "energy_total_wh": car.energy_total_wh,
                        "energy_last_min_wh": car.energy_last_min_wh,
                        "energy_ts": car.energy_ts,
                        "device_temp_c": car.device_temp_c,
                        "device_temp_f": car.device_temp_f,
                        "ambient_temp": car.ambient_temp,
                        "source": car.source,
                    }
                })
        except Exception as e:
            logger.exception("Failed to emit car_heater_status over Socket.IO: %s", e)
    else:
        logger.warning("No shelly data provided in car heater status update")

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
    if commands:
        logger.info("Sending %s commands to car heater ESP", commands)


    # Return commands as a plain JSON list so ESP can act on them
    return jsonify(commands), 200
