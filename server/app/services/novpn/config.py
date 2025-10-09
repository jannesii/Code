import os
import re
from typing import List, Dict, Optional, Tuple
import subprocess
import logging

logger = logging.getLogger(__name__)

NOVPN_CONFIG_PATH = os.path.expanduser("~/.config/novpn/devices.conf")
_DEVICE_CMD = "/usr/local/bin/novpn-device.sh"


def _ensure_parent_dir(path: str) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)


def _parse_bool(val: str) -> bool:
    return str(val).strip().lower() in {"1", "true", "yes", "on"}


def _format_bool(val: bool) -> str:
    return "true" if bool(val) else "false"


def _parse_device_line(line: str) -> Optional[Dict[str, object]]:
    """Parse one device line; returns dict with name, mac, novpn, nodns or None.

    Expected format (free ordering of flags is tolerated):
      /usr/local/bin/novpn-device.sh -name "Foo" -mac aa:bb:... -novpn true -nodns false
    """
    if not line.strip() or line.lstrip().startswith('#'):
        return None
    if _DEVICE_CMD not in line:
        return None
    # Tokenize respecting quoted name
    tokens = re.findall(r'"[^\"]*"|\S+', line)
    if not tokens or tokens[0] != _DEVICE_CMD:
        return None

    name: Optional[str] = None
    mac: Optional[str] = None
    novpn: Optional[bool] = None
    nodns: Optional[bool] = None

    i = 1
    while i < len(tokens):
        tok = tokens[i]
        if tok == '-name' and i + 1 < len(tokens):
            val = tokens[i+1]
            name = val.strip('"')
            i += 2
        elif tok == '-mac' and i + 1 < len(tokens):
            mac = tokens[i+1]
            i += 2
        elif tok == '-novpn' and i + 1 < len(tokens):
            novpn = _parse_bool(tokens[i+1])
            i += 2
        elif tok == '-nodns' and i + 1 < len(tokens):
            nodns = _parse_bool(tokens[i+1])
            i += 2
        else:
            i += 1

    if not name or not mac:
        return None
    # Default missing flags to False
    return {
        'name': name,
        'mac': mac.lower(),
        'novpn': bool(novpn),
        'nodns': bool(nodns),
    }


def _restart_novpn_master() -> bool:
    """Restart the novpn-master service via systemctl.

    Returns True if restart succeeded, False otherwise.
    """
    try:
        cmd: List[str] = ["/usr/bin/systemctl", "restart", "novpn-master"]
        # Use sudo if not running as root
        if os.geteuid() != 0:
            cmd.insert(0, "/usr/bin/sudo")

        logger.debug("Restarting novpn-master: %s", " ".join(cmd))
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            timeout=float(os.getenv("NOVPN_RESTART_TIMEOUT_S", "10")),
        )
        if proc.returncode != 0:
            logger.warning(
                "Failed to restart novpn-master (returncode=%s): %s",
                proc.returncode,
                (proc.stderr or proc.stdout).strip(),
            )
            return False
        logger.info("Successfully restarted novpn-master.")
        return True
    except Exception as e:
        logger.warning("Exception while restarting novpn-master: %s", e)
        return False


def list_devices(path: str = NOVPN_CONFIG_PATH) -> List[Dict[str, object]]:
    """Return devices from config file; missing file yields empty list."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        return []
    devices: List[Dict[str, object]] = []
    for ln in lines:
        d = _parse_device_line(ln)
        if d:
            devices.append(d)
    return devices


def _rewrite_line_with(line: str, *, novpn: Optional[bool] = None, nodns: Optional[bool] = None) -> str:
    """Rewrite the -novpn/-nodns flags in a device line, preserving other parts."""
    def _replace_flag(s: str, flag: str, value: Optional[bool]) -> str:
        if value is None:
            return s
        pattern = re.compile(rf"({flag}\s+)(\S+)")
        if pattern.search(s):
            return pattern.sub(rf"\1{_format_bool(value)}", s)
        # If flag missing, append at end
        sep = '' if s.endswith('\n') else ''
        end_nl = '\n' if s.endswith('\n') else ''
        base = s[:-1] if end_nl else s
        return f"{base} {flag} {_format_bool(value)}{end_nl}"

    out = _replace_flag(line, '-novpn', novpn)
    out = _replace_flag(out, '-nodns', nodns)
    return out


def update_device_flags(mac: str, *, novpn: Optional[bool] = None, nodns: Optional[bool] = None,
                        path: str = NOVPN_CONFIG_PATH) -> Tuple[bool, Optional[Dict[str, object]]]:
    """Update -novpn/-nodns for the device (by MAC). Returns (ok, updated_device).

    Preserves comments and unrelated lines. Creates the file if missing.
    """
    mac_norm = mac.lower().strip()
    _ensure_parent_dir(path)

    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []

    found = False
    new_lines: List[str] = []
    for ln in lines:
        d = _parse_device_line(ln)
        if d and d.get('mac') == mac_norm:
            found = True
            ln = _rewrite_line_with(ln, novpn=novpn, nodns=nodns)
        new_lines.append(ln)

    if not found:
        return False, None

    tmp_path = f"{path}.tmp"
    with open(tmp_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    os.replace(tmp_path, path)

    # Restart novpn-master to apply changes
    if not _restart_novpn_master():
        logger.warning(
            "Warning: novpn-master restart failed after updating device flags.")

    # Return updated snapshot
    updated = None
    for ln in new_lines:
        d = _parse_device_line(ln)
        if d and d.get('mac') == mac_norm:
            updated = d
            break
    return True, updated
