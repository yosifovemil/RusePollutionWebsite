import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask
from waitress import serve

from auth import auth
from authenticate.logins import login_manager
from config import Config
from views import views

config = Config()

app = Flask(__name__)
app.config['SECRET_KEY'] = config.website_secret
app.register_blueprint(views, url_prefix="/")
app.register_blueprint(auth, url_prefix="/")
app.config['TEMPLATES_AUTO_RELOAD'] = True

login_manager.init_app(app)

# Logger setup
log_location = os.path.join(os.path.expanduser("~"), "logs", "RusePollutionWebsite.log")
logger = logging.getLogger('tdm')
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(log_location, maxBytes=100000, backupCount=3)
logger.addHandler(handler)

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=3000, threads=4)
