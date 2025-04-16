from flask import Flask, render_template, request, abort
import json
from datetime import datetime
import random
from flask_socketio import SocketIO, emit

server = Flask(__name__)
socketio = SocketIO(server, cors_allowed_origins="*")

@server.route('/')
def get_home_page():
    return render_template('index.html')

@server.route('/3d')
def get_3d_page():
    return render_template('3d.html')

@server.route('3d/image', methods=['POST'])
def update_image():
    data = request.get_json()
    if not data or 'image' not in data:
        abort(400, 'Invalid image data')
    
    image_data = data['image']
    # Process the image data as needed
    print(f"Received image data: {image_data}")
    
    # Send a response back to the client
    return json.dumps({'status': 'success', 'message': 'Image received successfully'})

@server.route('/3d/temphum', methods=['POST'])
def update_temperature_humidity():
    data = request.get_json()
    if not data or 'temperature' not in data or 'humidity' not in data:
        abort(400, 'Invalid temperature/humidity data')
    
    temperature = data['temperature']
    humidity = data['humidity']
    # Process the temperature and humidity data as needed
    print(f"Received temperature: {temperature}, humidity: {humidity}")
    
    # Send a response back to the client
    return json.dumps({'status': 'success', 'message': 'Temperature and humidity received successfully'})

@server.route('/3d/status', methods=['POST'])
def update_timelapse_status():
    data = request.get_json()
    if not data or 'status' not in data:
        abort(400, 'Invalid status data')
    
    status = data['status']
    # Process the status data as needed
    print(f"Received timelapse status: {status}")
    
    # Send a response back to the client
    return json.dumps({'status': 'success', 'message': 'Timelapse status received successfully'})


if __name__ == '__main__':
   socketio.run(server, port=5555, debug=True)