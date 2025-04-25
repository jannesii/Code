# models.py

from dataclasses import dataclass

# --- Data classes for domain models ---
@dataclass
class User:
    id: int
    username: str
    password_hash: str
    is_admin: bool = False

@dataclass
class TemperatureHumidity:
    id: int
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