from picamera2 import Picamera2
import cv2
from time import sleep

picam2 = Picamera2()
config = picam2.create_preview_configuration()

# Adjust the preview resolution if supported (example: 1920x1080)
config["main"]["size"] = (1920, 1080)

picam2.configure(config)
picam2.start()

sleep(2)

while True:
    frame = picam2.capture_array()
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    cv2.imshow("Live Feed", frame_bgr)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
picam2.stop()
picam2.close()