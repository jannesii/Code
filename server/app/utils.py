import logging
from threading import Timer
from flask import session, flash, current_app

logger = logging.getLogger(__name__)

def _pop_flashes(app) -> None:
    """
    Background callback: remove all flashes from session
    inside the given app context.
    """
    try:
        with app.app_context():
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
        "Flashed %r with category %r; will clear in %ds",
        message, category, delay
    )

    # Grab the real Flask app object
    app = current_app._get_current_object()

    # Schedule the pop, passing in the app so we can push a context later
    timer = Timer(delay, _pop_flashes, args=(app,))
    timer.daemon = True
    timer.start()
