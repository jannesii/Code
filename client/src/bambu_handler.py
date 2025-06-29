from time import sleep
import logging
import os
import bambulabs_api as bl

logger = logging.getLogger(__name__)


class BambuHandler:

    _instance: "BambuHandler | None" = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        IP = os.getenv("BAMBU_IP")
        ACCESS_CODE = os.getenv("BAMBU_SERIAL")
        SERIAL = os.getenv("BAMBU_ACCESS_CODE")

        self.printer = bl.Printer(IP, ACCESS_CODE, SERIAL)

        self.printer.mqtt_start()

        while not self.printer.mqtt_client_ready():
            logger.info("Connecting to printer...")
            sleep(1)
        sleep(2)
        logger.info("Printer connected!")

    def pause_print(self) -> bool:
        if self.printer.pause_print():
            logger.info("Print paused successfully.")
            return True
        else:
            logger.error("Failed to pause print.")
            return False

    def resume_print(self) -> bool:
        if self.printer.resume_print():
            logger.info("Print resumed successfully.")
            return True
        else:
            logger.error("Failed to resume print.")
            return False

    def stop_print(self):
        if self.printer.stop_print():
            logger.info("Print stopped successfully.")
            return True
        else:
            logger.error("Failed to stop print.")
            return False
    def stop_print(self):
        if self.printer.stop_print():
            logger.info("Print stopped successfully.")
            return True
        else:
            logger.error("Failed to stop print.")
            return False
        
    def home_printer(self):
        if self.printer.home_printer():
            logger.info("Printer homed successfully.")
            return True
        else:
            logger.error("Failed to home printer.")
            return False

    def prepare_for_photo(self):
        gcode = [
            "G92 E0",
            "G17",
            "G2 Z{layer_z + 0.4} I0.86 J0.86 P1 F20000 ; spiral lift a little",
            "G1 Z{max_layer_z + 0.4}",
            "G1 X-48.2 Y128 F18000 ; move to safe pos",
            "M400 P1700",
            "G1 X-28.2 F18000",
            "G1 X-48.2 F18000 ; move to safe pos",
            "G1 X-28.2 F18000",
            "G1 X-48.2 F18000 ; move to safe pos",
            "G1 X-28.2 F18000",
            "G1 X-48.2 F18000 ; move to safe pos",
            "G1 X-28.2 F18000",
        ]

        try:
            if self.gcode_status == "RUNNING" and self.status == "PRINTING":
                logger.info("Preparing for photo...")
                return self.printer.gcode(gcode=gcode, gcode_check=False)
        except ValueError as e:
            logger.exception(e)

    def to_dict(self) -> dict:
        """Return all @property values automatically."""
        props = {
            name: attr
            for name, attr in type(self).__dict__.items()
            if isinstance(attr, property)
        }
        return {name: getattr(self, name) for name in props}

    @property
    def bed_temperature(self) -> (float | None):
        """Current bed temperature (°C)."""
        return round(self.printer.get_bed_temperature(), 2)

    @property
    def nozzle_temperature(self) -> (float | None):
        """Current nozzle temperature (°C)."""
        return round(self.printer.get_nozzle_temperature(), 2)

    @property
    def file_name(self) -> str:
        """Name of the file currently printing."""
        return self.printer.get_file_name()

    @property
    def percentage(self) -> (int | str | None):
        """Print completion percentage (0–100)."""
        return self.printer.get_percentage()

    @property
    def remaining_time(self) -> (int | str | None):
        """Elapsed print time (in seconds)."""
        return self.printer.get_time()

    @property
    def print_speed(self) -> int:
        """Current print speed (mm/s or as reported by the printer)."""
        return self.printer.get_print_speed()

    @property
    def current_layer(self) -> int:
        """Index of the layer currently being printed."""
        return self.printer.current_layer_num()

    @property
    def total_layers(self) -> int:
        """Total number of layers in the print job."""
        return self.printer.total_layer_num()

    @property
    def nozzle_type(self) -> str:
        """Type of the nozzle (as reported by the printer)."""
        nozzle = self.printer.nozzle_type().name
        if "_" in nozzle:
            parts = nozzle.split("_")
            return " ".join(parts)
        return nozzle

    @property
    def nozzle_diameter(self) -> float:
        """Diameter of the nozzle (mm)."""
        return self.printer.nozzle_diameter()

    @property
    def print_error_code(self) -> int:
        """Last error code from the printer (0 if no error)."""
        return self.printer.print_error_code()

    @property
    def status(self) -> str:
        status = self.printer.get_current_state().name

        if "_" in status:
            parts = status.split("_")
            return " ".join(parts)
        return status

    @property
    def gcode_status(self) -> str:
        status = self.printer.get_state().name
        return status
