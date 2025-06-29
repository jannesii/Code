# run.py
import os

from app import create_app
from signal_handler import SignalHandler

os.environ["SECRET_KEY"] = "test_e"
os.environ["FLASK_DEBUG"] = "1"
os.environ["RATE_LIMIT_WHITELIST"] = '["127.0.0.1", "192.168.0.2", "192.168.1.51"]'
os.environ["ALLOWED_WS_ORIGINS"] = '["http://127.0.0.1:5555"]'
os.environ["DB_PATH"] = "data.db"
os.environ["WEB_USERNAME"] = "admin"
os.environ["WEB_PASSWORD"] = "scrypt:32768:8:1$4ZEkkw6YC8GzE1RD$cf9d9137ffbb507ab4e19be812c3b874c196a0426a6eed0b797c4d1219ac2c618303fef44ff5ca8c21b0efe90a4c4ab63b2b87321b6de0cb90391afcfd924490"

app, socketio = create_app(development=True)
#SignalHandler(socketio)

if __name__ == "__main__":
        
    socketio.run(
        app,
        host="127.0.0.1",
        port=5555,
        debug=True,
    )
