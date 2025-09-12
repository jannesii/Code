"""Bootstrap initialization for long‑lived services (AC, Hue, Socket events).

Moves heavy wiring out of the app factory to keep it lean and testable.
"""

from __future__ import annotations

import os
import threading
import logging
from typing import Any, Dict

from tuya_iot import TuyaOpenAPI

from .ac.thermostat import ACThermostat
from .ac.controller import ACController
from .hue.controller import HueController
from ..extensions import socketio
from ..sockets.handlers import SocketEventHandler


logger = logging.getLogger(__name__)


def _make_notify(ctrl) -> Any:
    """Create a notifier that emits events to browser views via SocketEventHandler."""

    def _notify(event: str, payload: Dict[str, Any]):
        try:
            handler = SocketEventHandler(socketio, ctrl)
            handler.emit_to_views(event, payload)
        except Exception:
            try:
                socketio.emit(event, payload)
            except Exception:
                pass

    return _notify


def init_services(app) -> Dict[str, Any]:
    """Initialize AC thermostat, Hue controller, and Socket event handlers.

    Returns a dictionary of created service instances.
    """
    services: Dict[str, Any] = {}

    # Ensure Socket event handlers are registered (singleton takes care of idempotency)
    app.sio_handler = SocketEventHandler(socketio, app.ctrl)  # type: ignore[attr-defined]

    # --- AC / Thermostat ---
    ACCESS_ID = os.getenv("TUYA_ACCESS_ID")
    ACCESS_KEY = os.getenv("TUYA_ACCESS_KEY")
    API_ENDPOINT = os.getenv("TUYA_API_ENDPOINT")
    USERNAME = os.getenv("TUYA_USERNAME")
    PASSWORD = os.getenv("TUYA_PASSWORD")
    COUNTRY_CODE = os.getenv("TUYA_COUNTRY_CODE")
    SCHEMA = os.getenv("TUYA_SCHEMA")
    DEVICE_ID = os.getenv("TUYA_DEVICE_ID")

    try:
        api = TuyaOpenAPI(API_ENDPOINT, ACCESS_ID, ACCESS_KEY)
        api.connect(USERNAME, PASSWORD, COUNTRY_CODE, SCHEMA)
        ac_controller = ACController(device_id=DEVICE_ID, api=api)
        THERMOSTAT_LOCATION = os.getenv("THERMOSTAT_LOCATION", "Tietokonepöytä")
        # Load thermostat configuration from DB (seed default if missing)
        try:
            cfg = app.ctrl.get_thermostat_conf()  # type: ignore[attr-defined]
        except Exception as e:
            logger.warning("thermo: failed to load config from DB: %s", e)
            cfg = None
        if cfg is None:
            try:
                logger.warning("thermo: seeding default thermostat config in DB")
                cfg = app.ctrl.ensure_thermostat_conf_seeded_from(None)  # type: ignore[attr-defined]
            except Exception:
                pass

        ac_thermostat = ACThermostat(
            ac=ac_controller,
            cfg=cfg,  # type: ignore[arg-type]
            ctrl=app.ctrl,  # type: ignore[attr-defined]
            location=THERMOSTAT_LOCATION,
            notify=_make_notify(app.ctrl),  # type: ignore[attr-defined]
        )
        app.ac_thermostat = ac_thermostat  # type: ignore[attr-defined]
        t = threading.Thread(target=ac_thermostat.run_forever, daemon=True)
        t.start()
        services["ac_thermostat"] = ac_thermostat
        logger.info("Tuya AC controller started for device %s", DEVICE_ID)
    except Exception as e:
        logger.exception("Failed to initialize AC thermostat: %s", e)

    # --- Hue time‑based routine ---
    try:
        hue_bridge_ip = os.getenv("HUE_BRIDGE_IP")
        hue_username = os.getenv("HUE_USERNAME")
        hue = HueController(hue_bridge_ip, hue_username)
        hue.start_time_based_routine(apply_immediately=False)
        services["hue_controller"] = hue
    except Exception as e:
        logger.exception("Failed to initialize Hue routine: %s", e)

    return services

