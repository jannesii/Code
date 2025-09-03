from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from typing import Tuple

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request, current_app


# ---------------------------
# Configuration & Logging
# ---------------------------

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("esp32_server")


# ---------------------------
# Datatypes
# ---------------------------

@dataclass
class BackendConfig:
    server: str
    username: str
    password: str


# ---------------------------
# Backend (CSRF) Session Setup
# ---------------------------

_CSRF_RE = re.compile(r'name="csrf_token"\s+value="([^"]+)"')

def _require_env() -> BackendConfig:
    """
    Load required configuration from environment variables and validate them.
    """
    # Load a system-wide .env file if present (override=True allows service env to win)
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
    """
    Perform a login dance to obtain a session (cookies) and CSRF token.
    Returns (session, csrf_token).
    """
    session = requests.Session()
    login_url = f"{cfg.server}/login"

    # 1) GET login page (sets cookies, contains CSRF)
    resp_get = session.get(login_url, timeout=timeout)
    if resp_get.status_code != 200:
        raise RuntimeError(f"GET {login_url} failed with status {resp_get.status_code}")

    token = _extract_csrf_token(resp_get.text)
    logger.debug("Obtained CSRF token")

    # 2) POST credentials + CSRF
    payload = {"username": cfg.username, "password": cfg.password, "csrf_token": token}
    headers = {"Referer": login_url}
    resp_post = session.post(login_url, data=payload, headers=headers, timeout=timeout)

    if resp_post.status_code != 200 or "Invalid credentials" in (resp_post.text or ""):
        raise RuntimeError("Login failed: invalid credentials or unexpected response")

    # 3) Default headers for subsequent JSON POSTs
    session.headers.update(
        {
            "X-CSRFToken": token,
            "X-CSRF-Token": token,
            "Referer": cfg.server,  # some CSRF setups check Referer origin
        }
    )

    logger.info("Authenticated to backend")
    return session, token


# ---------------------------
# Flask App Factory
# ---------------------------

def create_app() -> Flask:
    """
    Application factory (works well with gunicorn: `gunicorn server:app`).
    """
    app = Flask(__name__, template_folder="app/templates")

    # Load/validate env once at startup
    cfg = _require_env()
    app.config["BACKEND_CONFIG"] = cfg

    # Lazily created per worker so we can handle transient failures on boot
    app.config["REST_SESSION"] = None  # type: ignore[assignment]
    app.config["CSRF_TOKEN"] = None

    @app.get("/healthz")
    def healthz():
        ready = app.config.get("REST_SESSION") is not None
        status = 200 if ready else 503
        return jsonify({"ok": ready}), status

    @app.post("/temperature")
    def temperature():
        # Ensure session exists (retry once if needed)
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
        logger.info("Got reading: %s", data)  # e.g., {'temperature_c': 25.5, 'humidity_pct': 54.2}

        # Forward to backend API
        url = f"{current_app.config['BACKEND_CONFIG'].server}/api/temperature"
        try:
            resp = session.post(url, json=data, timeout=5.0)
            if resp.status_code != 200:
                logger.error("Failed to post temperature data: %s", getattr(resp, 'text', ''))
                return jsonify({"ok": False, "error": "upstream_error"}), 502
        except requests.RequestException as e:
            logger.error("Error posting to backend: %s", e)
            return jsonify({"ok": False, "error": "network_error"}), 502

        return jsonify({"ok": True}), 200

    return app


# Expose app for gunicorn: `gunicorn --bind 192.168.10.50:8080 server:app`
app = create_app()


if __name__ == "__main__":
    # Dev server only; use gunicorn in production.
    host = os.getenv("FLASK_RUN_HOST", "192.168.10.50")
    port = int(os.getenv("FLASK_RUN_PORT", "8080"))
    app.run(host=host, port=port, debug=True)
