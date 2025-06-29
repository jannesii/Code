#!/usr/bin/env python3
import time
import logging
import threading
from typing import Callable, Dict, Optional

from gpiozero import Button
logger = logging.getLogger(__name__)

class ButtonHandler:
    """Counts GPIO button presses within a timeout and dispatches callbacks."""

    def __init__(
        self,
        button: Button,
        timeout: float,
        callbacks: Dict[int, Callable[[], None]],
        logger: logging.Logger
    ) -> None:
        """
        button: gpiozero.Button instance
        timeout: max seconds between presses for a sequence
        callbacks: map of press-count to function
        """
        self.button = button
        self.timeout = timeout
        self.callbacks = callbacks
        self.count = 0
        self.timer: Optional[threading.Timer] = None
        self.last_time = 0.0

        self.button.when_pressed = self._on_press
        self.button.when_released = lambda: None

    def _on_press(self) -> None:
        """
        Internal handler for each button press.
        Increments count and resets the sequence timer.
        """
        now = time.time()
        delta = now - self.last_time if self.last_time else 0.0
        self.last_time = now
        self.count += 1
        logger.info("ButtonHandler: Δ%.2fs, count=%d", delta, self.count)
        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(self.timeout, self._process)
        self.timer.start()

    def _process(self) -> None:
        """
        Called when the press-sequence timer expires.
        Invokes the callback for the counted presses.
        """
        cb = self.callbacks.get(self.count)
        if cb:
            logger.info(
                "ButtonHandler: invoking callback for count %d", self.count)
            try:
                cb()
            except Exception:
                logger.exception("ButtonHandler: callback error")
        else:
            logger.info(
                "ButtonHandler: no action for count %d", self.count)
        self.count = 0

    def cancel(self) -> None:
        """
        Cancel any pending sequence timer.
        """
        if self.timer:
            self.timer.cancel()
