# run.py
import logging
import os

from app import create_app

app, socketio = create_app()

if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG")
    logger = logging.getLogger(__name__)
    logger.info(f"DEBUG: {debug}")
    if debug:
        logging.getLogger("werkzeug").setLevel(logging.DEBUG)
        logging.basicConfig(level=logging.DEBUG)
        logger.debug("Debug mode enabled")
        logger.warning("Debug mode enabled")
    else:
        logging.basicConfig(level=logging.INFO)
        
    socketio.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT")),
        debug=debug,
    )
