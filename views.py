import configparser

from flask import Blueprint, render_template, send_file, request, redirect
from graphs.config import Config
import logging
from logging.handlers import RotatingFileHandler
from time import strftime
import traceback
import os

views = Blueprint(__name__, "views")

# Logger setup
log_location = os.path.join(os.path.expanduser("~"), "logs", "RusePollutionWebsite.log")
logger = logging.getLogger('tdm')
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(log_location, maxBytes=100000, backupCount=3)
logger.addHandler(handler)

# Config
config = Config()


@views.after_request
def after_request(response):
    timestamp = strftime('[%Y-%b-%d %H:%M]: ')
    logger.info('%s %s %s %s %s %s', timestamp, request.remote_addr, request.method, request.scheme, request.full_path,
                response.status)
    return response


@views.errorhandler(Exception)
def exceptions(e):
    tb = traceback.format_exc()
    timestamp = strftime('[%Y-%b-%d %H:%M]: ')
    logger.error('%s %s %s %s %s 5xx INTERNAL SERVER ERROR\n%s', timestamp, request.remote_addr, request.method,
                 request.scheme, request.full_path, tb)
    return e.status_code


@views.route("/")
def index():
    return render_template("NAPHTALENE.html")


@views.route("/<page>", methods=["GET"])
def page(page):
    compound_names = [compound.get_name() for compound in config.get_compounds()]
    if page in compound_names:
        return render_template("{compound}.html".format(compound=page))
    elif page == "help":
        return render_template("help.html")
    else:
        logger.error("Invalid page requested {page}".format(page=page))
        return redirect("/", code=302)


@views.route('/download/<path:filename>', methods=["GET", "POST"])
def downloadFile(filename):
    compounds = config.get_compounds()
    compound_names = [compound.get_name() for compound in compounds]
    if filename in compound_names:
        try:
            path = f'./csv/{filename}.csv'
            return send_file(path, mimetype='text/csv', as_attachment=True)
        except Exception as e:
            print(str(e))
    else:
        logger.error("Invalid filename requested {filename}".format(filename=filename))
        return redirect("/", code=302)
