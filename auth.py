import logging
import secrets

from flask import Blueprint, redirect, url_for, render_template, session, request, abort, Request
from flask_login import logout_user, login_user

from authenticate.google_auth import GoogleAuth
from authenticate.logins import login_or_register
from config import Config

auth = Blueprint(__name__, "auth")
config = Config()
google_auth = GoogleAuth(google_secret=config.google_secret)
logger = logging.getLogger('tdm')


@auth.route("/")
def landing():
    return render_template("landing.html", google_client_id=config.google_secret['client_id'])


@auth.route("/login")
def login():
    session['oauth2_state'] = secrets.token_urlsafe(16)

    login_redirect = google_auth.login_redirect(
        oauth2_state=session['oauth2_state'],
        redirect_uri=__get_redirect_uri()
    )

    return redirect(login_redirect)


@auth.route("/login_callback")
def login_callback():
    if not __validate_login_callback_request(request=request):
        abort(401)

    try:
        user_info = google_auth.get_user_info(
            auth_code=request.args['code'],
            redirect_uri=__get_redirect_uri()
        )

        user = login_or_register(user_info, logger)
        if user is None:
            logger.warning(f"Invalid login attempt:\n{user_info}")
            abort(401)
        else:
            login_user(user)

        return redirect(url_for("views.graph"))

    except Exception:
        abort(401)


@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.landing"))


def __validate_login_callback_request(request: Request) -> bool:
    if 'error' in request.args:
        logger.error("Received error(s) from Google authorization:")
        for k, v in request.args.items():
            if k.startswith('error'):
                logger.error(f'{k}: {v}')

        return False

    if request.args['state'] != session.get('oauth2_state'):
        logger.error(f"Received wrong state: {request.args['state']}")
        return False

    if 'code' not in request.args:
        logger.error("Value 'code' not found in request")
        return False

    return True


def __get_redirect_uri():
    return url_for('auth.login_callback', _external=True)
