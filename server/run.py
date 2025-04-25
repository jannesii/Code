# run.py
import logging
import os

from app import create_app

app, socketio = create_app()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    debug = os.getenv("FLASK_DEBUG")
    if debug:
        logging.getLogger("werkzeug").setLevel(logging.DEBUG)
        logging.warning("Debug mode enabled")
        
    socketio.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT")),
        debug=debug,
    )
