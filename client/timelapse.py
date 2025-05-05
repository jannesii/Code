#!/usr/bin/env python3
import os
import sys
import time
import json
import base64
import logging
import threading
import subprocess
from datetime import datetime
from typing import Callable, Dict, Optional

import cv2
import requests
import re
import socketio
from gpiozero import LED, Button
from picamera2 import Picamera2  # type: ignore[reportMissingImports]
from libcamera import controls  # type: ignore[reportMissingImports]

from dht import DHT22Sensor

# GPIO pins
RED_LED_PIN = 17
YELLOW_LED_PIN = 23
GREEN_LED_PIN = 27
CAPTURE_BUTTON_PIN = 22
DHT_PIN = 24


def setup_logging() -> logging.Logger:
    """
    Configure and return the root logger for the application.
    """
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s: %(message)s"))
    root = logging.getLogger()
    if not root.handlers:
        root.addHandler(handler)
    root.setLevel(logging.INFO)
    return root


class CameraManager:
    """Handles camera initialization, autofocus, and frame capture."""

    def __init__(self, logger: logging.Logger) -> None:
        """
        Initialize Picamera2, start preview, and activate autofocus.
        """
        self.logger = logger
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
            self.logger.info("CameraManager: autofocus activated")
        except Exception:
            self.logger.exception("CameraManager: error activating autofocus")

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
            self.logger.exception("CameraManager: error capturing frame")
            return None

    def shutdown(self) -> None:
        """
        Stop preview and release camera resources.
        """
        try:
            self.picam2.stop_preview()
            self.picam2.close()
            self.logger.info("CameraManager: camera shutdown completed")
        except Exception:
            self.logger.exception("CameraManager: error during shutdown")


class VideoEncoder:
    """Wraps ffmpeg for H.264 transcoding."""

    def __init__(self, logger: logging.Logger, ffmpeg_path: str = "/usr/bin/ffmpeg") -> None:
        """
        Initialize with a logger and optional ffmpeg binary path.
        """
        self.logger = logger
        self.ffmpeg_path = ffmpeg_path

    def encode(self, input_file: str) -> bool:
        """
        Transcode the given MP4 file to H.264 using ffmpeg.
        Returns True on success, False on failure.
        """
        if not os.path.exists(self.ffmpeg_path):
            self.logger.error(
                "VideoEncoder: ffmpeg not found at %s", self.ffmpeg_path)
            return False

        output = input_file.replace("_timelapse.mp4", "_timelapse_h264.mp4")
        cmd = [
            self.ffmpeg_path,
            "-i", input_file,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-crf", "23",
            output
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
            os.remove(input_file)
            self.logger.info("VideoEncoder: created %s", output)
            return True
        except subprocess.CalledProcessError as e:
            err = e.stderr.decode(errors='ignore')
            self.logger.error("VideoEncoder: ffmpeg error: %s", err)
            return False
        except Exception:
            self.logger.exception("VideoEncoder: unexpected error")
            return False


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
        self.logger = logger
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
        self.logger.info("ButtonHandler: Δ%.2fs, count=%d", delta, self.count)
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
            self.logger.info(
                "ButtonHandler: invoking callback for count %d", self.count)
            try:
                cb()
            except Exception:
                self.logger.exception("ButtonHandler: callback error")
        else:
            self.logger.info(
                "ButtonHandler: no action for count %d", self.count)
        self.count = 0

    def cancel(self) -> None:
        """
        Cancel any pending sequence timer.
        """
        if self.timer:
            self.timer.cancel()


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
        self.logger = logger

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
                self.logger.info("TimelapseSession: created %s", path)

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
            self.logger.info("TimelapseSession: started")
            self._set_active_leds()

    def pause_and_resume(self) -> None:
        """
        Pause if active and not already paused, otherwise resume.
        """
        if self.active:
            if not self.paused:
                self.paused = True
                self.logger.info("TimelapseSession: paused")
                self._set_paused_leds()
            else:
                self.resume()

    def resume(self) -> None:
        """
        Resume a paused timelapse.
        """
        if self.active and self.paused:
            self.paused = False
            self.logger.info("TimelapseSession: resumed")
            self._set_active_leds()

    def stop(self, create_video: bool = True) -> None:
        """
        Stop timelapse and optionally assemble video.
        create_video: if False, skip video creation.
        """
        self.active = False
        self.should_create = create_video
        self.logger.info(
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
                self.logger.info("TimelapseSession: saved %s", filename)
            except Exception:
                self.logger.exception("TimelapseSession: error saving image")

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
            self.logger.info("TimelapseSession: no images to assemble")
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
                self.logger.info(
                    "TimelapseSession: video created %s", video_name)
                if not self.encoder.encode(video_name):
                    self.logger.warning(
                        "TimelapseSession: encoder fallback, video kept as-is")
            except Exception:
                self.logger.exception("TimelapseSession: error creating video")
        else:
            self.logger.info(
                "TimelapseSession: video creation skipped by user")

        for img in self.images:
            try:
                os.remove(img)
                self.logger.info("TimelapseSession: deleted %s", img)
            except Exception:
                self.logger.exception(
                    "TimelapseSession: error deleting %s", img)
        self.images.clear()
        self._set_streaming_leds()


class StatusReporter:
    """
    Handles HTTP login, Socket.IO connection, and periodic updates:
    sends status, temperature/humidity, and preview images when idle.
    """

    def __init__(
        self,
        session: TimelapseSession,
        dht: DHT22Sensor,
        logger: logging.Logger
    ) -> None:
        """
        session: TimelapseSession instance
        dht: DHT22Sensor instance for readings
        """
        self.session = session
        self.dht = dht
        self.logger = logger

        self.rest = requests.Session()
        self._login()

        self.sio = socketio.Client(logger=True)
        self.sio.on('connect',    self.on_connect)
        self.sio.on('disconnect', self.on_disconnect)
        self.sio.on('error',      self.on_error)
        self.sio.on('timelapse_conf', self.on_config)

        self.status_interval = None
        self.temphum_interval = None
        self.image_interval = None

        conf = self.get_config()
        if conf:
            self.on_config(conf)

    def _login(self) -> None:
        """Authenticate via HTTP to obtain session cookies (with CSRF)."""
        login_url = f"{os.getenv('SERVER')}/login"

        # 1) GET login page to set cookie and grab CSRF token
        resp_get = self.rest.get(login_url)
        self.logger.info("Fetched login page (%s) for CSRF token", login_url)
        if resp_get.status_code != 200:
            self.logger.error("Failed to GET login page: %s",
                              resp_get.status_code)
            sys.exit(1)

        # 2) Extract CSRF token from hidden input
        m = re.search(r'name="csrf_token" value="([^"]+)"', resp_get.text)
        if not m:
            self.logger.error("CSRF token not found on login page")
            sys.exit(1)
        token = m.group(1)
        self.logger.debug("Using CSRF token: %s", token)

        # 3) POST credentials + CSRF
        payload = {
            "username": os.getenv("RASPI_USERNAME"),
            "password": os.getenv("RASPI_PASSWORD"),
            "csrf_token": token,
        }
        headers = {"Referer": login_url}
        self.logger.debug("Posting to %s with Referer header", login_url)
        resp_post = self.rest.post(
            login_url,
            data=payload,
            headers=headers
        )
        if resp_post.status_code != 200 or "Invalid credentials" in resp_post.text:
            self.logger.error(
                "StatusReporter: login failed: %s", resp_post.text)
            sys.exit(1)

        self.logger.info("StatusReporter: logged in")

    def connect(self) -> None:
        """
        Establish Socket.IO connection and start background loops
        for status, temphum, and preview image streaming.
        """
        cookies = "; ".join(
            f"{k}={v}" for k, v in self.rest.cookies.get_dict().items())
        self.sio.connect(
            os.getenv("SERVER"),
            headers={"Cookie": cookies},
            transports=["websocket", "polling"]
        )
        threading.Thread(target=self._status_loop, daemon=True).start()
        threading.Thread(target=self._temphum_loop, daemon=True).start()
        threading.Thread(target=self._image_loop, daemon=True).start()

        # hook timelapse capture to immediate send
        self.session.image_callback = self.send_image

    def _status_loop(self) -> None:
        """Periodically emit the current timelapse status."""
        while True:
            try:
                state = ("paused" if self.session.paused
                         else "active" if self.session.active
                         else "inactive")
                self.sio.emit('status', {'status': state})
            except Exception:
                self.logger.exception("StatusReporter: error sending status")
            time.sleep(self.status_interval)

    def _temphum_loop(self) -> None:
        """Periodically read DHT22 and emit temperature/humidity."""
        while True:
            try:
                data = self.dht.read()
                self.sio.emit('temphum', data)
            except Exception:
                self.logger.exception("StatusReporter: error sending temphum")
            time.sleep(self.temphum_interval)

    def _image_loop(self) -> None:
        """
        Stream preview images only when timelapse is not active.
        """
        while True:
            try:
                if not self.session.active:
                    threading.Thread(
                        target=self.session._blink_red_led, args=(True, 0.2)).start()
                    jpeg = self.session.camera.capture_frame()
                    if jpeg:
                        self.send_image(jpeg)
            except Exception:
                self.logger.exception("StatusReporter: error in image loop")
            time.sleep(self.image_interval)

    def send_image(self, jpeg_bytes: bytes) -> None:
        """
        Emit a base64-encoded image over Socket.IO.
        """
        try:
            payload = base64.b64encode(jpeg_bytes).decode('utf-8')
            with open("/home/jannesi/Code/frame.jpg", "wb") as f:
                f.write(payload)
            self.sio.emit('image', {'image': payload})
        except Exception:
            self.logger.exception("StatusReporter: error sending image")

    def on_connect(self) -> None:
        """Socket.IO connect handler."""
        self.logger.info("StatusReporter: connected to server")

    def on_disconnect(self) -> None:
        """Socket.IO disconnect handler."""
        self.logger.info("StatusReporter: disconnected from server")

    def on_error(self, data: dict) -> None:
        """Socket.IO error handler."""
        self.logger.error("StatusReporter: server error: %s", data)

    def on_config(self, data: dict) -> None:
        """
        Handle configuration updates from server.
        Updates image, status, and temphum intervals.
        """
        try:
            self.image_interval = data['image_delay']
            self.status_interval = data['status_delay']
            self.temphum_interval = data['temphum_delay']
            self.logger.info("StatusReporter: config updated %r", data)
        except KeyError as e:
            self.logger.warning("StatusReporter: invalid config key %s", e)

    def get_config(self) -> Optional[dict]:
        """
        Return the current configuration settings.
        """
        url = f"{os.getenv('SERVER')}/api/timelapse_config"

        resp = self.rest.get(url)
        if resp.status_code == 200:
            try:
                data = resp.json()
                self.logger.info("StatusReporter: config retrieved %r", data)
                return data
            except json.JSONDecodeError:
                self.logger.error(
                    "StatusReporter: error decoding JSON response")
        else:
            self.logger.error(
                "StatusReporter: failed to retrieve config, status code: %d", resp.status_code)
            return None
        return None


def main() -> None:
    """
    Application entry point: set up components and enter main loop.
    """
    logger = setup_logging()

    red_led = LED(RED_LED_PIN)
    yellow_led = LED(YELLOW_LED_PIN)
    green_led = LED(GREEN_LED_PIN)

    camera = CameraManager(logger)
    encoder = VideoEncoder(logger)
    session = TimelapseSession(
        camera, encoder,
        red_led, yellow_led, green_led,
        os.getcwd(), logger
    )
    dht = DHT22Sensor(DHT_PIN, logger=logger)
    reporter = StatusReporter(session, dht, logger)

    callbacks: Dict[int, Callable[[], None]] = {
        3: session.start_and_stop,
        4: session.pause_and_resume,
        5: lambda: session.stop(create_video=False),
        1: session.capture
    }
    button = Button(CAPTURE_BUTTON_PIN, pull_up=True, bounce_time=0.01)
    handler = ButtonHandler(button, timeout=0.3,
                            callbacks=callbacks, logger=logger)

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


if __name__ == "__main__":
    main()
