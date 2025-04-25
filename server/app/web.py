# app/web.py
import logging
from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from flask_login import login_required, current_user
from dataclasses import asdict
from .utils import check_vals


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
    ctrl = current_app.ctrl
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
    ctrl = current_app.ctrl
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '')
        
        if not current_user.is_admin:
            flash("Sinulla ei ole oikeuksia lisätä käyttäjiä.", "error")
            logger.warning("Non-admin user %s attempted to add user with username: %s", current_user.get_id(), u)
            return redirect(url_for('web.get_settings_page'))

        logger.debug("Adding user %s", u)
        try:
            ctrl.register_user(u, p)
            flash(f"Käyttäjä «{u}» lisätty onnistuneesti.", 'success')
            logger.info("User %s added by %s", u, current_user.get_id())
            return redirect(url_for('web.get_settings_page'))
        except ValueError as ve:
            flash(str(ve), "error")
            logger.warning("Add user failed: %s", ve)

    return render_template('add_user.html')


@web_bp.route('/settings/delete_user', methods=['GET', 'POST'])
@login_required
def delete_user():
    ctrl = current_app.ctrl
    users = ctrl.get_all_users()
    if request.method == 'POST':
        u = request.form.get('username')
        
        if not current_user.is_admin:
            flash("Sinulla ei ole oikeuksia poistaa käyttäjiä.", "error")
            logger.warning("Non-admin user %s attempted to delete user with username: %s", current_user.get_id(), u)
            return redirect(url_for('web.get_settings_page'))

        if not u:
            flash("Valitse ensin käyttäjä.", "error")
            logger.warning("No user selected for deletion")
            return redirect(url_for('web.get_settings_page'))
        if u == current_user.get_id():
            flash("Et voi poistaa omaa tiliäsi.", "error")
            logger.warning("Self‑deletion attempt by %s", u)
            return render_template('delete_user.html', users=users)
        else:
            try:
                ctrl.delete_user(u)
                flash(f"Käyttäjä «{u}» poistettu.", "success")
                logger.info("User %s deleted by %s", u, current_user.get_id())
            except Exception as e:
                flash(f"Poisto epäonnistui: {e}", "error")
                logger.error("Error deleting %s: %s", u, e)
                return render_template('delete_user.html', users=users)
        return redirect(url_for('web.get_settings_page'))
    return render_template('delete_user.html', users=users)


@web_bp.route('/settings/timelapse_conf', methods=['GET', 'POST'])
@login_required
def timelapse_conf():
    ctrl = current_app.ctrl
    vals = {}
    if request.method == 'POST':
        vals = {
            'image_delay':   int(request.form.get('image_delay', '0')),
            'temphum_delay': int(request.form.get('temphum_delay', '0')),
            'status_delay':  int(request.form.get('status_delay', '0'))
        }
        
        if not current_user.is_admin:
            flash("Sinulla ei ole oikeuksia muuttaa asetuksia.", "error")
            logger.warning("Non-admin user %s attempted to change timelapse settings", current_user.get_id())
            return redirect(url_for('web.get_settings_page'))
        
        logger.debug("Timelapse config: %s", vals)
        try:
            check_failed = check_vals(**vals)
            
            if check_failed:
                for c in check_failed:
                    flash(c['msg'], c['cat'])
                logger.warning("Invalid timelapse input: %s", check_failed)
                return render_template('timelapse_conf.html', **vals)
            else:
                ctrl.update_timelapse_conf(**vals)
                current_app.socketio.emit('timelapse_conf', vals)
                flash("Timelapsen konfiguraatio päivitetty onnistuneesti.", "success")
                logger.info("Timelapse updated %s by %s",
                            vals, current_user.get_id())
                return redirect(url_for('web.get_settings_page'))
        except ValueError as ve:
            flash(str(ve), "error")
            logger.warning("Invalid timelapse input: %s", ve)
    else:
        conf = ctrl.get_timelapse_conf() or vals
        vals = {
            'image_delay':   conf.image_delay,
            'temphum_delay': conf.temphum_delay,
            'status_delay':  conf.status_delay
        }
    return render_template(
        'timelapse_conf.html',
        **vals
    )
