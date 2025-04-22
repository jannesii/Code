# app/__init__.py
# Application factory setting up Flask, extensions, and blueprints
import json
from datetime import timedelta
from flask import Flask
from flask_login import LoginManager
from flask_socketio import SocketIO

from .controller import Controller
from .auth import auth_bp, login_manager as auth_login_manager
from .web import web_bp
from .api import api_bp
from .socket_handlers import SocketEventHandler


def create_app(config_path: str = 'config.json'):
    # Load configuration
    with open(config_path, 'r') as f:
        config = json.load(f)

    # Initialize Flask application
    app = Flask(__name__)
    app.config['SECRET_KEY'] = config.get('api_key')
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

    # Initialize domain controller
    db_path = config.get('db_path', 'app.db')
    ctrl = Controller(db_path)
    # make the controller available to blueprints via current_app.ctrl
    app.ctrl = ctrl

    # Initialize Flask-Login
    auth_login_manager.init_app(app)
    auth_login_manager.login_view = 'auth.login'

    # Initialize SocketIO
    socketio = SocketIO(
        app,
        cors_allowed_origins="*",
        max_http_buffer_size=10 * 1024 * 1024,
        ping_timeout=60,
        ping_interval=25
    )

    # Register Blueprints
    app.register_blueprint(auth_bp, url_prefix='')
    app.register_blueprint(web_bp, url_prefix='')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Attach SocketIO event handlers
    SocketEventHandler(socketio, ctrl)

    return app, socketio, ctrl

# End of app/__init__.py
