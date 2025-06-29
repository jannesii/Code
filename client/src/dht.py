import time
import board
import adafruit_dht
import logging

logger = logging.getLogger(__name__)

class DHT22Sensor:
    """
    CircuitPython-based DHT22 interface supporting both board pin objects and BCM pin numbers.

    Usage:
        sensor = DHT22Sensor(pin=board.D4)
        # or
        sensor = DHT22Sensor(pin=24)  # BCM24
        temp, hum = sensor.read()
    """
    def __init__(self, pin, retries=3, delay=2.0, logger=None):
        """
        Initialize the DHT22 sensor interface.

        :param pin: GPIO pin object from board module or an integer BCM pin number.
        :param retries: Number of read attempts before giving up.
        :param delay: Delay in seconds between retries.
        """
        # Accept integer BCM pin by converting to board pin
        if isinstance(pin, int):
            pin_name = f"D{pin}"
            try:
                pin = getattr(board, pin_name)
            except AttributeError:
                raise ValueError(f"Invalid BCM pin number: {pin}")

        self.dht = adafruit_dht.DHT22(pin, use_pulseio=False)
        self.retries = retries
        self.delay = delay
        self.temperature = None
        self.humidity = None

    def read(self) -> dict:
        """
        Try up to self.retries times to read temperature and humidity.

        :returns: (temperature_C, humidity_percent)
        :raises RuntimeError: If sensor data could not be read.
        """
        for attempt in range(1, self.retries + 1):
            try:
                temp = self.dht.temperature
                hum = self.dht.humidity
                if temp is not None and hum is not None:
                    self.temperature = temp
                    self.humidity = hum
                    logger.info(f"Read OK: {temp:.1f}°C, {hum:.1f}%")
                    return {'temperature': self.temperature, 'humidity': self.humidity}
            except RuntimeError as e:
                logger.warning(
                    f"Attempt {attempt} failed ({e}), retrying in {self.delay}s...")
                time.sleep(self.delay)
            except Exception as e:
                logger.error(f"Fatal DHT error: {e}")
                raise
        msg = f"Failed DHT read after {self.retries} attempts"
        logger.error(msg)
        raise RuntimeError(msg)

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
