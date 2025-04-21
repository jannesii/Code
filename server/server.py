# server.py
# Flask server with login (username/password + "remember me") for web interface
# and API key authentication for socket clients, using Controller & models.

from flask import (
    Flask, render_template, request, abort, redirect,
    url_for, flash, session, jsonify
)
from flask_socketio import SocketIO
from flask_login import (
    LoginManager, UserMixin,
    login_user, login_required,
    logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import hmac
import json
from datetime import timedelta, datetime
from dataclasses import asdict
import pytz

# ——————————————
# Domain imports
# ——————————————
from models import (
    User as DomainUser,
    TemperatureHumidity,
    Status,
    ImageData
)

# ——————————————
# Controller
# ——————————————
from controller import Controller
ctrl = Controller('app.db')

# ——————————————
# Flask App & Config
# ——————————————
server = Flask(__name__)
server.config['SECRET_KEY'] = 'replace-with-a-secure-random-key'
# “Remember me” sessions last 7 days
server.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

socketio = SocketIO(
    server,
    cors_allowed_origins="*",
    max_http_buffer_size=10 * 1024 * 1024,
    ping_timeout=60,
    ping_interval=25
)

# ——————————————
# Load config.json
# ——————————————
with open('config.json', 'r') as f:
    config = json.load(f)

API_KEY = config.get('api_key')
WEB_USERNAME = config.get('web_username')
WEB_PASSWORD = config.get('web_password')

if not API_KEY:
    raise RuntimeError("API key not found in config.json")
if not WEB_USERNAME or not WEB_PASSWORD:
    raise RuntimeError("Web username/password not configured in config.json")

# — Seed admin user into DB if missing —
try:
    ctrl.register_user(WEB_USERNAME, WEB_PASSWORD)
except ValueError:
    # already exists, ignore
    pass


# ——————————————
# Flask‑Login setup
# ——————————————
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(server)


class AuthUser(UserMixin):
    """Flask‑Login user."""

    def __init__(self, username: str):
        self.id = username


@login_manager.user_loader
def load_user(user_id: str):
    # only return a user if they exist in the DB
    if ctrl.get_user_by_username(user_id):
        return AuthUser(user_id)
    return None

# ——————————————
# Authentication routes
# ——————————————


@server.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        if ctrl.authenticate_user(username, password):
            session.permanent = remember
            login_user(AuthUser(username), remember=remember)
            next_page = request.args.get('next') or url_for('get_home_page')
            return redirect(next_page)

        flash('Virheellinen käyttäjätunnus tai salasana', 'error')

    return render_template('login.html')


@server.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ——————————————
# Web interface (protected)
# ——————————————


@server.route('/')
@login_required
def get_home_page():
    return render_template('index.html')


@server.route('/3d')
@login_required
def get_3d_page():
    # Fetch latest records via Controller
    img_obj = ctrl.get_last_image()
    th_obj = ctrl.get_last_temphum()
    st_obj = ctrl.get_last_status()

    # Convert dataclass → dict for Jinja
    last_image = asdict(img_obj) if img_obj else None
    last_temphum = asdict(th_obj) if th_obj else None
    last_status = asdict(st_obj) if st_obj else None

    return render_template(
        '3d.html',
        last_image=last_image,
        last_temphum=last_temphum,
        last_status=last_status,
        api_key=API_KEY
    )


@server.route('/settings')
@login_required
def settings():
    """Settings landing page with tiles."""
    return render_template('settings.html')


@server.route('/settings/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        try:
            ctrl.register_user(username, password)
            flash(f"Käyttäjä «{username}» lisätty onnistuneesti.", "success")
            return redirect(url_for('settings'))
        except ValueError as ve:
            flash(str(ve), "error")
    return render_template('add_user.html')


@server.route('/settings/delete_user', methods=['GET', 'POST'])
@login_required
def delete_user():
    users_list = ctrl.get_all_users()

    if request.method == 'POST':
        username = request.form.get('username')
        # Jos ei valittu käyttäjää, näytä virhe ja palaa
        if not username:
            flash("Valitse ensin käyttäjä.", "error")
            return redirect(url_for('settings'))

        # estetään oman tilin poisto
        if username == current_user.get_id():
            flash("Et voi poistaa omaa tiliäsi.", "error")
        else:
            try:
                ctrl.delete_user(username)
                flash(f"Käyttäjä «{username}» poistettu.", "success")
            except Exception as e:
                flash(f"Poisto epäonnistui: {e}", "error")

        return redirect(url_for('settings'))

    return render_template('delete_user.html', users=users_list)

# ——————————————
# SocketIO handlers
# ——————————————


@socketio.on('connect')
def handle_connect(auth):
    # refuse if no valid API key
    if not handle_auth(auth):
        return False
    print(f"Client connected: {request.sid}")


@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")


@socketio.on('image')
def handle_image(data):
    if not data or 'image' not in data:
        socketio.emit('error', {'message': 'Invalid image data'})
        return
    saved = ctrl.record_image(data['image'])
    socketio.emit('image2v', {'image': saved.image})
    print("📡 Broadcasting image.")


@socketio.on('temphum')
def handle_temphum(data):
    temp = data.get('temperature')
    hum = data.get('humidity')
    if temp is None or hum is None:
        socketio.emit(
            'error', {'message': 'Invalid temperature/humidity data'})
        return
    saved = ctrl.record_temphum(temp, hum)
    socketio.emit('temphum2v', {
        'temperature': saved.temperature,
        'humidity':    saved.humidity
    })
    print(
        f"📡 Broadcasting temphum: temp={saved.temperature}, hum={saved.humidity}")


@socketio.on('status')
def handle_status(data):
    status = data.get('status')
    if status is None:
        socketio.emit('error', {'message': 'Invalid status data'})
        return
    saved = ctrl.record_status(status)
    socketio.emit('status2v', {'status': saved.status})
    print(f"📡 Broadcasting status: {saved.status}")


@server.route('/api/temphum')
@login_required
def api_temphum():
    """
    Query string:
      ?date=YYYY-MM-DD   (defaults to today in UTC)
    Returns JSON array of:
      [{ timestamp: "...", temperature: 23.5, humidity: 56.2 }, ...]
    """
    finland_tz = pytz.timezone('Europe/Helsinki')
    date_str = request.args.get(
        'date',
        datetime.now(finland_tz).date().isoformat()
    )
    data = ctrl.get_temphum_for_date(date_str)
    return jsonify([
        {
            'timestamp':      d.timestamp,
            'temperature':    d.temperature,
            'humidity':       d.humidity
        }
        for d in data
    ])


# ——————————————
# Helper for socket auth
# ——————————————


def handle_auth(auth: dict) -> bool:
    key = (auth or {}).get('api_key')
    return bool(key and hmac.compare_digest(key, API_KEY))


if __name__ == '__main__':
    socketio.run(
        server,
        host='0.0.0.0',
        port=5555,
        debug=True
    )
