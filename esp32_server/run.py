from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from typing import Tuple

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request, current_app
import socketio
from socketio.exceptions import BadNamespaceError

# ---------------------------
# Configuration & Logging
# ---------------------------

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("esp32_server")
logging.getLogger("socketio.client").setLevel(logging.WARNING)

# Socket.IO namespace (set to e.g. "/esp32" if your backend uses a custom ns)
SIO_NAMESPACE = os.getenv("SIO_NAMESPACE", "/")

# ---------------------------
# Datatypes
# ---------------------------

@dataclass
class BackendConfig:
    server: str
    username: str
    password: str

def on_connect() -> None:
    logger.info("connected to server namespace %s", SIO_NAMESPACE)

def on_disconnect() -> None:
    logger.info("disconnected from server namespace %s", SIO_NAMESPACE)

def on_error(data: dict) -> None:
    logger.error("server error: %s", data)

def on_server_shutdown() -> None:
    logger.info("server is shutting down")
    sio.disconnect()

def connect() -> None:
    """Optional: place background loops or one-time connect logic here."""
    pass

sio = socketio.Client(logger=True, reconnection=True)
sio.on('connect',    on_connect,    namespace=SIO_NAMESPACE)
sio.on('disconnect', on_disconnect, namespace=SIO_NAMESPACE)
sio.on('error',      on_error,      namespace=SIO_NAMESPACE)
sio.on('server_shutdown', on_server_shutdown, namespace=SIO_NAMESPACE)

# ---------------------------
# Backend (CSRF) Session Setup
# ---------------------------

_CSRF_RE = re.compile(r'name="csrf_token"\s+value="([^"]+)"')

def _require_env() -> BackendConfig:
    load_dotenv("/etc/esp32_server.env", override=True)
    server = os.getenv("SERVER", "").rstrip("/")
    username = os.getenv("USERNAME", "")
    password = os.getenv("PASSWORD", "")
    if not server or not username or not password:
        missing = [k for k, v in {"SERVER": server, "USERNAME": username, "PASSWORD": password}.items() if not v]
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")
    return BackendConfig(server=server, username=username, password=password)

def _extract_csrf_token(html: str) -> str:
    m = _CSRF_RE.search(html or "")
    if not m:
        raise RuntimeError("CSRF token not found on login page")
    return m.group(1)

def _authenticate_session(cfg: BackendConfig, timeout: float = 5.0) -> Tuple[requests.Session, str]:
    session = requests.Session()
    login_url = f"{cfg.server}/login"
    resp_get = session.get(login_url, timeout=timeout)
    if resp_get.status_code != 200:
        raise RuntimeError(f"GET {login_url} failed with status {resp_get.status_code}")
    token = _extract_csrf_token(resp_get.text)
    payload = {"username": cfg.username, "password": cfg.password, "csrf_token": token}
    headers = {"Referer": login_url}
    resp_post = session.post(login_url, data=payload, headers=headers, timeout=timeout)
    if resp_post.status_code != 200 or "Invalid credentials" in (resp_post.text or ""):
        raise RuntimeError("Login failed: invalid credentials or unexpected response")
    session.headers.update(
        {
            "X-CSRFToken": token,
            "X-CSRF-Token": token,
            "Referer": cfg.server,
        }
    )
    logger.info("Authenticated to backend")
    return session, token

def _cookies_header(session: requests.Session) -> dict[str, str]:
    cookie_str = "; ".join(f"{k}={v}" for k, v in session.cookies.get_dict().items())
    return {"Cookie": cookie_str} if cookie_str else {}

def _ensure_sio_connected(cfg: BackendConfig, session: requests.Session, namespace: str = SIO_NAMESPACE) -> None:
    """
    Make sure the global `sio` client is connected to the desired namespace.
    Reconnects with session cookies if needed.
    """
    # Already connected to this namespace?
    try:
        if sio.connected and sio.get_sid(namespace=namespace):
            return
    except Exception:
        # Fall through to reconnect
        pass

    # (Re)connect synchronously and only to the desired namespace
    sio.connect(
        cfg.server,
        headers=_cookies_header(session),
        transports=["websocket", "polling"],
        namespaces=[namespace],
        wait=True,   # block until connected
    )
    logger.info("Socket.IO connected to %s (namespace %s)", cfg.server, namespace)

# ---------------------------
# Flask App Factory
# ---------------------------

def create_app() -> Flask:
    app = Flask(__name__, template_folder="app/templates")

    cfg = _require_env()
    app.config["BACKEND_CONFIG"] = cfg
    app.config["REST_SESSION"] = None  # type: ignore[assignment]
    app.config["CSRF_TOKEN"] = None

    @app.get("/healthz")
    def healthz():
        ready = app.config.get("REST_SESSION") is not None and sio.connected
        status = 200 if ready else 503
        return jsonify({"ok": ready}), status

    @app.post("/temperature")
    def temperature():
        session = current_app.config.get("REST_SESSION")
        if session is None:
            try:
                session, token = _authenticate_session(current_app.config["BACKEND_CONFIG"])
                current_app.config["REST_SESSION"] = session
                current_app.config["CSRF_TOKEN"] = token
            except Exception as e:
                logger.error("Backend not ready: %s", e)
                return jsonify({"ok": False, "error": "backend_unavailable"}), 503

        data = request.get_json(force=True, silent=True) or {}
        logger.info("Got reading: %s", data)

        try:
            _ensure_sio_connected(current_app.config["BACKEND_CONFIG"], session, namespace=SIO_NAMESPACE)
            sio.emit('esp32_temphum', data, namespace=SIO_NAMESPACE)
        except BadNamespaceError:
            # One forced reconnect attempt
            logger.warning("Namespace %s not connected; reconnecting once...", SIO_NAMESPACE)
            try:
                sio.disconnect()
            except Exception:
                pass
            try:
                _ensure_sio_connected(current_app.config["BACKEND_CONFIG"], session, namespace=SIO_NAMESPACE)
                sio.emit('esp32_temphum', data, namespace=SIO_NAMESPACE)
            except Exception as e:
                logger.error("Emit failed after reconnect: %s", e)
                return jsonify({"ok": False, "error": "socket_disconnected"}), 503
        except Exception as e:
            logger.error("Socket.IO emit error: %s", e)
            return jsonify({"ok": False, "error": "socket_error"}), 502

        return jsonify({"ok": True}), 200

    return app

app = create_app()

if __name__ == "__main__":
    host = os.getenv("FLASK_RUN_HOST", "192.168.10.50")
    port = int(os.getenv("FLASK_RUN_PORT", "8080"))
    app.run(host=host, port=port, debug=True)
