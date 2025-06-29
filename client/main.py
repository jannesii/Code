#!/usr/bin/env python3
import logging


from src import execute_main_loop

logging.basicConfig(
    level=logging.DEBUG,      # show INFO+ from the root
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
)

if __name__ == "__main__":
    execute_main_loop()
