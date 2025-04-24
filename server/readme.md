# Server – Flask + Socket.IO Backend & Website

> **Live dashboard, API & WebSocket gateway for your Bambu Lab A1 timelapse system**
>
> Runs on a Raspberry Pi (or any Linux host) and exposes a password‑protected web UI, JSON API and real‑time WebSocket stream for images, temperature/humidity and printer status.
>
> It is designed to sit behind an Nginx reverse‑proxy and reach the public Internet through a Cloudflare Tunnel – no port forwarding required.

---

## Features

| Category | Details |
|----------|---------|
| **Web UI** | Jinja‑templates served by Flask (`index.html`, `3d.html`, `settings/*.html`) with a minimal Bootstrap‑like style. |
| **Auth** | Local user accounts stored in SQLite. Login handled by Flask‑Login. |
| **Realtime** | WebSocket channel powered by Flask‑SocketIO (Eventlet). Emits `image2v`, `temphum2v`, `status2v` events to all connected browsers. |
| **REST API** | `GET /api/temphum?date=YYYY‑MM‑DD` – full day of sensor readings.<br>`GET /api/timelapse_config` – current image / sensor intervals. |
| **Database** | Single SQLite file `app.db` auto‑created on first run. Trigger keeps only the **10 newest images** to save disk space. |
| **Extensible** | Controller layer cleanly separates business logic from Flask; easy to swap to PostgreSQL or add new endpoints. |

---

## Directory layout

```text
server/
├── app/
│   ├── __init__.py        # create_app(), Socket.IO, blueprints
│   ├── auth.py            # Login / logout routes & user loader
│   ├── web.py             # Protected HTML pages
│   ├── utils.py           # Helper functions
│   ├── api.py             # JSON endpoints
│   ├── socket_handlers.py # WebSocket event handlers
│   ├── controller.py      # All business logic (DB wrapper)
│   ├── database.py        # Thread‑safe SQLite singleton
│   ├── static/            # CSS & JS assets
│   └── templates/         # Jinja2 templates
├── models.py              # dataclass DTOs shared by controller
├── run.py                 # Development entry‑point (debug server)
├── requirements.txt       # Python deps
└── readme.md              # ← you are here
```

---

## Quick start (development)

```bash
# 1. Clone just the server folder or the whole repo
$ git clone https://github.com/Jannnesi/Code.git && cd Code/server

# 2. Python ≥3.11 recommended
$ python -m venv .venv && source .venv/bin/activate
$ pip install -r requirements.txt

# 3. Create a minimal config.json
$ cat > config.json <<'EOF'
{
  "web_username": "admin",
  "web_password": "change‑me",
  "secret_key": "$(openssl rand -hex 32)",
  "database_uri": "app.db"
}
EOF

# 4. Kick it off (development mode, port 5555)
$ python run.py
```
Browse to **http://localhost:5555** and log in with the credentials above.

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

### End‑to‑end flow

```
Browser → Cloudflare edge → cloudflared tunnel → Nginx (TLS offload) → Gunicorn → Flask / Socket.IO
```
All WebSocket upgrades (`Connection: Upgrade`) are passed straight through, so live images and data stream without polling.

---

## Socket.IO events (client ↔ server)

| Event (→ server) | Payload | Description |
|------------------|---------|-------------|
| `image`          | `{ image: <base64 str> }`      | Push single JPEG/PNG frame from timelapse client |
| `temphum`        | `{ temperature: float, humidity: float }` | Sensor reading |
| `status`         | `{ status: str }`              | Free‑form printer status string |

| Event (← server) | Payload |
|------------------|---------|
| `image2v`        | Same `{ image }`; broadcast to all browsers |
| `temphum2v`      | Same `{ temperature, humidity }` |
| `status2v`       | Same `{ status }` |

---

## Database schema (auto‑migrated)

```sql
-- users
id·INT PK, username·TEXT UNIQUE, password_hash·TEXT
-- temphum
id, timestamp TEXT, temperature REAL, humidity REAL
-- status
id, timestamp TEXT, status TEXT
-- images (last 10 rows kept by trigger)
id, timestamp TEXT, image TEXT (base64)
-- timelapse_conf
id = 1, image_delay INT, temphum_delay INT, status_delay INT
```

---

## Maintaining & troubleshooting

```bash
# tail live logs
journalctl -u jannenkoti -f

# open interactive Python shell with app context
python - <<'PY'
from app import create_app
app, _ = create_app('config.json')
ctx = app.app_context(); ctx.push()  # then play with app.ctrl ...
PY
```

*Questions, bugs or ideas?* Open an issue or ping **@Jannnesi**.

---

© 2025 Janne Siirtola.  Licensed under the MIT License.

