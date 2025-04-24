from threading import Timer
from flask import session

def pop_flashes(delay: int = 3) -> None:
    """Remove all flashes from the session."""
    Timer(delay, lambda: session.pop('_flashes', None)).start()