import logging
import os
from pathlib import Path
from typing import Dict, Any

import apsw.bestpractice
import pandas as pd

from config import Config

apsw.bestpractice.apply(apsw.bestpractice.recommended)


class DBClient:

    def __init__(self):
        self.config = Config()

    def run_query(self, query: str):
        self.db.execute(query)

    def __extract_results(self, cursor: apsw.Connection) -> list:
        headings = []
        rows = []
        for db_row in cursor:
            if not headings:
                headings = [desc[0] for desc in cursor.description]

            row = dict(zip(headings, db_row))
            rows.append(row)

        return rows

    def select_single_row(self, query: str) -> dict | None:
        rows = self.__extract_results(self.db.execute(query))
        if len(rows) == 0:
            return None
        elif len(rows) > 1:
            raise Exception("More than 1 results found")
        else:
            return rows[0]

    def select_query(self, query: str) -> pd.DataFrame:
        data = self.__extract_results(self.db.execute(query))
        data_frame = pd.DataFrame(data)

        if 'date' in data_frame.columns:
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
