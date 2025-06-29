#!/usr/bin/env python3
import os
import time
import logging
import threading
from datetime import datetime
from typing import Callable, Optional

import cv2
from gpiozero import LED

from .camera_manager import CameraManager
from .video_encoder import VideoEncoder

logger = logging.getLogger(__name__)

class TimelapseSession:
    """
    Manages timelapse state, photo storage, video creation,
    image callbacks, and RGB LED indicators.
    """

    def __init__(
        self,
        camera: CameraManager,
        encoder: VideoEncoder,
        red_led: LED,
        yellow_led: LED,
        green_led: LED,
        root_dir: str,
        logger: logging.Logger
    ) -> None:
        """
        camera: CameraManager instance
        encoder: VideoEncoder instance
        red_led, yellow_led, green_led: gpiozero.LED instances
        root_dir: base directory for Photos/Timelapses
        """
        self.camera = camera
        self.encoder = encoder
        self.red_led = red_led
        self.yellow_led = yellow_led
        self.green_led = green_led
        self.root = root_dir

        self.images: list[str] = []
        self.active = False
        self.paused = False
        self.should_create = True
        self.image_callback: Optional[Callable[[bytes], None]] = None

        # ensure directories exist
        for subdir in ("Photos", "Timelapses"):
            path = os.path.join(self.root, subdir)
            if not os.path.exists(path):
                os.makedirs(path)
                logger.info("TimelapseSession: created %s", path)

        # initialize to streaming-preview LED state
        self._set_streaming_leds()

    def _set_streaming_leds(self) -> None:
        """Turn on red LED for streaming, others off."""
        self.red_led.on()
        self.yellow_led.off()
        self.green_led.off()

    def _set_active_leds(self) -> None:
        """Turn on green LED when timelapse active."""
        self.red_led.off()
        self.yellow_led.off()
        self.green_led.on()

    def _set_paused_leds(self) -> None:
        """Turn on yellow LED when timelapse paused."""
        self.red_led.off()
        self.yellow_led.on()
        self.green_led.off()

    def _set_stopped_leds(self) -> None:
        """Turn all LEDs off when timelapse stopped."""
        self.red_led.off()
        self.yellow_led.off()
        self.green_led.off()

    def start_and_stop(self) -> None:
        """
        Toggle timelapse: start if inactive, otherwise stop with video.
        """
        if self.active:
            self.stop(create_video=True)
        else:
            self.active = True
            self.paused = False
            self.images.clear()
            logger.info("TimelapseSession: started")
            self._set_active_leds()

    def pause_and_resume(self) -> None:
        """
        Pause if active and not already paused, otherwise resume.
        """
        if self.active:
            if not self.paused:
                self.paused = True
                logger.info("TimelapseSession: paused")
                self._set_paused_leds()
            else:
                self.resume()

    def resume(self) -> None:
        """
        Resume a paused timelapse.
        """
        if self.active and self.paused:
            self.paused = False
            logger.info("TimelapseSession: resumed")
            self._set_active_leds()

    def stop(self, create_video: bool = True) -> None:
        """
        Stop timelapse and optionally assemble video.
        create_video: if False, skip video creation.
        """
        self.active = False
        self.should_create = create_video
        logger.info(
            "TimelapseSession: stopped, create_video=%s", create_video)
        self._set_stopped_leds()
        self.finalize()

    def capture(self) -> None:
        """
        Capture one frame, send immediately if callback set,
        and save to disk if timelapse active and not paused.
        """
        data = self.camera.capture_frame()
        if data is None:
            return

        # send preview or timelapse frame immediately
        if self.image_callback:
            self.image_callback(data)

        # save frames for timelapse video
        if self.active and not self.paused:
            threading.Thread(target=self._blink_red_led,
                             args=(False, 0.2)).start()
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = os.path.join(
                self.root, "Photos", f"capture_{timestamp}.jpg")
            try:
                with open(filename, "wb") as f:
                    f.write(data)
                self.images.append(filename)
                logger.info("TimelapseSession: saved %s", filename)
            except Exception:
                logger.exception("TimelapseSession: error saving image")

    def _blink_red_led(self, reverse, delay) -> None:
        """Briefly blink the red LED to indicate a capture."""
        if reverse:
            self.red_led.off()
            time.sleep(delay)
            self.red_led.on()
        else:
            self.red_led.on()
            time.sleep(delay)
            self.red_led.off()

    def finalize(self) -> None:
        """
        Assemble captured images into a video if requested,
        then clean up image files and reset LEDs.
        """
        if not self.images:
            logger.info("TimelapseSession: no images to assemble")
        elif self.should_create:
            fps = min(25, len(self.images)) or 1
            video_name = os.path.join(
                self.root,
                "Timelapses",
                f"{datetime.now():%Y-%m-%d_%H-%M-%S}_timelapse.mp4"
            )
            try:
                first = cv2.imread(self.images[0])
                h, w, _ = first.shape
                writer = cv2.VideoWriter(
                    video_name,
                    cv2.VideoWriter_fourcc(*"mp4v"),
                    fps,
                    (w, h)
                )
                if not writer.isOpened():
                    raise RuntimeError("VideoWriter failed")
                for img in self.images:
                    frame = cv2.imread(img)
                    if frame is not None:
                        writer.write(frame)
                writer.release()
                logger.info(
                    "TimelapseSession: video created %s", video_name)
                if not self.encoder.encode(video_name):
                    logger.warning(
                        "TimelapseSession: encoder fallback, video kept as-is")
            except Exception:
                logger.exception("TimelapseSession: error creating video")
        else:
            logger.info(
                "TimelapseSession: video creation skipped by user")

        for img in self.images:
            try:
                os.remove(img)
                logger.info("TimelapseSession: deleted %s", img)
            except Exception:
                logger.exception(
                    "TimelapseSession: error deleting %s", img)
        self.images.clear()
        self._set_streaming_leds()
