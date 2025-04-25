# run.py
import os

from app import create_app

app, socketio = create_app()

if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG")
    if debug == "1":
        debug = True
    else:
        debug = False
    socketio.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT")),
        debug=debug,
    )
