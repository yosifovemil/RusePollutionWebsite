import logging
import os
import secrets
import traceback
from logging.handlers import RotatingFileHandler
from time import strftime

from flask import Blueprint, render_template, request, session, url_for, redirect, abort, Request

from authenticate.google_auth import GoogleAuth
from config import Config
from database.website_db import WebsiteDB
from graph import graph_generator
from graph.graph_picker import GraphPicker
from graph.interval import *
from static.form import form_builder
from utils.graph_util import parse_date_range

views = Blueprint(__name__, "views")

# Logger setup
log_location = os.path.join(os.path.expanduser("~"), "logs", "RusePollutionWebsite.log")
logger = logging.getLogger('tdm')
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(log_location, maxBytes=100000, backupCount=3)
logger.addHandler(handler)

# Config
config = Config()
graph_picker = GraphPicker()
website_db = WebsiteDB()
google_auth = GoogleAuth(google_secret=config.google_secret)


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


@views.route("/", methods=["GET", "POST"])
def graph():
    measurement = request.values.get("measurement", default="Бензен")
    raw_dates = request.values.get("dates", default="01/12/2023 - 10/12/2023")
    start_date, end_date = parse_date_range(raw_dates)

    interval = request.values.get("interval", default=INTERVAL_DAILY)
    if interval not in VALID_INTERVALS:
        return ""  # TODO error

    try:
        graph = graph_generator.make_apexchart(measurement, start_date, end_date, interval)
    except Exception as e:
        print(e)
        graph = None

    form = form_builder.build(dates=raw_dates, measurement=measurement, interval=interval)

    return render_template(
        "graph_form.html",
        graph=graph,
        form=form,
        start_date=start_date,
        end_date=end_date
    )


@views.route("/login")
def login():
    session['oauth2_state'] = secrets.token_urlsafe(16)

    login_redirect = google_auth.login_redirect(
        oauth2_state=session['oauth2_state'],
        redirect_uri=__get_redirect_uri()
    )

    return redirect(login_redirect)


@views.route("/login_callback")
def login_callback():
    if not __validate_login_callback_request(request=request):
        abort(401)

    try:
        user_info = google_auth.get_user_info(
            auth_code=request.args['code'],
            redirect_uri=__get_redirect_uri()
        )

        user = website_db.get_user(user_info['email'])
        if user is None:
            logging.warning(f"Invalid login attempt:\n{user_info}")
        elif not bool(user['registered']):
            updated_user = {
                'email': user['email'],
                'name': user_info['name'],
                'photo': user_info['picture'],
                'registered': 1
            }
            website_db.update_user(updated_user)
            return f"Registered in database:<br />{user}"
        else:
            return f"Welcome back {user['name']}."

    except Exception:
        abort(401)


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
    return url_for('views.login_callback', _external=True)
