import logging

from flask import Blueprint, redirect, url_for, render_template, request
from flask_login import logout_user, login_user, login_required
from authlib.integrations.flask_client import OAuth
from authenticate.user_manager import google_login, temp_user_login
from authenticate.user import User
from config import Config

auth_blueprint = Blueprint(__name__, "auth")
config = Config()
logger = logging.getLogger('tdm')

oauth = OAuth()
oauth.register(
    name="google",
    client_id=config.google_secret['client_id'],
    client_secret=config.google_secret['client_secret'],
    api_base_url='https://www.googleapis.com/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
    access_token_url="https://oauth2.googleapis.com/token",
    jwks_uri="https://www.googleapis.com/oauth2/v3/certs",
    client_kwargs={'scope': 'openid email profile'}
)


@auth_blueprint.route('/')
def root():
    return redirect(url_for("auth.index"))


@auth_blueprint.route('/index')
def index():
    return render_template("index.html")


@auth_blueprint.route('/login')
def login():
    redirect_uri = url_for('auth.login_callback', _external=True)
    redirect_uri="https://air.dishairuse.com/login_callback"
    return oauth.google.authorize_redirect(redirect_uri)


@auth_blueprint.route('/login_callback')
def login_callback():
    token = oauth.google.authorize_access_token()
    resp = oauth.google.post(f'/oauth2/v2/tokeninfo?access_token={token["access_token"]}&id_token={token["id_token"]}')
    resp.raise_for_status()
    verified_info = resp.json()

    user_info = {
        'email': verified_info['email'],
        'google_id': verified_info['user_id'],
        'name': token['userinfo']['name'],
        'photo': token['userinfo']['picture']
    }

    user = google_login(user_info=user_info, logger=logger)
    return redirect_after_login(user)


@auth_blueprint.route("/temp_user_login", methods=['POST'])
def temp_login():
    username = request.values.get("username")
    password = request.values.get("password")

    user = temp_user_login(username=username, password=password)
    return redirect_after_login(user)


@auth_blueprint.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.index"))


def redirect_after_login(user: User):
    if user is None:
        return redirect(url_for("auth.index"))
    else:
        login_user(user)
        return redirect(url_for('views.graph'))
