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

def continuous_stream_update(camera, controller):
    """
    Continuously capture frames at a low framerate and update the shared stream image.
    """
    global streaming_active
    while streaming_active and not controller.timelapse_active:
        with camera_lock:
            try:
                # Capture a frame for the stream.
                frame = camera.capture_array()
            except Exception as e:
                print("Error capturing stream frame:", e)
                sleep(0.2)
                continue
        # Convert the frame to BGR for JPEG encoding.
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        ret, jpeg = cv2.imencode('.jpg', frame_bgr)
        if ret:
            stream_state.latest_frame_jpeg = jpeg.tobytes()
            # Emit a SocketIO event to notify clients of a new frame.
            socketio.emit('update_frame')
        sleep(1)  # Update at 1 FPS (adjust as needed)

class TimelapseController:
    def __init__(self, picam2, red_led, yellow_led, green_led, capture_button):
        self.picam2 = picam2
        self.red_led = red_led
        self.yellow_led = yellow_led
        self.green_led = green_led
        

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
        capture_button.when_released = self.red_led_off
        
        self.enable_autofocus()

    def red_led_off(self):
        self.red_led.off()

    def enable_autofocus(self):
        """Activate autofocus and autoexposure if the camera supports it."""
        try:
            self.picam2.set_controls({
                "AfMode": controls.AfModeEnum.Continuous,
                "AfRange": controls.AfRangeEnum.Normal,
                "AfWindows": [(16384, 16384, 49152, 49152)],
                "ExposureValue": -0.5,
            })
            print("Autofocus activated.")
        except Exception as e:
            print("Error activating autofocus:", e)

    def capture_photo(self):
        """Capture a photo, update the streaming image and save it."""
        try:
            with camera_lock:
                image = self.picam2.capture_array()
            image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            filename = f"Photos/capture_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.jpg"
            cv2.imwrite(filename, image_bgr)
            print(f"Image captured and saved as {filename}")
            self.captured_files.append(filename)
            ret, jpeg = cv2.imencode('.jpg', image_bgr)
            if ret:
                stream_state.latest_frame_jpeg = jpeg.tobytes()
                # Emit an event so the browser gets the new frame immediately.
                socketio.emit('update_frame')
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
        self.red_led.toggle()
        now = time()
        self.last_press_time = now
        self.button_press_count += 1
        print("Button pressed; count:", self.button_press_count)
        self.reset_timer()

    def process_button_sequence(self):
        """Called after cutoff_time has passed with no new button press.
           Determines which action to take based on the count of presses."""
        global streaming_active
        count = self.button_press_count
        print("Processing button sequence with count:", count)
        self.button_press_count = 0  # reset counter for next sequence

        # --- BEFORE TIMELAPSE START ---
        if not self.timelapse_active:
            if count >= self.startup_count:
                self.green_led.on()
                streaming_active = False  # stop continuous streaming
                self.timelapse_active = True
                print("Timelapse started! Use the same button for actions.")
                #self.enable_autofocus()
            else:
                print("Not enough presses to start timelapse.")
            return

        # --- WHEN TIMELAPSE IS ACTIVE ---
        # If timelapse is paused, 4 quick presses will resume it.
        if self.timelapse_paused:
            if count >= self.pause_count:
                self.yellow_led.off()
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
            self.yellow_led.on()
            self.timelapse_paused = True
            print("Timelapse paused.")
        elif count == self.end_count:
            # 3 quick presses trigger ending the timelapse.
            print("Timelapse ended.")
            self.timelapse_stop = True
            self.red_led.off()
            self.green_led.off()
        else:
            print("Unrecognized press sequence:", count)

def create_timelapse_video(image_files):
    """Combine captured images into a timelapse video and delete the images."""
    image_files.sort()
    first_frame = cv2.imread(image_files[0])
    height, width, _ = first_frame.shape

    default_fps = 25  # Use 25 fps if enough images.
    num_images = len(image_files)
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
    red_led = LED(RED_LED_PIN)
    yellow_led = LED(YELLOW_LED_PIN)
    green_led = LED(GREEN_LED_PIN)
    capture_button = Button(CAPTURE_BUTTON_PIN, pull_up=True, bounce_time=0.01)
    # The pause_button is defined but not used in this implementation.

    # Initialize and configure the camera.
    picam2 = Picamera2()
    config = picam2.create_still_configuration()
    picam2.configure(config)
    picam2.start_preview()
    picam2.start()
    sleep(2)  # Allow camera settings to settle

    # Create timelapse controller.
    controller = TimelapseController(picam2, red_led, yellow_led, green_led, capture_button)

    # Start the continuous streaming thread (only active before timelapse starts).
    stream_thread = threading.Thread(target=continuous_stream_update, args=(picam2, controller), daemon=True)
    stream_thread.start()

    # Start the Flask streaming server in its own thread.
    server_thread = threading.Thread(target=stream_server.run_server, daemon=True)
    server_thread.start()

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
