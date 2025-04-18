import time
import board
import adafruit_dht
import logging

class DHT22Sensor:
    """
    CircuitPython-based DHT22 interface.
    Usage:
        sensor = DHT22Sensor(pin=board.D4)
        temp, hum = sensor.read()
    """
    def __init__(self, pin, retries=3, delay=2.0):
        # pin: e.g. board.D4 (BCM4)
        self.dht = adafruit_dht.DHT22(pin, use_pulseio=False)
        self.retries = retries
        self.delay = delay
        self.temperature = None
        self.humidity = None

        # Setup logging
        self.logger = logging.getLogger(self.__class__.__name__)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s"))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def read(self):
        """Try up to self.retries times to get a reading."""
        for i in range(1, self.retries + 1):
            try:
                temp = self.dht.temperature
                hum  = self.dht.humidity
                if temp is not None and hum is not None:
                    self.temperature = temp
                    self.humidity = hum
                    self.logger.info(f"Read OK: {temp:.1f}°C, {hum:.1f}%")
                    return temp, hum
            except RuntimeError as e:
                self.logger.warning(
                    f"Attempt {i} failed ({e}), retrying in {self.delay}s…")
                time.sleep(self.delay)
            except Exception as e:
                self.logger.error(f"Fatal DHT error: {e}")
                raise
        msg = f"Failed DHT read after {self.retries} attempts"
        self.logger.error(msg)
        raise RuntimeError(msg)

    def get_temperature(self):
        if self.temperature is None:
            raise RuntimeError("Call read() first")
        return self.temperature

    def get_humidity(self):
        if self.humidity is None:
            raise RuntimeError("Call read() first")
        return self.humidity
