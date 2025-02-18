from gpiozero import LED
import time

led = LED(17)

while True:
    print("Turning LED ON")
    led.on()
    time.sleep(2)
    print("Turning LED OFF")
    led.off()
    time.sleep(2)
