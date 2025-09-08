import subprocess
import threading
import time


class PresenceWatcher:
    """
    Periodically pings an IP in a background thread and updates a single public
    variable: `im_home` (True if ping succeeds, False otherwise).
    """

    def __init__(self, ip: str = "192.168.10.128", interval_seconds: float = 10.0, timeout_ms: int = 1000):
        """
        :param ip: The device IP to ping (your phone).
        :param interval_seconds: How often to ping.
        :param timeout_ms: Per-ping timeout in milliseconds.
        """
        self.im_home: bool = False  # <-- the single public state variable

        self._ip = ip
        self._interval = float(interval_seconds)
        self._timeout_ms = int(timeout_ms)
        self._stop_evt = threading.Event()
        self._thread: threading.Thread | None = None

    def _ping_once(self) -> bool:
        """
        Returns True if the ping command reports success, False otherwise.
        Handles Windows vs. Unix ping flags and uses a short timeout.
        """
        timeout_seconds = max(1, round(self._timeout_ms / 1000))
        cmd = ["ping", "-c", "1", "-W", str(timeout_seconds), self._ip]

        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
            return result.returncode == 0
        except Exception:
            return False

    def _loop(self):
        # Initial check right away
        self.im_home = self._ping_once()

        # Then poll on the requested interval
        while not self._stop_evt.wait(self._interval):
            self.im_home = self._ping_once()

    def start(self):
        """Start the background watcher thread (idempotent)."""
        if self._thread and self._thread.is_alive():
            return
        self._stop_evt.clear()
        self._thread = threading.Thread(target=self._loop, name="PresenceWatcher", daemon=True)
        self._thread.start()

    def stop(self, wait: bool = False):
        """Stop the background watcher thread."""
        self._stop_evt.set()
        if wait and self._thread:
            self._thread.join()


# --- Example usage ---
if __name__ == "__main__":
    watcher = PresenceWatcher(ip="192.168.10.128", interval_seconds=5, timeout_ms=1000)
    watcher.start()
    try:
        # Demo: print state every 5 seconds
        while True:
            print("im_home:", watcher.im_home)
            time.sleep(5)
    except KeyboardInterrupt:
        watcher.stop(wait=True)
