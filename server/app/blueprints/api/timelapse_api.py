"""Timelapse configuration API routes.

Endpoints:
- /timelapse_config (GET)
"""
from __future__ import annotations

import logging

from flask import Blueprint, jsonify, current_app
from flask import request  # kept for parity, not currently used
from flask_login import login_required, current_user

from ...core.controller import Controller


timelapse_bp = Blueprint("api_timelapse", __name__, url_prefix="")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@timelapse_bp.route('/timelapse_config')
@login_required
def get_timelapse_config():
    ctrl: Controller = current_app.ctrl  # type: ignore
    conf = ctrl.get_timelapse_conf()
    vals = {
        'image_delay':   conf.image_delay,
        'temphum_delay': conf.temphum_delay,
        'status_delay':  conf.status_delay
    } if conf else {}
    logger.info(
        "API /timelapse_config by %s",
        current_user.get_id()
    )
    return jsonify(vals)

