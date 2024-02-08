import json

import pandas as pd
from database.client import DBClient
from graph.interval import summarise_to_interval
from functools import reduce


def make_apexchart(measurement: str, start_date: str, end_date: str, interval: str) -> dict:
    db_client = DBClient()
    query = f"""
    SELECT date, Station.name AS stationName, MeasurementInterval.name as interval, value
    FROM Reading
    LEFT JOIN Station ON Reading.stationId = Station.id
    LEFT JOIN Measurement ON Reading.measurementId = Measurement.id
    LEFT JOIN MeasurementInterval ON Reading.intervalId = MeasurementInterval.id
    WHERE Measurement.name = '{measurement}'
    AND date >= '{start_date}'
    AND date <= '{end_date}'
    """

    query_data = db_client.run_query(query)
    data = build_graph_data(query_data, interval)

    stations = data.columns.tolist()
    stations.remove("date")

    series = []
    for station in stations:
        series.append({
            'name': station,
            'data': data[station].round(1).tolist()
        })

    dates = (data['date'].astype('int64')/1000000).tolist()

    y_vals = json.dumps(series, ensure_ascii=False).replace("NaN", "null")

    graph = {
        "x_vals": dates,
        "y_vals": y_vals,
        "title_text": measurement,
        "chart_type": "line" if len(dates) > 10 else "bar"
    }

    return graph


def build_graph_data(data: pd.DataFrame, interval: str) -> pd.DataFrame:
    station_dfs = []
    for (station, group_interval), group in data.groupby(['stationName', 'interval'], as_index=False):
        summarised_data = summarise_to_interval(
            data=group[['date', 'value']].copy(),
            old_interval=group_interval,
            new_interval=interval
        )

        if summarised_data is None:
            continue

        summarised_data.columns = ['date', station]
        station_dfs.append(summarised_data)

    return reduce(merge_on_date, station_dfs)


def merge_on_date(a: pd.DataFrame, b: pd.DataFrame) -> pd.DataFrame:
    return a.merge(b, how='outer', on='date')