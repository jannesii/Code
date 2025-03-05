# stream_server.py
from flask import Flask, Response, render_template_string
import stream_state

app = Flask(__name__)

HTML_PAGE = """
<html>
  <head>
    <title>Camera Feed</title>
    <script type="text/javascript">
      // Update the image every 1000ms (1 second)
      setInterval(function() {
          var image = document.getElementById("stream");
          // Append a dummy query parameter to prevent browser caching
          image.src = "/current_frame.jpg?rand=" + new Date().getTime();
      }, 1000);
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
    # Run the Flask server so that it is accessible on the local network.
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
