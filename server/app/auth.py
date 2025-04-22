# app/auth.py
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required

from .controller import Controller

auth_bp = Blueprint('auth', __name__)
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

class AuthUser(UserMixin):
    def __init__(self, username: str):
        self.id = username

@login_manager.user_loader
def load_user(user_id: str):
    # retrieve Controller from app
    ctrl: Controller = current_app.ctrl
    if ctrl.get_user_by_username(user_id):
        return AuthUser(user_id)
    return None

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    ctrl: Controller = current_app.ctrl
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'
        if ctrl.authenticate_user(username, password):
            session.permanent = remember
            login_user(AuthUser(username), remember=remember)
            next_page = request.args.get('next') or url_for('web.home')
            return redirect(next_page)
        flash('Invalid username or password', 'error')
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('_flashes', None)
    return redirect(url_for('auth.login'))