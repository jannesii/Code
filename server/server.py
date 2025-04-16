from flask import Flask, render_template, request, abort
import json
from datetime import datetime
import random
from flask_socketio import SocketIO, emit
import base64
import cv2
import numpy as np

server = Flask(__name__)
socketio = SocketIO(server, cors_allowed_origins="*")


@server.route('/')
def get_home_page():
    return render_template('index.html')


@server.route('/3d')
def get_3d_page():
    with open('last_image.json', 'r') as f:
        last_image = json.load(f)
    return render_template('3d.html', last_image=last_image)


@server.route('/3d/image', methods=['POST'])
def update_image():
    data = request.get_json()
    if not data or 'image' not in data:
        abort(400, 'Invalid image data')

    # The image is a base64-encoded string in the JSON.
    image_data = data['image']
    
    with open('last_image.json', 'w') as f:
        json.dump(data, f)

    # Decode the base64 string to get the original binary data.
    try:
        decoded_data = base64.b64decode(image_data)
    except Exception as e:
        abort(400, f"Decoding error: {e}")

    # If you need to convert the binary data into an image for processing,
    # you can use numpy and OpenCV:
    try:
        # Convert the bytes into a NumPy array.
        nparr = np.frombuffer(decoded_data, np.uint8)
        # Decode the NumPy array as an image.
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            abort(400, "Failed to decode image into an array")
        socketio.emit('image', {'image': image_data})
    except Exception as e:
        abort(400, f"Image processing error: {e}")

    # Now you have the image as a NumPy array (img), and you can proceed to process it as needed.
    print(f"Received image decoded successfully. Image shape: {img.shape}")
    
    # Optionally, save the image to verify correct decoding:
    #cv2.imwrite('received_image.jpg', img)


    # Return a success response.
    return json.dumps({'status': 'success', 'message': 'Image received and decoded successfully'})


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

    socketio.emit('status', data)

    # Send a response back to the client
    return json.dumps({'status': 'success', 'message': 'Timelapse status received successfully'})


if __name__ == '__main__':
    socketio.run(server, host='0.0.0.0', port=5555, debug=True)
