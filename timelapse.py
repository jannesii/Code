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

# GPIO pins
LED_PIN = 17       # LED
CAPTURE_BUTTON_PIN = 22    # Microswitch
PAUSE_BUTTON_PIN = 27   # Microswitch

class TimelapseController:
    def __init__(self, picam2, led, capture_button):
        self.picam2 = picam2
        self.led = led

        # Timelapse state variables
        self.timelapse_active = False
        self.timelapse_stop = False
        self.timelapse_paused = False

        # Button press counter and timer
        self.button_press_count = 0
        self.button_timer = None
        self.last_press_time = 0

        self.captured_files = []

        # Command thresholds
        self.startup_count = 3  # 3 quick presses to start timelapse
        self.end_count = 3      # 3 quick presses to end timelapse
        self.pause_count = 4    # 4 quick presses to pause/resume timelapse

        self.cutoff_time = 0.3  # maximum time gap between presses

        # Attach button event handlers (only one button now)
        capture_button.when_pressed = self.button_press_handler
        capture_button.when_released = self.led_off

    def led_off(self):
        self.led.off()

    def enable_autofocus(self):
        """Activate autofocus and autoexposure if the camera supports it."""
        try:
            self.picam2.set_controls({
                "AfMode": controls.AfModeEnum.Continuous,
                "AfRange": controls.AfRangeEnum.Normal,
                "AfWindows": [(16384, 16384, 49152, 49152)],
                "ExposureValue": -0.1,
            })
            print("Autofocus activated.")
        except Exception as e:
            print("Error activating autofocus:", e)

    def capture_photo(self):
        """Capture a photo and save it."""
        try:
            image = self.picam2.capture_array()
            image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            filename = f"Photos/capture_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.jpg"
            cv2.imwrite(filename, image_bgr)
            print(f"Image captured and saved as {filename}")
            self.captured_files.append(filename)
        except Exception as e:
            print("Error capturing image:", e)

    def reset_timer(self):
        """Reset (or start) the timer that waits for the end of the press sequence."""
        if self.button_timer is not None:
            self.button_timer.cancel()
        self.button_timer = threading.Timer(self.cutoff_time, self.process_button_sequence)
        self.button_timer.start()

    def button_press_handler(self):
        """Handle each button press by incrementing the counter and restarting the timer."""
        self.led.toggle()
        now = time()
        self.last_press_time = now
        self.button_press_count += 1
        print("Button pressed; count:", self.button_press_count)
        self.reset_timer()

    def process_button_sequence(self):
        """Called after cutoff_time has passed with no new button press.
           Determines which action to take based on the count of presses."""
        count = self.button_press_count
        print("Processing button sequence with count:", count)
        self.button_press_count = 0  # reset counter for next sequence

        # --- BEFORE TIMELAPSE START ---
        if not self.timelapse_active:
            if count >= self.startup_count:
                self.timelapse_active = True
                print("Timelapse started! Use the same button for actions.")
                self.enable_autofocus()
            else:
                print("Not enough presses to start timelapse.")
            return

        # --- WHEN TIMELAPSE IS ACTIVE ---
        # If timelapse is paused, 4 quick presses will resume it.
        if self.timelapse_paused:
            if count >= self.pause_count:
                self.timelapse_paused = False
                print("Resuming timelapse!")
            else:
                print("Press sequence not recognized while paused.")
            return

        # --- ACTIVE AND NOT PAUSED ---
        # Define what different press counts mean:
        if count == 1:
            # A single press captures a photo.
            self.capture_photo()
        elif count == self.pause_count:
            # 4 quick presses trigger pause.
            self.timelapse_paused = True
            print("Timelapse paused.")
        elif count == self.end_count:
            # 3 quick presses trigger ending the timelapse.
            print("Timelapse ended.")
            self.timelapse_stop = True
            self.led.off()
        else:
            print("Unrecognized press sequence:", count)

def create_timelapse_video(image_files):
    """Combine captured images into a timelapse video and delete the images."""
    # Sort files so they are in order.
    image_files.sort()
    first_frame = cv2.imread(image_files[0])
    height, width, _ = first_frame.shape

    default_fps = 25  # Use 25 fps if enough images.
    num_images = len(image_files)
    # If num_images is less than default_fps, use num_images as FPS (if at least 1).
    fps = default_fps if num_images >= default_fps and num_images > 0 else (num_images if num_images > 0 else default_fps)
    print(f"Using fps: {fps}")

    video_filename = f"Timelapses/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_timelapse.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"avc1")
    video_writer = cv2.VideoWriter(video_filename, fourcc, fps, (width, height))

    for fname in image_files:
        frame = cv2.imread(fname)
        if frame is None:
            print(f"Warning: Could not read {fname}, skipping.")
            continue
        video_writer.write(frame)
    video_writer.release()
    print(f"Timelapse video created as {video_filename}")

    # Delete the captured images.
    for fname in image_files:
        try:
            os.remove(fname)
        except Exception as e:
            print(f"Failed to delete {fname}: {e}")
    print("Photos deleted.")

def main():
    # Initialize LED and button.
    led = LED(LED_PIN)
    capture_button = Button(CAPTURE_BUTTON_PIN, pull_up=True, bounce_time=0.01)
    pause_button = Button(PAUSE_BUTTON_PIN, pull_up=True, bounce_time=0.01)

    # Initialize and configure the camera.
    picam2 = Picamera2()
    config = picam2.create_still_configuration()
    picam2.configure(config)
    picam2.start_preview()
    picam2.start()
    sleep(2)  # Allow camera settings to settle


    # Create timelapse controller.
    controller = TimelapseController(picam2, led, capture_button)

    print(f"Press the button {controller.startup_count} times, with no more than {controller.cutoff_time} seconds between presses, to start timelapse capture.")
    try:
        # Monitor timelapse activity.
        while True:
            sleep(0.1)
            if controller.timelapse_active:
                # End timelapse if 30 minutes pass since the last press.
                if time() - controller.last_press_time >= 60*30:
                    print("No button press for 30 minutes. Timelapse ended.")
                    break
                elif controller.timelapse_stop:
                    print("Timelapse ended by button press.")
                    break
    except KeyboardInterrupt:
        print("\nExiting program.")

    # Clean up camera resources.
    picam2.stop_preview()
    picam2.close()

    # Create video if any photos were captured.
    if controller.captured_files:
        create_timelapse_video(controller.captured_files)
    else:
        print("No images were captured, so no timelapse video was created.")

if __name__ == "__main__":
    main()
