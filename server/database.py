# database.py
import sqlite3
import threading
from typing import Any, List, Optional, Tuple

class DatabaseManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_path: str = 'app.db'):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DatabaseManager, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_path: str = 'app.db'):
        if getattr(self, '_initialized', False):
            return
        self._initialized = True
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self) -> None:
        # Ensure all required tables exist
        tables = {
            'users': (
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'username TEXT UNIQUE NOT NULL, '
                'password_hash TEXT NOT NULL'
            ),
            'temphum': (
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'timestamp TEXT NOT NULL, '
                'temperature REAL NOT NULL, '
                'humidity REAL NOT NULL'
            ),
            'status': (
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'timestamp TEXT NOT NULL, '
                'status TEXT NOT NULL'
            ),
            'images': (
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'timestamp TEXT NOT NULL, '
                'image TEXT NOT NULL'
            ),
        }
        for name, schema in tables.items():
            self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {name} ({schema})")
        self.conn.commit()

    def execute_query(
        self,
        query: str,
        params: Tuple[Any, ...] = ()
    ) -> None:
        self.cursor.execute(query, params)
        self.conn.commit()

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