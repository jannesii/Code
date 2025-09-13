"""API routes."""
import logging
import os
import tempfile
from datetime import datetime
import pytz
from flask import Blueprint, request, jsonify, current_app, send_from_directory, render_template
from flask_login import login_required, current_user
import threading
from ...core.controller import Controller
from ...services.ac.thermostat import ACThermostat
from typing import Any, Dict
from datetime import timedelta
from ...extensions import csrf
from ...security import require_api_key
from datetime import timezone

# In-memory state for ESP32 test telemetry (no DB persistence)
_esp32_test_last: dict[str, Any] = {
    'last_seen': None,   # UTC datetime
    'location': None,    # str | None
    'uptime_ms': None,   # int | None
    'remote_addr': None,  # str | None
    'data': None,        # original payload
}

api_bp = Blueprint('api', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@api_bp.route('/esp32_temphum', methods=['GET'])
@login_required
def get_esp32_temphum():
    ctrl: Controller = current_app.ctrl  # type: ignore
    finland_tz = pytz.timezone('Europe/Helsinki')
    date_str = request.args.get(
        'date', datetime.now(finland_tz).date().isoformat())
    location = request.args.get('location', 'default').strip()
    logger.info(
        "API /esp32_temphum for %s by %s",
        date_str, current_user.get_id()
    )
    data = ctrl.get_esp32_temphum_for_date(date_str, location)
    return jsonify([
        {
            'timestamp': d.timestamp,
            'temperature': d.temperature,
            'humidity': d.humidity,
            'ac_on': getattr(d, 'ac_on', None)
        }
        for d in data
    ])

ac_check_flag = True

@api_bp.route('/esp32_temphum', methods=['POST'])
@require_api_key
@csrf.exempt
def post_esp32_temphum():

    data = request.get_json(silent=True) or {}
    location, temp, hum, error = data.get('location'), data.get(
        'temperature_c'), data.get('humidity_pct'), data.get('error')

    if error:
        logger.error(f'ESP32 ERROR: {error} | Location: {location}')
        return jsonify({
            'ok': False,
            'error': 'device_error',
            'message': str(error),
        }), 400

    if location is None or temp is None or hum is None:
        logger.warning("Bad esp32 temphum payload: %s", data)
        return jsonify({
            'ok': False,
            'error': 'invalid_payload',
            'message': 'location, temperature_c, humidity_pct required',
        }), 400

    valid_locations = ["Keittiö", "Makuuhuone",
                       "Tietokonepöytä", "WC", "Parveke", "test"]
    if location not in valid_locations:
        logger.warning(f"Invalid esp32 location: {location}")
        return jsonify({
            'ok': False,
            'error': 'invalid_payload',
            'message': 'Invalid location',
        }), 400

    ctrl: Controller = current_app.ctrl
    # Derive current AC state if available
    try:
        ac_thermo: ACThermostat | None = getattr(
            current_app, 'ac_thermostat', None)  # type: ignore
        ac_on_val: bool | None = bool(
            ac_thermo.is_on) if ac_thermo is not None else None
        if ac_on_val is None:
            # Fallback to persisted DB flag if thermostat not in memory
            conf = ctrl.get_thermostat_conf()
            if conf and conf.current_phase in ('on', 'off'):
                ac_on_val = (conf.current_phase == 'on')
    except Exception:
        ac_on_val = None

    saved = ctrl.record_esp32_temphum(
        location, temp, hum, ac_on=ac_on_val)
    current_app.sio_handler.emit_to_views('esp32_temphum', {
        'location': saved.location,
        'temperature': saved.temperature,
        'humidity':    saved.humidity,
        'ac_on':       saved.ac_on
    })
    def reset_flag():
        global ac_check_flag
        ac_check_flag = True
        
    # Trigger immediate thermostat check once per minute at most
    global ac_check_flag
    if ac_check_flag:
        ac_check_flag = False
        # Wait a second to make sure all sensors have reported
        threading.Timer(1, ac_thermo.step_on_off_check).start() if ac_thermo else None
        # Reset flag after 10 seconds
        threading.Timer(10, reset_flag).start()
        
    return jsonify({
        'ok': True,
        'received': {
            'location': saved.location,
            'temp': saved.temperature,
            'hum': saved.humidity
        },
    })


@api_bp.route('/esp32_test', methods=['GET', 'POST'])
@csrf.exempt
def esp32_test():
    """
    Protected endpoint for testing ESP32 Wi‑Fi/internet connectivity.

    - Requires API key (Authorization: Bearer <token> or X-API-Key).
    - POST: device sends JSON every second: { location, uptime_ms, ... } (stored in-memory only).
    - GET:  returns HTML page by default; `?format=json` returns latest status as JSON.
    """
    global _esp32_test_last

    if request.method == 'POST':
        payload = request.get_json(silent=True) or {}
        # Normalize/validate minimal fields
        location = (payload.get('location') or 'default') if isinstance(
            payload, dict) else 'default'
        try:
            uptime_ms = int(payload.get('uptime_ms')) if isinstance(
                payload, dict) and 'uptime_ms' in payload else None
        except Exception:
            uptime_ms = None
        remote = (request.headers.get('X-Forwarded-For')
                  or request.remote_addr or '').split(',')[0].strip()
        now_utc = datetime.now(timezone.utc)

        _esp32_test_last = {
            'last_seen': now_utc,
            'location': location,
            'uptime_ms': uptime_ms,
            'remote_addr': remote,
            'data': payload,
        }
        logger.info("/api/esp32_test POST from %s loc=%s uptime_ms=%s",
                    remote, location, uptime_ms)
        return jsonify({
            'ok': True,
            'received': {'location': location, 'uptime_ms': uptime_ms},
            'server_time': now_utc.isoformat(),
        })

    # GET — return JSON if requested, otherwise render minimal standalone page
    def _status_json() -> Dict[str, Any]:
        last = _esp32_test_last
        now_utc = datetime.now(timezone.utc)
        last_seen = last.get('last_seen')
        age_s = None
        online = False
        if last_seen is not None:
            try:
                age_s = (now_utc - last_seen).total_seconds()
                online = age_s is not None and age_s <= 5.0
            except Exception:
                age_s = None
                online = False
        return {
            'online': bool(online),
            'age_seconds': age_s,
            'last_seen': last_seen.isoformat() if last_seen else None,
            'location': last.get('location'),
            'uptime_ms': last.get('uptime_ms'),
            'remote_addr': last.get('remote_addr'),
            'data': last.get('data'),
        }

    wants_json = (
        request.args.get('format') == 'json' or
        request.args.get('json') in {'1', 'true', 'yes'} or
        (request.accept_mimetypes['application/json']
         >= request.accept_mimetypes['text/html'])
    )
    if wants_json:
        return jsonify(_status_json())
    return render_template('esp32_test.html')


@api_bp.route('/ac/status')
@login_required
def get_ac_status():
    """Return current AC on/off status from the running thermostat."""
    ac_thermo = getattr(current_app, 'ac_thermostat', None)  # type: ignore
    if ac_thermo is None:
        logger.warning(
            "API /ac/status requested but thermostat not initialized")
        return jsonify({
            "is_on": None,
            "thermostat_enabled": None,
            "thermo_active": None,
            "mode": None,
            "fan_speed": None,
            "sleep_enabled": None,
            "sleep_start": None,
            "sleep_stop": None,
            "sleep_time_active": None,
            "sleep_schedule": None,
        }), 503
    try:
        enabled = getattr(ac_thermo, '_enabled', True)
        try:
            st = ac_thermo.ac.get_status()
            mode = st.get('mode') if isinstance(st, dict) else None
            fan = st.get('fan_speed_enum') if isinstance(st, dict) else None
        except Exception:
            mode = None
            fan = None
        return jsonify({
            "is_on": bool(ac_thermo.is_on),
            "thermostat_enabled": bool(enabled),
            "thermo_active": bool(enabled),
            "mode": mode,
            "fan_speed": fan,
            "sleep_enabled": bool(getattr(ac_thermo.cfg, 'sleep_active', True)),
            "sleep_start": getattr(ac_thermo.cfg, 'sleep_start', None),
            "sleep_stop": getattr(ac_thermo.cfg, 'sleep_stop', None),
            "sleep_time_active": bool(ac_thermo._is_sleep_time_window_now()),
            "sleep_schedule": getattr(ac_thermo.cfg, 'sleep_weekly', None),
            "setpoint_c": float(getattr(ac_thermo.cfg, 'target_temp', 0.0)),
            "pos_hysteresis": float(getattr(ac_thermo.cfg, 'pos_hysteresis', 0.0)),
            "neg_hysteresis": float(getattr(ac_thermo.cfg, 'neg_hysteresis', 0.0)),
            "min_on_s": int(getattr(ac_thermo.cfg, 'min_on_s', 240)),
            "min_off_s": int(getattr(ac_thermo.cfg, 'min_off_s', 240)),
            "poll_interval_s": int(getattr(ac_thermo.cfg, 'poll_interval_s', 15)),
            "smooth_window": int(getattr(ac_thermo.cfg, 'smooth_window', 5)),
            "max_stale_s": getattr(ac_thermo.cfg, 'max_stale_s', None),
            "control_locations": getattr(ac_thermo.cfg, 'control_locations', None),
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


@api_bp.route('/hvac/avg_rates_today')
@login_required
def hvac_avg_rates_today():
    """
    Compute today's average cooling and heating rates from ESP32 readings + AC events.
    - Returns rates in °C/h, and if ROOM_THERMAL_CAPACITY_J_PER_K is set, also W.
    - Location defaults to THERMOSTAT_LOCATION.
    """
    ctrl: Controller = current_app.ctrl  # type: ignore
    finland_tz = pytz.timezone('Europe/Helsinki')
    # Prefer explicit query param, then app config, then env var, then 'default'
    location = request.args.get('location')
    if not location:
        try:
            location = current_app.config.get(
                'THERMOSTAT_LOCATION')  # type: ignore
        except Exception:
            location = None
    if not location:
        location = os.getenv('THERMOSTAT_LOCATION', 'Tietokonepöytä')

    now_local = datetime.now(finland_tz)
    start_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
    date_str = start_local.date().isoformat()

    readings = ctrl.get_esp32_temphum_for_date(date_str, location)
    logger.debug("avg_rates: location=%s date=%s (Helsinki) readings=%d",
                 location, date_str, len(readings))

    # Prepare events with initial state
    start_iso = start_local.isoformat()
    end_iso = now_local.isoformat()
    events = ctrl.get_ac_events_between(start_iso, end_iso)
    init_state = ctrl.get_last_ac_state_before(start_iso)
    logger.debug("avg_rates: window=%s..%s events=%d init_state=%s",
                 start_iso, end_iso, len(events), init_state)
    if init_state is None:
        try:
            conf = ctrl.get_thermostat_conf()
            if conf and conf.current_phase in ('on', 'off'):
                init_state = (conf.current_phase == 'on')
        except Exception:
            init_state = None

    def _parse_iso(s: str):
        try:
            x = s.strip()
            if x.endswith('Z'):
                x = x[:-1]
            dt = datetime.fromisoformat(x)
            if dt.tzinfo is None:
                dt = finland_tz.localize(dt)
            return dt
        except Exception:
            return None

    ev_idx = 0
    cur_state = init_state
    ev_dts = []
    for e in events:
        dt = _parse_iso(e['timestamp'])
        if dt is not None:
            ev_dts.append((dt, bool(e['is_on'])))
    if ev_dts:
        logger.debug("avg_rates: first_events=%s", [
                     ev_dts[i][0].isoformat() for i in range(min(5, len(ev_dts)))])
    else:
        logger.debug("avg_rates: no events inside window")

    points: list[tuple[datetime, float, bool | None]] = []
    skipped_ts = 0
    for r in readings:
        ts = _parse_iso(r.timestamp)
        if ts is None:
            skipped_ts += 1
            continue
        while ev_idx < len(ev_dts) and ev_dts[ev_idx][0] <= ts:
            cur_state = ev_dts[ev_idx][1]
            ev_idx += 1
        try:
            tval = float(r.temperature)
        except Exception:
            continue
        points.append((ts, tval, cur_state))
    if points:
        logger.debug("avg_rates: points=%d first_ts=%s last_ts=%s skipped_ts=%d", len(
            points), points[0][0].isoformat(), points[-1][0].isoformat(), skipped_ts)
    else:
        logger.debug("avg_rates: points=0 skipped_ts=%d", skipped_ts)

    if len(points) < 2:
        return jsonify({
            'location': location,
            'date': date_str,
            'cooling_rate_c_per_h': None,
            'heating_rate_c_per_h': None,
            'cooling_power_w': None,
            'heating_power_w': None,
            'time_on_s': 0,
            'time_off_s': 0,
            'pairs_on': 0,
            'pairs_off': 0,
        })

    points.sort(key=lambda x: x[0])
    MAX_GAP_S = 15 * 60
    sum_dt_on = 0.0
    sum_dT_on = 0.0
    sum_dt_off = 0.0
    sum_dT_off = 0.0
    pairs_on = 0
    pairs_off = 0
    skipped_no_state = 0
    skipped_bad_gap = 0
    skipped_nonpos_dt = 0

    for i in range(1, len(points)):
        t0, T0, s0 = points[i - 1]
        t1, T1, s1 = points[i]
        if s0 is None:
            skipped_no_state += 1
            continue
        dt = (t1 - t0).total_seconds()
        if dt <= 0:
            skipped_nonpos_dt += 1
            continue
        if dt > MAX_GAP_S:
            skipped_bad_gap += 1
            continue
        dT = (T1 - T0)
        if s0 is True:
            sum_dt_on += dt
            sum_dT_on += dT
            pairs_on += 1
        else:
            sum_dt_off += dt
            sum_dT_off += dT
            pairs_off += 1

    cooling_rate_per_s = (sum_dT_on / sum_dt_on) if sum_dt_on > 0 else None
    heating_rate_per_s = (sum_dT_off / sum_dt_off) if sum_dt_off > 0 else None

    cooling_rate_c_per_h = (cooling_rate_per_s *
                            3600.0) if cooling_rate_per_s is not None else None
    heating_rate_c_per_h = (heating_rate_per_s *
                            3600.0) if heating_rate_per_s is not None else None
    logger.debug(
        "avg_rates: sums on(dt=%.1fs,dT=%.3f) off(dt=%.1fs,dT=%.3f) pairs on=%d off=%d skipped(no_state=%d, nonpos_dt=%d, big_gap=%d)",
        sum_dt_on, sum_dT_on, sum_dt_off, sum_dT_off, pairs_on, pairs_off, skipped_no_state, skipped_nonpos_dt, skipped_bad_gap
    )

    cap_env = (current_app.config.get('ROOM_THERMAL_CAPACITY_J_PER_K') or  # type: ignore
               current_app.config.get('room_thermal_capacity_j_per_k') or
               os.getenv('ROOM_THERMAL_CAPACITY_J_PER_K'))
    try:
        Ceq = float(cap_env) if cap_env is not None else None
        if Ceq is not None and (Ceq <= 0 or not (Ceq < float('inf'))):
            Ceq = None
    except Exception:
        Ceq = None

    cooling_power_w = None
    heating_power_w = None
    if Ceq is not None:
        if cooling_rate_per_s is not None:
            cooling_power_w = max(0.0, -cooling_rate_per_s * Ceq)
        if heating_rate_per_s is not None:
            heating_power_w = max(0.0, heating_rate_per_s * Ceq)
    logger.debug(
        "avg_rates: rates C/h cool=%s heat=%s Ceq=%s => power W cool=%s heat=%s",
        cooling_rate_c_per_h, heating_rate_c_per_h, Ceq, cooling_power_w, heating_power_w
    )

    return jsonify({
        'location': location,
        'date': date_str,
        'cooling_rate_c_per_h': cooling_rate_c_per_h,
        'heating_rate_c_per_h': heating_rate_c_per_h,
        'cooling_power_w': cooling_power_w,
        'heating_power_w': heating_power_w,
        'time_on_s': int(sum_dt_on),
        'time_off_s': int(sum_dt_off),
        'pairs_on': pairs_on,
        'pairs_off': pairs_off,
    })

# .##.....##.##....##.##.....##..######..########.########.
# .##.....##.###...##.##.....##.##....##.##.......##.....##
# .##.....##.####..##.##.....##.##.......##.......##.....##
# .##.....##.##.##.##.##.....##..######..######...##.....##
# .##.....##.##..####.##.....##.......##.##.......##.....##
# .##.....##.##...###.##.....##.##....##.##.......##.....##
# ..#######..##....##..#######...######..########.########.


@api_bp.route('/timelapse_config')
@login_required
def get_timelapse_config():
    ctrl: Controller = current_app.ctrl  # type: ignore
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
    ctrl: Controller = current_app.ctrl  # type: ignore
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


@api_bp.route('/temphum')
@login_required
def get_temphum():
    ctrl: Controller = current_app.ctrl  # type: ignore
    finland_tz = pytz.timezone('Europe/Helsinki')
    date_str = request.args.get(
        'date', datetime.now(finland_tz).date().isoformat())
    logger.info(
        "API /temphum for %s by %s",
        date_str, current_user.get_id()
    )
    data = ctrl.get_temphum_for_date(date_str)
    return jsonify([
        {
            'timestamp': d.timestamp,
            'temperature': d.temperature,
            'humidity': d.humidity,
            'ac_on': getattr(d, 'ac_on', None)
        }
        for d in data
    ])
