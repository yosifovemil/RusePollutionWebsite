import bcrypt

from authenticate.user import User
from database.website_db import WebsiteDB

website_db = WebsiteDB()


def login(user_info: dict) -> User | None:
    db_user = website_db.lookup_temp_user(user_info['username'])

    if (db_user is not None and
            bcrypt.checkpw(db_user['password'], user_info['password'])):
        return User(db_user)

    return None
