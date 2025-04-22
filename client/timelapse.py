#!/usr/bin/env python3
import os
import cv2
import sys
import time
import subprocess
from time import sleep, time
from datetime import datetime
import threading
import requests
import ssl
import base64
import json
import socketio
import logging

from dht import DHT22Sensor

from gpiozero import LED, Button
from picamera2 import Picamera2
from libcamera import controls

# Global lock to prevent concurrent camera access.
camera_lock = threading.Lock()


# Global variable to hold the current timelapse controller for keyboard simulation.
current_controller = None

# GPIO pins
RED_LED_PIN = 17             # LED
YELLOW_LED_PIN = 23
GREEN_LED_PIN = 27
CAPTURE_BUTTON_PIN = 22  # Button for capture & commands

DHT_PIN = 24

# ANSI escape codes for colors.
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
RESET = "\033[0m"


class TimelapseController:
    def __init__(self, red_led, yellow_led, green_led, capture_button):
        self.red_led = red_led
        self.yellow_led = yellow_led
        self.green_led = green_led

        self.server = 'https://jannenkoti.com'

        self.get_api_key()
        self.init_logger()

        self.sio = SocketIOClient(self, self.server, self.API_KEY, self.logger)
        self.sio.start()

        self.dht = DHT22Sensor(DHT_PIN, logger=self.logger)
        self.dht.read()
        # Initialize and configure the camera.
        self.picam2 = Picamera2()
        self.config = self.picam2.create_still_configuration(
            main={"size": (1920, 1080)}
        )
        self.picam2.configure(self.config)
        self.picam2.start_preview()
        self.picam2.start()
        sleep(2)  # Allow camera settings to settle

        # Timelapse state variables
        self.timelapse_active = False
        self.timelapse_stop = False
        self.timelapse_paused = False
        self.create_timelapse = True
        self.streaming_active = True  # Flag to control streaming

        # Button press counter and timer (active during session)
        self.button_press_count = 0
        self.button_timer = None
        self.last_press_time = 0

        self.captured_files = []

        # Command thresholds
        self.startup_count = 3  # 3 quick presses to start timelapse
        self.end_count = 3      # 3 quick presses to end timelapse
        self.pause_count = 4    # 4 quick presses to pause/resume timelapse
        self.end_no_video_count = 5  # 5 quick presses to end timelapse without video

        self.cutoff_time = 0.3  # maximum time gap between presses

        self.temp = "N/A"
        self.hum = "N/A"
        self.thread_flag = True
        
        self.image_delay = 10  # Delay between image captures in seconds
        self.temphum_delay = 60  # Delay between temperature/humidity readings in seconds
        self.status_delay = 10  # Delay between status updates in seconds

        # Attach button event handlers.
        capture_button.when_pressed = self.button_press_handler
        capture_button.when_released = self.red_led_off

        self.enable_autofocus()

        self.start_threads()
        
    def init_logger(self):
        # Setup logging
        self.logger = logging.getLogger(self.__class__.__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s"))
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def get_api_key(self):
        with open("config.json") as f:
            config = json.load(f)
            self.API_KEY = config["api_key"]
            self.headers = {'X-API-KEY': self.API_KEY}
            if not self.API_KEY:
                self.logger.info("API key not found in config.json")
                sys.exit(1)

    def red_led_off(self):
        self.red_led.off()

    def enable_autofocus(self):
        """Activate autofocus and autoexposure if supported."""
        try:
            self.picam2.set_controls({
                "AfMode": controls.AfModeEnum.Continuous,
                "AfRange": controls.AfRangeEnum.Normal,
                "AfWindows": [(16384, 16384, 49152, 49152)],
                "ExposureValue": -0.5,
            })
            self.logger.info("\nAutofocus activated.\n")
        except Exception as e:
            self.logger.info("Error activating autofocus:", e)

    def start_threads(self):
        """Start threads for continuous streaming and timelapse control."""
        self.streaming_thread = threading.Thread(
            target=self.continuous_stream_update, daemon=True)
        #self.streaming_thread.start()

        self.status_thread = threading.Thread(
            target=self.send_status, daemon=True)
        self.status_thread.start()

        self.temphum_thread = threading.Thread(
            target=self.send_temperature_humidity, daemon=True)
        self.temphum_thread.start()

    def stop_threads(self):
        """Stop all threads."""
        self.thread_flag = False
        self.streaming_thread.join()
        self.status_thread.join()
        self.temphum_thread.join()

    def send_temperature_humidity(self):
        """Send the current temperature and humidity to the server."""
        while self.thread_flag:
            try:
                self.sio.emit('temphum', self.dht.read())
                sleep(self.temphum_delay)  # Delay between readings
            except Exception as e:
                self.logger.info(
                    f"Error sending temperature and humidity: {e}")
                sleep(5)  # Retry after a short delay

    def send_status(self):
        """Send the current status of the timelapse to the server."""
        while self.thread_flag:
            try:
                if self.timelapse_paused:
                    status = "paused"
                elif self.timelapse_active:
                    status = "active"
                else:
                    status = "inactive"

                self.sio.emit('status', {'status': status})
                sleep(self.status_delay)  # Delay between status updates
            except Exception as e:
                self.logger.info(f"Error sending status: {e}")
                sleep(5)  # Retry after a short delay

    def send_image(self, image):
        """Send the captured image to the server."""
        try:
            url = f"{self.server}/3d/image"
            # Convert the binary JPEG data into a base64-encoded string.
            encoded_image = base64.b64encode(image).decode('utf-8')
            data = {'image': encoded_image}
            self.sio.emit('image', data)
        except Exception as e:
            self.logger.info(f"Error sending image: {e}")

    def capture_photo(self):
        """Capture a photo, update the streaming image, and save it."""
        try:
            with camera_lock:
                image = self.picam2.capture_array()
            image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            if not self.streaming_active:
                filename = f"Photos/capture_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.jpg"
                cv2.imwrite(filename, image_bgr)
                self.logger.info(
                    f"Image captured at {datetime.now().strftime('%H-%M-%S')}.")
                self.captured_files.append(filename)

            ret, jpeg = cv2.imencode('.jpg', image_bgr)
            if ret:
                # Send the image to the server.
                self.send_image(jpeg.tobytes())
        except Exception as e:
            self.logger.info("Error capturing image:", e)

    def continuous_stream_update(self):
        """
        Continuously capture frames at a low framerate and update the shared stream image.
        """
        while self.streaming_active and not self.timelapse_active and self.thread_flag:
            self.capture_photo()  # Capture a frame

            sleep(self.image_delay)  # Adjust sleep time for desired FPS
        self.logger.info("Continuous streaming stopped.")

    def reset_timer(self):
        """Reset (or start) the timer that waits for the end of the press sequence."""
        if self.button_timer is not None:
            self.button_timer.cancel()
        self.button_timer = threading.Timer(
            self.cutoff_time, self.process_button_sequence)
        self.button_timer.start()

    def button_press_handler(self):
        current_time = time()
        elapsed = current_time - self.last_press_time if self.last_press_time else 0
        self.last_press_time = current_time
        self.button_press_count += 1
        self.logger.info(f"Δ {elapsed:.2f}s,\t #{self.button_press_count}")
        self.red_led.toggle()
        self.reset_timer()

    def process_button_sequence(self):
        # ANSI escape codes for colors.
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        RED = "\033[31m"
        RESET = "\033[0m"

        count = self.button_press_count
        log_string = f"Seq: {count} -> "  # Short sequence count
        self.button_press_count = 0  # reset counter

        if not self.timelapse_active:
            if count >= self.startup_count:
                self.green_led.on()
                # Stop continuous streaming for timelapse.
                self.streaming_active = False
                self.timelapse_active = True
                log_string += f"{GREEN}start{RESET}"
            else:
                log_string += "no start"
            return

        if self.timelapse_paused:
            if count >= self.pause_count:
                self.yellow_led.off()
                self.timelapse_paused = False
                log_string += f"{GREEN}resume{RESET}"
            else:
                log_string += "no action"
            return

        if count == 1:
            self.capture_photo()
        elif count == self.pause_count:
            self.yellow_led.on()
            self.timelapse_paused = True
            log_string += f"{YELLOW}pause{RESET}"
        elif count == self.end_count:
            log_string += f"{RED}end{RESET}\n"
            self.timelapse_stop = True
            self.create_timelapse = True
            self.red_led.off()
            self.green_led.off()
        elif count == self.end_no_video_count:
            log_string += f"{RED}end NO VIDEO{RESET}\n"
            self.timelapse_stop = True
            self.create_timelapse = False
            self.red_led.off()
            self.green_led.off()
        else:
            log_string += f"?({count})"
            
        self.logger.info(log_string)

    def finalize_timelapse(self):
        """
        Finalize the timelapse session by creating the timelapse video and resetting LED states.
        """
        if self.captured_files:
            self.create_timelapse_video()
        else:
            self.logger.info("No images were captured, so no timelapse video was created.\n")

        self.red_led.off()
        self.yellow_led.off()
        self.green_led.off()

    def create_timelapse_video(self):
        """Combine captured images into a timelapse video and delete the images."""
        self.captured_files.sort()

        if self.create_timelapse:
            # Ensure we have a valid first frame.
            first_filename = self.captured_files[0]
            if not os.path.exists(first_filename):
                self.logger.info(
                    f"Warning: First frame {first_filename} not found. Skipping timelapse creation.")
                return

            first_frame = cv2.imread(first_filename)
            if first_frame is None:
                self.logger.info(
                    f"Warning: Could not read {first_filename}. Skipping timelapse creation.")
                return

            height, width, _ = first_frame.shape

            default_fps = 25  # Use 25 fps if enough images.
            num_images = len(self.captured_files)
            fps = default_fps if num_images >= default_fps and num_images > 0 else (
                num_images if num_images > 0 else default_fps)
            self.logger.info(f"Using fps: {fps}")

            try:
                video_filename = f"Timelapses/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_timelapse.mp4"
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                video_writer = cv2.VideoWriter(
                    video_filename, fourcc, fps, (width, height))

                for fname in self.captured_files:
                    if not os.path.exists(fname):
                        self.logger.info(f"Warning: {fname} does not exist. Skipping.")
                        continue
                    frame = cv2.imread(fname)
                    if frame is None:
                        self.logger.info(f"Warning: Could not read {fname}. Skipping.")
                        continue
                    video_writer.write(frame)

                if not video_writer.isOpened():
                    raise Exception(
                        "Failed to open the video writer. Please check the codec and device configuration.")

                video_writer.release()

                # Transcode the video to H.264 using FFMPEG.
                self.encode_video(video_filename)

                self.logger.info(
                    f"Timelapse video created as {os.path.basename(video_filename)}\n")
            except Exception as e:
                self.logger.info(f"Error creating timelapse video: {e}")
                sys.exit(1)
        else:
            self.logger.info(f"{RED}No timelapse video created.{RESET}\n")

        # Delete the captured images if they exist.
        for fname in self.captured_files:
            if os.path.exists(fname):
                try:
                    os.remove(fname)
                except Exception as e:
                    self.logger.info(f"Failed to delete {fname}: {e}")
            else:
                self.logger.info(f"{fname} already deleted or not found.")
        self.logger.info("Photos deleted.\n")

    def encode_video(self, input_file):
        # Run FFMPEG to transcode the video.
        self.logger.info(f"Transcoding {input_file} to H.264 format...")
        # Ensure the output filename is different from the input filename.
        output_file = input_file.replace(
            "_timelapse.mp4", "_timelapse_h264.mp4")

        ffmpeg_cmd = [
            'ffmpeg',
            '-i', input_file,
            '-c:v', 'libx264',        # Use the software-based H.264 encoder.
            # Set pixel format for maximum compatibility.
            '-pix_fmt', 'yuv420p',
            # Constant rate factor (adjust quality as needed).
            '-crf', '23',
            output_file
        ]

        try:
            subprocess.run(ffmpeg_cmd, check=True)
            self.logger.info(f"H.264 timelapse video created as {output_file}")
            # Remove the original video file after transcoding.
            os.remove(input_file)
        except subprocess.CalledProcessError as e:
            self.logger.info("FFMPEG transcoding failed:", e)
        except Exception as e:
            self.logger.info(f"Error during video encoding: {e}")

    def shutdown_camera(self):
        """
        Shutdown the camera by stopping the preview and closing the device.
        This releases the camera resource so a new session can be started.
        """
        try:
            self.picam2.stop_preview()
            self.picam2.close()
            self.logger.info("Camera shutdown completed.\n")
        except Exception as e:
            self.logger.info("Error during camera shutdown:", e)

    def __del__(self):
        # Varmista, että attribuutit on olemassa ennen kutsua
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
    def __init__(self, controller, server_url, API_KEY, logger):
        self.controller = controller
        self.server_url = server_url
        self.auth = {'api_key': API_KEY}
        self.logger = logger

        self.sio = socketio.Client()

        self.sio.on('connect', handler=self.on_connect)
        self.sio.on('disconnect', handler=self.on_disconnect)
        self.sio.on('error', handler=self.on_error)
        self.sio.on('timelapse_conf', handler=self.on_timelapse_conf)

    def start(self):
        self.sio.connect(self.server_url, auth=self.auth)

    def emit(self, event, data, max_retries: int = 3, delay: float = 2.0):
        """Emit an event to the server, retrying on error after `delay` seconds."""
        attempt = 0
        while True:
            try:
                self.sio.emit(event, data)
                self.logger.info(f"Emitting event: {event}")
                return  # success, exit
            except Exception as e:
                attempt += 1
                self.logger.info(
                    f"Error emitting event '{event}' (attempt {attempt}): {e!r}")
                if attempt >= max_retries:
                    self.logger.info(f"Giving up after {attempt} failed attempts.")
                    return
                sleep(delay)
                
    def on_timelapse_conf(self, data):
        """Handle the timelapse configuration update from the server."""
        try:
            self.controller.image_delay = data['image_delay']
            self.controller.temphum_delay = data['temphum_delay']
            self.controller.status_delay = data['status_delay']
            self.logger.info(f"Timelapse configuration updated: {data}")
            
        except KeyError as e:
            self.logger.info(f"Invalid configuration data received: {e}")

    def on_connect(self):
        self.logger.info("⚡ Connected to server")

    def on_disconnect(self):
        self.logger.info("👋 Disconnected from server")

    def on_error(self, data):
        self.logger.info(f"⚠️ Error: {data['message']}")





def main():
    # Reset the streaming flag at the beginning.

    # Initialize LEDs and button.
    red_led = LED(RED_LED_PIN)
    yellow_led = LED(YELLOW_LED_PIN)
    green_led = LED(GREEN_LED_PIN)
    capture_button = Button(CAPTURE_BUTTON_PIN, pull_up=True, bounce_time=0.01)

    # Create a new timelapse controller session.
    controller = TimelapseController(
        red_led, yellow_led, green_led, capture_button)
    logger = controller.logger

    try:
        while True:
            logger.info(
                f"Press the button {controller.startup_count} times (within {controller.cutoff_time} sec between presses) to start timelapse capture.\n"
                "Or just press ENTER to simulate a button press.\n"
            )

            # Monitor timelapse session.
            while True:
                sleep(0.1)
                if controller.timelapse_active:
                    # End timelapse if 30 minutes pass without any button press.
                    if time() - controller.last_press_time >= 60 * 30:
                        logger.info("No button press for 30 minutes. Timelapse ended.\n")
                        break
                    elif controller.timelapse_stop:
                        logger.info("Timelapse ended by button press.\n")
                        break

            controller.timelapse_active = False  # Reset the timelapse state.

            # Finalize the timelapse (create video, clean up photos, and reset LEDs).
            controller.finalize_timelapse()

            # Shutdown the camera to release the resource before starting a new session.
            controller.shutdown_camera()

            logger.info(f"{GREEN}Ready for a new timelapse session.{RESET}\n")

            return  # Exit the loop after one session for testing purposes.
    except KeyboardInterrupt:
        logger.info("\nExiting program.")


if __name__ == "__main__":
    main()
