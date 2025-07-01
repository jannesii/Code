#!/usr/bin/env python3
import time
import logging
import threading
from typing import Callable, Dict, Optional

from gpiozero import Button
from .timelapse_session import TimelapseSession
logger = logging.getLogger(__name__)

class ButtonHandler:
    """Counts GPIO button presses within a timeout and dispatches callbacks."""

    def __init__(
        self,
        button: Button,
        session: TimelapseSession,
    ) -> None:
        """
        button: gpiozero.Button instance
        timeout: max seconds between presses for a sequence
        callbacks: map of press-count to function
        """
        self.button = button
        self.session = session
        self.last_time = 0.0

        self.button.when_pressed = self._on_press
        self.button.when_released = lambda: None

    def _on_press(self) -> None:
        """
        Internal handler for each button press.
        Increments count and resets the sequence timer.
        """
        self.session.capture()
        now = time.time()
        delta = now - self.last_time if self.last_time else 0.0
        self.last_time = now
        logger.info("Δ%.2fs", delta)

