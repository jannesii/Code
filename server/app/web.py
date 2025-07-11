# app/web.py
import logging
from operator import ne
from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from flask_login import login_required, current_user
from dataclasses import asdict
from .utils import check_vals
from .controller import Controller


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
    ctrl: Controller = current_app.ctrl  # type: ignore
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


@web_bp.route('/settings')
@login_required
def get_settings_page():
    logger.info("Rendering settings for %s", current_user.get_id())
    return render_template('settings.html')


@web_bp.route('/settings/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    ctrl: Controller = current_app.ctrl  # type: ignore
    if not current_user.is_admin:
        flash("Sinulla ei ole oikeuksia lisätä käyttäjiä.", "error")
        logger.warning("Non-admin user %s attempted to add user.",
                       current_user.get_id())
        return redirect(url_for('web.user_list'))
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '')
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
                flash(
                    f"Väliaikainen käyttäjä «{u}» lisätty onnistuneesti.", 'success')
            else:
                ctrl.register_user(u, p)
                flash(f"Käyttäjä «{u}» lisätty onnistuneesti.", 'success')
            logger.info("User %s added by %s", u, current_user.get_id())
            return redirect(url_for('web.user_list'))
        except ValueError as ve:
            flash(str(ve), "error")
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
                current_app.socketio.emit(
                    'timelapse_conf', vals)  # type: ignore
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
    ctrl: Controller = current_app.ctrl  # type: ignore
    if not current_user.is_admin:
        flash("Sinulla ei ole oikeuksia hallita käyttäjiä.", "error")
        logger.warning(
            "Non-admin user %s attempted to access user management.", current_user.get_id())
        return redirect(url_for('web.get_settings_page'))
    if request.method == 'POST':
        username = request.form.get('delete_user')
        if username:
            try:
                user = ctrl.get_user_by_username(username, include_pw=False)
                if user.is_admin:
                    flash("Et voi poistaa ylläpitäjätilejä.", "error")
                    logger.warning(
                        "Attempted to delete admin user %s by %s", username, current_user.get_id())
                    return redirect(url_for('web.user_list'))
                if username == current_user.get_id():
                    flash("Et voi poistaa omaa tiliäsi.", "error")
                    logger.warning("Self-deletion attempt by %s", username)
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
    ctrl: Controller = current_app.ctrl  # type: ignore
    user = ctrl.get_user_by_username(username, include_pw=False)
    if not current_user.is_admin:
        flash("Sinulla ei ole oikeuksia muokata käyttäjiä.", "error")
        logger.warning(
            "Non-admin user %s attempted to edit user %s", current_user.get_id(), username)
        next_url = request.args.get("next") or url_for("users.user_list")
        return redirect(next_url)
    if not user:
        flash('Käyttäjää ei löytynyt.', 'error')
        return redirect(url_for('web.user_list'))
    if user.is_admin:
        flash('Et voi muokata ylläpitäjätilejä.', 'error')
        return redirect(url_for('web.user_list'))
    if request.method == 'POST':
        new_username = request.form.get('username')
        is_temporary = bool(request.form.get('is_temporary'))
        expires_at = request.form.get('expires_at')
        is_admin = bool(request.form.get('is_admin'))

        #ctrl.update_user(user.id, new_username, is_temporary, expires_at, is_admin)
        flash('Käyttäjä päivitetty.', 'success')
        return redirect(url_for('web.user_list'))
    return render_template('edit_user.html', user=user)
