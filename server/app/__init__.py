import threading
import eventlet
eventlet.monkey_patch()
from .controller import Controller
from flask_limiter.util import get_remote_address
from flask_limiter import Limiter
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask import Flask, send_from_directory, request, current_app
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
        # Global whitelist: exempt specific IPs or CIDRs via env RATE_LIMIT_WHITELIST
        # Examples: ["192.168.10.0/24", "127.0.0.1", "10.0.*"]
        try:
            from ipaddress import ip_address, ip_network
        except Exception:
            ip_address = ip_network = None  # type: ignore

        def _rate_limit_whitelist_filter() -> bool:
            try:
                addr_raw = request.headers.get('X-Forwarded-For', request.remote_addr)  # respect proxies if present
                if not addr_raw:
                    return False
                addr = str(addr_raw).split(',')[0].strip()
                wl = current_app.config.get('whitelist', []) or []
                for item in wl:
                    s = str(item).strip()
                    if not s:
                        continue
                    # Support wildcard suffix like 192.168.10.*
                    if s.endswith('.*'):
                        if addr.startswith(s[:-1]):
                            return True
                        continue
                    # Support CIDR ranges like 192.168.10.0/24
                    if '/' in s and ip_address and ip_network:
                        try:
                            if ip_address(addr) in ip_network(s, strict=False):
                                return True
                            continue
                        except Exception:
                            # fall through to exact compare
                            pass
                    # Exact IP match
                    if addr == s:
                        return True
                return False
            except Exception:
                return False
        try:
            limiter.request_filter(_rate_limit_whitelist_filter)  # type: ignore[attr-defined]
        except Exception:
            pass
        logger.info("Rate limiting enabled (whitelist size: %d)", len(app.config.get('whitelist', []) or []))

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
    
    # ─── Seed admin user (Root-Admin) ───
    try:
        if not _is_windows:
            app.ctrl.register_user(  # type: ignore
                app.config["WEB_USERNAME"],
                password_hash=app.config["WEB_PASSWORD"],
                is_admin=True,
                is_root_admin=True
            )
        else:
            app.ctrl.register_user(  # type: ignore
                app.config["WEB_USERNAME"],
                password=app.config["WEB_PASSWORD"],
                is_admin=True,
                is_root_admin=True
            )
        logger.info("Seeded admin user %s (is_admin=True, is_root_admin=True)",
                    app.config["WEB_USERNAME"])
    except ValueError:
        app.ctrl.set_user_as_admin(
            app.config["WEB_USERNAME"], True)  # type: ignore
        logger.info("Ensured %s has is_admin=True (existing)", app.config["WEB_USERNAME"])

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
    def _shutdown_tasks():
        """Run best-effort shutdown side effects outside hub mainloop.

        Avoid doing blocking work directly in the eventlet hub signal context.
        """
        try:
            app.ctrl.log_message("Server shutting down", "system")  # type: ignore
        except Exception as e:
            logging.getLogger(__name__).warning("Shutdown log_message failed: %s", e)
        try:
            socketio.emit('server_shutdown')
            socketio.stop()
        except Exception as e:
            logging.getLogger(__name__).warning("Shutdown emit failed: %s", e)

    def exit_signal(signum, frame):
        # Offload to a greenlet so we don't call blocking functions from the hub mainloop
        try:
            logging.getLogger(__name__).info("Caught exit signal %s", signum)
            eventlet.spawn_n(_shutdown_tasks)
        except Exception:
            # As a last resort, swallow errors to not interfere with Gunicorn shutdown
            pass
        # Let Gunicorn control worker shutdown; avoid calling socketio.stop() here
    signal.signal(signal.SIGTERM, exit_signal)
    signal.signal(signal.SIGINT, exit_signal)
    app.socketio = socketio  # type: ignore
    logger.info("Socket.IO ready (origins: %s)", allowed_ws_origins)
    
    ACCESS_ID = os.getenv("TUYA_ACCESS_ID")
    ACCESS_KEY = os.getenv("TUYA_ACCESS_KEY")
    API_ENDPOINT = os.getenv("TUYA_API_ENDPOINT")
    USERNAME = os.getenv("TUYA_USERNAME")
    PASSWORD = os.getenv("TUYA_PASSWORD")
    COUNTRY_CODE = os.getenv("TUYA_COUNTRY_CODE")
    SCHEMA = os.getenv("TUYA_SCHEMA")
    DEVICE_ID = os.getenv("TUYA_DEVICE_ID")
    
    from .ac_thermostat import ACThermostat
    from .ac_controller import ACController
    from tuya_iot import TuyaOpenAPI

    api = TuyaOpenAPI(API_ENDPOINT, ACCESS_ID, ACCESS_KEY)
    api.connect(USERNAME, PASSWORD, COUNTRY_CODE, SCHEMA)

    ac_controller = ACController(device_id=DEVICE_ID, api=api)
    # Read thermostat location for shared temp source (defaults to previous value)
    THERMOSTAT_LOCATION = os.getenv("THERMOSTAT_LOCATION", "Tietokonepöytä")
    # Simple notifier that emits socket events from the thermostat loop
    def _notify(event: str, payload: dict):
        """Notify only browser views via the SocketEventHandler helper."""
        try:
            # Import here to avoid circulars at module import time
            from .socket_handlers import SocketEventHandler
            handler = SocketEventHandler(socketio, app.ctrl)  # type: ignore
            handler.emit_to_views(event, payload)
        except Exception:
            # Fallback: best-effort broadcast if handler unavailable
            try:
                socketio.emit(event, payload)
            except Exception:
                pass


    # Load thermostat configuration from DB for runtime
    try:
        _conf = app.ctrl.get_thermostat_conf()  # type: ignore
    except Exception as e:
        _conf = None
        logger.warning("Failed to load thermostat configuration from DB: %s", e)

    if _conf is None:
        # Ensure thermostat config exists in DB (seed defaults if missing)
        try:
            logging.warning("Seeding default thermostat configuration in DB")
            _conf = app.ctrl.ensure_thermostat_conf_seeded_from(None)  # type: ignore
        except Exception:
            pass

    ac_thermostat = ACThermostat(
        ac=ac_controller,
        cfg=_conf,  # type: ignore
        ctrl=app.ctrl,  # type: ignore
        location=THERMOSTAT_LOCATION,
        notify=_notify,
    )
    # Expose thermostat on the app for API access
    app.ac_thermostat = ac_thermostat  # type: ignore
    ac_thread = threading.Thread(target=ac_thermostat.run_forever, daemon=True)
    ac_thread.start()
    logger.info("Tuya AC controller started for device %s", DEVICE_ID)
    
    from .hue_controller import HueController
    
    hue_bridge_ip = os.getenv("HUE_BRIDGE_IP")
    hue_username  = os.getenv("HUE_USERNAME")

    hue = HueController(hue_bridge_ip, hue_username)
    hue.start_time_based_routine(apply_immediately=False)

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

    # ─── Template asset registry (component self-contained CSS/JS) ───
    # Allows included templates to register their own assets and have them
    # automatically emitted in base.html without manual per-page wiring.
    from flask import g

    class _AssetRegistry:
        def __init__(self):
            self.styles = []  # list[str]
            self.scripts = []  # list[str]

        def style(self, href: str):
            try:
                if href and href not in self.styles:
                    self.styles.append(href)
            except Exception:
                pass
            return ""

        def script(self, src: str):
            try:
                if src and src not in self.scripts:
                    self.scripts.append(src)
            except Exception:
                pass
            return ""

    @app.context_processor
    def _inject_assets():
        if not hasattr(g, "_assets"):
            g._assets = _AssetRegistry()
        return {"assets": g._assets}

    return app, socketio
