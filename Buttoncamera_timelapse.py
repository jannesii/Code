#!/usr/bin/env python3
from gpiozero import LED, Button
from picamera2 import Picamera2
import cv2
import time
from time import sleep, time
import os

# Define GPIO pins
LED_PIN = 17   # GPIO pin for LED
BUTTON_PIN = 22  # GPIO pin for microswitch

# Initialize components
led = LED(LED_PIN)
button = Button(BUTTON_PIN, pull_up=True, bounce_time=0.05)  # Internal pull-up resistor

# Initialize and configure Picamera2 for still images
picam2 = Picamera2()
config = picam2.create_still_configuration()
picam2.configure(config)
picam2.start_preview()
picam2.start()

# Allow camera settings to settle
sleep(2)

# Global variables to track timelapse state and button presses
timelapse_active = False
last_press_time = 0
press_count = 0
captured_files = []  # List to store captured filenames

def capture_photo():
    """Capture a photo using Picamera2 and save it."""
    global captured_files
    try:
        # Capture the image (RGB)
        image = picam2.capture_array()
        # Convert to BGR for OpenCV
        image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        # Create unique filename using timestamp
        filename = f"capture_{int(time())}.jpg"
        cv2.imwrite(filename, image_bgr)
        print(f"Image captured and saved as {filename}")
        captured_files.append(filename)
    except Exception as e:
        print("Error capturing image:", e)

def button_press_handler():
    """Handle a button press and start timelapse after 5 rapid presses."""
    global timelapse_active, last_press_time, press_count
    now = time()
    # Check if the time between consecutive presses is <= 1.5 seconds
    if now - last_press_time <= 1.5:
        press_count += 1
    else:
        press_count = 1  # reset the count if too much delay

    last_press_time = now

    if not timelapse_active:
        if press_count >= 5:
            timelapse_active = True
            print("Timelapse started!")
            try:
                # Activate continuous autofocus
                picam2.set_controls({"AfMode": "Continuous"})
                print("Autofocus activated.")
            except Exception as e:
                print("Unable to activate autofocus:", e)
        else:
            print(f"Press {5 - press_count} more time(s) quickly to start timelapse.")
            # Do not capture photo or toggle LED until timelapse starts.
            return

    led.toggle()  # Toggle LED for feedback
    capture_photo()

# Attach the event to the button press
button.when_pressed = button_press_handler
button.when_released = led.off

print("Press the button 5 times (within 1.5 seconds between presses) to start timelapse capture (5 seconds of inactivity ends timelapse).")

try:
    # Main loop monitoring inactivity after timelapse started
    while True:
        sleep(0.1)
        if timelapse_active:
            # If 120 seconds have passed since the last press, end timelapse
            if time() - last_press_time >= 120:
                print("No button press for 120 seconds. Timelapse ended.")
                break

except KeyboardInterrupt:
    print("\nExiting program.")

# Stop camera preview and release resources
picam2.stop_preview()
picam2.close()

# Combine captured images into a timelapse video if any photos were taken
if captured_files:
    # Sort files (filenames include timestamp so they sort correctly)
    captured_files.sort()
    # Read the first image to determine frame size
    first_frame = cv2.imread(captured_files[0])
    height, width, _ = first_frame.shape
    
    # Define video filename and video writer
    video_filename = "timelapse.avi"
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    fps = 2  # Adjust frames per second as needed
    video_writer = cv2.VideoWriter(video_filename, fourcc, fps, (width, height))
    
    for fname in captured_files:
        frame = cv2.imread(fname)
        if frame is None:
            print(f"Warning: Could not read {fname}, skipping.")
            continue
        video_writer.write(frame)
    
    video_writer.release()
    print(f"Timelapse video created as {video_filename}")

    # Delete the captured JPG files after video creation
    for fname in captured_files:
        try:
            os.remove(fname)
            print(f"Deleted {fname}")
        except Exception as e:
            print(f"Failed to delete {fname}: {e}")
else:
    print("No images were captured, so no timelapse video was created.")