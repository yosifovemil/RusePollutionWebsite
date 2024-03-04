import json
from functools import reduce

import pandas as pd

from database.data_db import DataDB
from graph.interval import summarise_to_interval
from graph.limits import LEGAL_LIMITS


def make_apexchart(measurement: str, start_date: str, end_date: str, interval: str) -> dict:
    db_client = DataDB()
    if measurement == 'p-о- Крезол':
        query = build_query(measurements=['p-Крезол', 'о-Крезол'], start_date=start_date, end_date=end_date)
    elif measurement == 'Ксилен':
        query = build_query(measurements=['Ксилен', 'm- p-Ксилен', 'о-Ксилен'], start_date=start_date, end_date=end_date)
    else:
        query = build_query(measurements=[measurement], start_date=start_date, end_date=end_date)

    query_data = db_client.select_query(query)
    query_data = query_data.groupby(['date', 'stationName', 'interval', 'unit'], as_index=False).sum()
    data = build_graph_data(query_data, interval)

    stations = data.columns.tolist()
    stations.remove("date")

    series = []
    y_stats_data = []
    for station in stations:
        series.append({
            'name': station,
            'data': data[station].round(1).tolist()
        })

        y_stats_data = y_stats_data + data[station].round(1).tolist()

    dates = (data['date'].astype('int64') / 1000000).tolist()

    y_vals = json.dumps(series, ensure_ascii=False).replace("NaN", "null")

    annotations = build_annotations(
        y_stats_data=y_stats_data,
        measurement=measurement,
        interval=interval
    )

    yaxis_title = get_unit(query_data)

    graph = {
        "x_vals": dates,
        "y_vals": y_vals,
        "title_text": measurement,
        "annotations": annotations,
        "yaxis_title": yaxis_title,
        "chart_type": "line" if len(dates) > 10 else "bar"
    }

    return graph


def build_query(measurements: list[str], start_date: str, end_date: str) -> str:
    measurements_q = "('" + str.join("', '", measurements) + "')"
    return f"""
    SELECT date, Station.name AS stationName, MeasurementInterval.name as interval, value, Measurement.unit as unit
    FROM Reading
    LEFT JOIN Station ON Reading.stationId = Station.id
    LEFT JOIN Measurement ON Reading.measurementId = Measurement.id
    LEFT JOIN MeasurementInterval ON Reading.intervalId = MeasurementInterval.id
    WHERE Measurement.name IN {measurements_q}
    AND date >= '{start_date}'
    AND date <= '{end_date}'
    """


def build_graph_data(data: pd.DataFrame, interval: str) -> pd.DataFrame:
    data = data.copy()[['date', 'stationName', 'interval', 'value']]

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


def build_annotations(y_stats_data: list[float], measurement: str, interval: str) -> dict:
    annotations = {
        'y_min': min(y_stats_data)
    }
    if measurement in LEGAL_LIMITS.keys() and interval in LEGAL_LIMITS[measurement].keys():
        annotations['limit'] = LEGAL_LIMITS[measurement][interval]
        annotations['y_max'] = max(max(y_stats_data), annotations['limit'])
    else:
        annotations['limit'] = "undefined"
        annotations['y_max'] = max(y_stats_data)

    return annotations


def get_unit(query_data: pd.DataFrame) -> str:
    units = query_data['unit'].unique()
    if len(units) == 1:
        return units[0]
    else:
        return "Грешка с мерните единици"


def dummy_graph(measurement: str) -> dict:
    return {
        "x_vals": [],
        "y_vals": [],
        "title_text": measurement,
        "annotations": {
            'y_min': "",
            'y_max': "",
            'limit': ""
        },
        "yaxis_title": "",
        "chart_type": "line"
    }
