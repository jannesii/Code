Flask + Socket.IO Application Setup and Traffic Flow  

1. Application and Service  
   • The Flask + Socket.IO app is defined in `run.py`, exposing both REST endpoints and WebSocket handlers.  
   • It is served by Gunicorn using the Eventlet worker class.  
   • Gunicorn listens on 127.0.0.1:5555.  
   • Managed by systemd as `jannenkoti.service`, running under user `jannesi`, with automatic restarts on failure.  

2. Local Reverse Proxy (Nginx)  
   • Nginx listens on all LAN interfaces (0.0.0.0) on ports 80 and 443.  
   • HTTP (port 80) and HTTPS (port 443) are both accepted.  
   • TLS termination via Let’s Encrypt certificates (managed by Certbot).  
   • ACME challenge served from `/var/www/letsencrypt/.well-known/acme-challenge/`.  
   • All `/` requests (including WebSocket Upgrade) are forwarded to `http://127.0.0.1:5555`.  

3. Encrypted Tunnel (Cloudflare Tunnel / cloudflared)  
   • Named tunnel (`d5768148-…`) configured in `~/.cloudflared/config.yml`.  
   • Runs as systemd service (`cloudflared.service`), outbound to Cloudflare’s edge.  
   • Maps hostnames `jannenkoti.com` and `www.jannenkoti.com` → `http://localhost:5555`.  

4. DNS Configuration (Cloudflare)  
   • Authoritative DNS for `jannenkoti.com` at Cloudflare.  
   • Both `jannenkoti.com` and `www.jannenkoti.com` are CNAMEs to the Tunnel’s `*.cfargotunnel.com`.  
   • No home‑network port‑forwarding required.  

5. End‑to‑End Request Flow  
   1. Client resolves `jannenkoti.com` → Cloudflare edge.  
   2. Cloudflare tunnels to Pi via `cloudflared`.  
   3. `cloudflared` proxies to Nginx (127.0.0.1:5555).  
   4. Nginx terminates TLS and proxies to Gunicorn (127.0.0.1:5555).  
   5. Gunicorn dispatches to Flask + Socket.IO app.  
   6. Responses and WebSocket messages traverse the path in reverse.  

6. Code Structure  
   • `run.py`  
     – Entrypoint: loads config, invokes `create_app()`, starts Socket.IO.  
   • `config.json`  
     – Holds `api_key`, `web_username`/`web_password`, `database_uri`.  
   • `app/` (Python package)  
     - `__init__.py`  
       · `create_app()`: sets up Flask, Socket.IO, Flask‑Login, Controller, Blueprints, Socket handlers.  
     - `database.py`  
       · `DatabaseManager` singleton: initializes SQLite connection, creates tables/triggers. citeturn1file0  
     - `controller.py`  
       · `Controller`: business logic, wraps `DatabaseManager`, handles users, temphum, status, images, timelapse conf. citeturn1file1  
     - `auth.py`  
       · Auth Blueprint: `AuthUser`, login/logout routes, user loader.  
     - `web.py`  
       · Web Blueprint: protected UI routes (`/`, `/3d`, `/settings/*`).  
     - `api.py`  
       · API Blueprint (`/api/temphum`): JSON data endpoints.  
     - `socket_handlers.py`  
       · `SocketEventHandler`: groups Socket.IO event handlers (`connect`, `image`, `temphum`, `status`).  
     - `templates/`  
       · Jinja2 templates: `index.html`, `login.html`, `3d.html`, `settings.html`, `add_user.html`, `delete_user.html`, `timelapse_conf.html`.  
   • Top‑level `static/`  
     – CSS and JS assets served at `/static/`.  
   • `models.py`  
     – Data classes: `User`, `TemperatureHumidity`, `Status`, `ImageData`, `TimelapseConf`.  
   • `app.db`  
     – SQLite database file used by `DatabaseManager`.  

— End of overview —