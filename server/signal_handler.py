import os
import tempfile
import signal
import logging
# Choose a “user” signal that is present on both platforms
if os.name == "nt":              # Windows
    USER_SIGNAL = signal.SIGBREAK      # handled with Ctrl+Break
    USER_KILL = signal.CTRL_BREAK_EVENT  # value to pass to os.kill
else:                             # Linux / macOS
    USER_SIGNAL = signal.SIGUSR1
    USER_KILL = USER_SIGNAL

logger = logging.getLogger(__name__)


class SignalHandler:
    def __init__(self, socketio) -> None:
        self.socketio = socketio
        self.pid_file = os.path.join(
            tempfile.gettempdir(), "server.pid"
        )
        self._write_pid()
        self._register()

    def _write_pid(self):
        pid = os.getpid()
        with open(self.pid_file, "w") as f:
            f.write(str(pid))
        logger.info("PID %s written to %s", pid, self.pid_file)

    def _register(self):
        signal.signal(USER_SIGNAL, self._handle)   # <— works on both OSes
        logger.info("Registered handler for %s", USER_SIGNAL.name)

    def _handle(self, signum, frame):
        logger.info("Caught %s, scheduling emit", signum)
        self.socketio.start_background_task(self._emit_server_signal)

    def _emit_server_signal(self):
        try:
            self.socketio.emit("image")
            logger.debug("'image' event emitted")
        except Exception as exc:
            logger.exception("Emit failed: %s", exc)
