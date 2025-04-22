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
import socketio
from gpiozero import LED, Button
from picamera2 import Picamera2
from libcamera import controls

from dht import DHT22Sensor

# GPIO pins
RED_LED_PIN = 17
YELLOW_LED_PIN = 23
GREEN_LED_PIN = 27
CAPTURE_BUTTON_PIN = 22
DHT_PIN = 24


def setup_logging() -> logging.Logger:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s: %(message)s"))
    root = logging.getLogger()
    if not root.handlers:
        root.addHandler(handler)
    root.setLevel(logging.INFO)
    return root


def load_config(path: str = "config.json") -> dict:
    with open(path) as f:
        cfg = json.load(f)
    cfg.setdefault("server", "https://jannenkoti.com")
    return cfg


class CameraManager:
    """Handles camera initialization, autofocus, and frame capture."""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.picam2 = Picamera2()
        config = self.picam2.create_still_configuration(
            main={"size": (1920, 1080)})
        self.picam2.configure(config)
        self.picam2.start_preview()
        self.picam2.start()
        time.sleep(2)
        self.enable_autofocus()

    def enable_autofocus(self):
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
        """Capture a single frame and return it as JPEG bytes."""
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

    def shutdown(self):
        """Shutdown camera preview and release resources."""
        try:
            self.picam2.stop_preview()
            self.picam2.close()
            self.logger.info("CameraManager: camera shutdown completed")
        except Exception:
            self.logger.exception("CameraManager: error during shutdown")


class VideoEncoder:
    """Wraps ffmpeg for H.264 transcoding."""

    def __init__(self, logger: logging.Logger, ffmpeg_path: str = "/usr/bin/ffmpeg"):
        self.logger = logger
        self.ffmpeg_path = ffmpeg_path

    def encode(self, input_file: str) -> bool:
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
    """Counts button presses within a timeout and dispatches callbacks."""

    def __init__(
        self,
        button: Button,
        timeout: float,
        callbacks: Dict[int, Callable[[], None]],
        logger: logging.Logger
    ):
        self.button = button
        self.timeout = timeout
        self.callbacks = callbacks
        self.logger = logger
        self.count = 0
        self.timer: Optional[threading.Timer] = None
        self.last_time = 0.0

        self.button.when_pressed = self._on_press
        self.button.when_released = lambda: None

    def _on_press(self):
        now = time.time()
        delta = now - self.last_time if self.last_time else 0.0
        self.last_time = now
        self.count += 1
        self.logger.info("ButtonHandler: Δ%.2fs, count=%d", delta, self.count)
        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(self.timeout, self._process)
        self.timer.start()

    def _process(self):
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

    def cancel(self):
        if self.timer:
            self.timer.cancel()


class TimelapseSession:
    """Manages timelapse state, photo storage, video creation, image callbacks, and LEDs."""

    def __init__(
        self,
        camera: CameraManager,
        encoder: VideoEncoder,
        red_led: LED,
        yellow_led: LED,
        green_led: LED,
        root_dir: str,
        logger: logging.Logger
    ):
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

        # initial LED state: streaming preview
        self._set_streaming_leds()

    def _set_streaming_leds(self):
        self.red_led.on()
        self.yellow_led.off()
        self.green_led.off()

    def _set_active_leds(self):
        self.red_led.off()
        self.yellow_led.off()
        self.green_led.on()

    def _set_paused_leds(self):
        self.red_led.off()
        self.yellow_led.on()
        self.green_led.off()

    def _set_stopped_leds(self):
        self.red_led.off()
        self.yellow_led.off()
        self.green_led.off()

    def _red_led_on_off(self):
        self.red_led.on()
        time.sleep(0.2)
        self.red_led.off()

    def _red_led_off_on(self):
        self.red_led.off()
        time.sleep(0.2)
        self.red_led.on()

    def start_and_stop(self):
        if self.active:
            self.stop(create_video=True)
        else:
            self.active = True
            self.paused = False
            self.images.clear()
            self.logger.info("TimelapseSession: started")
            self._set_active_leds()

    def pause_and_resume(self):
        if self.active:
            if not self.paused:
                self.paused = True
                self.logger.info("TimelapseSession: paused")
                self._set_paused_leds()
            else:
                self.resume()

    def resume(self):
        if self.active and self.paused:
            self.paused = False
            self.logger.info("TimelapseSession: resumed")
            self._set_active_leds()

    def stop(self, create_video: bool = True):
        self.active = False
        self.should_create = create_video
        self.logger.info(
            "TimelapseSession: stopped, create_video=%s", create_video)
        self._set_stopped_leds()
        self.finalize()

    def capture(self):
        # always grab a frame
        data = self.camera.capture_frame()
        if data is None:
            return

        # immediately send it if callback is set
        if self.image_callback:
            self.image_callback(data)

        # if timelapse is active and not paused, save for video
        if self.active and not self.paused:
            # Blink the red LED to indicate capture
            threading.Thread(target=self._red_led_on_off).start()

            
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

    def finalize(self):
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
        # after finishing, return to streaming LED state
        self._set_streaming_leds()


class StatusReporter:
    """Handles HTTP login, Socket.IO connection, and periodic updates including image streaming."""

    def __init__(
        self,
        config: dict,
        session: TimelapseSession,
        dht: DHT22Sensor,
        logger: logging.Logger
    ):
        self.config = config
        self.session = session
        self.dht = dht
        self.logger = logger

        self.rest = requests.Session()
        self._login()

        self.sio = socketio.Client(logger=True)
        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.on_disconnect)
        self.sio.on('error', self.on_error)
        self.sio.on('timelapse_conf', self.on_config)

        self.status_interval = config.get("status_delay", 10)
        self.temphum_interval = config.get("temphum_delay", 10)
        self.image_interval = config.get("image_delay", 10)

    def _login(self):
        url = f"{self.config['server']}/login"
        resp = self.rest.post(url, data={
            "username": self.config["username"],
            "password": self.config["password"]
        })
        if resp.status_code != 200 or "Invalid credentials" in resp.text:
            self.logger.error("StatusReporter: login failed: %s", resp.text)
            sys.exit(1)
        self.logger.info("StatusReporter: logged in")

    def connect(self):
        cookies = "; ".join(
            f"{k}={v}" for k, v in self.rest.cookies.get_dict().items())
        self.sio.connect(
            self.config["server"],
            headers={"Cookie": cookies},
            transports=["websocket", "polling"]
        )
        threading.Thread(target=self._status_loop, daemon=True).start()
        threading.Thread(target=self._temphum_loop, daemon=True).start()
        threading.Thread(target=self._image_loop, daemon=True).start()

        # link session capture to immediate sending
        self.session.image_callback = self.send_image

    def _status_loop(self):
        while True:
            try:
                state = ("paused" if self.session.paused
                         else "active" if self.session.active
                         else "inactive")
                self.sio.emit('status', {'status': state})
            except Exception:
                self.logger.exception("StatusReporter: error sending status")
            time.sleep(self.status_interval)

    def _temphum_loop(self):
        while True:
            try:
                data = self.dht.read()
                self.sio.emit('temphum', data)
            except Exception:
                self.logger.exception("StatusReporter: error sending temphum")
            time.sleep(self.temphum_interval)

    def _image_loop(self):
        while True:
            try:
                # only stream preview when timelapse not active
                if not self.session.active:
                    # Blink the red LED to indicate capture
                    threading.Thread(target=self.session._red_led_off_on).start()
                    
                    jpeg = self.session.camera.capture_frame()
                    if jpeg:
                        self.send_image(jpeg)
            except Exception:
                self.logger.exception("StatusReporter: error in image loop")
            time.sleep(self.image_interval)

    def send_image(self, jpeg_bytes: bytes):
        try:
            payload = base64.b64encode(jpeg_bytes).decode('utf-8')
            self.sio.emit('image', {'image': payload})
        except Exception:
            self.logger.exception("StatusReporter: error sending image")

    def on_connect(self):
        self.logger.info("StatusReporter: connected to server")

    def on_disconnect(self):
        self.logger.info("StatusReporter: disconnected from server")

    def on_error(self, data):
        self.logger.error("StatusReporter: server error: %s", data)

    def on_config(self, data):
        try:
            self.image_interval = data['image_delay']
            self.status_interval = data['status_delay']
            self.temphum_interval = data['temphum_delay']
            self.logger.info("StatusReporter: config updated %r", data)
        except KeyError as e:
            self.logger.warning("StatusReporter: invalid config key %s", e)


def main():
    logger = setup_logging()
    cfg = load_config()

    red_led = LED(RED_LED_PIN)
    yellow_led = LED(YELLOW_LED_PIN)
    green_led = LED(GREEN_LED_PIN)

    camera = CameraManager(logger)
    encoder = VideoEncoder(logger)
    session = TimelapseSession(
        camera, encoder, red_led, yellow_led, green_led, os.getcwd(), logger)
    dht = DHT22Sensor(DHT_PIN, logger=logger)
    reporter = StatusReporter(cfg, session, dht, logger)

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
