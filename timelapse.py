#!/usr/bin/env python3
import os
import cv2
import time
from time import sleep, time
from datetime import datetime
import threading

from gpiozero import LED, Button
from picamera2 import Picamera2
from libcamera import controls

# Import shared streaming state and web server
import stream_state
import stream_server
from stream_server import socketio  # import the SocketIO instance

# Global lock to prevent concurrent camera access.
camera_lock = threading.Lock()
# Flag to control continuous streaming (active before timelapse starts).
streaming_active = True

# GPIO pins
RED_LED_PIN = 17             # LED
YELLOW_LED_PIN = 23
GREEN_LED_PIN = 27
CAPTURE_BUTTON_PIN = 22  # Button for capture & commands

# ANSI escape codes for colors.
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
RESET = "\033[0m"


def continuous_stream_update(camera, controller):
    """
    Continuously capture frames at a low framerate and update the shared stream image.
    """
    global streaming_active
    while streaming_active and not controller.timelapse_active:
        with camera_lock:
            try:
                frame = camera.capture_array()
            except Exception as e:
                print("Error capturing stream frame:", e)
                sleep(1)
                continue
        # Convert the frame to BGR for JPEG encoding.
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        ret, jpeg = cv2.imencode('.jpg', frame_bgr)
        if ret:
            stream_state.latest_frame_jpeg = jpeg.tobytes()
            socketio.emit('update_frame')
        sleep(0.1)  # Adjust sleep time for desired FPS


class TimelapseController:
    def __init__(self, red_led, yellow_led, green_led, capture_button):
        self.red_led = red_led
        self.yellow_led = yellow_led
        self.green_led = green_led

        # Initialize and configure the camera.
        self.picam2 = Picamera2()
        self.config = self.picam2.create_still_configuration()
        self.picam2.configure(self.config)
        self.picam2.start_preview()
        self.picam2.start()
        sleep(2)  # Allow camera settings to settle

        # Timelapse state variables
        self.timelapse_active = False
        self.timelapse_stop = False
        self.timelapse_paused = False
        self.create_timelapse = True

        # Button press counter and timer (active during session)
        self.button_press_count = 0
        self.button_timer = None
        self.last_press_time = 0

        self.captured_files = []

        # Command thresholds
        self.startup_count = 3  # 3 quick presses to start timelapse
        self.end_count = 3      # 3 quick presses to end timelapse
        self.pause_count = 4    # 4 quick presses to pause/resume timelapse
        
        self.end_no_video_count = 5

        self.cutoff_time = 0.3  # maximum time gap between presses

        # Attach button event handlers.
        capture_button.when_pressed = self.button_press_handler
        capture_button.when_released = self.red_led_off

        self.enable_autofocus()

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
            print("\nAutofocus activated.\n")
        except Exception as e:
            print("Error activating autofocus:", e)

    def capture_photo(self):
        """Capture a photo, update the streaming image, and save it."""
        try:
            with camera_lock:
                image = self.picam2.capture_array()
            image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            filename = f"Photos/capture_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.jpg"
            cv2.imwrite(filename, image_bgr)
            print(f"Image captured at {datetime.now().strftime('%H-%M-%S')}.")
            self.captured_files.append(filename)
            ret, jpeg = cv2.imencode('.jpg', image_bgr)
            if ret:
                stream_state.latest_frame_jpeg = jpeg.tobytes()
                socketio.emit('update_frame')
        except Exception as e:
            print("Error capturing image:", e)

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
        print(f"Δ {elapsed:.2f}s,\t #{self.button_press_count}")
        self.red_led.toggle()
        self.reset_timer()

    def process_button_sequence(self):
        # ANSI escape codes for colors.
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        RED = "\033[31m"
        RESET = "\033[0m"

        global streaming_active
        count = self.button_press_count
        print(f"Seq: {count} -> ", end="")  # Short sequence count
        self.button_press_count = 0  # reset counter

        if not self.timelapse_active:
            if count >= self.startup_count:
                self.green_led.on()
                streaming_active = False  # Stop continuous streaming for timelapse.
                self.timelapse_active = True
                print(f"{GREEN}start{RESET}")
            else:
                print("no start")
            return

        if self.timelapse_paused:
            if count >= self.pause_count:
                self.yellow_led.off()
                self.timelapse_paused = False
                print(f"{GREEN}resume{RESET}")
            else:
                print("no action")
            return

        if count == 1:
            self.capture_photo()
        elif count == self.pause_count:
            self.yellow_led.on()
            self.timelapse_paused = True
            print(f"{YELLOW}pause{RESET}")
        elif count == self.end_count:
            print(f"{RED}end{RESET}\n")
            self.timelapse_stop = True
            self.create_timelapse = True
            self.red_led.off()
            self.green_led.off()
        elif count == self.end_no_video_count:
            print(f"{RED}end NO VIDEO{RESET}\n")
            self.timelapse_stop = True
            self.create_timelapse = False
            self.red_led.off()
            self.green_led.off()
        else:
            print(f"?({count})")



    def finalize_timelapse(self):
        """
        Finalize the timelapse session by creating the timelapse video and resetting LED states.
        """
        if self.captured_files:
            self.create_timelapse_video()
        else:
            print("No images were captured, so no timelapse video was created.\n")

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
                print(
                    f"Warning: First frame {first_filename} not found. Skipping timelapse creation.")
                return

            first_frame = cv2.imread(first_filename)
            if first_frame is None:
                print(
                    f"Warning: Could not read {first_filename}. Skipping timelapse creation.")
                return

            height, width, _ = first_frame.shape

            default_fps = 25  # Use 25 fps if enough images.
            num_images = len(self.captured_files)
            fps = default_fps if num_images >= default_fps and num_images > 0 else (
                num_images if num_images > 0 else default_fps)
            print(f"Using fps: {fps}")

            video_filename = f"Timelapses/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_timelapse.mp4"
            fourcc = cv2.VideoWriter_fourcc(*"avc1")
            video_writer = cv2.VideoWriter(
                video_filename, fourcc, fps, (width, height))

            for fname in self.captured_files:
                if not os.path.exists(fname):
                    print(f"Warning: {fname} does not exist. Skipping.")
                    continue
                frame = cv2.imread(fname)
                if frame is None:
                    print(f"Warning: Could not read {fname}. Skipping.")
                    continue
                video_writer.write(frame)
            video_writer.release()
            print(f"Timelapse video created as {os.path.basename(video_filename)}\n")
        else:
            print(f"{RED}No timelapse video created.{RESET}\n")

        # Delete the captured images if they exist.
        for fname in self.captured_files:
            if os.path.exists(fname):
                try:
                    os.remove(fname)
                except Exception as e:
                    print(f"Failed to delete {fname}: {e}")
            else:
                print(f"{fname} already deleted or not found.")
        print("Photos deleted.\n")

    def shutdown_camera(self):
        """
        Shutdown the camera by stopping the preview and closing the device.
        This releases the camera resource so a new session can be started.
        """
        try:
            self.picam2.stop_preview()
            self.picam2.close()
            print("Camera shutdown completed.\n")
        except Exception as e:
            print("Error during camera shutdown:", e)


def main():
    global streaming_active
    # Reset the streaming flag at the beginning.
    streaming_active = True

    # Initialize LEDs and button.
    red_led = LED(RED_LED_PIN)
    yellow_led = LED(YELLOW_LED_PIN)
    green_led = LED(GREEN_LED_PIN)
    capture_button = Button(CAPTURE_BUTTON_PIN, pull_up=True, bounce_time=0.01)

    # Start the Flask streaming server only once.
    server_thread = threading.Thread(
        target=stream_server.run_server, daemon=True)
    server_thread.start()

    try:
        while True:
            # Create a new timelapse controller session.
            controller = TimelapseController(
                red_led, yellow_led, green_led, capture_button)

            # Start continuous streaming (active until timelapse starts).
            stream_thread = threading.Thread(target=continuous_stream_update, args=(
                controller.picam2, controller), daemon=True)
            stream_thread.start()

            print(
                f"Press the button {controller.startup_count} times (within {controller.cutoff_time} sec between presses) to start timelapse capture.\n")

            # Monitor timelapse session.
            while True:
                sleep(0.1)
                if controller.timelapse_active:
                    # End timelapse if 30 minutes pass without any button press.
                    if time() - controller.last_press_time >= 60 * 30:
                        print("No button press for 30 minutes. Timelapse ended.\n")
                        break
                    elif controller.timelapse_stop:
                        print("Timelapse ended by button press.\n")
                        break

            # Finalize the timelapse (create video, clean up photos, and reset LEDs).
            controller.finalize_timelapse()

            # Shutdown the camera to release the resource before starting a new session.
            controller.shutdown_camera()

            # Reset the streaming flag for the next session.
            streaming_active = True
            print(f"{GREEN}Ready for a new timelapse session.{RESET}\n")
    except KeyboardInterrupt:
        print("\nExiting program.")


if __name__ == "__main__":
    main()
