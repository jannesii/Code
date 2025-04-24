# run.py
import logging
import os

from app import create_app

app, socketio = create_app()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    debug = os.getenv("FLASK_DEBUG")
    socketio.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT")),
        debug=debug,
    )
