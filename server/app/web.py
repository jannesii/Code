# app/web.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from dataclasses import asdict

web_bp = Blueprint('web', __name__)

@web_bp.route('/')
@login_required
def home():
    return render_template('index.html')

@web_bp.route('/3d')
@login_required
def page_3d():
    ctrl = current_app.ctrl
    img_obj = ctrl.get_last_image()
    th_obj = ctrl.get_last_temphum()
    st_obj = ctrl.get_last_status()
    last_image = asdict(img_obj) if img_obj else None
    last_temphum = asdict(th_obj) if th_obj else None
    last_status = asdict(st_obj) if st_obj else None
    api_key = current_app.config.get('API_KEY')
    return render_template('3d.html', last_image=last_image, last_temphum=last_temphum, last_status=last_status, api_key=api_key)

@web_bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@web_bp.route('/settings/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    ctrl = current_app.ctrl
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        try:
            ctrl.register_user(username, password)
            flash(f"User '{username}' added.", "success")
            return redirect(url_for('web.settings'))
        except ValueError as e:
            flash(str(e), "error")
    return render_template('add_user.html')

@web_bp.route('/settings/delete_user', methods=['GET', 'POST'])
@login_required
def delete_user():
    ctrl = current_app.ctrl
    users = ctrl.get_all_users()
    if request.method == 'POST':
        username = request.form.get('username')
        if not username:
            flash("Select a user first.", "error")
            return redirect(url_for('web.delete_user'))
        if username == current_user.get_id():
            flash("Cannot delete your own account.", "error")
        else:
            try:
                ctrl.delete_user(username)
                flash(f"User '{username}' deleted.", "success")
            except Exception as e:
                flash(f"Deletion failed: {e}", "error")
        return redirect(url_for('web.delete_user'))
    return render_template('delete_user.html', users=users)

@web_bp.route('/settings/timelapse_conf', methods=['GET', 'POST'])
@login_required
def timelapse_conf():
    ctrl = current_app.ctrl
    if request.method == 'POST':
        image_delay = request.form.get('image_delay', '').strip()
        temphum_delay = request.form.get('temphum_delay', '')
        status_delay = request.form.get('status_delay', '')
        try:
            ctrl.update_timelapse_conf(
                image_delay=int(image_delay),
                temphum_delay=int(temphum_delay),
                status_delay=int(status_delay)
            )
            conf = {
                'image_delay': int(image_delay),
                'temphum_delay': int(temphum_delay),
                'status_delay': int(status_delay)
            }
            current_app.extensions['socketio'].emit('timelapse_conf', conf)
            flash("Timelapse configuration updated.", "success")
            return redirect(url_for('web.settings'))
        except ValueError as e:
            flash(str(e), "error")
    else:
        conf = ctrl.get_timelapse_conf()
        image_delay = conf.image_delay
        temphum_delay = conf.temphum_delay
        status_delay = conf.status_delay
    return render_template('timelapse_conf.html', image_delay=image_delay, temphum_delay=temphum_delay, status_delay=status_delay)
