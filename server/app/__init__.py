import eventlet
eventlet.monkey_patch()
from .controller import Controller
from flask_limiter.util import get_remote_address
from flask_limiter import Limiter
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask import Flask, send_from_directory
import pathlib
import tempfile
from datetime import timedelta
import os
import logging
import json
import signal

# ─── Module-level limiter ───
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],
    storage_uri="redis://localhost:6379",
    storage_options={"socket_connect_timeout": 30},
    strategy="moving-window",
)


def create_app():
    logger = logging.getLogger(__name__)
    logger.info("Starting application")
    logger.debug("Debug logging enabled")
    _is_windows = os.name == "nt"

    # ─── SECRET_KEY ───
    secret = os.getenv("SECRET_KEY", "test")
    if not secret:
        raise RuntimeError("SECRET_KEY is missing – add to environment.")

    raw = os.getenv("RATE_LIMIT_WHITELIST", "")
    if raw:
        try:
            whitelist = json.loads(raw)
        except json.JSONDecodeError:
            raise RuntimeError("RATE_LIMIT_WHITELIST isn’t valid JSON list")
    else:
        whitelist = []
    logger.info("Rate limit whitelist: %s", whitelist)
    # ─── Flask app & config ───
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=secret,
        PERMANENT_SESSION_LIFETIME=timedelta(days=7),
        SESSION_COOKIE_SECURE=not _is_windows,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        WEB_USERNAME=os.getenv("WEB_USERNAME", "admin"),
        WEB_PASSWORD=os.getenv("WEB_PASSWORD", "admin"),
        # ← CSRF tokens now expire after 1 hour
        WTF_CSRF_TIME_LIMIT=None,
        whitelist=whitelist,
    )
    
    HLS_ROOT = pathlib.Path("/srv/hls")    # parent of “printer1”

    @app.route("/live/<path:filename>")
    def live(filename):
        return send_from_directory(HLS_ROOT, filename)
    
    # ─── Rate limiting ───
    if not _is_windows:
        limiter.init_app(app)
        logger.info("Rate limiting enabled")

    # ─── CSRF protection ───
    csrf = CSRFProtect()
    csrf.init_app(app)
    logger.info("CSRF protection enabled (1 h token lifetime)")

    # ─── Domain-controller ───
    db_path = os.getenv("DB_PATH", os.path.join(
        tempfile.gettempdir(), "timelapse.db"))
    if not db_path:
        raise RuntimeError("DB_PATH is missing – add to environment.")
    app.ctrl = Controller(db_path)  # type: ignore
    logger.info("Controller init: %s", db_path)

    # ─── Seed admin user ───
    try:
        if not _is_windows:
            app.ctrl.register_user(  # type: ignore
                app.config["WEB_USERNAME"],
                password_hash=app.config["WEB_PASSWORD"],
                is_admin=True
            )
        else:
            app.ctrl.register_user(  # type: ignore
                app.config["WEB_USERNAME"],
                password=app.config["WEB_PASSWORD"],
                is_admin=True
            )
        logger.info("Seeded admin user %s (is_admin=True)",
                    app.config["WEB_USERNAME"])
    except ValueError:
        app.ctrl.set_user_as_admin(
            app.config["WEB_USERNAME"], True)  # type: ignore
        logger.info("Ensured %s has is_admin=True", app.config["WEB_USERNAME"])

    # ─── Flask-Login ───
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"  # type: ignore
    login_manager.init_app(app)
    from .auth import load_user, AuthAnonymous, kick_if_expired
    app.before_request(kick_if_expired)
    login_manager.user_loader(load_user)
    login_manager.anonymous_user = AuthAnonymous
    logger.info("Login manager ready")

    # ─── Socket.IO ───
    raw = os.getenv("ALLOWED_WS_ORIGINS", '["http://127.0.0.1:5555"]')
    if raw:
        try:
            allowed_ws_origins = json.loads(raw)
            logger.info("Allowed WebSocket origins: %s", allowed_ws_origins)
        except json.JSONDecodeError:
            raise RuntimeError("ALLOWED_WS_ORIGINS isn’t valid JSON list")
    else:
        allowed_ws_origins = []

    if not _is_windows:
        socketio = SocketIO(
            app,
            async_mode="eventlet",
            message_queue="redis://localhost:6379",
            cors_allowed_origins=allowed_ws_origins,
            max_http_buffer_size=10 * 1024 * 1024,
            ping_interval=10,
            ping_timeout=20,
            logger=True,
        )
    else:
        socketio = SocketIO(
            app,
            async_mode="eventlet",
            cors_allowed_origins=allowed_ws_origins,
            max_http_buffer_size=10 * 1024 * 1024,
            ping_interval=10,
            ping_timeout=20,
            logger=True,
        )
    def exit_signal():
        socketio.emit('server_shutdown')
        socketio.stop()
    signal.signal(signal.SIGTERM, exit_signal)
    signal.signal(signal.SIGINT, exit_signal)
    app.socketio = socketio  # type: ignore
    logger.info("Socket.IO ready (origins: %s)", allowed_ws_origins)
    # ─── Socket event handlers ───
    from .socket_handlers import SocketEventHandler
    SocketEventHandler(socketio, app.ctrl)  # type: ignore

    # ─── Blueprints ───
    from .auth import auth_bp
    from .web import web_bp
    from .api import api_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp)

    return app, socketio
