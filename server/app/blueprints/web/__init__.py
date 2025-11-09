"""Web (HTML) routes aggregator.

Defines the `web` blueprint and imports per-area modules that attach
handlers via `@web_bp.route`.
"""

from flask import Blueprint

web_bp = Blueprint('web', __name__)

# Import modules to register routes on the shared `web_bp` blueprint
from . import (
    pages_web,
    settings_core_web,
    settings_users_web,
    settings_ops_web,
    settings_timelapse_web,
    settings_novpn_web,
)
