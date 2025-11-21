"""Car heater control and status page."""
from __future__ import annotations

import logging
from dataclasses import asdict

from flask import render_template, current_app
from flask_login import login_required, current_user

from ...utils import get_ctrl
from ...core import Controller, CarHeaterStatus

from . import web_bp


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@web_bp.route('/car_heater', methods=['GET'])
@login_required
def get_car_heater_page():
    """Render the car heater dashboard page."""
    ctrl: Controller = get_ctrl()
    logger.info("Rendering car heater page for %s", current_user.get_id())

    last: CarHeaterStatus | None = ctrl.get_last_car_heater_status()
    last_status = asdict(last) if last is not None else None

    return render_template(
        'car_heater.html',
        last_status=last_status,
    )

