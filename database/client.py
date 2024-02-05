import apsw.bestpractice
import os
from pathlib import Path
import logging

import pandas as pd

from graphs.config import Config
from utils import formats
from utils.singleton import Singleton

apsw.bestpractice.apply(apsw.bestpractice.recommended)


class DBClient(metaclass=Singleton):

    def __init__(self):
        config = Config()
        self.db = setup_connection(config.db_path)
        self.graph_picker_query = read_file(Path("database/sql/graph_picker_choices.sql"))

    def run_query(self, query: str) -> pd.DataFrame:
        cursor = self.db.execute(query)
        columns = [description[0] for description in cursor.description]
        data = [row for row in cursor]
        data_frame = pd.DataFrame(data, columns=columns)

        if 'date' in columns:
            data_frame['date'] = pd.to_datetime(data_frame['date'], format="%Y-%m-%d %H:%M:%S")

        return data_frame


def setup_connection(db_location: Path):
    if not db_location.parent.absolute().exists():
        os.mkdir(db_location.parent.absolute())

    connection = apsw.Connection(str(db_location))
    connection.pragma("foreign_keys", True)

    check = connection.pragma("integrity_check")
    if check != "ok":
        logging.error("Integrity check errors", check)

    return connection


def read_file(file: Path):
    f = file.open()
    content = f.read()
    f.close()
    return content
