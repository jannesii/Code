# Updated script
#!/usr/bin/env bash
set -e

echo "[INFO] Restarting esp32_server service..."
sudo systemctl restart esp32_server

echo "[INFO] Tailing esp32_server service logs..."
journalctl -u esp32_server.service -f
