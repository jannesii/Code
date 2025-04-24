import logging
from threading import Timer
from flask import session, flash, current_app

logger = logging.getLogger(__name__)

def _pop_flashes() -> None:
    """
    Background callback: remove all flashes from session
    inside a fresh app context.
    """
    try:
        with current_app.app_context():
            session.pop('_flashes', None)
            logger.info("Popped all flashes from session")
    except Exception as e:
        logger.error("Failed to pop flashes: %s", e)

def flash_with_timeout(
    message: str,
    category: str = 'info',
    delay: int = 3
) -> None:
    """
    Flash a message and schedule a session pop after `delay` seconds.
    """
    flash(message, category)
    logger.info(
        "Flashed message %r with category %r (will clear in %ds)",
        message, category, delay
    )
    Timer(delay, _pop_flashes).start()
