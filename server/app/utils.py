import logging
from threading import Timer
from flask import session, flash, current_app

logger = logging.getLogger(__name__)

def check_vals(image_delay: int, temphum_delay: int, status_delay: int):
    """Check if the values are valid."""
    logger.debug("Checking values: image_delay=%s, temphum_delay=%s, status_delay=%s", image_delay, temphum_delay, status_delay)
    
    try:
        ret = []
        if (image_delay < 5):
            msg, cat = "Kuvan viiveen on oltava suurempi tai yhtä suuri kuin 5 sekuntia.", "error"
            ret.append({"msg": msg, "cat": cat})
        if (temphum_delay <= 0):
            msg, cat = "Lämpötilan ja kosteuden viiveen on oltava suurempi kuin 0 sekuntia.", "error"
            ret.append({"msg": msg, "cat": cat})
        if (status_delay <= 0):
            msg, cat = "Tilatiedon viiveen on oltava suurempi kuin 0 sekuntia.", "error"
            ret.append({"msg": msg, "cat": cat})
    except ValueError as ve:
        msg, cat = "Virheellinen syöte: " + str(ve), "error"
        ret.append({"msg": msg, "cat": cat})
    
    return ret
