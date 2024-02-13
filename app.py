import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask, url_for, render_template, session, jsonify, Blueprint
from flask_pyoidc import OIDCAuthentication
from flask_pyoidc.provider_configuration import ClientMetadata, ProviderConfiguration
from flask_pyoidc.user_session import UserSession
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

app = Flask(__name__)

app.register_blueprint(views, url_prefix="/")

app.config.update(
    OIDC_REDIRECT_URI="http://localhost:3000/login_callback",
    SECRET_KEY=config.website_secret,
    TEMPLATES_AUTO_RELOAD=True
)

client_metadata = ClientMetadata(
    client_id=config.google_secret['client_id'],
    client_secret=config.google_secret['client_secret'],
    post_logout_redirect_uris="http://localhost:3000/logout"
)

provider_config = ProviderConfiguration(
    issuer="https://accounts.google.com",
    client_metadata=client_metadata
)

auth = OIDCAuthentication({'default': provider_config}, app)


@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/login")
@auth.oidc_auth('default')
def login():
    user_session = UserSession(session)
    return jsonify(access_token=user_session.access_token,
                   id_token=user_session.id_token,
                   userinfo=user_session.userinfo)


#
#     session['oauth2_state'] = secrets.token_urlsafe(16)
#
#     login_redirect = google_auth.login_redirect(
#         oauth2_state=session['oauth2_state'],
#         redirect_uri=__get_redirect_uri()
#     )
#
#     return redirect(login_redirect)
#
#
# @auth.route("/login_callback")
# def login_callback():
#     if not __validate_login_callback_request(request=request):
#         abort(401)
#
#     try:
#         user_info = google_auth.get_user_info(
#             auth_code=request.args['code'],
#             redirect_uri=__get_redirect_uri()
#         )
#
#         user = login_or_register(user_info, logger)
#         if user is None:
#             logger.warning(f"Invalid login attempt:\n{user_info}")
#             abort(401)
#         else:
#             login_user(user)
#
#         return redirect(url_for("views.graph"))
#
#     except Exception:
#         abort(401)
#
#
@app.route("/logout")
def logout():
    return "Logged out"
    # logout_user()
    # return redirect(url_for("auth.landing"))


#
#
# def __validate_login_callback_request(request: Request) -> bool:
#     if 'error' in request.args:
#         logger.error("Received error(s) from Google authorization:")
#         for k, v in request.args.items():
#             if k.startswith('error'):
#                 logger.error(f'{k}: {v}')
#
#         return False
#
#     if request.args['state'] != session.get('oauth2_state'):
#         logger.error(f"Received wrong state: {request.args['state']}")
#         return False
#
#     if 'code' not in request.args:
#         logger.error("Value 'code' not found in request")
#         return False
#
#     return True
#
#
# def __get_redirect_uri():
#     return url_for('auth.login_callback', _external=True)


if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=3000, threads=4)
