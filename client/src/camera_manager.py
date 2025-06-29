import time
import logging
from typing import Optional

import cv2
from picamera2 import Picamera2  # type: ignore[reportMissingImports]
from libcamera import controls  # type: ignore[reportMissingImports]

logger = logging.getLogger(__name__)

class CameraManager:
    """Handles camera initialization, autofocus, and frame capture."""

    def __init__(self, logger: logging.Logger) -> None:
        """
        Initialize Picamera2, start preview, and activate autofocus.
        """
        self.picam2 = Picamera2()
        config = self.picam2.create_still_configuration(
            main={"size": (1920, 1080)})
        self.picam2.configure(config)
        self.picam2.start_preview()
        self.picam2.start()
        time.sleep(2)
        self.enable_autofocus()

    def enable_autofocus(self) -> None:
        """
        Enable continuous autofocus and autoexposure if supported.
        """
        try:
            self.picam2.set_controls({
                "AfMode": controls.AfModeEnum.Continuous,
                "AfRange": controls.AfRangeEnum.Normal,
                "AfWindows": [(16384, 16384, 49152, 49152)],
                "ExposureValue": -0.5,
            })
            logger.info("CameraManager: autofocus activated")
        except Exception:
            logger.exception("CameraManager: error activating autofocus")

    def capture_frame(self) -> Optional[bytes]:
        """
        Capture a single still frame and return it as JPEG-encoded bytes.
        Returns None on failure.
        """
        try:
            raw = self.picam2.capture_array()
            bgr = cv2.cvtColor(raw, cv2.COLOR_RGB2BGR)
            ret, jpeg = cv2.imencode('.jpg', bgr)
            if not ret:
                raise RuntimeError("encode failure")
            return jpeg.tobytes()
        except Exception:
            logger.exception("CameraManager: error capturing frame")
            return None

    def shutdown(self) -> None:
        """
        Stop preview and release camera resources.
        """
        try:
            self.picam2.stop_preview()
            self.picam2.close()
            logger.info("CameraManager: camera shutdown completed")
        except Exception:
            logger.exception("CameraManager: error during shutdown")