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

    def update_user(self):
        # TODO update user's values with info from their Google account
        pass

    def get_user(self):
        # TODO get user info from DB
        pass
