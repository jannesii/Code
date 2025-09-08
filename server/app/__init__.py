import threading
import eventlet
eventlet.monkey_patch()
from .core.controller import Controller
from flask import Flask, send_from_directory, request, current_app
import pathlib
import tempfile
from datetime import timedelta
import os
import logging
import json
import signal

from .extensions import limiter, csrf, login_manager, socketio


def create_app():
    logger = logging.getLogger(__name__)
    logger.info("Starting application")
    logger.debug("Debug logging enabled")
    _is_windows = os.name == "nt"

    # ─── Flask app & config ───
    app = Flask(__name__)
    from .config import load_settings
    settings = load_settings(is_windows=_is_windows)
    app.config.update(settings)
    logger.info("Rate limit whitelist: %s", app.config.get('whitelist', []))
    
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
    csrf.init_app(app)
    logger.info("CSRF protection enabled (1 h token lifetime)")

    # ─── Domain-controller ───
    db_path = app.config.get("DB_PATH")
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
    login_manager.login_view = "auth.login"  # type: ignore
    login_manager.init_app(app)
    from .blueprints.auth.routes import load_user, AuthAnonymous, kick_if_expired
    app.before_request(kick_if_expired)
    login_manager.user_loader(load_user)
    login_manager.anonymous_user = AuthAnonymous
    logger.info("Login manager ready")

    # ─── Socket.IO ───
    allowed_ws_origins = app.config.get('ALLOWED_WS_ORIGINS', [])
    logger.info("Allowed WebSocket origins: %s", allowed_ws_origins)

    if not _is_windows:
        socketio.init_app(
            app,
            async_mode="eventlet",
            message_queue="redis://localhost:6379",
            cors_allowed_origins=allowed_ws_origins,
            max_http_buffer_size=10 * 1024 * 1024,
            ping_interval=10,
            ping_timeout=20,
        )
    else:
        socketio.init_app(
            app,
            async_mode="eventlet",
            cors_allowed_origins=allowed_ws_origins,
            max_http_buffer_size=10 * 1024 * 1024,
            ping_interval=10,
            ping_timeout=20,
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
    
    # ─── Services (AC thermostat, Hue, Socket events) ───
    from .services.bootstrap import init_services
    init_services(app)


    # ─── Blueprints ───
    from .blueprints import register_blueprints
    register_blueprints(app)

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
