#!/usr/bin/env python3
import os
import cv2
import time
from time import sleep, time
from datetime import datetime

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

        self.startup_press_count = 0  # for starting timelapse
        self.action_press_count = 0   # for actions when timelapse is active
        self.last_press_time = 0

        self.captured_files = []

        # thresholds
        self.startup_count = 3
        self.end_count = 3
        self.pause_count = 4

        self.cutoff_time = 0.3

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

    def button_press_handler(self):
        now = time()
        self.led.toggle()

        # --- BEFORE TIMELAPSE START ---
        if not self.timelapse_active:
            # Startup: count 3 quick presses to start timelapse.
            if self.startup_press_count == 0 or (now - self.last_press_time <= self.cutoff_time):
                self.startup_press_count += 1
            else:
                self.startup_press_count = 1
            self.last_press_time = now
            print(f"Startup press count: {self.startup_press_count}")
            if self.startup_press_count >= self.startup_count:
                self.timelapse_active = True
                self.startup_press_count = 0
                self.last_press_time = now
                print("Timelapse started! Use the same button to capture photos, pause, or end.")
                self.enable_autofocus()
            return

        # --- WHEN TIMELAPSE IS ACTIVE ---
        # Check if we're in paused mode
        if self.timelapse_paused:
            # While paused, count presses to resume (4 quick presses required)
            if self.action_press_count == 0 or (now - self.last_press_time <= self.cutoff_time):
                self.action_press_count += 1
            else:
                self.action_press_count = 1
            self.last_press_time = now
            print(f"Resume press count (paused): {self.action_press_count}")
            if self.action_press_count >= self.pause_count:
                self.timelapse_paused = False
                self.action_press_count = 0
                print("Resuming timelapse!")
            return

        # When active and not paused:
        # We use action_press_count to differentiate between capturing a photo,
        # ending the timelapse (3 quick presses), or pausing (4 quick presses).
        if self.action_press_count == 0 or (now - self.last_press_time <= self.cutoff_time):
            self.action_press_count += 1
        else:
            # If the gap was too long, assume a single press intended for a photo capture.
            self.action_press_count = 1
            self.capture_photo()
        self.last_press_time = now
        print(f"Active press count: {self.action_press_count}")

        # Decide what to do once the count reaches one of our thresholds.
        # Note: Depending on your application, you might want to wait a tiny bit
        # (or use an asynchronous callback) to let the user finish the sequence.
        if self.action_press_count == self.pause_count:
            # 4 quick presses trigger pause.
            self.timelapse_paused = True
            self.action_press_count = 0
            print("Timelapse paused.")
        elif self.action_press_count == self.end_count:
            # 3 quick presses trigger end.
            print("Timelapse ended.")
            self.timelapse_stop = True
            self.action_press_count = 0
            self.led.off()
        # Otherwise, if no threshold is reached, you might choose to capture a photo
        # after a delay if no further press occurs. (This example triggers capture on a timeout
        # when the gap is too long, as handled in the 'else' clause above.)

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
