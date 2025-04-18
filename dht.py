import time
import logging

try:
    import Adafruit_DHT
except ImportError:
    raise ImportError("Adafruit_DHT library not found. Install with `pip install Adafruit_DHT`.")

class DHT22Sensor:
    """
    Class to interface with a DHT22 temperature and humidity sensor.

    Usage:
        sensor = DHT22Sensor(pin=4, retries=5, delay=2)
        temp, hum = sensor.read()
    """
    def __init__(self, pin: int, retries: int = 3, delay: float = 2.0):
        """
        Initialize the DHT22 sensor interface.

        :param pin: GPIO pin number (BCM) where the data line is connected.
        :param retries: Number of read attempts before giving up.
        :param delay: Delay in seconds between retries.
        """
        self.pin = pin
        self.sensor = Adafruit_DHT.DHT22
        self.retries = retries
        self.delay = delay
        self.temperature = None
        self.humidity = None

        # Configure logging
        self.logger = logging.getLogger(self.__class__.__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def read(self) -> tuple[float, float]:
        """
        Attempt to read the sensor. Updates self.temperature and self.humidity on success.

        :returns: (temperature_C, humidity_percent)
        :raises RuntimeError: If sensor data could not be read.
        """
        self.logger.info(f"Reading DHT22 at GPIO pin {self.pin} (retries={self.retries}, delay={self.delay}s)")
        for attempt in range(1, self.retries + 1):
            humidity, temperature = Adafruit_DHT.read_retry(
                self.sensor,
                self.pin,
                retry_count=1,
                delay_seconds=self.delay
            )
            if humidity is not None and temperature is not None:
                self.temperature = temperature
                self.humidity = humidity
                self.logger.info(f"Read successful: Temp={temperature:.1f}°C, Hum={humidity:.1f}%")
                return temperature, humidity
            else:
                self.logger.warning(f"Attempt {attempt} failed, retrying in {self.delay}s...")
                time.sleep(self.delay)

        err = f"Failed to read from DHT22 after {self.retries} attempts"
        self.logger.error(err)
        raise RuntimeError(err)

    def get_temperature(self) -> float:
        """
        Get last read temperature value.

        :returns: temperature in Celsius
        :raises RuntimeError: If no successful read has occurred.
        """
        if self.temperature is None:
            raise RuntimeError("Temperature not yet read. Call read() first.")
        return self.temperature

    def get_humidity(self) -> float:
        """
        Get last read humidity value.

        :returns: relative humidity in percent
        :raises RuntimeError: If no successful read has occurred.
        """
        if self.humidity is None:
            raise RuntimeError("Humidity not yet read. Call read() first.")
        return self.humidity
