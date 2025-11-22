import logging
import threading
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class CarHeaterService:
    """
    In-memory command queue for the car heater ESP.

    Commands are queued by the web UI (or other callers) and consumed
    by the ESP when it POSTs status updates. The service maintains an
    internal thread for future background housekeeping but currently
    only manages the queue in a thread-safe manner.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._commands: List[Dict[str, Any]] = []
        self._stop_event = threading.Event()
        self._thread = threading.Thread(
            target=self._run, name="CarHeaterService", daemon=True
        )
        self._thread.start()
        logger.info("CarHeaterService thread started")

    def queue_command(self, command: Dict[str, Any]) -> None:
        """
        Queue a command to be sent to the ESP on the next status update.

        The command must be JSON-serializable (dict of simple types).
        """
        if not isinstance(command, dict):
            raise TypeError("command must be a dict")
        with self._lock:
            self._commands.append(command)
        logger.debug("Queued car heater command: %r", command)

    def get_queued_commands(self) -> List[Dict[str, Any]]:
        """
        Atomically return and clear all queued commands.

        Called from the car_heater status API to respond to the ESP.
        """
        with self._lock:
            if not self._commands:
                return []
            commands = list(self._commands)
            self._commands.clear()
        logger.debug("Returning %d queued car heater commands", len(commands))
        return commands

    def stop(self) -> None:
        """Signal the background thread to stop (best-effort)."""
        self._stop_event.set()

    def _run(self) -> None:
        """
        Background loop.

        Currently acts as a lightweight heartbeat to allow future
        housekeeping (e.g. expiring old commands). It sleeps most of
        the time to avoid unnecessary CPU usage.
        """
        try:
            while not self._stop_event.is_set():
                # Sleep with wake-up on stop_event for low CPU usage.
                self._stop_event.wait(timeout=60.0)
        except Exception:
            logger.exception("CarHeaterService thread crashed")


__all__ = ["CarHeaterService"]

