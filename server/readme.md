# Server – Flask + Socket.IO Backend & Website

Live dashboard, API and WebSocket gateway for your timelapse + home devices setup.
Runs on Linux (Raspberry Pi or any host) and exposes a password‑protected web UI,
JSON API and real‑time WebSocket stream for images, temperature/humidity, printer
status, and AC thermostat state.

---

## Features

- Web UI: Jinja templates (`index.html`, `3d.html`, `settings/*.html`).
- Auth: Local users in SQLite with Flask‑Login (Root‑Admin is seeded on first run).
- Realtime: Flask‑SocketIO (Eventlet) for live updates (images, sensors, printer, AC).
- REST API: Temperature/humidity, configs, AC metrics, G‑code queue.
- Database: SQLite auto‑migrated; controller layer isolates logic.
- Integrations:
  - Tuya/Smart Life AC via OpenAPI with local thermostat loop and sleep schedule.
  - Philips Hue time‑based light routine (optional).

---

## Directory Layout

```text
server/
├── app/
│   ├── __init__.py          # create_app(); config; extension init; registers blueprints
│   ├── extensions.py        # Limiter, CSRF, LoginManager, SocketIO singletons
│   ├── config.py            # Centralized environment settings
│   ├── security.py          # Rate limiting setup + whitelist filter
│   ├── assets.py            # Template asset registry helper
│   ├── blueprints/          # Flask blueprints grouped by area
│   │   ├── __init__.py      # register_blueprints(app)
│   │   ├── auth/            # login/logout, user loader, rate‑limit handler
│   │   ├── web/             # protected HTML routes
│   │   └── api/             # JSON API routes
│   ├── sockets/
│   │   └── handlers.py      # Socket.IO event handlers (views/clients/esp32)
│   ├── services/
│   │   ├── bootstrap.py     # Initializes AC thermostat, Hue routine, socket events
│   │   ├── ac/              # Tuya AC controller and thermostat loop
│   │   ├── hue/             # Hue controller and time‑based routine
│   │   └── presence/        # Presence watcher
│   ├── core/
│   │   ├── controller.py    # Business logic + DB gateway
│   │   ├── database.py      # Thread‑safe SQLite wrapper
│   │   └── models.py        # Dataclass DTOs and config models
│   ├── utils.py             # Web helpers, flashes, validation
│   ├── static/              # CSS & JS assets
│   └── templates/           # Jinja2 templates
├── run.py                   # Development entry‑point (debug server)
├── requirements.txt         # Python deps
└── readme.md                # ← you are here
```

---

## Requirements

- Python 3.11+
- Eventlet
- Redis (for Flask‑Limiter storage and Socket.IO message queue)

Install deps:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

All settings are read from environment variables (see `app/config.py`).

Minimum viable dev setup:

```bash
export SECRET_KEY="$(openssl rand -hex 32)"
export WEB_USERNAME=admin
export WEB_PASSWORD=change-me
export ALLOWED_WS_ORIGINS='["http://127.0.0.1:5555"]'
# required: path to the SQLite database file
# recommended for dev:
export DB_PATH="/tmp/timelapse.db"
# optional: rate-limit whitelist as JSON list
export RATE_LIMIT_WHITELIST='["127.0.0.1","192.168.10.0/24"]'
```

Optional integrations (auto‑skipped if unset):

- Tuya AC (cloud): `TUYA_ACCESS_ID`, `TUYA_ACCESS_KEY`, `TUYA_API_ENDPOINT`,
  `TUYA_USERNAME`, `TUYA_PASSWORD`, `TUYA_COUNTRY_CODE`, `TUYA_SCHEMA`, `TUYA_DEVICE_ID`
- Hue: `HUE_BRIDGE_IP`, `HUE_USERNAME`
- Thermostat tuning: `THERMOSTAT_LOCATION` (default `Tietokonepöytä`),
  `ROOM_THERMAL_CAPACITY_J_PER_K` (for power estimation)
- Limiter backend: `RATE_LIMIT_STORAGE_URI` (default `redis://localhost:6379`)

## Quick Start (development)

```bash
source .venv/bin/activate
export SECRET_KEY=dev
export WEB_USERNAME=admin WEB_PASSWORD=admin
export DB_PATH=/tmp/timelapse.db
python run.py
```

Browse http://127.0.0.1:5555 and log in with the credentials above. The first
admin user is created automatically on startup.

Note: the app sets session cookies with the Secure flag. Some browsers may not
send Secure cookies over plain HTTP on localhost, which can affect login during
local testing. Running behind TLS (e.g., via Nginx) avoids this.

---

## Production deployment

### 1 / Gunicorn service
Create `/etc/systemd/system/jannenkoti.service`:

```ini
[Unit]
Description=Bambu timelapse web server
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/Code/server
Environment=PYTHONUNBUFFERED=1
ExecStart=/home/pi/Code/server/.venv/bin/gunicorn \
          --worker-class eventlet \
          --workers 1 \
          --bind 127.0.0.1:5555 \
          --access-logfile - \
          --error-logfile - \
          run:app
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now jannenkoti
```

### 2 / Nginx reverse‑proxy with HTTPS

```nginx
server {
    listen 80;
    server_name jannenkoti.com www.jannenkoti.com;

    location /.well-known/acme-challenge/ {
        root /var/www/letsencrypt;
    }

    location / {
        proxy_pass              http://127.0.0.1:5555;
        proxy_set_header Host   $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_http_version      1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Run **Certbot** once, then replace port 80 listener with the `listen 443 ssl;` block Certbot inserts.

### 3 / Cloudflare Tunnel (no port‑forwarding!)
Install `cloudflared` and create `~/.cloudflared/config.yml`:

```yaml
tunnel: d5768148‑your‑uuid
credentials-file: /home/pi/.cloudflared/d5768148.json

ingress:
  - hostname: jannenkoti.com
    service: http://localhost:5555
  - hostname: www.jannenkoti.com
    service: http://localhost:5555
  - service: http_status:404
```

Enable the service:
```bash
sudo systemctl enable --now cloudflared
```

### End‑to‑End Flow

```
Browser → Cloudflare edge → cloudflared tunnel → Nginx (TLS offload) → Gunicorn → Flask / Socket.IO
```
All WebSocket upgrades (`Connection: Upgrade`) are passed straight through, so live images and data stream without polling.

---

## HTTP API

Examples (all routes require login):

- `GET /api/temphum?date=YYYY-MM-DD` — Raspberry Pi sensor readings
- `GET /api/esp32_temphum?date=YYYY-MM-DD&location=<name>` — ESP32 readings
- `GET /api/timelapse_config` — current timelapse config
- `GET /api/gcode` — queued/submitted G‑code commands
- `GET /api/previewJpg` — serves `/tmp/preview.jpg`
- `GET /api/ac/status` — current AC status (if thermostat initialized)
- `GET /api/hvac/avg_rates_today` — cooling/heating rates from today (°C/h and W)

Other endpoints:

- `GET /live/<path:filename>` — serves HLS assets from `/srv/hls` (printer streams)

## Socket.IO Events (client ↔ server)

Core channel types:

- To server
  - `image`: `{ image: <base64 str> }`
  - `esp32_temphum`: `{ location: str, temperature_c: float, humidity_pct: float }`
  - `status`: `{ status: str }`
  - `printerAction`: `{ action: 'pause'|'resume'|'stop'|'home'|'timelapse_start'|'timelapse_stop'|'run_gcode', ... }`
  - `ac_control`: `{ action: 'power_on'|'power_off'|'thermostat_enable'|'thermostat_disable'|'set_mode'|'set_fan_speed'|'set_setpoint'|'set_hysteresis'|'set_hysteresis_split'|'set_sleep_enabled'|'set_sleep_times'|'status', ... }`

- To browser views
  - `image`: notify new frame available
  - `esp32_temphum`: `{ location, temperature, humidity, ac_on }`
  - `status`: `{ status }`
  - `ac_status`, `thermostat_status`, `ac_state`, `sleep_status`, `thermo_config`
  - `timelapse_conf`: updated config
  - `flash`: `{ category, message }`

---

## Database (auto‑migrated)

SQLite file path is controlled by `DB_PATH` (set this; recommended `/opt/<db-name>.db`). Tables include:

- `users` — accounts (admin/root‑admin flags; temporary expiry)
- `temphum` — Pi temperature/humidity
- `esp32_temphum` — ESP32 temperature/humidity with `location` and `ac_on`
- `status` — free‑form status messages
- `images` — last frames (pruned)
- `timelapse_conf` — capture intervals
- `thermostat_conf` — thermostat settings and phase tracking
- `ac_events` — AC on/off transitions for analytics

---

## Maintaining & troubleshooting

```bash
# tail live logs
journalctl -u jannenkoti -f

# open interactive Python shell with app context
python - <<'PY'
from app import create_app
app, socketio = create_app()
ctx = app.app_context(); ctx.push()
# then play with app.ctrl ...
print(app.ctrl.get_all_users())
PY
```

*Questions, bugs or ideas?* Open an issue or ping **@Jannnesi**.

---

© 2025 Janne Siirtola.  Licensed under the MIT License.
