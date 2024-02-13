import logging
import secrets

from flask import Blueprint, redirect, url_for, render_template, session, request, abort, Request
from flask_login import logout_user, login_user

from authenticate.google_auth import GoogleAuth
from authenticate.logins import login_or_register
from config import Config

auth = Blueprint(__name__, "auth")
config = Config()
google_auth = GoogleAuth(google_secret=config.google_secret)
logger = logging.getLogger('tdm')

