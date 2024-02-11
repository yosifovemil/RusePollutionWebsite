import logging
import os
from pathlib import Path

import apsw.bestpractice
import pandas as pd

from config import Config

apsw.bestpractice.apply(apsw.bestpractice.recommended)


class DBClient:

    def __init__(self):
        self.config = Config()

    def run_query(self, query: str):
        cursor = self.db.execute(query)
        return [row for row in cursor]

    def select_single_row(self, query: str):
        cursor = self.db.execute(query)
        columns = [description[0] for description in cursor.description]
        rows = [row for row in cursor]

        if len(rows) == 0:
            return None
        elif len(rows) > 1:
            raise Exception("More than 1 results found")
        else:
            values = rows[0]
            result = {}
            for key, val in zip(columns, values):
                result[key] = val

            return result

    def select_query(self, query: str) -> pd.DataFrame:
        cursor = self.db.execute(query)
        columns = [description[0] for description in cursor.description]
        data = [row for row in cursor]
        data_frame = pd.DataFrame(data, columns=columns)

        if 'date' in columns:
            data_frame['date'] = pd.to_datetime(data_frame['date'], format="%Y-%m-%d %H:%M:%S")

        return data_frame

    def setup_connection(self, db_location: Path, bootstrap_query: str = None):
        if not db_location.parent.absolute().exists():
            os.mkdir(db_location.parent.absolute())

        bootstrap = False
        if not db_location.exists() and bootstrap_query is not None:
            bootstrap = True

        connection = apsw.Connection(str(db_location))
        connection.pragma("foreign_keys", True)

        check = connection.pragma("integrity_check")
        if check != "ok":
            logging.error("Integrity check errors", check)
            raise Exception(f"Database {str(db_location)} failed integrity check")

        if bootstrap:
            connection.execute(bootstrap_query)

        return connection
