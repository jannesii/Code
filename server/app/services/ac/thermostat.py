import logging
from collections import deque
import time
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime, timedelta
import pytz
from ...core.controller import Controller
from .controller import ACController
from ...core.models import ThermostatConf

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ----------------------------
# Thermostat loop (no device temp reads)
# ----------------------------


class ACThermostat:
    def __init__(
        self,
        ac: ACController,
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
        self._is_on: bool = bool(ac_status.get(
            "switch", False)) if ac_status else False
        # Track last-known mode/fan to inform UI
        self._mode: Optional[str] = ac_status.get(
            "mode") if isinstance(ac_status, dict) else None
        self._fan_speed: Optional[str] = ac_status.get(
            "fan_speed_enum") if isinstance(ac_status, dict) else None
        self._enabled: bool = bool(getattr(cfg, 'thermo_active', True))
        self._is_sleep_time = self._is_sleep_time_window_now()
        # Temporary override to suppress sleep window until given epoch seconds
        self._sleep_override_until: Optional[float] = None
        self._last_change_ts: float = 0.0
        logger.debug(
            f"thermo: init {cfg} is_on={self._is_on} mode={self._mode} fan={self._fan_speed}")
        # Track persisted start ISO for the current phase
        self._phase_started_at_iso: str | None = getattr(
            cfg, 'phase_started_at', None)
        logger.debug(
            f"thermo: init current_phase={getattr(cfg, 'current_phase', None)} phase_started_at={self._phase_started_at_iso}")
        # Ensure current phase timestamp is sane for accurate deltas across restarts
        self.tz = pytz.timezone('Europe/Helsinki')

        def _parse_iso_to_epoch(s: Optional[str]) -> Optional[float]:
            if not s:
                return None
            try:
                x = str(s).strip()
                # Handle 'Z' while avoiding double offsets like '+00:00Z'
                if x.endswith('Z'):
                    x = x[:-1]
                # datetime.fromisoformat can't parse 'Z', but can parse '+00:00'.
                # If no explicit offset remains, assume UTC.
                dt = datetime.fromisoformat(x)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=self.tz)
                return dt.timestamp()
            except Exception as e:
                logger.exception(
                    f"thermo: failed to parse ISO timestamp {s}: {e}")
                return None
        started_epoch = _parse_iso_to_epoch(self._phase_started_at_iso)
        logger.debug(
            f"thermo: parsed phase_started_at={self._phase_started_at_iso} -> {started_epoch}")
        now_epoch = time.time()
        if self._is_on:
            # If persisted phase mismatches or missing ts, reset start to now
            if getattr(cfg, 'current_phase', None) != 'on' or started_epoch is None:
                # Persist UTC in RFC3339 format with trailing 'Z'
                self._phase_started_at_iso = datetime.fromtimestamp(
                    now_epoch, tz=self.tz).isoformat()
                self._persist_conf()
        else:
            if getattr(cfg, 'current_phase', None) != 'off' or started_epoch is None:
                self._phase_started_at_iso = datetime.fromtimestamp(
                    now_epoch, tz=self.tz).isoformat()

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
        ok = (self._now() - self._last_change_ts) >= self.cfg.min_off_s and not self._is_sleep_time_window_now()
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
                sleep_weekly=getattr(self.cfg, 'sleep_weekly', None),
                control_locations=getattr(self.cfg, 'control_locations', None),
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
            s = str(start_iso).strip()
            if s.endswith('Z'):
                s = s[:-1]
            dt = datetime.fromisoformat(s)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=self.tz)
            phase_s = max(0.0, time.time() - dt.timestamp())
            if output_format == "minutes":
                return int(phase_s) // 60 if phase_s >= 60 else None
            return int(phase_s)
        except Exception as e:
            logger.exception(
                "thermo: compute_phase_duration failed for %s: %s", start_iso, e)
            return None

    def _record_transition(self) -> int | None:
        """Record OFF→ON transition, accumulate OFF seconds, persist. Returns OFF minutes."""
        minutes: int | None = self._compute_phase_duration(
            self._phase_started_at_iso)
        # Log AC on/off event into DB for slope segmentation
        try:
            self.ctrl.record_ac_event(is_on=bool(
                self._is_on), source='thermostat')
        except Exception as e:
            logger.debug("thermo: failed to record ac_event: %s", e)

        # set persisted phase start (UTC 'Z')
        self._phase_started_at_iso = datetime.now(self.tz).isoformat()
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
        
    def _parse_epoch_to_hhmm(self, epoch: float) -> str:
        try:
            dt = datetime.fromtimestamp(epoch, tz=self.tz)
            return dt.strftime("%H:%M")
        except Exception:
            return "??:??"

    def _now_minutes_local(self) -> int:
        lt = time.localtime()
        return lt.tm_hour * 60 + lt.tm_min

    def _is_sleep_time_window_now(self) -> bool:
        """Return True if current local time falls within configured sleep window.
        Supports optional weekly schedule; falls back to single start/stop."""
        # Weekly schedule JSON in cfg.sleep_weekly, expected shape:
        # { mon: {start:"HH:MM", stop:"HH:MM"}, tue: {...}, ... }
        if not getattr(self.cfg, 'sleep_active', True):
            return False
        # Honor temporary override: when active, pretend not in sleep window
        try:
            if self._sleep_override_until is not None:
                now = time.time()
                if now < float(self._sleep_override_until):
                    return False
                # Expired -> clear override
                self._sleep_override_until = None
        except Exception:
            self._sleep_override_until = None
        try:
            weekly = getattr(self.cfg, 'sleep_weekly', None)
            if weekly:
                import json
                if isinstance(weekly, str):
                    schedule = json.loads(weekly)
                else:
                    schedule = weekly
                # Map weekday 0=Mon..6=Sun
                wday = time.localtime().tm_wday  # 0=Mon
                keys = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
                key = keys[wday] if 0 <= wday < len(keys) else None
                if key and isinstance(schedule, dict) and key in schedule:
                    day = schedule.get(key) or {}
                    start = (day.get('start') or '').strip() or None
                    stop = (day.get('stop') or '').strip() or None
                    # Reuse single-day logic
                    start_m = self._parse_hhmm_to_minutes(start)
                    stop_m = self._parse_hhmm_to_minutes(stop)
                    if start_m is None or stop_m is None:
                        return False
                    now_m = self._now_minutes_local()
                    if start_m == stop_m:
                        return False
                    if start_m < stop_m:
                        return start_m <= now_m < stop_m
                    active = (now_m >= start_m) or (now_m < stop_m)
                    return active
        except Exception as e:
            logger.exception("thermo: failed weekly sleep parse: %s", e)
        # Fallback: single start/stop
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
        """Read latest temperature from selected control locations and apply smoothing.
        If multiple locations are selected, use their average.
        """
        # Selected control locations from config (JSON string), fallback to single thermostat location
        locs: list[str] = []
        try:
            import json
            sel = getattr(self.cfg, 'control_locations', None)
            if sel:
                if isinstance(sel, str):
                    locs = [str(x)
                            for x in json.loads(sel) if isinstance(x, str)]
                elif isinstance(sel, (list, tuple)):
                    locs = [str(x) for x in sel if isinstance(x, str)]
        except Exception:
            locs = []
        if not locs:
            locs = [self.location]

        temps: list[float] = []
        used_locs: list[str] = []
        latest_ts: Optional[str] = None
        max_stale = self.cfg.max_stale_s

        def _parse_iso_to_epoch(ts: Optional[str]) -> Optional[float]:
            if not ts:
                return None
            s = str(ts).strip()
            try:
                if s.endswith('Z'):
                    s = s[:-1]
                dt = datetime.fromisoformat(s)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=self.tz)
                return dt.timestamp()
            except Exception:
                try:
                    return float(s)
                except Exception:
                    return None

        for loc in locs:
            rec = self.ctrl.get_last_esp32_temphum_for_location(loc)
            if rec is None or rec.temperature is None:
                continue
            ts_epoch = _parse_iso_to_epoch(getattr(rec, 'timestamp', None))
            if max_stale is not None and ts_epoch is not None:
                age = self._now() - ts_epoch
                if age > max_stale:
                    logger.debug(
                        "thermo: skipping stale reading for %s age=%.1fs > %ss", loc, age, max_stale)
                    continue
            try:
                temps.append(float(rec.temperature))
                used_locs.append(loc)
                if latest_ts is None:
                    latest_ts = getattr(rec, 'timestamp', None)
            except Exception:
                continue

        if not temps:
            logger.debug(
                "thermo: no fresh DB readings for control locations=%s", locs)
            return None

        t = sum(temps) / len(temps)
        ts = latest_ts  # ISO string (first of included)
        logger.debug(
            "thermo: read temps %s -> avg=%.2f from used_locs=%s (sample ts=%s)", temps, t, used_locs, ts)
        self._temps.append(float(t))
        if len(self._temps) == 0:
            return None
        if self.cfg.smooth_window <= 1:
            logger.debug("thermo: raw temp=%.2f (no smoothing)", float(t))
            return float(t)
        smoothed = sum(self._temps) / len(self._temps)
        logger.debug("thermo: smoothed temp=%.2f window=%d",
                     smoothed, len(self._temps))
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
                self.notify('thermostat_status', {"enabled": bool(
                    self._enabled), "thermo_active": bool(self._enabled)})
        except Exception as e:
            logger.debug("thermo: notify thermo failed: %s", e)

    def _emit_sleep_status(self) -> None:
        try:
            if self.notify:
                payload: Dict[str, Any] = {
                    "sleep_enabled": bool(getattr(self.cfg, 'sleep_active', True)),
                    "sleep_start": getattr(self.cfg, 'sleep_start', None),
                    "sleep_stop": getattr(self.cfg, 'sleep_stop', None),
                    "sleep_time_active": bool(self._is_sleep_time_window_now()),
                }
                # Attach weekly schedule (as dict) if present
                weekly = getattr(self.cfg, 'sleep_weekly', None)
                if weekly:
                    try:
                        import json
                        payload["sleep_schedule"] = json.loads(
                            weekly) if isinstance(weekly, str) else weekly
                    except Exception:
                        payload["sleep_schedule"] = None
                # Attach temporary override info if active
                if self._sleep_override_until is not None:
                    payload["sleep_override_until"] = self._parse_epoch_to_hhmm(
                        float(self._sleep_override_until))
                        
                self.notify('sleep_status', payload)
        except Exception as e:
            logger.debug("thermo: notify sleep failed: %s", e)

    def _emit_config(self) -> None:
        try:
            if self.notify:
                payload: Dict[str, Any] = {
                    "setpoint_c": float(self.cfg.target_temp),
                    "pos_hysteresis": float(self.cfg.pos_hysteresis),
                    "neg_hysteresis": float(self.cfg.neg_hysteresis),
                    "min_on_s": int(self.cfg.min_on_s),
                    "min_off_s": int(self.cfg.min_off_s),
                    "poll_interval_s": int(self.cfg.poll_interval_s),
                    "smooth_window": int(self.cfg.smooth_window),
                    "max_stale_s": None if self.cfg.max_stale_s is None else int(self.cfg.max_stale_s),
                }
                try:
                    payload["control_locations"] = getattr(
                        self.cfg, 'control_locations', None)
                except Exception:
                    pass
                self.notify('thermo_config', payload)
        except Exception as e:
            logger.debug("thermo: notify config failed: %s", e)

    def set_control_locations(self, locs: List[str]) -> None:
        try:
            import json
            # sanitize and ensure at least one
            names = [str(x).strip() for x in (locs or []) if str(x).strip()]
            if not names:
                # keep existing or fallback to default location
                names = []
            # Always ensure at least one by falling back to current default
            if not names:
                names = [self.location]
            self.cfg.control_locations = json.dumps(names)
        except Exception as e:
            logger.debug("thermo: set_control_locations failed: %s", e)
            return
        self._persist_conf()
        self._emit_config()

    def _emit_ac_state(self) -> None:
        try:
            if self.notify:
                self.notify(
                    'ac_state', {"mode": self._mode, "fan_speed": self._fan_speed})
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
        self._last_change_ts = self._now
        self._emit_status()

    def set_sleep_enabled(self, enabled: bool) -> None:
        self.cfg.sleep_active = bool(enabled)
        self._persist_conf()
        self._emit_sleep_status()
        self.step_sleep_check()

    def set_sleep_times(self, start: Optional[str], stop: Optional[str]) -> None:
        self.cfg.sleep_start = start
        self.cfg.sleep_stop = stop
        self._persist_conf()
        self._emit_sleep_status()
        self.step_sleep_check()

    def set_sleep_schedule(self, schedule: Dict[str, Dict[str, Optional[str]]]) -> None:
        """Set weekly sleep schedule from dict mapping days to {start, stop}."""
        try:
            import json
            # Normalize keys to mon..sun and HH:MM
            keys = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
            norm: Dict[str, Dict[str, Optional[str]]] = {}
            for k in keys:
                d = schedule.get(k) if isinstance(schedule, dict) else None
                if isinstance(d, dict):
                    s = d.get('start')
                    e = d.get('stop')
                    norm[k] = {
                        'start': s if isinstance(s, str) and ':' in s else None,
                        'stop': e if isinstance(e, str) and ':' in e else None,
                    }
            self.cfg.sleep_weekly = json.dumps(norm)
        except Exception as e:
            logger.debug("thermo: set_sleep_schedule failed: %s", e)
            return
        self._persist_conf()
        self._emit_sleep_status()
        self.step_sleep_check()

    def disable_sleep_for(self, minutes: int) -> None:
        """Temporarily disable sleep enforcement for the given minutes.
        Does not change persistent sleep configuration.
        """
        try:
            m = int(minutes)
        except Exception:
            return
        if m <= 0:
            return
        self._sleep_override_until = time.time() + (m * 60)
        logger.info("thermo: sleep override enabled for %d minutes (until %s)", m, (datetime.now() + timedelta(minutes=m)).strftime("%H:%M"))
        # Re-evaluate sleep state and inform listeners
        self._emit_sleep_status()
        self.step_sleep_check()

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

    # --- Runtime config setters ---
    def set_min_on_s(self, seconds: int) -> None:
        try:
            v = int(seconds)
            if v < 0:
                return
            self.cfg.min_on_s = v
        except Exception:
            return
        self._persist_conf()
        self._emit_config()

    def set_min_off_s(self, seconds: int) -> None:
        try:
            v = int(seconds)
            if v < 0:
                return
            self.cfg.min_off_s = v
        except Exception:
            return
        self._persist_conf()
        self._emit_config()

    def set_poll_interval_s(self, seconds: int) -> None:
        try:
            v = int(seconds)
            if v <= 0:
                return
            self.cfg.poll_interval_s = v
        except Exception:
            return
        self._persist_conf()
        self._emit_config()

    def set_smooth_window(self, n: int) -> None:
        try:
            v = int(n)
            if v < 1:
                v = 1
            self.cfg.smooth_window = v
            # Recreate smoothing buffer with new window size
            from collections import deque as _dq
            self._temps = _dq(self._temps, maxlen=max(1, v))
        except Exception:
            return
        self._persist_conf()
        self._emit_config()

    def set_max_stale_s(self, seconds: Optional[int]) -> bool:
        try:
            if seconds is None:
                self.cfg.max_stale_s = None
            else:
                v = int(seconds)
                self.cfg.max_stale_s = None if v < 0 else v
        except Exception:
            return
        self._persist_conf()
        self._emit_config()

    def step_sleep_check(self) -> None:
        logger.debug("thermo: step_sleep_check: sleep_active=%s is_sleep_time=%s is_on=%s",
                     getattr(self.cfg, 'sleep_active', True), self._is_sleep_time_window_now(), self._is_on)

        new_sleep = self._is_sleep_time_window_now()
        if new_sleep != self._is_sleep_time:
            s = "ENTERING" if new_sleep else "EXITING"
            logger.info(f"thermo: {s} sleep time window")
            self._is_sleep_time = new_sleep
            self._emit_sleep_status()

        if new_sleep:
            if self._is_on:
                if self._can_turn_off():
                    logger.info("thermo: sleep active — turning OFF")
                    self.turn_off()
                    self._last_change_ts = self._now()
                    self._emit_status()
                else:
                    wait = self.cfg.min_on_s - \
                        (self._now() - self._last_change_ts)
                    logger.debug(
                        "thermo: sleep active — waiting min-on %.0fs before OFF", max(0, wait))
            else:
                logger.debug("thermo: sleep active — staying OFF")
            logger.debug("thermo: sleeping %ss (sleep mode)",
                         self.cfg.poll_interval_s)
            time.sleep(self.cfg.poll_interval_s)
            return False
        return True

    def step_on_off_check(self) -> None:
        temp = self._read_external_temp()
        if temp is None:
            logger.warning(
                "thermo: no valid temp (missing or stale); skipping")
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
                logger.info(
                    f"thermo: ON trigger: temp={temp:.2f} <= {off_at:.2f}; turned on after {time_delta} min")
                if time_delta:
                    self.ctrl.log_message(
                        (f"AC ON, delta={time_delta} min, on_at={on_at}, off_at={off_at}"), log_type="ac")
                try:
                    self.ac.set_temperature(16)
                except Exception as e:
                    logger.debug(
                        "thermo: failed to set device temp to 16: %s", e)
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
                logger.info(
                    f"thermo: OFF trigger: temp={temp:.2f} <= {off_at:.2f}; turned off after {time_delta} min")
                if time_delta:
                    self.ctrl.log_message(
                        (f"AC OFF, delta={time_delta} min, on_at={on_at}, off_at={off_at}"), log_type="ac")

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

    def step(self):
        """One control step using external temperature."""
        # Refresh actual device state at the very beginning and inform listeners if changed
        try:
            status = self.ac.get_status()
            if isinstance(status, dict) and 'switch' in status:
                new_is_on = bool(status.get('switch', False))
                if new_is_on != self._is_on:
                    logger.info(
                        "thermo: device state changed externally -> %s", "ON" if new_is_on else "OFF")
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
        resume = self.step_sleep_check()
        self.step_on_off_check() if resume else None

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
