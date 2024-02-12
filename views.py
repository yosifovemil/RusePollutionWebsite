import logging
import traceback
from time import strftime

from flask import Blueprint, render_template, request, url_for, redirect
from flask_login import current_user

from graph import graph_generator
from graph.graph_picker import GraphPicker
from graph.interval import *
from static.form import form_builder
from utils.graph_util import parse_date_range

views = Blueprint(__name__, "views")
logger = logging.getLogger('tdm')

graph_picker = GraphPicker()


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


@views.route("/graph", methods=["GET", "POST"])
def graph():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.landing"))

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
