# app/__init__.py
import json
import logging
from datetime import timedelta
from flask import Flask
from flask_socketio import SocketIO
from flask_login import LoginManager
from .controller import Controller

def create_app(config_path: str):
    # — Initialize logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logging.getLogger('engineio.server').setLevel(logging.INFO)
    logger.info("Starting application")

    # — Load config
    with open(config_path, 'r') as f:
        cfg = json.load(f)

    # — Flask app
    app = Flask(__name__)
    app.config['SECRET_KEY'] = cfg.get('secret_key', 'replace-with-a-secure-random-key')
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
    app.config['API_KEY'] = cfg['api_key']
    app.config['WEB_USERNAME'] = cfg['web_username']
    app.config['WEB_PASSWORD'] = cfg['web_password']

    # — Domain controller
    db_path = cfg.get('database_uri', 'app.db')
    app.ctrl = Controller(db_path)
    logger.info("Controller initialized with DB %s", db_path)

    # — Seed admin user
    try:
        app.ctrl.register_user(app.config['WEB_USERNAME'], app.config['WEB_PASSWORD'])
        logger.info("Seeded admin user %s", app.config['WEB_USERNAME'])
    except ValueError:
        logger.info("Admin user already exists")

    # — Flask‑Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    from .auth import load_user
    login_manager.user_loader(load_user)
    logger.info("Login manager configured")

    # — SocketIO
    socketio = SocketIO(
        app,
        async_mode='eventlet',
        message_queue='redis://localhost:6379',
        cors_allowed_origins="*",
        max_http_buffer_size=10 * 1024 * 1024,
        ping_timeout=60,
        ping_interval=25
    )
    app.socketio = socketio
    logger.info("SocketIO initialized")

    # — Register blueprints
    from .auth import auth_bp
    from .web import web_bp
    from .api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp)
    logger.info("Blueprints registered")

    # — Socket event handlers
    from .socket_handlers import SocketEventHandler
    SocketEventHandler(socketio, app.ctrl)
    logger.info("Socket handlers set up")

    return app, socketio
