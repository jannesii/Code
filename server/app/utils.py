import logging
from flask import session, flash, current_app, redirect, url_for
from flask_login import current_user
from typing import Optional, Tuple
from datetime import datetime
import pytz

from .controller import Controller

logger = logging.getLogger(__name__)

def check_vals(image_delay: int, temphum_delay: int, status_delay: int):
    """Check if the values are valid."""
    logger.debug("Checking values: image_delay=%s, temphum_delay=%s, status_delay=%s", image_delay, temphum_delay, status_delay)
    
    ret = []
    try:
        if (image_delay <= 0):
            msg, cat = "Kuvan viiveen on oltava suurempi kuin 0 sekuntia.", "error"
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


# --- Web helpers to reduce repetition ---

def get_ctrl() -> Controller:
    """Return the shared Controller instance from the Flask app."""
    return current_app.ctrl  # type: ignore


def require_admin_or_redirect(message: str, redirect_endpoint: str):
    """If current user is not admin, flash message and return a redirect.
    Caller should check and return this value if not None.
    """
    if not getattr(current_user, 'is_admin', False):
        flash(message, 'error')
        logger.warning("Non-admin user %s blocked: %s", current_user.get_id(), message)
        return redirect(url_for(redirect_endpoint))
    return None


def combine_local_date_time(date_str: str, time_str: str, tz_name: str = 'Europe/Helsinki') -> str:
    """Combine HTML date (YYYY-MM-DD) and time (HH:MM) into ISO string in given timezone.
    Raises ValueError on invalid input.
    """
    if not date_str or not time_str:
        raise ValueError('Missing date or time')
    fin = pytz.timezone(tz_name)
    dt_naive = datetime.fromisoformat(f"{date_str}T{time_str}")
    dt_local = fin.localize(dt_naive)
    return dt_local.isoformat()


def can_edit_user(user) -> Tuple[bool, Optional[str]]:
    """Return False and a message if the target user cannot be edited."""
    if getattr(user, 'is_root_admin', False):
        return False, 'Et voi muokata Root-Admin tiliä.'
    return True, None


def can_delete_user(target_user, acting_user_id: str) -> Tuple[bool, Optional[str]]:
    """Return False and a message if the target user cannot be deleted."""
    if getattr(target_user, 'is_root_admin', False):
        return False, 'Et voi poistaa Root-Admin tiliä.'
    if getattr(target_user, 'username', None) == acting_user_id:
        return False, 'Et voi poistaa omaa tiliäsi.'
    return True, None
