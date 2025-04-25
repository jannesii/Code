# app/__init__.py

import json
import logging
import os
from datetime import timedelta

import eventlet

eventlet.monkey_patch()

from flask import Flask
from flask_socketio import SocketIO
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from .controller import Controller

# --- Rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],
    storage_uri="redis://localhost:6379",
    storage_options={"socket_connect_timeout": 30},
    strategy="moving-window",
)

def create_app():
    # --- Logging
    if os.getenv("FLASK_DEBUG"):
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger("werkzeug").setLevel(logging.DEBUG)
        logging.getLogger("flask_limiter").setLevel(logging.DEBUG)
        logging.getLogger("flask_socketio").setLevel(logging.DEBUG)
        logging.getLogger("eventlet").setLevel(logging.DEBUG)
        logging.getLogger("redis").setLevel(logging.DEBUG)
        logging.getLogger("socketio").setLevel(logging.DEBUG)
        logging.getLogger("flask").setLevel(logging.DEBUG)
        
    else: 
        logging.basicConfig(level=logging.INFO)
        
    logger = logging.getLogger(__name__)
    logger.info("Starting application")
    logger.debug("Debug logging enabled")
    
    # --- SECRET_KEY
    secret = os.getenv("SECRET_KEY")
    if not secret:
        raise RuntimeError("SECRET_KEY is missing – add to environment.")

    # --- Flask-app
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=secret,
        PERMANENT_SESSION_LIFETIME=timedelta(days=7),
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        WEB_USERNAME=os.getenv("WEB_USERNAME"),
        WEB_PASSWORD=os.getenv("WEB_PASSWORD"),
        WTF_CSRF_TIME_LIMIT=None,
    )
    
    # --- Rate limiting init
    limiter.init_app(app)
    logger.info("Rate limiting enabled")
    
    # --- CSRF
    csrf = CSRFProtect()
    csrf.init_app(app)
    logger.info("CSRF protection enabled")

    # --- Domain-controller
    db_path = os.getenv("DB_PATH")
    if not db_path:
        raise RuntimeError("DB_PATH is missing – add to environment.")
    app.ctrl = Controller(db_path)
    logger.info("Controller init: %s", db_path)

    # --- Seed admin
    try:
        app.ctrl.register_user(app.config["WEB_USERNAME"], password_hash=app.config["WEB_PASSWORD"])
        logger.info("Seeded admin user %s", app.config["WEB_USERNAME"])
    except ValueError:
        logger.info("Admin user already exists")

    # --- Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    from .auth import load_user
    login_manager.user_loader(load_user)
    logger.info("Login manager ready")

    # --- Socket.IO
    raw = os.getenv("ALLOWED_WS_ORIGINS")
    if raw:
        try:
            allowed_ws_origins = json.loads(raw)
        except json.JSONDecodeError:
            raise RuntimeError("ALLOWED_WS_ORIGINS ei ole validia JSON-listaa")
        
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
    app.socketio = socketio
    logger.info("Socket.IO ready (origins: %s)", allowed_ws_origins)

    # --- Blueprints
    from .auth import auth_bp
    from .web import web_bp
    from .api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp)

    # --- Socket-event handler
    from .socket_handlers import SocketEventHandler

    SocketEventHandler(socketio, app.ctrl)

    return app, socketio
