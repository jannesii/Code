"""Web (HTML) routes."""
import logging
from operator import ne
from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from flask_login import login_required, current_user
from dataclasses import asdict
import time
from ...utils import (
    check_vals, get_ctrl, require_admin_or_redirect, combine_local_date_time,
    can_edit_user, can_delete_user, flash_error, flash_success, flash_info,
    get_new_password_pair, validate_password_pair,
)
from ...core.controller import Controller


web_bp = Blueprint('web', __name__)
logger = logging.getLogger(__name__)


@web_bp.route('/')
@login_required
def get_home_page():
    logger.info("Rendering home for %s", current_user.get_id())
    return render_template('index.html')


@web_bp.route('/3d')
@login_required
def get_3d_page():
    ctrl: Controller = get_ctrl()
    logger.info("Rendering 3D page for %s", current_user.get_id())
    img = ctrl.get_last_image()
    th = ctrl.get_last_temphum()
    st = ctrl.get_last_status()
    return render_template(
        '3d.html',
        last_image=asdict(img) if img else None,
        last_temphum=asdict(th) if th else None,
        last_status=asdict(st) if st else None,
    )


@web_bp.route('/temperatures', methods=['GET'])
@login_required
def get_temperatures_page():
    ctrl: Controller = get_ctrl()
    locations = ctrl.get_unique_locations()
    logger.info("Rendering temperatures page for %s", current_user.get_id())
    return render_template('temperatures.html', locations=locations)


@web_bp.route('/settings')
@login_required
def get_settings_page():
    logger.info("Rendering settings for %s", current_user.get_id())
    return render_template('settings.html')


@web_bp.route('/settings/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    ctrl: Controller = get_ctrl()
    # Root-Admin cannot change password (by requirement)
    me = ctrl.get_user_by_username(current_user.get_id(), include_pw=False)
    if me and getattr(me, 'is_root_admin', False):
        flash_error('Root-Admin ei voi vaihtaa salasanaa.')
        return redirect(url_for('web.get_settings_page'))

    if request.method == 'POST':
        current_pw = (request.form.get('current_password') or '').strip()
        new_pw, confirm_pw = get_new_password_pair(request.form)

        # Validate input
        if not current_pw:
            flash_error('Syötä nykyinen salasana.')
            return render_template('change_password.html')
        ok, msg = validate_password_pair(new_pw, confirm_pw, required=True, min_len=6)
        if not ok:
            flash_error(msg or 'Virheellinen salasana.')
            return render_template('change_password.html')

        # Verify current password
        if not ctrl.authenticate_user(current_user.get_id(), current_pw):
            flash_error('Nykyinen salasana on virheellinen.')
            return render_template('change_password.html')

        # Update password
        try:
            ctrl.update_user(current_username=current_user.get_id(), password=new_pw)
            ctrl.log_message(log_type='info', message=f"User {current_user.get_id()} changed password")
            flash_success('Salasana vaihdettu.')
            return redirect(url_for('web.get_settings_page'))
        except Exception as e:
            flash_error(f"Salasanan vaihto epäonnistui: {e}")
            return render_template('change_password.html')

    return render_template('change_password.html')


@web_bp.route('/settings/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    ctrl: Controller = get_ctrl()
    guard = require_admin_or_redirect("Sinulla ei ole oikeuksia lisätä käyttäjiä.", 'web.user_list')
    if guard:
        return guard
    if request.method == 'POST':
        u = (request.form.get('username') or '').strip()
        p, p2 = get_new_password_pair(request.form)
        ok, msg = validate_password_pair(p, p2, required=True, min_len=6)
        if not ok:
            flash_error(msg or 'Virheellinen salasana.')
            return render_template('add_user.html')
        is_temp = bool(request.form.get('is_temporary'))
        duration_value = int(request.form.get(
            'duration_value', '1')) if is_temp else None
        duration_unit = request.form.get(
            'duration_unit', 'hours') if is_temp else None
        logger.debug("Adding user %s", u)
        try:
            if is_temp:
                logger.info("Adding temporary user %s (temporary=%s, duration=%s %s)",
                            u, is_temp, duration_value, duration_unit)
                ctrl.create_temporary_user(u, p, duration_value, duration_unit)
                flash_success(f"Väliaikainen käyttäjä «{u}» lisätty onnistuneesti.")
            else:
                ctrl.register_user(u, p)
                flash_success(f"Käyttäjä «{u}» lisätty onnistuneesti.")
            logger.info("User %s added by %s", u, current_user.get_id())
            return redirect(url_for('web.user_list'))
        except ValueError as ve:
            flash_error(str(ve))
            logger.warning("Add user failed: %s", ve)

    return render_template('add_user.html')


@web_bp.route('/settings/delete_user', methods=['GET', 'POST'])
@login_required
def delete_user():
    ctrl: Controller = current_app.ctrl  # type: ignore
    users = ctrl.get_all_users(exclude_admin=True, exclude_current=True)
    if not current_user.is_admin:
        flash("Sinulla ei ole oikeuksia poistaa käyttäjiä.", "error")
        logger.warning(
            "Non-admin user %s attempted to delete user.", current_user.get_id())
        return redirect(url_for('web.get_settings_page'))
    if request.method == 'POST':
        if 'delete_temp_users' in request.form:
            try:
                ctrl.delete_temporary_users()
                flash("Kaikki väliaikaiset käyttäjät poistettu.", "success")
            except Exception as e:
                flash(
                    f"Väliaikaisten käyttäjien poisto epäonnistui: {e}", "error")
                return render_template('delete_user.html', users=users)
        else:
            u = request.form.get('username')
            if not u:
                flash("Valitse ensin käyttäjä.", "error")
                logger.warning("No user selected for deletion")
                return redirect(url_for('web.get_settings_page'))
            if u == current_user.get_id():
                flash("Et voi poistaa omaa tiliäsi.", "error")
                logger.warning("Self‑deletion attempt by %s", u)
            else:
                try:
                    ctrl.delete_user(u)
                    flash(f"Käyttäjä «{u}» poistettu.", "success")
                    logger.info("User %s deleted by %s",
                                u, current_user.get_id())
                except Exception as e:
                    flash(f"Poisto epäonnistui: {e}", "error")
                    logger.error("Error deleting %s: %s", u, e)
                    return render_template('delete_user.html', users=users)
        return redirect(url_for('web.get_settings_page'))

    for user in users:
        logger.info("User %s: %s", user.username, asdict(user))
    return render_template('delete_user.html', users=users)


@web_bp.route('/settings/timelapse_conf', methods=['GET', 'POST'])
@login_required
def timelapse_conf():
    ctrl: Controller = current_app.ctrl  # type: ignore
    vals = {}
    if not current_user.is_admin:
        flash("Sinulla ei ole oikeuksia muuttaa asetuksia.", "error")
        logger.warning(
            "Non-admin user %s attempted to change timelapse settings", current_user.get_id())
        return redirect(url_for('web.get_settings_page'))
    if request.method == 'POST':
        try:
            vals = {
                'image_delay':   int(request.form.get('image_delay', '0')),
                'temphum_delay': int(request.form.get('temphum_delay', '0'))*60,
                'status_delay':  int(request.form.get('status_delay', '0'))
            }

            logger.debug("Timelapse config: %s", vals)
            check_failed = check_vals(**vals)

            if check_failed:
                for c in check_failed:
                    flash(c['msg'], c['cat'])
                logger.warning("Invalid timelapse input: %s", check_failed)
                return render_template('timelapse_conf.html', **vals)
            else:
                ctrl.update_timelapse_conf(**vals)
                # Emit only to connected timelapse clients (not to views)
                try:
                    from ...sockets.handlers import SocketEventHandler
                    handler = SocketEventHandler(current_app.socketio, ctrl)  # type: ignore
                    handler.emit_to_clients('timelapse_conf', vals)
                except Exception:
                    # Fallback to broadcast if handler unavailable
                    current_app.socketio.emit('timelapse_conf', vals)  # type: ignore
                flash("Timelapsen konfiguraatio päivitetty onnistuneesti.", "success")
                logger.info("Timelapse updated %s by %s",
                            vals, current_user.get_id())
                return redirect(url_for('web.get_settings_page'))
        except ValueError as ve:
            flash(str(ve), "error")
            logger.warning("Invalid timelapse input: %s", ve)
    else:
        conf = ctrl.get_timelapse_conf()
        if conf:
            vals = {
                'image_delay':   conf.image_delay,
                'temphum_delay': int(conf.temphum_delay/60),
                'status_delay':  conf.status_delay
            }
    return render_template(
        'timelapse_conf.html',
        **vals
    )


@web_bp.route('/settings/users', methods=['GET', 'POST'])
@login_required
def user_list():
    ctrl: Controller = get_ctrl()
    guard = require_admin_or_redirect("Sinulla ei ole oikeuksia hallita käyttäjiä.", 'web.get_settings_page')
    if guard:
        return guard
    if request.method == 'POST':
        username = request.form.get('delete_user')
        if username:
            try:
                user = ctrl.get_user_by_username(username, include_pw=False)
                ok, msg = can_delete_user(user, current_user.get_id()) if user else (False, 'Käyttäjää ei löytynyt.')
                if not ok:
                    flash(msg, 'error')
                    return redirect(url_for('web.user_list'))
                ctrl.delete_user(username)
                flash(f"Käyttäjä «{username}» poistettu.", "success")
            except Exception as e:
                flash(f"Poisto epäonnistui: {e}", "error")
    users = ctrl.get_all_users(
        exclude_admin=False, exclude_current=False, exclude_expired=False)
    return render_template('users.html', users=users)


@web_bp.route('/settings/users/edit/<username>', methods=['GET', 'POST'])
@login_required
def edit_user(username):
    ctrl: Controller = get_ctrl()
    user = ctrl.get_user_by_username(username, include_pw=False)
    if not current_user.is_admin:
        flash("Sinulla ei ole oikeuksia muokata käyttäjiä.", "error")
        logger.warning(
            "Non-admin user %s attempted to edit user %s", current_user.get_id(), username)
        next_url = request.args.get("next") or url_for("users.user_list")
        return redirect(next_url)
    if not user:
        flash_error('Käyttäjää ei löytynyt.')
        return redirect(url_for('web.user_list'))
    ok, msg = can_edit_user(user)
    if not ok:
        flash_error(msg)
        return redirect(url_for('web.user_list'))
    if request.method == 'POST':
        new_username = (request.form.get('username') or '').strip()
        # Support both new and legacy field names for password change
        password = (request.form.get('new_password') or request.form.get('password') or '').strip()
        password_confirm = (request.form.get('new_password_confirm') or request.form.get('password_confirm') or '').strip()
        is_admin = bool(request.form.get('is_admin'))
        is_temporary = bool(request.form.get('is_temporary'))

        expires_date = (request.form.get('expires_date') or '').strip()
        expires_time = (request.form.get('expires_time') or '').strip()
        expires_at: str | None = None
        if is_temporary and (expires_date and expires_time):
            try:
                expires_at = combine_local_date_time(expires_date, expires_time)
            except Exception:
                flash_error('Virheellinen vanhenemisaika.')
                return render_template('edit_user.html', user=user)
        elif is_temporary:
            # Allow temporary without specific expiry (left blank)
            expires_at = None

        # Validate password if provided
        if password:
            ok, msg = validate_password_pair(password, password_confirm, required=True, min_len=6)
            if not ok:
                flash_error(msg or 'Virheellinen salasana.')
                return render_template('edit_user.html', user=user)

        try:
            updated = ctrl.update_user(
                current_username=username,
                new_username=new_username or None,
                password=password or None,
                is_temporary=is_temporary,
                is_admin=is_admin,
                expires_at=expires_at,
            )
            flash_success('Käyttäjä päivitetty.')
            return redirect(url_for('web.user_list'))
        except ValueError as ve:
            flash_error(str(ve))
        except Exception as e:
            flash_error(f"Päivitys epäonnistui: {e}")
    return render_template('edit_user.html', user=user)


@web_bp.route('/settings/logs')
@login_required
def logs():
    guard = require_admin_or_redirect("Sinulla ei ole oikeuksia tarkastella lokitietoja.", 'web.get_settings_page')
    if guard:
        return guard
    ctrl: Controller = get_ctrl()
    logs = ctrl.get_logs(limit=200)
    return render_template('logs.html', logs=logs)


@web_bp.route('/settings/api_keys', methods=['GET', 'POST'])
@login_required
def api_keys():
    """Manage API keys: create and delete (secure storage)."""
    guard = require_admin_or_redirect("Sinulla ei ole oikeuksia hallita API-avaimia.", 'web.get_settings_page')
    if guard:
        return guard

    ctrl: Controller = get_ctrl()
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
                        _, token = ctrl.create_api_key(name=name, created_by=current_user.get_id())
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
