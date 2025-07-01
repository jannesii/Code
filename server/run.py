# run.py
import os
import logging

from app import create_app
from signal_handler import SignalHandler

logging.basicConfig(
    level=logging.INFO,
    datefmt="%H:%M:%S"
)
logging.getLogger("socketio.server").setLevel(logging.WARNING)
app, socketio = create_app()

if os.name != 'nt':
    SignalHandler(socketio)

if __name__ == "__main__":
    socketio.run(
        app,
        host="127.0.0.1",
        port=int(os.getenv("PORT", 5555))
    )
