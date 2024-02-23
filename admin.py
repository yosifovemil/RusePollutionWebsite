from flask import Blueprint, request, render_template, redirect, url_for
from flask_login import login_required, current_user
from authenticate import user_manager
from authenticate.admin import verify_permissions

admin = Blueprint(__name__, "admin")


@admin.route("/admin")
def admin_panel():
    if verify_permissions(current_user):
        return render_template("admin.html")
    else:
        return redirect(url_for("auth.index"))


@admin.route("/add_temp_user", methods=['POST'])
@login_required
def add_temp_user():
    username = request.values.get("username")
    password = request.values.get("password")
    if verify_permissions(current_user):
        user_manager.add_temp_user(username, password)

    return redirect(url_for("admin.admin_panel"))


@admin.route("/add_google_user", methods=['POST'])
@login_required
def add_google_user():
    email = request.values.get("email")
    if verify_permissions(current_user):
        user_manager.add_google_user(email)

    return redirect(url_for("admin.admin_panel"))
