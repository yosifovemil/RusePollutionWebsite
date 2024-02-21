import email.header
from pathlib import Path

import apsw.bestpractice

from authenticate.user import User
from database.client import DBClient
from utils.file_io import read_file

apsw.bestpractice.apply(apsw.bestpractice.recommended)


class WebsiteDB(DBClient):

    def __init__(self):
        super().__init__()
        self.db_bootstrap = read_file(Path("database/sql/bootstrap_website_db.sql"))
        self.db = self.setup_connection(db_location=self.config.website_db_path, bootstrap_query=self.db_bootstrap)

    def update_user(self, user: User):
        query = (
            "UPDATE Users "
            "SET "
            f"username = '{user.username}', "
            f"name = '{user.name}', "
            f"photo = '{user.photo}' "
            "WHERE "
            f"id = '{user.id}'"
        )

        self.run_query(query=query)

    def lookup_user(self, username: str) -> User | None:
        query = f"SELECT * FROM Users WHERE username = '{username}'"
        result = self.select_single_row(query)
        return adapt_db_user(result)

    def get_user(self, id):
        query = f"SELECT * FROM Users WHERE id = '{id}'"
        result = self.select_single_row(query)
        return adapt_db_user(result)

    def add_user(self, username: str, password_hash: str = None):
        query = "INSERT INTO Users VALUES (?, ?, ?, ?, ?, ?, ?, ?)"

        self.db.execute(
            query,
            (None, username, password_hash, None, None, True, False, 'temporary',)
        )

    def create_user(self, username: str, password_hash: bytes):
        query = (
            "INSERT INTO Users"
            f"Values (NULL, '{username}', '{password_hash}', NULL, NULL, TRUE, FALSE, 'temporary'"
        )

        self.db.execute(query)


def adapt_db_user(db_user: dict | None) -> User | None:
    if db_user is not None:
        return User(db_user)
    else:
        return db_user
