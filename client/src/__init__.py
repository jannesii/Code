#!/usr/bin/env python3
import os
import time
import logging
from typing import Callable, Dict

from gpiozero import LED, Button

from .bambu_handler import BambuHandler
from .button_handler import ButtonHandler
from .camera_manager import CameraManager
from .dht import DHT22Sensor
from .status_reporter import StatusReporter
from .timelapse_session import TimelapseSession
from .video_encoder import VideoEncoder


# GPIO pins
RED_LED_PIN = 17
YELLOW_LED_PIN = 23
GREEN_LED_PIN = 27
CAPTURE_BUTTON_PIN = 22
DHT_PIN = 24

logger = logging.getLogger(__name__)


def execute_main_loop() -> None:
    """
    Application entry point: set up components and enter main loop.
    """

    red_led = LED(RED_LED_PIN)
    yellow_led = LED(YELLOW_LED_PIN)
    green_led = LED(GREEN_LED_PIN)

    printer = BambuHandler()
    camera = CameraManager()
    encoder = VideoEncoder()
    session = TimelapseSession(
        camera, encoder,
        red_led, yellow_led, green_led,
        os.getcwd(), logger
    )
    dht = DHT22Sensor(DHT_PIN)
    reporter = StatusReporter(session, dht)

    callbacks: Dict[int, Callable[[], None]] = {
        3: session.start_and_stop,
        4: session.pause_and_resume,
        5: lambda: session.stop(create_video=False),
        1: session.capture
    }
    button = Button(CAPTURE_BUTTON_PIN, pull_up=True, bounce_time=0.01)
    handler = ButtonHandler(button, timeout=0.3,
                            callbacks=callbacks)

    reporter.connect()

    logger.info("Press the button to control timelapse")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down")
    finally:
        handler.cancel()
        session.finalize()
        camera.shutdown()
