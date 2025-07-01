import os
import time
import logging
from typing import Optional

import cv2

# Pi‑specific libraries are imported only when we are **not** on Windows,
# so the file can be imported everywhere.
if os.name != "nt":
    from picamera2 import Picamera2  # type: ignore[reportMissingImports]
    from libcamera import controls   # type: ignore[reportMissingImports]

logger = logging.getLogger(__name__)


class CameraManager:
    """
    Cross‑platform camera helper.

    * On Raspberry Pi  (os.name != "nt"):  uses Picamera2.
    * On Windows        (os.name == "nt"): uses cv2.VideoCapture(0).
    """

    def __init__(
        self,
        logger: logging.Logger = logger,
        camera_index: int = 0,
        resolution: tuple[int, int] = (1920, 1080),
    ) -> None:
        self.resolution = resolution
        self._is_windows = os.name == "nt"

        if self._is_windows:
            # ----- Windows / generic webcam path -----
            self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                raise RuntimeError("cannot open webcam")

            # Best‑effort resolution request
            width, height = resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            logger.info(
                "webcam opened (index %s) at %sx%s",
                camera_index,
                int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            )

        else:
            # ----- Raspberry Pi path -----
            self.picam2 = Picamera2()  # type: ignore[reportMissingImports]
            config = self.picam2.create_still_configuration()
            self.picam2.configure(config)
            self.picam2.start_preview()
            self.picam2.start()
            time.sleep(2)  # let AGC/AWB settle
            self._enable_autofocus()
            logger.info("Picamera2 initialised")

    # ------------------------------------------------------------------ #
    #  Raspberry‑Pi‑only helper
    # ------------------------------------------------------------------ #
    def _enable_autofocus(self) -> None:
        """Enable continuous autofocus (ignored on Windows)."""
        if self._is_windows:
            return  # autofocus control not available via OpenCV

        try:
            self.picam2.set_controls(
                {
                    "AfMode": controls.AfModeEnum.Continuous,   # type: ignore[reportMissingImports]
                    "AfRange": controls.AfRangeEnum.Normal,      # type: ignore[reportMissingImports]
                    "AfWindows": [(16384, 16384, 49152, 49152)],
                    "ExposureValue": -0.5,
                }
            )
            logger.info("autofocus activated")
        except Exception:
            logger.exception("error activating autofocus")

    # ------------------------------------------------------------------ #
    #  Public API
    # ------------------------------------------------------------------ #
    def capture_frame(self) -> Optional[bytes]:
        """
        Grab one frame and return JPEG‑encoded bytes.
        Returns None on failure.
        """
        try:
            if self._is_windows:
                ret, frame_bgr = self.cap.read()
                if not ret:
                    raise RuntimeError("webcam read failed")
            else:
                success = self.picam2.autofocus_cycle()
                if not success:
                    logger.warning("autofocus cycle failed, using last focus")
                raw_rgb = self.picam2.capture_array()
                # Convert to BGR for cv2.imencode
                frame_bgr = cv2.cvtColor(raw_rgb, cv2.COLOR_RGB2BGR)

            ok, jpeg = cv2.imencode(".jpg", frame_bgr)
            if not ok:
                raise RuntimeError("JPEG encode failed")
            return jpeg.tobytes()

        except Exception:
            logger.exception("error capturing frame")
            return None

    def shutdown(self) -> None:
        """Release camera resources."""
        try:
            if self._is_windows:
                self.cap.release()
                logger.info("webcam released")
            else:
                self.picam2.stop_preview()
                self.picam2.close()
                logger.info("Picamera2 shutdown completed")
        except Exception:
            logger.exception("error during shutdown")

    # ------------------------------------------------------------------ #
    #  Context‑manager helpers (optional quality‑of‑life)
    # ------------------------------------------------------------------ #
    def __enter__(self) -> "CameraManager":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.shutdown()
    """
    example usage:
    with CameraManager() as cam:
        jpeg_bytes = cam.capture_frame()
    """
