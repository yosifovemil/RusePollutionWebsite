import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask
from waitress import serve

from auth import oauth, auth_blueprint
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
app.config.update(
    SECRET_KEY=config.website_secret,
    TEMPLATES_AUTO_RELOAD=True,
)

oauth.init_app(app)

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=3000, threads=4)
