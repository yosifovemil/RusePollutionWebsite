from pathlib import Path

import apsw.bestpractice

from database.client import DBClient
from utils.file_io import read_file

apsw.bestpractice.apply(apsw.bestpractice.recommended)


class WebsiteDB(DBClient):

    def __init__(self):
        super().__init__()
        self.db_bootstrap = read_file(Path("database/sql/bootstrap_website_db.sql"))
        self.db = self.setup_connection(db_location=self.config.website_db_path, bootstrap_query=self.db_bootstrap)

    def update_user(self, user: dict):
        query = f"""
        UPDATE Users
        SET name = '{user['name']}',
            photo = '{user['photo']}',
            registered = '{user['registered']}'
        WHERE 
            email = '{user['email']}'
        """

        self.run_query(query=query)

    def lookup_user(self, email: str):
        query = f"SELECT * FROM Users WHERE email = '{email}'"
        return self.select_single_row(query)

    def lookup_temp_user(self, username: str):
        query = f"SELECT * FROM TempUsers WHERE username = '{username}'"
        return self.select_single_row(query)

    def get_user(self, id):
        query = f"SELECT * FROM Users WHERE id = '{id}'"
        return self.select_single_row(query)
