import os
import signal
import logging
from datetime import datetime

class SignalHandler:
    """
    Write our PID file and catch SIGUSR1.
    When received, emit a custom Socket.IO event (or do anything you like).
    """
    def __init__(self, socketio, pid_file: str = '/tmp/server.pid') -> None:
        self.socketio = socketio
        self.pid_file = pid_file
        self._write_pid()
        self._register()

    def _write_pid(self) -> None:
        pid = os.getpid()
        with open(self.pid_file, 'w') as f:
            f.write(str(pid))
        logging.info(f"SignalHandler: Wrote server PID {pid} to {self.pid_file}")

    def _register(self) -> None:
        signal.signal(signal.SIGUSR1, self._handle)
        logging.info("SignalHandler: Registered SIGUSR1 handler")

    def _handle(self, signum, frame) -> None:
        logging.info(f"{datetime.now()} SignalHandler: Caught signal {signum!r}")
        # Example action: broadcast to connected clients
        self.socketio.emit('server_signal', {'msg': 'SIGUSR1 received'})
