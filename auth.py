import logging
import secrets

from flask import Blueprint, redirect, url_for, render_template, session, request, abort, Request
from flask_login import logout_user, login_user
from authlib.integrations.flask_client import OAuth
from authenticate.google_login import login_or_register
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
def landing():
    return render_template("landing.html")


@auth_blueprint.route('/login')
def login():
    redirect_uri = url_for('auth.login_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth_blueprint.route('/login_callback')
def login_callback():
    token = oauth.google.authorize_access_token()
    resp = oauth.google.post(f'/oauth2/v2/tokeninfo?access_token={token["access_token"]}&id_token={token["id_token"]}')
    resp.raise_for_status()
    profile = resp.json()



    print(profile)
    return redirect(url_for('views.graph'))
