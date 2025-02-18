#!/usr/bin/env python3
from gpiozero import LED, Button
from picamera2 import Picamera2
import cv2
import time
from time import sleep, time
import os
from libcamera import controls

# Test
# Define GPIO pins
LED_PIN = 17   # GPIO pin for LED
BUTTON_PIN = 22  # GPIO pin for microswitch

# Initialize components
led = LED(LED_PIN)
button = Button(BUTTON_PIN, pull_up=True, bounce_time=0.05)  # Internal pull-up resistor

# Initialize and configure Picamera2 for still images
picam2 = Picamera2()
camera_controls = picam2.camera_controls

config = picam2.create_still_configuration()
picam2.configure(config)
picam2.start_preview()
picam2.start()

# Allow camera settings to settle
sleep(2)

# Global variables to track timelapse state and startup button presses
timelapse_active = False
timelapse_stop = False
last_press_time = 0
captured_files = []  # List to store captured filenames

# New globals for startup button press sequence.
startup_press_count = 0
end_press_count = 0
last_start_press_time = 0

def enable_autofocus():
    """Activate autofocus if the camera supports it."""
    try:
        # Example control for autofocus. Adjust control name/value as needed.
        #picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous,"AfWindows": (0.4, 0.4, 0.2, 0.2)})
        #picam2.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 0.0})
        picam2.set_controls({
            "AfMode": controls.AfModeEnum.Continuous,
            "AfRange": controls.AfRangeEnum.Normal,
            "AfWindows": [(16384, 16384, 49152, 49152)],
        })
        print("Autofocus activated.")
    except Exception as e:
        print("Error activating autofocus:", e)

def capture_photo():
    """Capture a photo using Picamera2 and save it."""
    global captured_files
    try:
        # Capture the image in RGB format.
        image = picam2.capture_array()
        # Convert image from RGB to BGR for OpenCV.
        image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        # Create a unique filename using the current timestamp.
        filename = f"Photos\\capture_{int(time())}.jpg"
        cv2.imwrite(filename, image_bgr)
        print(f"Image captured and saved as {filename}")
        captured_files.append(filename)
    except Exception as e:
        print("Error capturing image:", e)

def button_press_handler():
    """Handle a button press.
    
    Before timelapse starts, count presses and activate timelapse when 5 presses occur within 1.5 seconds intervals.
    After timelapse starts, capture photos on each press.
    """
    global last_press_time, timelapse_active, timelapse_stop, startup_press_count, last_start_press_time, end_press_count
    now = time()
    led.toggle()
    if not timelapse_active:
        # In startup phase: count the consecutive presses.
        if startup_press_count == 0 or (now - last_start_press_time <= 0.8):
            startup_press_count += 1
        else:
            # Reset if too much time has passed.
            startup_press_count = 1
        last_start_press_time = now
        print(f"Startup button press count: {startup_press_count}")
        if startup_press_count >= 5:
            timelapse_active = True
            last_press_time = now
            print("Timelapse started! Press the button to take photos.")
            enable_autofocus()
        return
    else:
        if end_press_count == 0 or (now - last_press_time <= 0.8):
            end_press_count += 1
        else:
            # Reset if too much time has passed.
            end_press_count = 1
            capture_photo()
        # Timelapse is active: update last press time, give LED feedback and capture photo.
        last_press_time = now
        print(f"End button press count: {end_press_count}")
        if end_press_count >= 5:
            print("Timelapse ended.")
            timelapse_stop = True
            end_press_count = 0
            led.off()
        return
    

# Attach the event to the button press.
button.when_pressed = button_press_handler
button.when_released = led.off

# Inform the user how to start the timelapse.
print("Press the button 5 times, with no more than 0.8 seconds between presses, to start timelapse capture.")
 
try:
    # Main loop monitoring inactivity after timelapse starts.
    while True:
        sleep(0.1)
        if timelapse_active:
            # End timelapse if 5 minutes (300 seconds) have passed since the last button press.
            if time() - last_press_time >= 60 * 5:
                print("No button press for 5 minutes. Timelapse ended.")
                break
            elif timelapse_stop:
                print("Timelapse ended by button press.")
                break

except KeyboardInterrupt:
    print("\nExiting program.")

# Stop camera preview and release resources.
picam2.stop_preview()
picam2.close()

# Combine captured images into a timelapse video if any photos were taken.
if captured_files:
    # Sort files (filenames include timestamps so they sort correctly).
    captured_files.sort()
    # Read the first image to determine frame size.
    first_frame = cv2.imread(captured_files[0])
    height, width, _ = first_frame.shape

    # Define video filename and create a VideoWriter object.
    video_filename = "timelapse.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"avc1")
    fps = 30  # Adjust frames per second as needed.
    video_writer = cv2.VideoWriter(video_filename, fourcc, fps, (width, height))

    for fname in captured_files:
        frame = cv2.imread(fname)
        if frame is None:
            print(f"Warning: Could not read {fname}, skipping.")
            continue
        video_writer.write(frame)

    video_writer.release()
    print(f"Timelapse video created as {video_filename}")

    # Delete the captured JPG files after video creation.
    for fname in captured_files:
        try:
            os.remove(fname)
            print(f"Deleted {fname}")
        except Exception as e:
            print(f"Failed to delete {fname}: {e}")
else:
    print("No images were captured, so no timelapse video was created.")