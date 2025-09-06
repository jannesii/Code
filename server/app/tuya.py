import logging
from collections import deque
from dataclasses import dataclass
import time
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime, timezone
from tuya_iot import TuyaOpenAPI
from .controller import Controller

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class TuyaACController:
    """
    Controller for a Tuya/Smart Life AC using Tuya Cloud OpenAPI.

    Supported DP codes (from your device):
      - switch (bool)                     -> power on/off
      - mode (enum)                       -> 'cold' | 'wet' | 'wind'
      - fan_speed_enum (enum)             -> 'low' | 'high'
      - temp_set (int, 16..31, °C)        -> target temperature
      - temp_current (int, -20..100, °C)  -> reported current temperature (read-only)

    Usage:
        api = TuyaOpenAPI(API_ENDPOINT, ACCESS_ID, ACCESS_KEY)
        api.connect(USERNAME, PASSWORD, COUNTRY_CODE, SCHEMA)

        ac = TuyaACController(api=api, device_id="YOUR_DEVICE_ID")
        ac.turn_on()
        ac.set_mode("cold")
        ac.set_fan_speed("high")
        ac.set_temperature(23)
        print(ac.get_status())
    """

    # Enumerations and ranges from your provided specs
    FAN_SPEEDS = {"low", "high"}
    MODES = {"cold", "wet", "wind"}
    TEMP_MIN = 16
    TEMP_MAX = 31

    def __init__(
        self,
        device_id: str,
        api: Optional[TuyaOpenAPI] = None,
        *,
        access_id: Optional[str] = None,
        access_key: Optional[str] = None,
        api_endpoint: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        country_code: Optional[str] = None,
        schema: Optional[str] = None,
        auto_connect: bool = True,
    ) -> None:
        """
        Initialize the controller.

        You can either pass an existing connected TuyaOpenAPI instance via `api`
        OR supply credentials (access_id/key, endpoint, username/password, country_code, schema)
        and this class will connect for you when auto_connect=True.
        """
        self.device_id = device_id

        if api is not None:
            self.api = api
        else:
            missing = [k for k, v in {
                "access_id": access_id,
                "access_key": access_key,
                "api_endpoint": api_endpoint,
                "username": username,
                "password": password,
                "country_code": country_code,
                "schema": schema,
            }.items() if not v]
            if missing:
                raise ValueError(f"Missing required params for API connection: {', '.join(missing)}")

            self.api = TuyaOpenAPI(api_endpoint, access_id, access_key)
            if auto_connect:
                self.api.connect(username, password, country_code, schema)

    # -------------------------
    # Public control operations
    # -------------------------

    def turn_on(self) -> Dict[str, Any]:
        return self._send_commands([{"code": "switch", "value": True}])

    def turn_off(self) -> Dict[str, Any]:
        return self._send_commands([{"code": "switch", "value": False}])

    def set_mode(self, mode: str) -> Dict[str, Any]:
        mode_l = mode.strip().lower()
        self._validate_mode(mode_l)
        return self._send_commands([{"code": "mode", "value": mode_l}])

    def set_fan_speed(self, speed: str) -> Dict[str, Any]:
        speed_l = speed.strip().lower()
        self._validate_fan_speed(speed_l)
        return self._send_commands([{"code": "fan_speed_enum", "value": speed_l}])

    def set_temperature(self, celsius: int) -> Dict[str, Any]:
        self._validate_temperature(celsius)
        return self._send_commands([{"code": "temp_set", "value": int(celsius)}])

    def set_state(
        self,
        *,
        power: Optional[bool] = None,
        mode: Optional[str] = None,
        fan_speed: Optional[str] = None,
        temperature: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Set multiple attributes in one request. Any argument left as None is ignored.
        """
        commands: List[Dict[str, Any]] = []
        if power is not None:
            commands.append({"code": "switch", "value": bool(power)})
        if mode is not None:
            mode_l = str(mode).strip().lower()
            self._validate_mode(mode_l)
            commands.append({"code": "mode", "value": mode_l})
        if fan_speed is not None:
            speed_l = str(fan_speed).strip().lower()
            self._validate_fan_speed(speed_l)
            commands.append({"code": "fan_speed_enum", "value": speed_l})
        if temperature is not None:
            self._validate_temperature(int(temperature))
            commands.append({"code": "temp_set", "value": int(temperature)})

        if not commands:
            raise ValueError("set_state: provide at least one of power/mode/fan_speed/temperature.")

        return self._send_commands(commands)

    def get_status(self) -> Dict[str, Any]:
        """
        Returns a dict keyed by DP code:
          {
            "switch": True/False,
            "mode": "cold"|"wet"|"wind",
            "fan_speed_enum": "low"|"high",
            "temp_set": int,
            "temp_current": int,
            ... (other codes if present)
          }
        """
        resp = self.api.get(f"/v1.0/iot-03/devices/{self.device_id}/status")
        self._ensure_ok(resp, "get_status")
        result = resp.get("result", [])
        status_map: Dict[str, Any] = {}
        for item in result:
            code = item.get("code")
            value = item.get("value")
            if code:
                status_map[code] = value
        return status_map

    # -------------------------
    # Internals / validation
    # -------------------------

    def _send_commands(self, commands: List[Dict[str, Any]]) -> Dict[str, Any]:
        resp = self.api.post(
            f"/v1.0/iot-03/devices/{self.device_id}/commands",
            {"commands": commands},
        )
        self._ensure_ok(resp, "send_commands")
        return resp

    @staticmethod
    def _ensure_ok(response: Dict[str, Any], action: str) -> None:
        if not isinstance(response, dict) or not response.get("success", False):
            raise RuntimeError(f"Tuya API {action} failed: {response}")

    def _validate_mode(self, mode: str) -> None:
        if mode not in self.MODES:
            raise ValueError(f"Invalid mode '{mode}'. Allowed: {sorted(self.MODES)}")

    def _validate_fan_speed(self, speed: str) -> None:
        if speed not in self.FAN_SPEEDS:
            raise ValueError(f"Invalid fan speed '{speed}'. Allowed: {sorted(self.FAN_SPEEDS)}")

    def _validate_temperature(self, celsius: int) -> None:
        if not (self.TEMP_MIN <= celsius <= self.TEMP_MAX):
            raise ValueError(
                f"Invalid temp_set {celsius}. Range: {self.TEMP_MIN}..{self.TEMP_MAX} °C"
            )

# ----------------------------
# Thermostat configuration
# ----------------------------
@dataclass
class ThermostatConfig:
    setpoint_c: float = 24.5           # target temperature
    deadband_c: float = 1.0            # total hysteresis width (e.g., 1.0°C)
    min_on_s: int = 240                # minimum ON runtime (compressor protection)
    min_off_s: int = 240               # minimum OFF downtime
    poll_interval_s: int = 15          # control loop period
    smooth_window: int = 5             # moving average window; 1 disables smoothing
    max_stale_s: Optional[int] = 120   # if not None, ignore temps older than this
    sleep_enabled: bool = True        # master toggle for sleep mode
    # Sleep window in local time (HH:MM 24h). If both set and enabled, sleep is active.
    sleep_start: Optional[str] = "22:00"
    sleep_stop: Optional[str] = "10:00"

# ----------------------------
# Thermostat loop (no device temp reads)
# ----------------------------
class ACThermostat:
    def __init__(
        self,
        ac: TuyaACController,
        cfg: ThermostatConfig,
        ctrl: Controller,
        location: str,
        notify: Optional[Callable[[str, Dict[str, Any]], None]] = None,
    ):
        self.ac = ac
        self.cfg = cfg
        self.ctrl = ctrl
        self.location = location
        self.notify = notify
        self._temps = deque(maxlen=max(1, cfg.smooth_window))
        ac_status = self.ac.get_status()
        self._is_on: bool = bool(ac_status.get("switch", False)) if ac_status else False
        # Track last-known mode/fan to inform UI
        self._mode: Optional[str] = ac_status.get("mode") if isinstance(ac_status, dict) else None
        self._fan_speed: Optional[str] = ac_status.get("fan_speed_enum") if isinstance(ac_status, dict) else None
        self._enabled: bool = True
        self._last_change_ts: float = 0.0
        logger.info(
            "thermo: init setpoint=%.2f deadband=%.2f min_on=%ss min_off=%ss poll=%ss smooth=%d max_stale=%s location=%s sleep_start=%s sleep_stop=%s",
            cfg.setpoint_c,
            cfg.deadband_c,
            cfg.min_on_s,
            cfg.min_off_s,
            cfg.poll_interval_s,
            cfg.smooth_window,
            str(cfg.max_stale_s),
            self.location,
            cfg.sleep_start,
            cfg.sleep_stop,
        )

    def _now(self) -> float:
        return time.time()

    def _can_turn_on(self) -> bool:
        ok = (self._now() - self._last_change_ts) >= self.cfg.min_off_s
        logger.debug("thermo: _can_turn_on=%s", ok)
        return ok

    def _can_turn_off(self) -> bool:
        ok = (self._now() - self._last_change_ts) >= self.cfg.min_on_s
        logger.debug("thermo: _can_turn_off=%s", ok)
        return ok

    def _parse_hhmm_to_minutes(self, s: Optional[str]) -> Optional[int]:
        if not s:
            return None
        s = s.strip()
        try:
            parts = s.split(":", 1)
            if len(parts) != 2:
                return None
            h = int(parts[0])
            m = int(parts[1])
            if not (0 <= h < 24 and 0 <= m < 60):
                return None
            return h * 60 + m
        except Exception:
            return None

    def _now_minutes_local(self) -> int:
        lt = time.localtime()
        return lt.tm_hour * 60 + lt.tm_min

    def _is_sleep_time(self) -> bool:
        if not getattr(self.cfg, 'sleep_enabled', True):
            return False
        start_m = self._parse_hhmm_to_minutes(self.cfg.sleep_start)
        stop_m = self._parse_hhmm_to_minutes(self.cfg.sleep_stop)
        if start_m is None or stop_m is None:
            return False
        now_m = self._now_minutes_local()
        if start_m == stop_m:
            logger.debug("thermo: sleep window start==stop; ignoring sleep")
            return False
        if start_m < stop_m:
            in_sleep = start_m <= now_m < stop_m
        else:
            # wraps past midnight
            in_sleep = (now_m >= start_m) or (now_m < stop_m)
        logger.debug(
            "thermo: sleep_check now=%02d:%02d start=%s stop=%s -> %s",
            now_m // 60,
            now_m % 60,
            self.cfg.sleep_start,
            self.cfg.sleep_stop,
            in_sleep,
        )
        return in_sleep

    def _read_external_temp(self) -> Optional[float]:
        """Read latest temperature for the configured location from Controller/DB and apply smoothing."""
        rec = self.ctrl.get_last_esp32_temphum_for_location(self.location)
        if rec is None:
            logger.debug("thermo: no DB reading for location=%s", self.location)
            return None
        t = rec.temperature
        ts = rec.timestamp  # ISO string stored by controller
        if t is None:
            logger.debug("thermo: DB reading missing temperature")
            return None
        # Stale check against max_stale_s
        if self.cfg.max_stale_s is not None and ts is not None:
            ts_epoch: Optional[float] = None
            s = str(ts).strip()
            if s:
                try:
                    if s.endswith('Z'):
                        s = s[:-1] + '+00:00'
                    dt = datetime.fromisoformat(s)
                    # If tz missing, treat as UTC to avoid local/UTC mismatch
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    ts_epoch = dt.timestamp()
                except Exception:
                    try:
                        ts_epoch = float(s)
                    except Exception:
                        logger.debug("thermo: could not parse timestamp=%r", ts)
                        ts_epoch = None
            if ts_epoch is not None:
                age = self._now() - ts_epoch
                if age > self.cfg.max_stale_s:
                    logger.warning("thermo: ignoring stale temp age=%.1fs > %ss", age, self.cfg.max_stale_s)
                    return None
            else:
                logger.debug("thermo: skipping stale-check due to unparsable ts=%r", ts)
        self._temps.append(float(t))
        if len(self._temps) == 0:
            return None
        if self.cfg.smooth_window <= 1:
            logger.debug("thermo: raw temp=%.2f (no smoothing)", float(t))
            return float(t)
        smoothed = sum(self._temps) / len(self._temps)
        logger.debug("thermo: smoothed temp=%.2f window=%d", smoothed, len(self._temps))
        return smoothed

    def _thresholds(self):
        half = self.cfg.deadband_c / 2.0
        on_at = self.cfg.setpoint_c + half   # for cooling: turn ON above this
        off_at = self.cfg.setpoint_c - half  # for cooling: turn OFF below this
        return on_at, off_at

    def _emit_status(self) -> None:
        """Notify listeners about current AC on/off state."""
        try:
            if self.notify:
                self.notify('ac_status', {"is_on": bool(self._is_on)})
        except Exception as e:
            logger.debug("thermo: notify failed: %s", e)

    def _emit_thermostat_status(self) -> None:
        try:
            if self.notify:
                self.notify('thermostat_status', {"enabled": bool(self._enabled)})
        except Exception as e:
            logger.debug("thermo: notify thermo failed: %s", e)

    def _emit_sleep_status(self) -> None:
        try:
            if self.notify:
                self.notify('sleep_status', {
                    "sleep_enabled": bool(getattr(self.cfg, 'sleep_enabled', True)),
                    "sleep_start": self.cfg.sleep_start,
                    "sleep_stop": self.cfg.sleep_stop,
                })
        except Exception as e:
            logger.debug("thermo: notify sleep failed: %s", e)

    def _emit_config(self) -> None:
        try:
            if self.notify:
                self.notify('thermo_config', {
                    "setpoint_c": float(self.cfg.setpoint_c),
                    "deadband_c": float(self.cfg.deadband_c),
                })
        except Exception as e:
            logger.debug("thermo: notify config failed: %s", e)

    def _emit_ac_state(self) -> None:
        try:
            if self.notify:
                self.notify('ac_state', {"mode": self._mode, "fan_speed": self._fan_speed})
        except Exception as e:
            logger.debug("thermo: notify ac_state failed: %s", e)

    def set_mode(self, mode: str) -> None:
        """Set AC mode immediately and update thermostat config for future ON events."""
        mode_l = str(mode).strip().lower()
        self.ac.set_mode(mode_l)
        self._mode = mode_l
        self._emit_ac_state()

    def set_fan_speed(self, speed: str) -> None:
        """Set AC fan speed immediately and update thermostat config for future ON events."""
        speed_l = str(speed).strip().lower()
        self.ac.set_fan_speed(speed_l)
        self._fan_speed = speed_l
        self._emit_ac_state()

    def enable(self) -> None:
        self._enabled = True
        self._emit_thermostat_status()

    def disable(self) -> None:
        self._enabled = False
        self._emit_thermostat_status()

    def set_power(self, on: bool) -> None:
        if on:
            self.ac.turn_on()
            self._is_on = True
        else:
            self.ac.turn_off()
            self._is_on = False
        self._last_change_ts = self._now()
        self._emit_status()

    def set_sleep_enabled(self, enabled: bool) -> None:
        self.cfg.sleep_enabled = bool(enabled)
        self._emit_sleep_status()

    def set_sleep_times(self, start: Optional[str], stop: Optional[str]) -> None:
        self.cfg.sleep_start = start
        self.cfg.sleep_stop = stop
        self._emit_sleep_status()

    # Thermostat parameters
    def set_setpoint(self, celsius: float) -> None:
        try:
            self.cfg.setpoint_c = float(celsius)
        except Exception:
            return
        self._emit_config()

    def set_hysteresis(self, deadband_c: float) -> None:
        try:
            db = float(deadband_c)
            if db <= 0:
                return
            self.cfg.deadband_c = db
        except Exception:
            return
        self._emit_config()

    def step(self):
        """One control step using external temperature."""
        # Refresh actual device state at the very beginning and inform listeners if changed
        try:
            status = self.ac.get_status()
            if isinstance(status, dict) and 'switch' in status:
                new_is_on = bool(status.get('switch', False))
                if new_is_on != self._is_on:
                    logger.info("thermo: device state changed externally -> %s", "ON" if new_is_on else "OFF")
                    self._is_on = new_is_on
                    self._emit_status()
            # Also track mode/fan changes
            if isinstance(status, dict):
                changed = False
                m = status.get('mode')
                f = status.get('fan_speed_enum')
                if m is not None and m != self._mode:
                    self._mode = m
                    changed = True
                if f is not None and f != self._fan_speed:
                    self._fan_speed = f
                    changed = True
                if changed:
                    self._emit_ac_state()
        except Exception as e:
            logger.debug("thermo: get_status failed at step start: %s", e)

        # If thermostat is disabled, skip any control actions
        if not self._enabled:
            time.sleep(self.cfg.poll_interval_s)
            return

        # Sleep mode: don't allow turning ON; if currently ON, try to turn OFF respecting min_on
        if self._is_sleep_time():
            if self._is_on:
                if self._can_turn_off():
                    logger.info("thermo: sleep active — turning OFF")
                    self.ac.turn_off()
                    self._is_on = False
                    self._last_change_ts = self._now()
                    self._emit_status()
                else:
                    wait = self.cfg.min_on_s - (self._now() - self._last_change_ts)
                    logger.debug("thermo: sleep active — waiting min-on %.0fs before OFF", max(0, wait))
            else:
                logger.debug("thermo: sleep active — staying OFF")
            logger.debug("thermo: sleeping %ss (sleep mode)", self.cfg.poll_interval_s)
            time.sleep(self.cfg.poll_interval_s)
            return
        temp = self._read_external_temp()
        if temp is None:
            logger.warning("thermo: no valid temp (missing or stale); skipping")
            time.sleep(self.cfg.poll_interval_s)
            return

        on_at, off_at = self._thresholds()
        logger.debug(
            "thermo: setpoint=%.2f deadband=%.2f on_at=%.2f off_at=%.2f",
            self.cfg.setpoint_c,
            self.cfg.deadband_c,
            on_at,
            off_at,
        )
        now = self._now()

        if not self._is_on:
            # OFF -> consider ON
            if temp >= on_at and self._can_turn_on():
                logger.info("thermo: ON trigger: temp=%.2f >= %.2f", temp, on_at)
                # Turn on device and force target device temperature to 16°C (doesn't change setpoint_c)
                self.ac.turn_on()
                try:
                    self.ac.set_temperature(16)
                except Exception as e:
                    logger.debug("thermo: failed to set device temp to 16: %s", e)
                self._is_on = True
                self._last_change_ts = now
                self._emit_status()
                logger.debug("thermo: state changed -> ON; temp_set=16")
            else:
                reasons = []
                if temp < on_at:
                    reasons.append(f"temp {temp:.2f} < on_at {on_at:.2f}")
                wait = self.cfg.min_off_s - (now - self._last_change_ts)
                if wait > 0:
                    reasons.append(f"min-off {wait:.0f}s")
                if reasons:
                    logger.debug("thermo: staying OFF: %s", ", ".join(reasons))
        else:
            # ON -> consider OFF
            if temp <= off_at and self._can_turn_off():
                logger.info("thermo: OFF trigger: temp=%.2f <= %.2f", temp, off_at)
                self.ac.turn_off()
                self._is_on = False
                self._last_change_ts = now
                self._emit_status()
                logger.debug("thermo: state changed -> OFF")
            else:
                reasons = []
                if temp > off_at:
                    reasons.append(f"temp {temp:.2f} > off_at {off_at:.2f}")
                wait = self.cfg.min_on_s - (now - self._last_change_ts)
                if wait > 0:
                    reasons.append(f"min-on {wait:.0f}s")
                if reasons:
                    logger.debug("thermo: staying ON: %s", ", ".join(reasons))

        logger.debug("thermo: sleeping %ss", self.cfg.poll_interval_s)
        time.sleep(self.cfg.poll_interval_s)

    def run_forever(self):
        logger.info("thermo: starting thermostat loop (external temp source)")
        while True:
            try:
                self.step()
            except Exception as e:
                logger.exception("thermo: error during control loop: %s", e)
                time.sleep(self.cfg.poll_interval_s)

    @property
    def is_on(self) -> bool:
        return bool(self._is_on)
