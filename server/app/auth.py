# app/auth.py
import logging
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, current_app, make_response
from flask_login import login_user, logout_user, login_required, current_user, UserMixin
from flask_limiter.errors import RateLimitExceeded
from . import limiter

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)


class AuthUser(UserMixin):
    """Flask‑Login user."""

    def __init__(self, username: str):
        self.id = username


def load_user(user_id: str):
    ctrl = current_app.ctrl
    user = ctrl.get_user_by_username(user_id)
    if user:
        logger.debug("Loaded user %s", user_id)
        return AuthUser(user_id)
    logger.warning("User %s not found", user_id)
    return None


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5/minute;20/hour", exempt_when=lambda: current_user.is_admin)
def login():
    logger.info("Accessed /login via %s", request.method)
    ctrl = current_app.ctrl

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'
        logger.debug("Login attempt for %s (remember=%s)", username, remember)

        if ctrl.authenticate_user(username, password):
            session.permanent = remember
            login_user(AuthUser(username), remember=remember)
            logger.info("User %s authenticated", username)

            next_page = request.args.get('next') or url_for('web.get_home_page')
            response = redirect(next_page)
            logger.debug(
                "Rate-limit headers: remaining=%s reset=%s",
                response.headers.get("X-RateLimit-Remaining"),
                response.headers.get("X-RateLimit-Reset")
            )
            return response

        flash('Virheellinen käyttäjätunnus tai salasana', 'error')
        logger.warning("Auth failed for %s", username)

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    username = current_user.get_id()
    logout_user()
    session.pop('_flashes', None)
    logger.info("User %s logged out", username)
    return redirect(url_for('auth.login'))

@auth_bp.errorhandler(RateLimitExceeded)
def handle_rate_limit(e):
    logger.warning(
        "Rate limit reached for %s on endpoint %s",
        request.remote_addr,
        request.endpoint
    )
    return make_response(
        render_template("429.html", retry_after=e.description),
        429
    )