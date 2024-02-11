import logging
import os
import secrets
import traceback
from logging.handlers import RotatingFileHandler
from time import strftime
from urllib.parse import urlencode

import requests
from flask import Blueprint, render_template, request, session, url_for, redirect, abort

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

    qs = urlencode({
        'client_id': config.google_secret['client_id'],
        'redirect_uri': url_for(
            'views.login_callback',
            _external=True
        ),
        'response_type': 'code',
        'scope': 'https://www.googleapis.com/auth/userinfo.email',
        'state': session['oauth2_state']
    })

    return redirect("https://accounts.google.com/o/oauth2/auth?" + qs)


@views.route("/login_callback")
def login_callback():
    if 'error' in request.args:
        print("GOT ERROR:")
        for k, v in request.args.items():
            if k.startswith('error'):
                print(f'{k}: {v}')

    # make sure that the state parameter matches the one we created in the
    # authorization request
    if request.args['state'] != session.get('oauth2_state'):
        print("STATE IS WRONG")
        abort(401)

    # make sure that the authorization code is present
    if 'code' not in request.args:
        print("No code found args")
        abort(401)

    # exchange the authorization code for an access token
    response = requests.post("https://accounts.google.com/o/oauth2/token", data={
        'client_id': config.google_secret['client_id'],
        'client_secret': config.google_secret['client_secret'],
        'code': request.args['code'],
        'grant_type': 'authorization_code',
        'redirect_uri': url_for('views.login_callback', _external=True),
    }, headers={'Accept': 'application/json'})

    print("GOOGLE RESPONSE:")
    print(response)

    if response.status_code != 200:
        abort(401)
    oauth2_token = response.json().get('access_token')
    if not oauth2_token:
        abort(401)

    # use the access token to get the user's email address
    response = requests.get('https://www.googleapis.com/oauth2/v3/userinfo', headers={
        'Authorization': 'Bearer ' + oauth2_token,
        'Accept': 'application/json',
    })

    if response.status_code != 200:
        abort(401)

    return response.json()
