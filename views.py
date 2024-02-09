from typing import Tuple

from flask import Blueprint, render_template, request

from graph.graph_picker import GraphPicker
from graph.interval import *
from config import Config
import logging
from logging.handlers import RotatingFileHandler
from time import strftime
import traceback
import os
from graph import graph_generator
from static.form import form_builder
from datetime import datetime, timedelta
import utils.formats as formats

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
    start_date, end_date = parse_dates(raw_dates)

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


def parse_dates(dates: str) -> tuple[str, str]:
    dates_str = dates.split("-")
    start_date = datetime.strptime(dates_str[0].strip(), "%d/%m/%Y")
    end_date = datetime.strptime(dates_str[1].strip(), "%d/%m/%Y") + timedelta(days=1)

    return start_date.strftime(formats.date_format), end_date.strftime(formats.date_format)
