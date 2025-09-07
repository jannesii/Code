# Updated script
#!/usr/bin/env bash
set -e
echo "[INFO] Pulling latest code..."
OUTPUT=$(git pull)
echo "[INFO] Git pull output:"
echo "$OUTPUT"

if echo "$OUTPUT" | grep -q "requirements.txt"; then
    echo "[INFO] requirements.txt changed. Setting up virtual environment and installing dependencies..."
    source ./.venv/bin/activate
    pip install -r requirements.txt
else
    echo "[INFO] No changes in requirements.txt. Skipping dependency installation."
fi

echo "[INFO] Restarting jannenkoti service..."
sudo systemctl restart jannenkoti

echo "[INFO] Tailing jannenkoti service logs..."
journalctl -u jannenkoti.service -f