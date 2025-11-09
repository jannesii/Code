"""Web (HTML) routes aggregator.

Defines the `web` blueprint and imports per-area modules that attach
handlers via `@web_bp.route`.
"""

from flask import Blueprint

web_bp = Blueprint('web', __name__)
