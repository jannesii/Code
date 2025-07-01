import json
import os
import time
import paramiko
from pathlib import Path

# ─── Load configuration ────────────────────────────────────────────────
with open("client/config.json", "r") as f:
    cfg = json.load(f)

HOST          = cfg["raspi_host"]
PORT          = cfg.get("raspi_port", 22)
USERNAME      = cfg["username"]

# Path to your private key (absolute or ~ expanded)
KEY_PATH      = Path(cfg.get("private_key_path", "~/.ssh/pi_key")).expanduser()
KEY_PASSPHRASE= cfg.get("private_key_passphrase")  # None if key is un‑encrypted

REMOTE_FOLDERS= cfg["remote_folders"]
POLL_INTERVAL = cfg.get("poll_interval", 10)       # seconds

# ─── Helper ────────────────────────────────────────────────────────────
def ensure_local_dir(remote_folder: str) -> Path:
    """
    Creates a matching local sub‑directory (basename of the parent folder)
    and returns the absolute path.
      e.g. "/home/pi/gcodes/out/" ➜ "./gcodes"
    """
    local_dir = Path.cwd() / Path(remote_folder).parent.name
    local_dir.mkdir(exist_ok=True)
    return local_dir

# ─── Main transfer routine ─────────────────────────────────────────────
def transfer_files():
    # Key‑based login
    pkey = paramiko.Ed25519Key.from_private_key_file(KEY_PATH)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(HOST, port=PORT, username=USERNAME, pkey=pkey)
        with ssh.open_sftp() as sftp:
            for remote_folder in REMOTE_FOLDERS:
                try:
                    remote_files = sftp.listdir(remote_folder)
                except FileNotFoundError:
                    print(f"⚠️  Remote folder not found: {remote_folder}")
                    continue

                if not remote_files:
                    print(f"📂 {remote_folder}: no files.")
                    continue

                local_dir = ensure_local_dir(remote_folder)

                for fname in remote_files:
                    r_path = f"{remote_folder}/{fname}"
                    l_path = local_dir / fname
                    print(f"⬇️  Downloading {r_path} → {l_path}")
                    sftp.get(r_path, str(l_path))
                    print("✅  Transfer complete; deleting remote copy…")
                    sftp.remove(r_path)
    except Exception as exc:
        print("❗ Error:", exc)
    finally:
        ssh.close()

# ─── Poll loop ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    while True:
        transfer_files()
        time.sleep(POLL_INTERVAL)
