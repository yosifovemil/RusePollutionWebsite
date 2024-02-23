import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask
from waitress import serve
from werkzeug.middleware.proxy_fix import ProxyFix

from admin import admin
from auth import oauth, auth_blueprint
from authenticate.user_manager import login_manager
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
app.register_blueprint(auth_blueprint, url_prefix="/")
app.register_blueprint(admin, url_prefix="/")
app.config.update(
    SECRET_KEY=config.website_secret,
    TEMPLATES_AUTO_RELOAD=True,
)

oauth.init_app(app)
login_manager.init_app(app)

app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=3000)
