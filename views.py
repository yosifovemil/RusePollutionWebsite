from flask import Blueprint, render_template

views = Blueprint(__name__, "views")


@views.route("/")
def home():
    return render_template("BENZENE.html")


@views.route("/BENZENE")
def benzene():
    return render_template("BENZENE.html")


@views.route("/NAPHTALENE")
def naphtalene():
    return render_template("NAPHTALENE.html")


@views.route("/O-CRESOL")
def ocresol():
    return render_template("O-CRESOL.html")


@views.route("/P-CRESOL")
def pcresol():
    return render_template("P-CRESOL.html")


@views.route("/PHENOL")
def phenol():
    return render_template("PHENOL.html")


@views.route("/TOLUENE")
def toluene():
    return render_template("TOLUENE.html")


@views.route("/XYLENE")
def xylene():
    return render_template("XYLENE.html")
