import os
import signal
import logging

class SignalHandler:
    """
    Write our PID file and catch SIGUSR1.
    When received, schedule a background task to emit the Socket.IO event.
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
        logging.info(f"SignalHandler: Caught signal {signum!r}, scheduling emit")
        # Schedule the actual emit in a background greenlet
        self.socketio.start_background_task(self._emit_server_signal)

    def _emit_server_signal(self) -> None:
        """
        Runs in its own greenlet, so blocking Redis publish is safe.
        """
        try:
            logging.debug("SignalHandler: Emitting 'server_signal' event")
            self.socketio.emit('server_signal', {'msg': 'SIGUSR1 received'})
            logging.info("SignalHandler: 'server_signal' emitted successfully")
        except Exception as e:
            logging.error(f"SignalHandler: Error emitting signal: {e}")
