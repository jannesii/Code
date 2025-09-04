# models.py

from dataclasses import dataclass
from datetime import datetime
import pytz

# --- Data classes for domain models ---


@dataclass
class User:
    id: int
    username: str
    password_hash: str
    is_admin: bool = False
    is_temporary: bool = False
    expires_at: str | None = None

    @property
    def is_expired(self) -> bool:
        """
        Return True if this is a temporary user and the
        expiry timestamp is in the past (UTC‑aware).
        """
        finland_tz = pytz.timezone('Europe/Helsinki')
        if not self.is_temporary or self.expires_at is None:
            return False
        expires_at_dt = self.expires_at
        if isinstance(expires_at_dt, str):
            try:
                expires_at_dt = datetime.fromisoformat(expires_at_dt)
                if expires_at_dt.tzinfo is None:
                    expires_at_dt = finland_tz.localize(expires_at_dt)
            except Exception:
                return False
        return expires_at_dt <= datetime.now(finland_tz)


@dataclass
class TemperatureHumidity:
    id: int
    timestamp: str
    temperature: float
    humidity: float

@dataclass
class ESP32TemperatureHumidity:
    id: int
    location: str
    timestamp: str
    temperature: float
    humidity: float

@dataclass
class Status:
    id: int
    timestamp: str
    status: str


@dataclass
class ImageData:
    id: int
    timestamp: str
    image: str  # base64-encoded image data


@dataclass
class TimelapseConf:
    id: int
    image_delay: int
    temphum_delay: int
    status_delay: int
