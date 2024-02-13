import logging
import os
from logging.handlers import RotatingFileHandler

from authlib.integrations.flask_client import OAuth
from flask import Flask, url_for, redirect, request
from waitress import serve

from config import Config
from views import views

# Logger setup
log_location = os.path.join(os.path.expanduser("~"), "logs", "RusePollutionWebsite.log")
logger = logging.getLogger('tdm')
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(log_location, maxBytes=100000, backupCount=3)
logger.addHandler(handler)

config = Config()

# Flask init
app = Flask(__name__)
app.register_blueprint(views, url_prefix="/")
app.config.update(
    SECRET_KEY=config.website_secret,
    TEMPLATES_AUTO_RELOAD=True,
)

oauth = OAuth(app)
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


@app.route('/login')
def login():
    redirect_uri = url_for('login_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@app.route('/login_callback')
def login_callback():
    token = oauth.google.authorize_access_token()
    resp = oauth.google.post(f'/oauth2/v2/tokeninfo?access_token={token["access_token"]}&id_token={token["id_token"]}')
    resp.raise_for_status()
    profile = resp.json()
    # do something with the token and profile
    return redirect(url_for('views.graph'))


if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=3000, threads=4)
