# run.py
from app import create_app

if __name__ == '__main__':
    app, socketio, ctrl = create_app('config.json')
    socketio.run(app, host='0.0.0.0', port=5555, debug=True)