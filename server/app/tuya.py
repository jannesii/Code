import logging
from collections import deque
import time
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime, timezone
from tuya_iot import TuyaOpenAPI
from .controller import Controller
from models import ThermostatConf

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
# Thermostat loop (no device temp reads)
# ----------------------------
class ACThermostat:
    def __init__(
        self,
        ac: TuyaACController,
        cfg: ThermostatConf,
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
        self._enabled: bool = bool(getattr(cfg, 'thermo_active', True))
        self._last_change_ts: float = 0.0
        """ logger.info(
            "thermo: init setpoint=%.2f deadband=%.2f min_on=%ss min_off=%ss poll=%ss smooth=%d max_stale=%s location=%s sleep_start=%s sleep_stop=%s",
            cfg.target_temp,
            cfg.pos_hysteresis + cfg.neg_hysteresis,
            cfg.min_on_s,
            cfg.min_off_s,
            cfg.poll_interval_s,
            cfg.smooth_window,
            str(cfg.max_stale_s),
            self.location,
            cfg.sleep_start,
            cfg.sleep_stop,
        ) """
        # Track persisted start ISO for the current phase
        self._phase_started_at_iso: str | None = getattr(cfg, 'phase_started_at', None)
        logger.debug(f"thermo: init current_phase={getattr(cfg, 'current_phase', None)} phase_started_at={self._phase_started_at_iso}")
        # Ensure current phase timestamp is sane for accurate deltas across restarts
        def _parse_iso_to_epoch(s: Optional[str]) -> Optional[float]:
            if not s:
                return None
            try:
                x = str(s)
                if x.endswith('Z'):
                    x = x[:-1] + '+00:00'
                dt = datetime.fromisoformat(x)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt.timestamp()
            except Exception as e:
                logger.exception(f"thermo: failed to parse ISO timestamp {s}: {e}")
                return None
        started_epoch = _parse_iso_to_epoch(self._phase_started_at_iso)
        logger.debug(f"thermo: parsed phase_started_at={self._phase_started_at_iso} -> {started_epoch}")
        now_epoch = time.time()
        if self._is_on:
            # If persisted phase mismatches or missing ts, reset start to now
            if getattr(cfg, 'current_phase', None) != 'on' or started_epoch is None:
                self._phase_started_at_iso = datetime.fromtimestamp(now_epoch, tz=timezone.utc).isoformat() + 'Z'
                self._persist_conf()
        else:
            if getattr(cfg, 'current_phase', None) != 'off' or started_epoch is None:
                self._phase_started_at_iso = datetime.fromtimestamp(now_epoch, tz=timezone.utc).isoformat() + 'Z'
                
                self._persist_conf()
        
        # Initialize last-change timestamp from the current phase start
        # so min_on/min_off are respected across restarts.
        started_epoch = _parse_iso_to_epoch(self._phase_started_at_iso)
        if started_epoch is not None:
            self._last_change_ts = min(now_epoch, float(started_epoch))
        else:
            self._last_change_ts = now_epoch

        # Log the computed phase age for visibility across restarts
        phase_lbl = 'ON' if self._is_on else 'OFF'
        age_min = self._compute_phase_duration(self._phase_started_at_iso) or 0
        logger.info(
            "thermo: current phase=%s age=%d min since %s",
            phase_lbl,
            age_min,
            self._phase_started_at_iso,
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
    
    def _persist_conf(self) -> None:
        """Persist current thermostat config to DB."""
        try:
            self.ctrl.save_thermostat_conf(
                sleep_active=self.cfg.sleep_active,
                sleep_start=self.cfg.sleep_start,
                sleep_stop=self.cfg.sleep_stop,
                target_temp=self.cfg.target_temp,
                pos_hysteresis=self.cfg.pos_hysteresis,
                neg_hysteresis=self.cfg.neg_hysteresis,
                thermo_active=self._enabled,
                min_on_s=int(self.cfg.min_on_s),
                min_off_s=int(self.cfg.min_off_s),
                poll_interval_s=int(self.cfg.poll_interval_s),
                smooth_window=int(self.cfg.smooth_window),
                max_stale_s=self.cfg.max_stale_s,
                current_phase=('on' if self._is_on else 'off'),
                phase_started_at=self._phase_started_at_iso,
            )
        except Exception as e:
            logger.debug("thermo: persist conf failed: %s", e)

    def _compute_phase_duration(self, start_iso: Optional[str], output_format: str = "minutes") -> Optional[int]:
        """Compute phase duration in minutes from ISO timestamp."""
        if not start_iso:
            return None
        try:
            s = start_iso
            x = s[:-1] + '+00:00' if s.endswith('Z') else s
            dt = datetime.fromisoformat(x)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            phase_s = max(0.0, time.time() - dt.timestamp())
            if output_format == "minutes":
                return int(phase_s) // 60 if phase_s >= 60 else None
            return int(phase_s)
        except Exception as e:
            logger.exception("thermo: compute_phase_duration failed for %s: %s", start_iso, e)
            return None

    def _record_transition(self) -> int | None:
        """Record OFF→ON transition, accumulate OFF seconds, persist. Returns OFF minutes."""
        minutes: int | None = self._compute_phase_duration(self._phase_started_at_iso)
        
        # set persisted phase start
        self._phase_started_at_iso = datetime.now(timezone.utc).isoformat() + 'Z'
        self._persist_conf()
        return minutes

    def _record_external_state(self, new_on: bool) -> None:
        """Update counters on external device state changes without issuing commands."""
        if new_on == self._is_on:
            return


        self._is_on = new_on
        self._record_transition()
        self._last_change_ts = self._now()
        self._emit_status()

    def turn_on(self) -> int | None:
        self.ac.turn_on()
        self._is_on = True
        minutes = self._record_transition()
        return minutes

    def turn_off(self) -> int | None:
        self.ac.turn_off()
        self._is_on = False
        minutes = self._record_transition()
        return minutes

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
        if not getattr(self.cfg, 'sleep_active', True):
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
        on_at = self.cfg.target_temp + float(self.cfg.pos_hysteresis)
        off_at = self.cfg.target_temp - float(self.cfg.neg_hysteresis)
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
                self.notify('thermostat_status', {"enabled": bool(self._enabled), "thermo_active": bool(self._enabled)})
        except Exception as e:
            logger.debug("thermo: notify thermo failed: %s", e)

    def _emit_sleep_status(self) -> None:
        try:
            if self.notify:
                self.notify('sleep_status', {
                    "sleep_enabled": bool(getattr(self.cfg, 'sleep_active', True)),
                    "sleep_start": self.cfg.sleep_start,
                    "sleep_stop": self.cfg.sleep_stop,
                })
        except Exception as e:
            logger.debug("thermo: notify sleep failed: %s", e)

    def _emit_config(self) -> None:
        try:
            if self.notify:
                self.notify('thermo_config', {
                    "setpoint_c": float(self.cfg.target_temp),
                    "pos_hysteresis": float(self.cfg.pos_hysteresis),
                    "neg_hysteresis": float(self.cfg.neg_hysteresis),
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
        self.cfg.thermo_active = True
        self._persist_conf()
        self._emit_thermostat_status()

    def disable(self) -> None:
        self._enabled = False
        self.cfg.thermo_active = False
        self._persist_conf()
        self._emit_thermostat_status()

    def set_power(self, on: bool) -> None:
        if on:
            self.turn_on()
            self._is_on = True
        else:
            self.turn_off()
            self._is_on = False
        self._last_change_ts = self._now()
        self._emit_status()

    def set_sleep_enabled(self, enabled: bool) -> None:
        self.cfg.sleep_active = bool(enabled)
        self._persist_conf()
        self._emit_sleep_status()

    def set_sleep_times(self, start: Optional[str], stop: Optional[str]) -> None:
        self.cfg.sleep_start = start
        self.cfg.sleep_stop = stop
        self._persist_conf()
        self._emit_sleep_status()

    # Thermostat parameters
    def set_setpoint(self, celsius: float) -> None:
        try:
            self.cfg.target_temp = float(celsius)
        except Exception:
            return
        self._persist_conf()
        self._emit_config()

    def set_hysteresis_split(self, pos_h: float, neg_h: float) -> None:
        try:
            p = float(pos_h)
            n = float(neg_h)
            if p < 0 or n < 0:
                return
            self.cfg.pos_hysteresis = p
            self.cfg.neg_hysteresis = n
        except Exception:
            return
        self._persist_conf()
        self._emit_config()

    # Backward-compatible single-value setter
    def set_hysteresis(self, deadband: float) -> None:
        try:
            d = float(deadband)
            if d < 0:
                return
        except Exception:
            return
        split = d / 2.0
        self.set_hysteresis_split(split, split)

    def step(self):
        """One control step using external temperature."""
        # Refresh actual device state at the very beginning and inform listeners if changed
        try:
            status = self.ac.get_status()
            if isinstance(status, dict) and 'switch' in status:
                new_is_on = bool(status.get('switch', False))
                if new_is_on != self._is_on:
                    logger.info("thermo: device state changed externally -> %s", "ON" if new_is_on else "OFF")
                    self._record_external_state(new_is_on)
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
                    self.turn_off()
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
            self.cfg.target_temp,
            self.cfg.pos_hysteresis + self.cfg.neg_hysteresis,
            on_at,
            off_at,
        )
        now = self._now()

        if not self._is_on:
            # OFF -> consider ON
            if temp >= on_at and self._can_turn_on():
                # Turn on device and force target device temperature to 16°C (doesn't change target_temp)
                time_delta = self.turn_on()
                logger.info(f"thermo: ON trigger: temp={temp:.2f} <= {off_at:.2f}; turned on after {time_delta}")
                if time_delta:
                    self.ctrl.log_message((f"AC ON, delta={time_delta} min, on_at={on_at}, off_at={off_at}"), log_type="ac")
                try:
                    self.ac.set_temperature(16)
                except Exception as e:
                    logger.debug("thermo: failed to set device temp to 16: %s", e)
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
                time_delta = self.turn_off()
                logger.info(f"thermo: OFF trigger: temp={temp:.2f} <= {off_at:.2f}; turned off after {time_delta}")
                if time_delta:
                    self.ctrl.log_message((f"AC OFF, delta={time_delta} min, on_at={on_at}, off_at={off_at}"), log_type="ac")

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
