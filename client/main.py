#!/usr/bin/env python3
import logging
import os


from src import execute_main_loop

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logging.getLogger("socketio.client").setLevel(logging.WARNING)
logging.getLogger("picamera2").setLevel(logging.INFO)

if __name__ == "__main__":
    execute_main_loop()
