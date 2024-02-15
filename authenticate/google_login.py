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
    db_user = website_db.get_user(id)
    if db_user is None:
        return None
    else:
        user = User(db_user)
        return user


def login_or_register(user_info: dict, logger: Logger) -> User | None:
    db_user = website_db.lookup_user(user_info['email'])

    if db_user is None:
        return None
    elif not bool(db_user['registered']):
        updated_user = {
            'email': db_user['email'],
            'name': user_info['name'],
            'photo': user_info['picture'],
            'registered': 1,
            'admin': user_info['admin']
        }
        website_db.update_user(updated_user)
        logger.info(f"Registered user: ${updated_user}")
        return User(updated_user)
    else:
        logger.info(f"User ${db_user['email']} logged in")
        return User(db_user)
