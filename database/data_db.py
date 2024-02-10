from pathlib import Path

import apsw.bestpractice

from database.client import DBClient
from utils.file_io import read_file

apsw.bestpractice.apply(apsw.bestpractice.recommended)


class DataDB(DBClient):

    def __init__(self):
        super().__init__()
        self.db = self.setup_connection(db_location=self.config.data_db_path)
        self.graph_picker_query = read_file(Path("database/sql/graph_picker_choices.sql"))
