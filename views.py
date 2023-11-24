from flask import Blueprint, render_template

views = Blueprint(__name__, "views")


@views.route("/")
def home():
    return render_template("index.html")


@views.route("/mobile")
def mobile():
    return render_template("index_mobile.html")
