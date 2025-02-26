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
        self.startup_press_count = 0
        self.end_press_count = 0
        self.last_start_press_time = 0
        self.last_press_time = 0
        self.captured_files = []

        # Attach button event handlers.
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
                "ExposureValue": -0.05,
                #"AeEnable": 1,
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
        """
        Handle a button press.
        
        Before timelapse starts, count presses (5 consecutive presses with <=0.8 sec gap
        starts timelapse). Once active, each press captures a photo. 5 consecutive presses will end the timelapse.
        """
        now = time()
        self.led.toggle()

        if not self.timelapse_active:
            # Counting presses to start timelapse.
            if self.startup_press_count == 0 or (now - self.last_start_press_time <= 0.8):
                self.startup_press_count += 1
            else:
                self.startup_press_count = 1
            self.last_start_press_time = now
            print(f"Startup button press count: {self.startup_press_count}")
            if self.startup_press_count >= 5:
                self.timelapse_active = True
                self.last_press_time = now
                print("Timelapse started! Press the button to take photos.")
                self.enable_autofocus()
            return

        # Timelapse is active: capture photos on press.
        if self.end_press_count == 0 or (now - self.last_press_time <= 0.8):
            if self.end_press_count == 0:
                self.capture_photo()
            else:
                print(f"End button press count: {self.end_press_count}")
            self.end_press_count += 1
        else:
            self.end_press_count = 1
            self.capture_photo()
        self.last_press_time = now

        if self.end_press_count >= 5:
            print("Timelapse ended.")
            self.timelapse_stop = True
            self.end_press_count = 0
            self.led.off()

def create_timelapse_video(image_files):
    """Combine captured images into a timelapse video and delete the images."""
    # Sort files so they are in order.
    image_files.sort()
    first_frame = cv2.imread(image_files[0])
    height, width, _ = first_frame.shape

    video_filename = f"Timelapses/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_timelapse.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"avc1")
    fps = 25  # Adjust frames per second as needed.
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

    print("Press the button 5 times, with no more than 0.8 seconds between presses, to start timelapse capture.")

    # Create timelapse controller.
    controller = TimelapseController(picam2, led, capture_button)

    try:
        # Monitor timelapse activity.
        while True:
            sleep(0.1)
            if controller.timelapse_active:
                # End timelapse if 5 minutes pass since the last press.
                if time() - controller.last_press_time >= 600:
                    print("No button press for 10 minutes. Timelapse ended.")
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
