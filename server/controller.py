# controller.py
from typing import Optional
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from models import User, TemperatureHumidity, Status, ImageData
from database import DatabaseManager

class Controller:
    def __init__(self, db_path: str = 'app.db'):
        self.db = DatabaseManager(db_path)

    # --- User operations ---
    def register_user(self, username: str, password: str) -> User:
        # Check if user exists
        existing = self.db.fetchone(
            "SELECT id, username, password_hash FROM users WHERE username = ?", (username,)
        )
        if existing is not None:
            raise ValueError("Username already exists")

        pw_hash = generate_password_hash(password)
        self.db.execute_query(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, pw_hash)
        )
        # Retrieve inserted user
        row = self.db.fetchone(
            "SELECT id, username, password_hash FROM users WHERE username = ?", (username,)
        )
        if row is None:
            raise RuntimeError("Failed to retrieve newly created user")

        return User(id=row['id'], username=row['username'], password_hash=row['password_hash'])

    def authenticate_user(self, username: str, password: str) -> bool:
        row = self.db.fetchone(
            "SELECT password_hash FROM users WHERE username = ?", (username,)
        )
        if row is None:
            return False
        return check_password_hash(row['password_hash'], password)

    # --- Sensor data operations ---
    def record_temphum(self, temperature: float, humidity: float) -> TemperatureHumidity:
        now = datetime.utcnow().isoformat()
        self.db.execute_query(
            "INSERT INTO temphum (timestamp, temperature, humidity) VALUES (?, ?, ?)",
            (now, temperature, humidity)
        )
        row = self.db.fetchone(
            "SELECT id, timestamp, temperature, humidity FROM temphum ORDER BY id DESC LIMIT 1"
        )
        if row is None:
            raise RuntimeError("Failed to retrieve inserted temphum record")
        return TemperatureHumidity(
            id=row['id'], timestamp=row['timestamp'],
            temperature=row['temperature'], humidity=row['humidity']
        )

    def get_last_temphum(self) -> Optional[TemperatureHumidity]:
        row = self.db.fetchone(
            "SELECT id, timestamp, temperature, humidity FROM temphum ORDER BY id DESC LIMIT 1"
        )
        if row is None:
            return None
        return TemperatureHumidity(
            id=row['id'], timestamp=row['timestamp'],
            temperature=row['temperature'], humidity=row['humidity']
        )

    def record_status(self, status: str) -> Status:
        now = datetime.utcnow().isoformat()
        self.db.execute_query(
            "INSERT INTO status (timestamp, status) VALUES (?, ?)",
            (now, status)
        )
        row = self.db.fetchone(
            "SELECT id, timestamp, status FROM status ORDER BY id DESC LIMIT 1"
        )
        if row is None:
            raise RuntimeError("Failed to retrieve inserted status record")
        return Status(id=row['id'], timestamp=row['timestamp'], status=row['status'])

    def get_last_status(self) -> Optional[Status]:
        row = self.db.fetchone(
            "SELECT id, timestamp, status FROM status ORDER BY id DESC LIMIT 1"
        )
        if row is None:
            return None
        return Status(id=row['id'], timestamp=row['timestamp'], status=row['status'])

    def record_image(self, image_base64: str) -> ImageData:
        now = datetime.utcnow().isoformat()
        self.db.execute_query(
            "INSERT INTO images (timestamp, image) VALUES (?, ?)",
            (now, image_base64)
        )
        row = self.db.fetchone(
            "SELECT id, timestamp, image FROM images ORDER BY id DESC LIMIT 1"
        )
        if row is None:
            raise RuntimeError("Failed to retrieve inserted image record")
        return ImageData(id=row['id'], timestamp=row['timestamp'], image=row['image'])

    def get_last_image(self) -> Optional[ImageData]:
        row = self.db.fetchone(
            "SELECT id, timestamp, image FROM images ORDER BY id DESC LIMIT 1"
        )
        if row is None:
            return None
        return ImageData(id=row['id'], timestamp=row['timestamp'], image=row['image'])
