# stream_server.py
from flask import Flask, Response, render_template_string
from flask_socketio import SocketIO
import stream_state
import logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)

app = Flask(__name__)
socketio = SocketIO(app)

HTML_PAGE = """
<html>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
    <style>
      /* Basic reset for margin and padding */
      body, html {
        margin: 0;
        padding: 0;
      }
      /* Container to limit the max width to 1920px and center content */
      .container {
        max-width: 1920px;
        margin: 0 auto;
      }
      /* Image scales to fill the container while maintaining its aspect ratio */
      img {
        display: block;
        width: 100%;
        height: auto;
      }
    </style>
  </head>
  <body>
    <div class="container">
      <img id="stream" src="/current_frame.jpg" alt="Camera Feed">
    </div>
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
