# run.py
import logging
from app import create_app

app, socketio = create_app('config.json')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    socketio.run(app, host='0.0.0.0', port=5555, debug=True)
