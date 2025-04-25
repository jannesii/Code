# controller.py
from typing import Optional, List
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import logging

from models import User, TemperatureHumidity, Status, ImageData, TimelapseConf
from .database import DatabaseManager
import pytz

logger = logging.getLogger(__name__)

class Controller:
    def __init__(self, db_path: str = 'app.db'):
        self.db = DatabaseManager(db_path)
        self.finland_tz = pytz.timezone('Europe/Helsinki')

    # --- User operations ---
    def register_user(self, username: str, password: str = None, password_hash: str = None) -> User:
        """
        Creates the user if it doesn't exist, or returns the existing one.
        Uses INSERT OR IGNORE to avoid UNIQUE errors, then SELECT to fetch.
        """
        logging.info(f"Registering user: {username}")

        # 1) Hash the password up front
        if password_hash is None:
            pw_hash = generate_password_hash(password)
        elif password is None and password_hash is None:
            raise ValueError("Either password or password_hash must be provided")
        else:
            pw_hash = password_hash

        # 2) Try to insert; if username exists, this is a no-op
        cursor = self.db.execute_query(
            "INSERT OR IGNORE INTO users (username, password_hash) VALUES (?, ?)",
            (username, pw_hash)
        )
        if cursor.rowcount == 1:
            logging.info(f"User '{username}' created successfully.")
        else:
            logging.info(f"User '{username}' already exists, skipping INSERT.")

        # 3) Fetch whatever is now in the table
        row = self.db.fetchone(
            "SELECT id, username, password_hash FROM users WHERE username = ?",
            (username,)
        )
        if row is None:
            # This really should never happen
            logging.error(f"After INSERT OR IGNORE, no row for '{username}' found.")
            raise RuntimeError(f"Failed to retrieve user '{username}'")

        logging.info(f"Returning user '{username}' with id={row['id']}")
        return User(
            id=row['id'],
            username=row['username'],
            password_hash=row['password_hash']
        )


    def authenticate_user(self, username: str, password: str) -> bool:
        row = self.db.fetchone(
            "SELECT password_hash FROM users WHERE username = ?", (username,)
        )
        if row is None:
            return False
        return check_password_hash(row['password_hash'], password)

    def get_all_users(self) -> list[User]:
        """Palauttaa listan kaikista käyttäjistä."""
        rows = self.db.fetchall(
            "SELECT id, username, password_hash FROM users",
            ()
        )
        return [
            User(id=row['id'], username=row['username'],
                 password_hash=row['password_hash'])
            for row in rows
        ]
        
    def get_user_by_username(self, username: str) -> User | None:
        row = self.db.fetchone(
            "SELECT id, username, password_hash FROM users WHERE username = ?",
            (username,)
        )
        if not row:
            return None
        return User(
            id=row['id'],
            username=row['username'],
            password_hash=row['password_hash']
        )

    def delete_user(self, username: str) -> None:
        """Poistaa käyttäjän annetulla käyttäjätunnuksella."""
        self.db.execute_query(
            "DELETE FROM users WHERE username = ?",
            (username,)
        )

    # --- Sensor data operations ---
    def record_temphum(self, temperature: float, humidity: float) -> TemperatureHumidity:
        now = datetime.now(self.finland_tz).isoformat()
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

    def get_temphum_for_date(self, date_str: str) -> List[TemperatureHumidity]:
        """
        Returns all TemperatureHumidity rows whose timestamp falls on `date_str`
        (ISO date, e.g. '2025-04-20'), ordered by timestamp.
        """
        rows = self.db.fetchall(
            """
            SELECT id, timestamp, temperature, humidity
              FROM temphum
             WHERE date(timestamp) = ?
             ORDER BY timestamp
            """,
            (date_str,)
        )
        return [
            TemperatureHumidity(
                id=row['id'],
                timestamp=row['timestamp'],
                temperature=row['temperature'],
                humidity=row['humidity']
            )
            for row in rows
        ]

    def update_status(self, status: str) -> Status:
        now = datetime.now(self.finland_tz).isoformat()
        self.db.execute_query(
            "UPDATE status SET timestamp = ?, status = ?",
            (now, status)
        )
        row = self.db.fetchone(
            "SELECT id, timestamp, status FROM status"
        )
        if row is None:
            raise RuntimeError("Failed to retrieve inserted status record")
        return Status(id=row['id'], timestamp=row['timestamp'], status=row['status'])

    def get_last_status(self) -> Optional[Status]:
        row = self.db.fetchone(
            "SELECT id, timestamp, status FROM status"
        )
        if row is None:
            return None
        return Status(id=row['id'], timestamp=row['timestamp'], status=row['status'])

    def record_image(self, image_base64: str) -> ImageData:
        now = datetime.now(self.finland_tz).isoformat()
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

    def get_timelapse_conf(self) -> Optional[TimelapseConf]:
        row = self.db.fetchone(
            "SELECT id, image_delay, temphum_delay, status_delay FROM timelapse_conf"
        )
        if row is None:
            return None
        return TimelapseConf(
            id=row['id'],
            image_delay=row['image_delay'],
            temphum_delay=row['temphum_delay'],
            status_delay=row['status_delay']
        )
        
    def update_timelapse_conf(self, image_delay: int, temphum_delay: int, status_delay: int) -> None:
        self.db.execute_query(
            """
            UPDATE timelapse_conf
               SET image_delay = ?,
                   temphum_delay = ?,
                   status_delay = ?
            """,
            (image_delay, temphum_delay, status_delay)
        )