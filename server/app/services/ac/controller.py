import logging
from typing import Any, Dict, List, Optional
from tuya_iot import TuyaOpenAPI

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class ACController:
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
