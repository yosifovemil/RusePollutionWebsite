import copy
from logging import Logger

from flask_login import LoginManager

from authenticate.user import Anonymous, User
from database.website_db import WebsiteDB

website_db = WebsiteDB()

login_manager = LoginManager()

login_manager.anonymous_user = Anonymous
login_manager.login_view = "login"
login_manager.login_message = u"Please log in to access this page."
login_manager.refresh_view = "reauth"


@login_manager.user_loader
def get_user(id):
    return website_db.get_user(id)


def google_login(user_info: dict, logger: Logger) -> User | None:
    db_user = website_db.lookup_user(user_info['email'])

    if db_user is None:
        return db_user

    if db_user.active:
        if db_user.name == "" or db_user.photo == "":
            updated_user = copy.deepcopy(db_user)

            updated_user.name = user_info['name']
            updated_user.photo = user_info['photo']

            website_db.update_user(updated_user)
            logger.info(f"User {db_user.username} signed up")
            return updated_user

        else:
            logger.info(f"User {db_user.username} logged in")
            return db_user


def login(user_info: dict) -> User | None:
    pass
