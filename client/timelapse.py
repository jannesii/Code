#!/usr/bin/env python3
import os
import cv2
import sys
import time
import subprocess
import threading
import logging
import shutil
import base64
import json
import socketio
import requests

from time import sleep, time as now
from datetime import datetime
from gpiozero import LED, Button
from picamera2 import Picamera2
from libcamera import controls
from dht import DHT22Sensor

# Global lock to prevent concurrent camera access.
camera_lock = threading.Lock()

# GPIO pins
RED_LED_PIN = 17
YELLOW_LED_PIN = 23
GREEN_LED_PIN = 27
CAPTURE_BUTTON_PIN = 22
DHT_PIN = 24

# ANSI escape codes for colors
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
RESET = "\033[0m"


class TimelapseController:
    def __init__(self, red_led, yellow_led, green_led, capture_button):
        self.red_led = red_led
        self.yellow_led = yellow_led
        self.green_led = green_led

        self.root_dir = os.getcwd()
        self.image_delay = 10
        self.temphum_delay = 10
        self.status_delay = 10
        self.server = 'https://jannenkoti.com'

        self.read_config()
        self.init_logger()

        self.sio = SocketIOClient(self, self.server, self.logger, self.config)
        self.sio.start()

        self.dht = DHT22Sensor(DHT_PIN, logger=self.logger)
        self.dht.read()

        self.picam2 = Picamera2()
        cam_config = self.picam2.create_still_configuration(main={"size": (1920, 1080)})
        self.picam2.configure(cam_config)
        self.picam2.start_preview()
        self.picam2.start()
        sleep(2)

        self.timelapse_active = False
        self.timelapse_stop = False
        self.timelapse_paused = False
        self.create_timelapse = True
        self.streaming_active = True

        self.button_press_count = 0
        self.button_timer = None
        self.last_press_time = 0

        self.captured_files = []
        self.startup_count = 3
        self.end_count = 3
        self.pause_count = 4
        self.end_no_video_count = 5
        self.cutoff_time = 0.3

        self.thread_flag = True

        capture_button.when_pressed = self.button_press_handler
        capture_button.when_released = self.red_led_off

        self.enable_autofocus()
        self.start_threads()

        photos_dir = os.path.join(self.root_dir, "Photos")
        timelapses_dir = os.path.join(self.root_dir, "Timelapses")
        if not os.path.exists(photos_dir):
            self.logger.info("Creating directory %s", photos_dir)
            os.makedirs(photos_dir)
        if not os.path.exists(timelapses_dir):
            self.logger.info("Creating directory %s", timelapses_dir)
            os.makedirs(timelapses_dir)

    def init_logger(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def read_config(self):
        with open("config.json") as f:
            self.config = json.load(f)

    def red_led_off(self):
        self.red_led.off()

    def enable_autofocus(self):
        try:
            self.picam2.set_controls({
                "AfMode": controls.AfModeEnum.Continuous,
                "AfRange": controls.AfRangeEnum.Normal,
                "AfWindows": [(16384, 16384, 49152, 49152)],
                "ExposureValue": -0.5,
            })
            self.logger.info("Autofocus activated")
        except Exception:
            self.logger.exception("Error activating autofocus")

    def start_threads(self):
        self.streaming_thread = threading.Thread(target=self.continuous_stream_update, daemon=True)
        self.streaming_thread.start()

        self.status_thread = threading.Thread(target=self.send_status, daemon=True)
        self.status_thread.start()

        self.temphum_thread = threading.Thread(target=self.send_temperature_humidity, daemon=True)
        self.temphum_thread.start()

    def stop_threads(self):
        self.thread_flag = False
        self.streaming_thread.join()
        self.status_thread.join()
        self.temphum_thread.join()

    def send_temperature_humidity(self):
        while self.thread_flag:
            try:
                self.sio.emit('temphum', self.dht.read())
                sleep(self.temphum_delay)
            except Exception:
                self.logger.exception("Error sending temperature and humidity")
                sleep(5)

    def send_status(self):
        while self.thread_flag:
            try:
                status = "paused" if self.timelapse_paused else "active" if self.timelapse_active else "inactive"
                self.sio.emit('status', {'status': status})
                sleep(self.status_delay)
            except Exception:
                self.logger.exception("Error sending status")
                sleep(5)

    def send_image(self, image):
        try:
            encoded = base64.b64encode(image).decode('utf-8')
            self.sio.emit('image', {'image': encoded})
        except Exception:
            self.logger.exception("Error sending image")

    def capture_photo(self):
        try:
            with camera_lock:
                image = self.picam2.capture_array()
            image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            if not self.streaming_active:
                filename = os.path.join(self.root_dir, "Photos", f"capture_{datetime.now():%Y-%m-%d_%H-%M-%S}.jpg")
                cv2.imwrite(filename, image_bgr)
                self.logger.info("Image captured at %s", filename)
                self.captured_files.append(filename)

            ret, jpeg = cv2.imencode('.jpg', image_bgr)
            if ret:
                self.send_image(jpeg.tobytes())
        except Exception:
            self.logger.exception("Error capturing image")

    def continuous_stream_update(self):
        while self.streaming_active and not self.timelapse_active and self.thread_flag:
            self.capture_photo()
            sleep(self.image_delay)
        self.logger.info("Continuous streaming stopped")

    def reset_timer(self):
        if self.button_timer:
            self.button_timer.cancel()
        self.button_timer = threading.Timer(self.cutoff_time, self.process_button_sequence)
        self.button_timer.start()

    def button_press_handler(self):
        now_time = now()
        elapsed = now_time - self.last_press_time if self.last_press_time else 0
        self.last_press_time = now_time
        self.button_press_count += 1
        self.logger.info("Δ %.2fs,  #%d", elapsed, self.button_press_count)
        self.red_led.toggle()
        self.reset_timer()

    def process_button_sequence(self):
        count = self.button_press_count
        self.button_press_count = 0
        log = f"Seq: {count} -> "

        if not self.timelapse_active:
            if count >= self.startup_count:
                self.green_led.on()
                self.streaming_active = False
                self.timelapse_active = True
                log += f"{GREEN}start{RESET}"
            else:
                log += "no start"
            self.logger.info(log)
            return

        if self.timelapse_paused:
            if count >= self.pause_count:
                self.yellow_led.off()
                self.timelapse_paused = False
                log += f"{GREEN}resume{RESET}"
            else:
                log += "no action"
            self.logger.info(log)
            return

        if count == 1:
            log += f"{GREEN}capture{RESET}"
            self.logger.info(log)
            self.capture_photo()
        elif count == self.pause_count:
            self.yellow_led.on()
            self.timelapse_paused = True
            log += f"{YELLOW}pause{RESET}"
            self.logger.info(log)
        elif count == self.end_count:
            self.timelapse_stop = True
            self.create_timelapse = True
            self.red_led.off()
            self.green_led.off()
            log += f"{RED}end{RESET}"
            self.logger.info(log)
        elif count == self.end_no_video_count:
            self.timelapse_stop = True
            self.create_timelapse = False
            self.red_led.off()
            self.green_led.off()
            log += f"{RED}end NO VIDEO{RESET}"
            self.logger.info(log)
        else:
            log += f"?({count})"
            self.logger.info(log)

    def finalize_timelapse(self):
        if self.captured_files:
            self.create_timelapse_video()
        else:
            self.logger.info("No images were captured; no video created")
        self.red_led.off()
        self.yellow_led.off()
        self.green_led.off()

    def create_timelapse_video(self):
        files = sorted(self.captured_files)
        self.logger.info("Creating timelapse video from %d images...", len(files))

        if self.create_timelapse:
            first = files[0]
            if not os.path.exists(first):
                self.logger.warning("First frame %s not found; skipping", first)
                return
            frame = cv2.imread(first)
            if frame is None:
                self.logger.warning("Could not read %s; skipping", first)
                return

            h, w, _ = frame.shape
            n = len(files)
            fps = 25 if n >= 25 else n if n > 0 else 25
            self.logger.info("Using fps: %d", fps)

            try:
                out_name = os.path.join(self.root_dir, "Timelapses", f"{datetime.now():%Y-%m-%d_%H-%M-%S}_timelapse.mp4")
                writer = cv2.VideoWriter(out_name, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
                if not writer.isOpened():
                    raise RuntimeError("VideoWriter failed to open")

                for fn in files:
                    if not os.path.exists(fn):
                        self.logger.warning("Missing %s; skipping", fn)
                        continue
                    frm = cv2.imread(fn)
                    if frm is None:
                        self.logger.warning("Could not read %s; skipping", fn)
                        continue
                    writer.write(frm)
                writer.release()

                if not self.encode_video(out_name):
                    self.logger.info("Timelapse video created as %s", out_name)
            except Exception:
                self.logger.exception("Error creating timelapse video")
        else:
            self.logger.info("Timelapse creation skipped by user")

        for fn in files:
            try:
                os.remove(fn)
                self.logger.info("Deleted %s", fn)
            except Exception:
                self.logger.exception("Failed to delete %s", fn)

    def encode_video(self, input_file) -> bool:
        self.logger.info("Transcoding %s to H.264 format…", input_file)
        ffmpeg_path = "/usr/bin/ffmpeg"
        if not os.path.exists(ffmpeg_path):
            self.logger.error("FFmpeg not found at %s; please install it", ffmpeg_path)
            return False

        self.logger.info("Using ffmpeg at %s", ffmpeg_path)
        output_file = input_file.replace("_timelapse.mp4", "_timelapse_h264.mp4")
        cmd = [
            ffmpeg_path, "-i", input_file,
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-crf", "23", output_file
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.logger.info("H.264 timelapse video created as %s", output_file)
            os.remove(input_file)
            return True
        except FileNotFoundError:
            self.logger.error("FFmpeg binary vanished between check and run")
            return False
        except subprocess.CalledProcessError as e:
            err = e.stderr.decode('utf-8', errors='replace')
            self.logger.error("FFmpeg transcoding failed: %s", err)
            return False
        except Exception:
            self.logger.exception("Unexpected error during video encoding")
            return False

    def shutdown_camera(self):
        try:
            self.picam2.stop_preview()
            self.picam2.close()
            self.logger.info("Camera shutdown completed")
        except Exception:
            self.logger.exception("Error during camera shutdown")

    def __del__(self):
        if hasattr(self, 'picam2'):
            try:
                self.shutdown_camera()
            except Exception:
                pass
        try:
            self.stop_threads()
        except Exception:
            pass


class SocketIOClient:
    def __init__(self, controller, server_url, logger, config):
        self.ctrl = controller
        self.server_url = server_url
        self.logger = logger
        self.config = config

        self.session = requests.Session()
        self.login()

        self.sio = socketio.Client(logger=True)
        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.on_disconnect)
        self.sio.on('error', self.on_error)
        self.sio.on('timelapse_conf', self.on_timelapse_conf)

        conf = self.get_timelapse_conf()
        if conf:
            self.on_timelapse_conf(conf)
            self.logger.info("Timelapse configuration retrieved and applied")

    def login(self):
        resp = self.session.post(f"{self.server_url}/login", data={
            'username': self.config['username'],
            'password': self.config['password']
        })
        if resp.status_code != 200 or "Invalid credentials" in resp.text:
            self.logger.error("Login failed: %s", resp.text)
            sys.exit(1)
        self.logger.info("Logged in; session cookie stored")

    def start(self):
        cookies = '; '.join(f"{k}={v}" for k, v in self.session.cookies.get_dict().items())
        self.sio.connect(self.server_url, headers={'Cookie': cookies}, transports=['websocket', 'polling'])

    def emit(self, event, data, max_retries=3, delay=2.0):
        attempt = 0
        while True:
            try:
                self.sio.emit(event, data)
                self.logger.info("Emitting event: %s", event)
                return
            except Exception as e:
                attempt += 1
                self.logger.error("Error emitting '%s' (attempt %d): %r", event, attempt, e)
                if attempt >= max_retries:
                    self.logger.info("Giving up after maximum retries")
                    return
                sleep(delay)

    def get_timelapse_conf(self):
        resp = self.session.get(f"{self.server_url}/api/timelapse_config")
        if resp.ok:
            return resp.json()
        self.logger.error("Failed to fetch timelapse configuration [%d]: %s", resp.status_code, resp.text)
        return None

    def on_timelapse_conf(self, data):
        try:
            self.ctrl.image_delay = data['image_delay']
            self.ctrl.temphum_delay = data['temphum_delay']
            self.ctrl.status_delay = data['status_delay']
            self.logger.info("Timelapse configuration updated: %r", data)
        except KeyError as e:
            self.logger.warning("Invalid configuration data: %s", e)

    def on_connect(self):
        self.logger.info("⚡ Connected to server")

    def on_disconnect(self):
        self.logger.info("👋 Disconnected from server")

    def on_error(self, data):
        self.logger.error("⚠️ Server error: %s", data.get('message'))


def main():
    red = LED(RED_LED_PIN)
    yellow = LED(YELLOW_LED_PIN)
    green = LED(GREEN_LED_PIN)
    button = Button(CAPTURE_BUTTON_PIN, pull_up=True, bounce_time=0.01)

    controller = TimelapseController(red, yellow, green, button)
    logger = controller.logger

    try:
        logger.info("Press the button %d times (within %.1fs) to start timelapse.",
                    controller.startup_count, controller.cutoff_time)
        while True:
            sleep(0.1)
            if controller.timelapse_active:
                if now() - controller.last_press_time >= 60 * 30:
                    logger.info("No button press for 30 minutes; ending timelapse")
                    break
                if controller.timelapse_stop:
                    logger.info("Timelapse ended by button press")
                    break

        controller.timelapse_active = False
        controller.finalize_timelapse()
        controller.shutdown_camera()
        logger.info("%sReady for a new timelapse session.%s", GREEN, RESET)
    except KeyboardInterrupt:
        logger.info("Exiting program")


if __name__ == "__main__":
    main()
