# stream_server.py
from flask import Flask, Response, render_template_string
from flask_socketio import SocketIO
import stream_state

app = Flask(__name__)
socketio = SocketIO(app)

HTML_PAGE = """
<html>
  <head>
    <title>Camera Feed</title>
    <!-- Include Socket.IO client library -->
    <script src="//cdnjs.cloudflare.com/ajax/libs/socket.io/3.0.3/socket.io.min.js"></script>
    <script type="text/javascript">
      document.addEventListener("DOMContentLoaded", function() {
          var socket = io();
          // Listen for the "update_frame" event to refresh the image
          socket.on('update_frame', function(data) {
              var image = document.getElementById("stream");
              image.src = "/current_frame.jpg?rand=" + new Date().getTime();
          });
      });
    </script>
  </head>
  <body>
    <h1>Camera Feed</h1>
    <img id="stream" src="/current_frame.jpg" alt="Camera Feed" style="max-width: 100%;">
  </body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/current_frame.jpg')
def current_frame():
    if stream_state.latest_frame_jpeg is None:
        return Response("No image available", status=503, mimetype='text/plain')
    return Response(stream_state.latest_frame_jpeg, mimetype='image/jpeg')

def run_server():
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, use_reloader=False)
