from database.client import DBClient
import pandas as pd
import json


class GraphPicker:
    def __init__(self):
        db_client = DBClient()
        self.choices = build_choices(db_client.run_query(db_client.graph_picker_query))


def build_choices(query_result: pd.DataFrame) -> str:
    measurements = dict()
    for measurement in query_result.measurement.unique():
        measurement_rows = query_result[query_result.measurement == measurement]

        stations = dict()
        for station in measurement_rows.station.unique():
            station_rows = measurement_rows[measurement_rows.station == station]
            intervals = station_rows.interval.unique().tolist()

            stations[station] = intervals

        measurements[measurement] = stations

    return json.dumps(measurements, ensure_ascii=False)
