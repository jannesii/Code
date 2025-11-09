"""Operational settings pages: logs and API keys."""
from __future__ import annotations

import logging

from flask import render_template, request
from flask_login import login_required, current_user

from ...utils import (
    get_ctrl,
    require_admin_or_redirect,
    flash_error, flash_success,
)

from .routes import web_bp


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@web_bp.route('/settings/logs')
@login_required
def logs():
    guard = require_admin_or_redirect(
        "Sinulla ei ole oikeuksia tarkastella lokitietoja.", 'web.get_settings_page')
    if guard:
        return guard
    ctrl = get_ctrl()
    logs = ctrl.get_logs(limit=200)
    return render_template('logs.html', logs=logs)


@web_bp.route('/settings/api_keys', methods=['GET', 'POST'])
@login_required
def api_keys():
    """Manage API keys: create and delete (secure storage)."""
    guard = require_admin_or_redirect(
        "Sinulla ei ole oikeuksia hallita API-avaimia.", 'web.get_settings_page')
    if guard:
        return guard

    ctrl = get_ctrl()
    created_token: str | None = None

    if request.method == 'POST':
        if 'create_key' in request.form:
            name = (request.form.get('key_name') or '').strip()
            if not name:
                flash_error('Anna nimi API-avaimelle.')
            else:
                # Prevent duplicate names (case-insensitive)
                existing = ctrl.list_api_keys()
                if any(k.name.lower() == name.lower() for k in existing):
                    flash_error('Samanniminen API-avain on jo olemassa.')
                else:
                    try:
                        _, token = ctrl.create_api_key(
                            name=name, created_by=current_user.get_id())
                        created_token = token  # show once
                        flash_success('API-avain luotu.')
                    except Exception as e:
                        flash_error(f'API-avaimen luonti epäonnistui: {e}')
        elif 'delete_key' in request.form:
            key_id = (request.form.get('delete_key') or '').strip()
            if not key_id:
                flash_error('Virheellinen avaimen tunniste.')
            else:
                try:
                    ctrl.delete_api_key(key_id)
                    flash_success('API-avain poistettu.')
                except Exception as e:
                    flash_error(f'Poisto epäonnistui: {e}')
        # Fall through to render

    keys = ctrl.list_api_keys()
    return render_template('api_keys.html', keys=keys, created_key=created_token)

