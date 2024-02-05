import configparser

import flask
from flask import Blueprint, render_template, send_file, request, redirect

from database.client import DBClient
from graph.graph_picker import GraphPicker
from graph.interval import *
from graphs.config import Config
import logging
from logging.handlers import RotatingFileHandler
from time import strftime
import traceback
import os
import pandas as pd
from graph import graph_generator
from static.menu import menu_builder
from datetime import datetime, timedelta
import utils.formats as formats

from static.menu.menu_items import menu_item_index

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


@views.route("/")
def index():
    menu = menu_builder.menu
    return render_template("graph_form.html", menu=menu, graph_choices=graph_picker.choices)


@views.route("/graph", methods=["GET", "POST"])
def graph():
    page, measurement = menu_item_index[request.values.get("page", default=0, type=int)]
    start_date = request.values.get(
        "start_date",
        default=(datetime(year=2023, month=12, day=31) - timedelta(days=5)).strftime(format=formats.date_format),
        type=str
    )
    end_date = request.values.get(
        "end_date",
        default=datetime(year=2023, month=12, day=31).strftime(format=formats.date_format),
        # TODO replace with datetime.now
        type=str
    )
    interval = request.values.get("interval", default=INTERVAL_DAILY)
    if interval not in VALID_INTERVALS:
        return ""  # TODO error

    graph = graph_generator.make_graph(measurement, start_date, end_date, interval)
    menu = menu_builder.menu

    return render_template("graph_form.html", graph=graph, menu=menu, page=page, start_date=start_date,
                           end_date=end_date)

#
#
# @views.route("/<page>", methods=["GET"])
# def page(page):
#     compound_names = [compound.get_name() for compound in config.get_compounds()]
#     if page in compound_names:
#         return render_template("{compound}.html".format(compound=page))
#     elif page == "help":
#         return render_template("help.html")
#     else:
#         logger.error("Invalid page requested {page}".format(page=page))
#         return redirect("/", code=302)
#
#
# @views.route('/download/<path:filename>', methods=["GET", "POST"])
# def downloadFile(filename):
#     compounds = config.get_compounds()
#     compound_names = [compound.get_name() for compound in compounds]
#     if filename in compound_names:
#         try:
#             path = f'./csv/{filename}.csv'
#             return send_file(path, mimetype='text/csv', as_attachment=True)
#         except Exception as e:
#             print(str(e))
#     else:
#         logger.error("Invalid filename requested {filename}".format(filename=filename))
#         return redirect("/", code=302)
