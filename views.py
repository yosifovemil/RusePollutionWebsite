import logging
import traceback
from time import strftime

from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

from component.nav_panel import nav_panel
from graph import graph_generator
from graph.graph_picker import GraphPicker
from graph.interval import *
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
@login_required
def graph():
    measurement = request.values.get("measurement", default="Бензен")
    raw_dates = request.values.get("dates", default="01/12/2023 - 10/12/2023")
    start_date, end_date = parse_date_range(raw_dates)

    interval = request.values.get("interval", default=INTERVAL_DAILY)
    if interval not in VALID_INTERVALS:
        return ""  # TODO error

    try:
        graph_component = graph_generator.make_apexchart(measurement, start_date, end_date, interval)
    except Exception as e:
        print(e)
        graph_component = None

    admin = current_user.admin

    graph_form = nav_panel.build_form(dates=raw_dates, measurement=measurement, interval=interval)
    nav_buttons = nav_panel.build_nav_buttons(admin=admin)
    admin_modal = ""  # TODO nav_panel.build_admin_modal(admin=admin)

    return render_template(
        "graph.html",
        graph=graph_component,
        graph_form=graph_form,
        nav_buttons=nav_buttons,
        start_date=start_date,
        end_date=end_date,
        admin_modal=admin_modal
    )
