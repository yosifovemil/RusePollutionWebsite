import copy
from logging import Logger

import bcrypt
from flask_login import LoginManager

from authenticate.user import Anonymous, User
from database.website_db import WebsiteDB

website_db = WebsiteDB()

login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.anonymous_user = Anonymous
login_manager.login_view = "login"
login_manager.login_message = u"Please log in to access this page."
login_manager.refresh_view = "reauth"


@login_manager.user_loader
def get_user(id) -> User:
    return website_db.get_user(id)


def google_login(user_info: dict, logger: Logger) -> User | None:
    db_user = website_db.lookup_user(user_info['email'])

    if db_user is None:
        return db_user

    if db_user.active:
        if db_user.name is None or db_user.photo is None:
            updated_user = copy.deepcopy(db_user)

            updated_user.name = user_info['name']
            updated_user.photo = user_info['photo']

            website_db.update_user(updated_user)
            logger.info(f"User {db_user.username} signed up")
            return updated_user

        else:
            logger.info(f"User {db_user.username} logged in")
            return db_user


def temp_user_login(username: str, password: str) -> User | None:
    db_user = website_db.lookup_user(username)
    password_b = bytes(password, encoding="UTF-8")

    if db_user is None:
        return db_user

    if db_user.active and bcrypt.checkpw(password_b, db_user.password):
        return db_user
    else:
        return None


def add_temp_user(username: str, password: str):
    password_b = bytes(password, encoding="UTF-8")
    password_hash = (
        bcrypt
        .hashpw(password_b, bcrypt.gensalt(16, b"2b"))
        .decode(encoding="UTF-8")
    )
    website_db.add_user(username=username, password_hash=password_hash)


def add_google_user(email: str):
    website_db.add_user(username=email)
