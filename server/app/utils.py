from threading import Timer
from flask import session

def __pop_flashes() -> None:
    """Remove all flashes from the session."""
    session.pop('_flashes', None)

def pop_flashes(delay: int = 3) -> None:
    """Remove all flashes from the session."""
    Timer(delay, __pop_flashes).start()