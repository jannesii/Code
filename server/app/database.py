# database.py
import sqlite3
from sqlite3 import Connection, Cursor
import threading
from typing import Any, List, Optional, Tuple

class DatabaseManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_path: str):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DatabaseManager, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_path: str):
        if getattr(self, '_initialized', False):
            return
        self._initialized = True
        self.db_path = db_path
        self.conn: Connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor: Cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self) -> None:
        # Ensure all required tables exist
        tables = {
            'users': (
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'username TEXT UNIQUE NOT NULL, '
                'password_hash TEXT NOT NULL, '
                'is_admin BOOLEAN NOT NULL DEFAULT FALSE, '
                'is_root_admin BOOLEAN NOT NULL DEFAULT 0, '
                'is_temporary BOOLEAN DEFAULT 0, '
                'expires_at TEXT'
            ),
            'temphum': (
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'timestamp TEXT NOT NULL, '
                'temperature REAL NOT NULL, '
                'humidity REAL NOT NULL'
            ),
            'esp32_temphum': (
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'location TEXT NOT NULL, '
                'timestamp TEXT NOT NULL, '
                'temperature REAL NOT NULL, '
                'humidity REAL NOT NULL'
            ),
            'status': (
                'id INTEGER PRIMARY KEY CHECK (id = 1),'
                'timestamp TEXT NOT NULL, '
                'status TEXT NOT NULL'
            ),
            'images': (
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'timestamp TEXT NOT NULL, '
                'image TEXT NOT NULL'
            ),
            'timelapse_conf': (
                'id INTEGER PRIMARY KEY CHECK (id = 1),'
                'image_delay INTEGER NOT NULL,'
                'temphum_delay INTEGER NOT NULL,'
                'status_delay INTEGER NOT NULL'
            ),
            'thermostat_conf': (
                'id INTEGER PRIMARY KEY CHECK (id = 1), '
                'sleep_active BOOLEAN NOT NULL, '
                'sleep_start TEXT, '
                'sleep_stop TEXT, '
                'target_temp REAL NOT NULL, '
                'pos_hysteresis REAL NOT NULL, '
                'neg_hysteresis REAL NOT NULL, '
                'thermo_active BOOLEAN NOT NULL DEFAULT 1'
            ),
            'gcode_commands': (
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'timestamp TEXT NOT NULL, '
                'gcode TEXT NOT NULL'
            ),
            'logs': (
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'timestamp TEXT NOT NULL, '
                'type TEXT NOT NULL, '
                'message TEXT NOT NULL'
            )
        }
        for name, schema in tables.items():
            self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {name} ({schema})")
        # Migrate existing users table to include is_root_admin if missing
        try:
            self.cursor.execute("PRAGMA table_info(users)")
            cols = [row[1] for row in self.cursor.fetchall()]
            if 'is_root_admin' not in cols:
                self.cursor.execute("ALTER TABLE users ADD COLUMN is_root_admin BOOLEAN NOT NULL DEFAULT 0")
        except Exception:
            pass

        # Migrate existing thermostat_conf to include thermo_active if missing
        try:
            self.cursor.execute("PRAGMA table_info(thermostat_conf)")
            cols = [row[1] for row in self.cursor.fetchall()]
            if 'thermo_active' not in cols:
                self.cursor.execute(
                    "ALTER TABLE thermostat_conf ADD COLUMN thermo_active BOOLEAN NOT NULL DEFAULT 1"
                )
        except Exception:
            pass
            
        # Insert default values for status and timelapse_conf if they don't exist
        self.cursor.execute("""
        INSERT OR IGNORE INTO status (id, timestamp, status)
        VALUES (1, datetime('now'), 'IDLE')
        """)

        self.cursor.execute("""
        INSERT OR IGNORE INTO timelapse_conf (id, image_delay, temphum_delay, status_delay)
        VALUES (1, 5, 10, 15)
        """)

        triggers = {
            'keep_only_last_10_images': """
            CREATE TRIGGER IF NOT EXISTS keep_only_last_10_images
            AFTER INSERT ON images
            FOR EACH ROW
            BEGIN
                DELETE FROM images
                WHERE id NOT IN (
                    SELECT id
                    FROM images
                    ORDER BY timestamp DESC
                    LIMIT 10
                );
            END;
            """,
            'cleanup_temphum_after_insert':"""  
            CREATE TRIGGER IF NOT EXISTS cleanup_temphum_after_insert
            AFTER INSERT ON temphum
            BEGIN
                DELETE FROM temphum
                WHERE timestamp < datetime('now', '-7 days');
            END;
            """,
            'cleanup_esp32_temphum_after_insert':"""  
            CREATE TRIGGER IF NOT EXISTS cleanup_esp32_temphum_after_insert
            AFTER INSERT ON esp32_temphum
            BEGIN
                DELETE FROM esp32_temphum
                WHERE timestamp < datetime('now', '-7 days');
            END;
            """
        }

        for name, trigger_sql in triggers.items():
            self.cursor.executescript(trigger_sql)

        # --- Indexes for performance-critical queries ---
        # Speed up latest-per-location lookups used by Controller.get_unique_locations()
        # Pattern: WHERE location = ? ORDER BY timestamp DESC, id DESC LIMIT 1
        # This composite index allows an efficient seek to the newest row per location.
        try:
            self.cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_esp32_temphum_loc_ts_id
                ON esp32_temphum (location, timestamp DESC, id DESC)
                """
            )
        except Exception:
            # Best-effort: ignore if SQLite version doesn't support DESC in index columns
            try:
                self.cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_esp32_temphum_loc_ts_id ON esp32_temphum (location, timestamp, id)"
                )
            except Exception:
                pass

        # Optional: help date-based reads per location
        # Pattern: WHERE date(timestamp) = ? AND location = ?
        # Expression indexes are supported by SQLite; if not, ignore.
        try:
            self.cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_esp32_temphum_date_loc
                ON esp32_temphum (date(timestamp), location)
                """
            )
        except Exception:
            pass

        self.conn.commit()

    def execute_query(
        self,
        query: str,
        params: Tuple[Any, ...] = ()
    ) -> Cursor:
        self.cursor.execute(query, params)
        self.conn.commit()
        return self.cursor

    def executemany(
        self,
        query: str,
        param_list: List[Tuple[Any, ...]]
    ) -> None:
        self.cursor.executemany(query, param_list)
        self.conn.commit()

    def fetchone(
        self,
        query: str,
        params: Tuple[Any, ...] = ()
    ) -> Optional[sqlite3.Row]:
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def fetchall(
        self,
        query: str,
        params: Tuple[Any, ...] = ()
    ) -> List[sqlite3.Row]:
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
