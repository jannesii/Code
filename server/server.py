# server.py
# This is a Flask server that serves a web interface and handles real-time updates via SocketIO.

from flask import Flask, render_template, request, abort, jsonify
from flask_socketio import SocketIO
from functools import wraps
import hmac
import json
from datetime import datetime

# Initialize Flask and SocketIO
server = Flask(__name__)
socketio = SocketIO(server, cors_allowed_origins="*")

# Load API key from configuration file
with open('config.json', 'r') as f:
    config = json.load(f)
API_KEY = config.get('api_key')
if not API_KEY:
    raise RuntimeError("API key not found in config.json")

# Decorator to require a valid API key


def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Look for the key in headers or query parameters
        provided_key = request.headers.get(
            'X-API-KEY') or request.args.get('api_key')
        if not provided_key or not hmac.compare_digest(provided_key, API_KEY):
            abort(401, 'Unauthorized: invalid or missing API key')
        return f(*args, **kwargs)
    return decorated


@server.route('/')
def get_home_page():
    return render_template('index.html')


@server.route('/3d')
def get_3d_page():
    try:
        with open('last_image.json', 'r') as f:
            last_image = json.load(f)
    except FileNotFoundError:
        last_image = None

    return render_template('3d.html', last_image=last_image, api_key=API_KEY)


@server.route('/3d/image', methods=['POST'])
@require_api_key
def update_image():
    data = request.get_json()
    if not data or 'image' not in data:
        abort(400, 'Invalid image data')

    # Save the latest image JSON
    with open('last_image.json', 'w') as f:
        json.dump(data, f)

    # Emit via SocketIO
    try:
        socketio.emit('image', {'image': data['image']})
    except Exception as e:
        abort(500, f"SocketIO emit error: {e}")

    return jsonify(status='success', message='Image received successfully')


@socketio.on('image')
def handle_image(data, auth):
    if not handle_auth(auth):
        print("❌ Virheellinen API‑avain SocketIO‑handle_imagessa")
        socketio.emit('error', {'message': 'Invalid API key'})
        return False

    if not data or 'image' not in data:
        socketio.emit('error', {'message': 'Invalid image data'})
        return

    # Save the latest image JSON
    with open('last_image.json', 'w') as f:
        json.dump(data, f)

    # Emit via SocketIO

    socketio.emit('image', {'image': data['image']})


@server.route('/3d/temphum', methods=['POST'])
@require_api_key
def update_temperature_humidity():
    data = request.get_json()
    if not data or 'temperature' not in data or 'humidity' not in data:
        abort(400, 'Invalid temperature/humidity data')

    # Save the latest temperature and humidity JSON
    with open('last_temphum.json', 'w') as f:
        json.dump(data, f)

    # Emit via SocketIO
    try:
        socketio.emit('temphum', data)
    except Exception as e:
        abort(500, f"SocketIO emit error: {e}")

    print(
        f"Received temperature: {data['temperature']}, humidity: {data['humidity']}")

    return jsonify(status='success', message='Temperature and humidity received successfully')


@socketio.on('temphum')
def handle_temphum(data, auth):
    if not handle_auth(auth):
        socketio.emit(
            'error', {'message': '❌ Virheellinen API‑avain SocketIO‑handle_temphumissa'})
        return False

    # Validointi
    temp = data.get('temperature')
    hum = data.get('humidity')
    if temp is None or hum is None:
        # Voit halutessasi lähettää virheilmoituksen clientille
        socketio.emit(
            'error', {'message': 'Invalid temperature/humidity data'})
        return

    # Tallenna tiedot
    with open('last_temphum.json', 'w') as f:
        json.dump(data, f)

    # Lähetä kaikille muille asiakkaille
    socketio.emit('temphum', data)
    print(f"📡 Broadcast temphum: temp={temp}, hum={hum}")


@server.route('/3d/status', methods=['POST'])
@require_api_key
def update_timelapse_status():
    data = request.get_json()
    if not data or 'status' not in data:
        abort(400, 'Invalid status data')

    with open('last_status.json', 'w') as f:
        json.dump(data, f)

    try:
        socketio.emit('status', data)
    except Exception as e:
        abort(500, f"SocketIO emit error: {e}")

    print(f"Received timelapse status: {data['status']}")

    return jsonify(status='success', message='Timelapse status received successfully')


@socketio.on('connect')
def handle_connect(auth):
    # auth on dict, jos client lähetti { auth: { api_key: ... } }
    if not handle_auth(auth):
        socketio.emit(
            'error', {'message': '❌ Virheellinen API‑avain SocketIO‑connectissa'})
        return False    # kieltäytyy yhteydestä
    print(f"Client connected: {request.sid}")


@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")


def handle_auth(auth):
    api_key = (auth or {}).get('api_key')
    if not api_key or not hmac.compare_digest(api_key, API_KEY):
        return False
    else:
        return True


if __name__ == '__main__':
    socketio.run(server, host='0.0.0.0', port=5555, debug=True)
