from datetime import datetime

import numpy as np

from data import readings, interval
from data.limits import LEGAL_LIMITS
from data.interval import INTERVAL_DAILY, INTERVAL_HOURLY, MODE_SUM, INTERVAL_30MIN
from database.data_db import DataDB
import pandas as pd

db = DataDB()


def event_table_exists() -> bool:
    query = "SELECT name FROM sqlite_master WHERE type='table'"
    results = db.select_query(query)
    return 'EmissionEvent' in results.name.values


def create_event_table():
    db.run_query(db.create_emissions_event_table_query)


def get_data(measurement: str) -> pd.DataFrame | None:
    query_data = readings.get_readings(measurement=measurement, intervals=[INTERVAL_HOURLY, INTERVAL_30MIN])
    if len(query_data) > 0:
        data = readings.group_and_summarise(query_data, INTERVAL_HOURLY)
        return data
    else:
        return None


def flush_events():
    query = "DELETE FROM EmissionEvent"
    db.run_query(query)


def format_data_for_db(data: pd.DataFrame) -> list[list]:
    data = data[['date', 'stationName', 'measurement', 'value']]

    db_data = []
    for i in data.index:
        vals = data.loc[i, :].values.tolist()
        vals[0] = vals[0].strftime("%Y-%m-%d")

        db_data.append(vals)

    return db_data


def insert_events(data: list[list]):
    query = "INSERT INTO EmissionEvent(date, station, measurement, percentage) VALUES (?, ?, ?, ?)"
    db.db.executemany(query, data)


def main():
    if not event_table_exists():
        create_event_table()

    flush_events()

    dfs = list()
    for measurement in LEGAL_LIMITS.keys():
        limit = LEGAL_LIMITS[measurement][INTERVAL_HOURLY]
        data = get_data(measurement)

        if data is not None:
            data['value'] = np.where(data['value'] >= limit, 1, 0)
            data = interval.summarise_to_interval(
                data=data,
                old_interval=INTERVAL_HOURLY,
                new_interval=INTERVAL_DAILY,
                mode=MODE_SUM
            )

            data['value'] = ((data.value * 100) / 24.0)
            data['measurement'] = measurement

            dfs.append(data)

    data = pd.concat(dfs)
    data.reset_index(inplace=True)
    db_data = format_data_for_db(data)
    insert_events(db_data)


if __name__ == "__main__":
    main()
