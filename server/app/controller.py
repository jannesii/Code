# controller.py
import os
import tempfile
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from flask_login import current_user
from werkzeug.security import generate_password_hash, check_password_hash
import logging

from models import User, TemperatureHumidity, ESP32TemperatureHumidity, Status, ImageData, TimelapseConf, ThermostatConf
from .database import DatabaseManager
import pytz
import sqlite3

logger = logging.getLogger(__name__)


class Controller:
    def __init__(self, db_path: str = os.getenv("DB_PATH", os.path.join(tempfile.gettempdir(), "timelapse.db"))):
        self.db = DatabaseManager(db_path)
        self.finland_tz = pytz.timezone('Europe/Helsinki')

    # --- User operations ---
    def register_user(
        self, 
        username: str, 
        password: str | None = None, 
        password_hash: str | None = None, 
        is_admin: bool = False, 
        is_root_admin: bool = False,
        is_temporary: bool = False, 
        expires_at: str | None = None
        ) -> User:
        """
        Creates the user if it doesn't exist, or returns the existing one.
        Uses INSERT OR IGNORE to avoid UNIQUE errors, then SELECT to fetch.
        """
        logger.info(f"Registering user: {username}")

        # 1) Hash the password up front
        if password_hash is None and password:
            pw_hash = generate_password_hash(password)
        elif password is None and password_hash is None:
            raise ValueError(
                "Either password or password_hash must be provided")
        else:
            pw_hash = password_hash

        # 2) Try to insert; if username exists, this is a no-op
        cursor = self.db.execute_query(
            "INSERT OR IGNORE INTO users (username, password_hash, is_admin, is_root_admin, is_temporary, expires_at) VALUES (?, ?, ?, ?, ?, ?)",
            (username, pw_hash, 1 if is_admin else 0, 1 if is_root_admin else 0, 1 if is_temporary else 0, expires_at)
        )
        if cursor.rowcount == 1:
            logger.info(f"User '{username}' created successfully.")
        else:
            logger.info(f"User '{username}' already exists, skipping INSERT.")

        # 3) Fetch whatever is now in the table
        row = self.db.fetchone(
            "SELECT id, username, password_hash, is_admin, is_root_admin, is_temporary, expires_at FROM users WHERE username = ?",
            (username,)
        )
        if row is None:
            # This really should never happen
            logger.error(
                f"After INSERT OR IGNORE, no row for '{username}' found.")
            raise RuntimeError(f"Failed to retrieve user '{username}'")

        logger.info(f"Returning user '{username}' with id={row['id']}")
        return User(
            id=row['id'],
            username=row['username'],
            password_hash=row['password_hash'],
            is_admin=row['is_admin'],
            is_root_admin=row['is_root_admin'],
            is_temporary=row['is_temporary'],
            expires_at=row['expires_at']
        )

    def create_temporary_user(self, username: str, password: str, duration_value: int = 1, duration_unit: str = "hours") -> User:
        """Creates a temporary user with expiration."""
        now = datetime.now(self.finland_tz)
        if duration_unit == "minutes":
            expires = now + timedelta(minutes=duration_value)
        elif duration_unit == "hours":
            expires = now + timedelta(hours=duration_value)
        elif duration_unit == "days":
            expires = now + timedelta(days=duration_value)
        else:
            expires = now + timedelta(hours=duration_value)
        expires_at = expires.isoformat()
        return self.register_user(username, password=password, is_temporary=True, expires_at=expires_at)

    def set_user_as_admin(self, username: str, is_admin: bool) -> None:
        """Sets the is_admin flag for the user with the given username."""
        self.db.execute_query(
            "UPDATE users SET is_admin = ? WHERE username = ?",
            (is_admin, username)
        )

    def authenticate_user(self, username: str, password: str) -> bool:
        row = self.db.fetchone(
            "SELECT password_hash FROM users WHERE username = ?", (username,)
        )
        if row is None:
            return False
        return check_password_hash(row['password_hash'], password)

    def get_all_users(self, exclude_admin: bool = False, exclude_current: bool = False, exclude_expired: bool = False) -> list[User]:
        """Palauttaa listan kaikista käyttäjistä."""
        rows = self.db.fetchall(
            "SELECT id, username, password_hash, is_admin, is_root_admin, is_temporary, expires_at FROM users",
            ()
        )
        users = [
            User(id=row['id'], username=row['username'],
                 password_hash=row['password_hash'], is_admin=row['is_admin'], is_root_admin=row['is_root_admin'], is_temporary=row['is_temporary'], expires_at=row['expires_at'])
            for row in rows
        ]
        if exclude_admin:
            users = [user for user in users if not user.is_admin]
        if exclude_current:
            users = [user for user in users if user.username !=
                     current_user.get_id()]
        if exclude_expired:
            now = datetime.now(self.finland_tz)
            users = [user for user in users if not user.is_temporary or not user.expires_at or datetime.fromisoformat(
                user.expires_at) > now]
        return users

    def get_user_by_username(self, username: str, include_pw: bool = True) -> User | None:
        row = self.db.fetchone(
            "SELECT id, username, password_hash, is_admin, is_root_admin, is_temporary, expires_at FROM users WHERE username = ?",
            (username,)
        )
        if not row:
            return None
        return User(
            id=row['id'],
            username=row['username'],
            password_hash=row['password_hash'] if include_pw else None,
            is_admin=row['is_admin'],
            is_root_admin=row['is_root_admin'],
            is_temporary=row['is_temporary'],
            expires_at=row['expires_at']
        )

    def delete_user(self, username: str) -> None:
        """Poistaa käyttäjän annetulla käyttäjätunnuksella."""
        self.db.execute_query(
            "DELETE FROM users WHERE username = ?",
            (username,)
        )

    def delete_temporary_users(self) -> None:
        """Deletes all temporary users."""
        self.db.execute_query(
            "DELETE FROM users WHERE is_temporary = 1",
            ()
        )

    def delete_expired_temporary_users(self) -> None:
        """Deletes all expired temporary users."""
        now = datetime.now(self.finland_tz).isoformat()
        self.db.execute_query(
            "DELETE FROM users WHERE is_temporary = 1 AND expires_at IS NOT NULL AND expires_at < ?",
            (now,)
        )

    def update_user(
        self,
        current_username: str,
        new_username: str | None = None,
        password: str | None = None,
        is_temporary: bool | None = None,
        is_admin: bool | None = None,
        expires_at: str | None = None,
    ) -> User:
        """
        Updates the given user's fields. Pass None for fields you don't want to change.
        If is_temporary is False, expires_at will be set to NULL regardless of value.
        Returns the updated User object.
        """
        row = self.db.fetchone(
            "SELECT id, username, password_hash, is_admin, is_temporary, expires_at FROM users WHERE username = ?",
            (current_username,)
        )
        if row is None:
            raise ValueError("User not found")

        updates: list[str] = []
        params: list[object] = []

        if new_username and new_username != current_username:
            updates.append("username = ?")
            params.append(new_username)

        if password:
            pw_hash = generate_password_hash(password)
            updates.append("password_hash = ?")
            params.append(pw_hash)

        if is_admin is not None:
            updates.append("is_admin = ?")
            params.append(1 if is_admin else 0)

        if is_temporary is not None:
            updates.append("is_temporary = ?")
            params.append(1 if is_temporary else 0)
            if is_temporary:
                # Set provided expires_at (can be None, meaning no expiry yet)
                updates.append("expires_at = ?")
                params.append(expires_at)
            else:
                # Clear expiry when switching to permanent
                updates.append("expires_at = NULL")

        elif expires_at is not None:
            # Only update expiry if caller asked and did not change is_temporary
            updates.append("expires_at = ?")
            params.append(expires_at)

        if not updates:
            # Nothing to change; return current user state
            return User(
                id=row['id'],
                username=row['username'],
                password_hash=row['password_hash'],
                is_admin=row['is_admin'],
                is_temporary=row['is_temporary'],
                expires_at=row['expires_at']
            )

        query = f"UPDATE users SET {', '.join(updates)} WHERE username = ?"
        params.append(current_username)

        try:
            self.db.execute_query(query, tuple(params))
        except sqlite3.IntegrityError as ie:
            # Likely UNIQUE constraint failure on username
            raise ValueError("Käyttäjätunnus on jo käytössä.") from ie

        return self.get_user_by_username(new_username or current_username)

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
        
    def record_esp32_temphum(self, location: str, temperature: float, humidity: float) -> ESP32TemperatureHumidity:
        now = datetime.now(self.finland_tz).isoformat()
        self.db.execute_query(
            "INSERT INTO esp32_temphum (location, timestamp, temperature, humidity) VALUES (?, ?, ?, ?)",
            (location, now, temperature, humidity)
        )
        row = self.db.fetchone(
            "SELECT id, location, timestamp, temperature, humidity FROM esp32_temphum ORDER BY id DESC LIMIT 1"
        )
        if row is None:
            raise RuntimeError("Failed to retrieve inserted esp32_temphum record")
        return ESP32TemperatureHumidity(
            id=row['id'], location=row['location'], timestamp=row['timestamp'],
            temperature=row['temperature'], humidity=row['humidity']
        )

    def get_last_esp32_temphum(self) -> Optional[ESP32TemperatureHumidity]:
        row = self.db.fetchone(
            "SELECT id, location, timestamp, temperature, humidity FROM esp32_temphum ORDER BY id DESC LIMIT 1"
        )
        if row is None:
            return None
        return ESP32TemperatureHumidity(
            id=row['id'], location=row['location'], timestamp=row['timestamp'],
            temperature=row['temperature'], humidity=row['humidity']
        )

    def get_esp32_temphum_for_date(self, date_str: str, location: str) -> List[ESP32TemperatureHumidity]:
        rows = self.db.fetchall(
            """
            SELECT id, location, timestamp, temperature, humidity
              FROM esp32_temphum
             WHERE date(timestamp) = ? AND location = ?
             ORDER BY timestamp
            """,
            (date_str, location)
        )
        return [
            ESP32TemperatureHumidity(
                id=row['id'],
                location=row['location'],
                timestamp=row['timestamp'],
                temperature=row['temperature'],
                humidity=row['humidity']
            )
            for row in rows
        ]

    def get_last_esp32_temphum_for_location(self, location: str) -> Optional[ESP32TemperatureHumidity]:
        """Return the most recent ESP32TemperatureHumidity row for a given location, or None."""
        row = self.db.fetchone(
            """
            SELECT id, location, timestamp, temperature, humidity
              FROM esp32_temphum
             WHERE location = ?
             ORDER BY timestamp DESC, id DESC
             LIMIT 1
            """,
            (location,)
        )
        if row is None:
            return None
        return ESP32TemperatureHumidity(
            id=row['id'],
            location=row['location'],
            timestamp=row['timestamp'],
            temperature=row['temperature'],
            humidity=row['humidity']
        )



    def get_unique_locations(self) -> List[Dict[str, Any]]:
        """
        Return the latest (most recent) reading per unique location,
        as a list of dicts with keys: location, temp, hum.
        """
        try:
            # Fast path: use a window function to rank rows per location
            rows = self.db.fetchall(
                """
                SELECT id, location, timestamp, temperature, humidity
                FROM (
                  SELECT e.*, ROW_NUMBER() OVER (
                              PARTITION BY location
                              ORDER BY timestamp DESC, id DESC
                            ) AS rn
                  FROM esp32_temphum AS e
                )
                WHERE rn = 1
                ORDER BY location
                """
            )
        except Exception:
            # Fallback for older SQLite versions without window functions
            rows = self.db.fetchall(
                """
                SELECT e.id, e.location, e.timestamp, e.temperature, e.humidity
                FROM esp32_temphum AS e
                WHERE e.id = (
                    SELECT e2.id
                      FROM esp32_temphum AS e2
                     WHERE e2.location = e.location
                     ORDER BY e2.timestamp DESC, e2.id DESC
                     LIMIT 1
                )
                ORDER BY e.location
                """
            )

        return [
            {
                "location": row["location"],
                "temperature": float(row["temperature"]) if row["temperature"] is not None else None,
                "humidity": float(row["humidity"]) if row["humidity"] is not None else None,
                "timestamp": row["timestamp"],
            }
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

    def record_gcode_command(self, gcode: str) -> None:
        logger.info(f"Recording G-code command: {gcode}")
        now = datetime.now(self.finland_tz).isoformat()
        self.db.execute_query(
            "INSERT INTO gcode_commands (timestamp, gcode) VALUES (?, ?)",
            (now, gcode)
        )

    def get_all_gcode_commands(self) -> List[str]:
        rows = self.db.fetchall(
            "SELECT gcode FROM gcode_commands ORDER BY id DESC"
        )
        gcode_set = set([row['gcode'] for row in rows])
        return list(gcode_set)

    def log_message(self, message: str, log_type: str = 'info') -> None:
        """
        Logs a message with the given type ('info', 'warning', 'error', 'auth', 'ac').
        """
        now = datetime.now(self.finland_tz).isoformat()
        self.db.execute_query(
            "INSERT INTO logs (timestamp, type, message) VALUES (?, ?, ?)",
            (now, log_type, message)
        )

    def get_logs(self, limit: int = 100) -> List[dict]:
        """
        Retrieves the most recent log messages.
        """
        rows = self.db.fetchall(
            "SELECT timestamp, type, message FROM logs ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        return [dict(row) for row in rows]

    # --- Thermostat configuration operations ---
    def get_thermostat_conf(self) -> ThermostatConf | None:
        row = self.db.fetchone(
            """
            SELECT id, sleep_active, sleep_start, sleep_stop, target_temp, pos_hysteresis, neg_hysteresis, thermo_active
              FROM thermostat_conf
             WHERE id = 1
            """
        )
        if row is None:
            return None
        return ThermostatConf(
            id=row['id'],
            sleep_active=bool(row['sleep_active']),
            sleep_start=row['sleep_start'],
            sleep_stop=row['sleep_stop'],
            target_temp=float(row['target_temp']),
            pos_hysteresis=float(row['pos_hysteresis']),
            neg_hysteresis=float(row['neg_hysteresis']),
            thermo_active=bool(row['thermo_active']) if 'thermo_active' in row.keys() else True,
        )

    def save_thermostat_conf(
        self,
        *,
        sleep_active: bool,
        sleep_start: str | None,
        sleep_stop: str | None,
        target_temp: float,
        pos_hysteresis: float,
        neg_hysteresis: float,
        thermo_active: bool,
    ) -> ThermostatConf:
        self.db.execute_query(
            """
            INSERT INTO thermostat_conf (id, sleep_active, sleep_start, sleep_stop, target_temp, pos_hysteresis, neg_hysteresis, thermo_active)
            VALUES (1, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                sleep_active = excluded.sleep_active,
                sleep_start = excluded.sleep_start,
                sleep_stop = excluded.sleep_stop,
                target_temp = excluded.target_temp,
                pos_hysteresis = excluded.pos_hysteresis,
                neg_hysteresis = excluded.neg_hysteresis,
                thermo_active = excluded.thermo_active
            """,
            (
                1 if sleep_active else 0,
                sleep_start,
                sleep_stop,
                float(target_temp),
                float(pos_hysteresis),
                float(neg_hysteresis),
                1 if thermo_active else 0,
            ),
        )
        conf = self.get_thermostat_conf()
        if conf is None:
            # This should never happen after UPSERT
            raise RuntimeError("Failed to save thermostat configuration")
        return conf

    def ensure_thermostat_conf_seeded_from(self, cfg: object | None = None) -> ThermostatConf:
        """
        Seed the thermostat configuration row from a given config-like object
        that provides attributes: setpoint_c, pos_hysteresis, neg_hysteresis, sleep_enabled,
        sleep_start, sleep_stop. If a row already exists, it is returned as-is.
        """
        existing = self.get_thermostat_conf()
        if existing is not None:
            return existing
        # Extract with safe fallbacks
        def _getattr(name: str, default):
            if cfg is None:
                return default
            return getattr(cfg, name, default)
        setpoint_c = float(_getattr('setpoint_c', 24.5))
        # If old single deadband exists, split evenly; else default 0.5/0.5
        pos_h = float(_getattr('pos_hysteresis', 0.5))
        neg_h = float(_getattr('neg_hysteresis', 0.5))
        sleep_enabled = bool(_getattr('sleep_enabled', True))
        thermo_active = bool(_getattr('thermo_active', True))
        sleep_start = _getattr('sleep_start', None)
        sleep_stop = _getattr('sleep_stop', None)
        return self.save_thermostat_conf(
            sleep_active=sleep_enabled,
            sleep_start=sleep_start,
            sleep_stop=sleep_stop,
            target_temp=setpoint_c,
            pos_hysteresis=pos_h,
            neg_hysteresis=neg_h,
            thermo_active=thermo_active,
        )
