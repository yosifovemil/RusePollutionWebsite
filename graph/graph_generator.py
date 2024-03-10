import json
from functools import reduce

import pandas as pd

from data.interval import summarise_to_interval
from data.limits import LEGAL_LIMITS
from data import readings, emissions
from datetime import datetime
import urllib.parse

SERVER_URL = 'https://air.dishairuse.com'
# SERVER_URL = 'http://localhost:3000'


def make_apexchart(measurement: str, start_date: str, end_date: str, interval: str) -> dict:
    query_data = readings.get_readings(measurement=measurement, start_date=start_date, end_date=end_date)
    data = readings.group_and_summarise(query_data, interval)
    data = data.pivot(index='date', columns='stationName', values='value')

    stations = data.columns.tolist()

    series = []
    y_stats_data = []
    for station in stations:
        series.append({
            'name': station,
            'data': data[station].round(1).tolist()
        })

        y_stats_data = y_stats_data + data[station].round(1).tolist()

    dates = (data.index.astype('int64') / 1000000).tolist()

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


def make_emissions_table(start_date: str, end_date: str):
    query_data = emissions.get_emissions(start_date=start_date, end_date=end_date)

    summary = query_data.groupby(['station', 'measurement'], as_index=False).percentage.mean().round(1)
    summary.sort_values("percentage", ascending=False, inplace=True)

    summary.columns = ['Станция', 'Измерване', '% от периода с емисии над нормата']

    summary_measurements = []
    for msmt in summary['Измерване'].values:
        summary_measurements += [build_URL(msmt, start_date, end_date)]

    summary['Измерване'] = summary_measurements

    return summary.to_html(index=False, escape=False)


def build_URL(measurement: str, start_date: str, end_date: str):
    start_date = convert_format(start_date, "%Y-%m-%d", "%d/%m/%Y")
    end_date = convert_format(end_date, "%Y-%m-%d", "%d/%m/%Y")
    interval = urllib.parse.quote('Средночасова стойност')

    url = (f'{SERVER_URL}/graph?' +
           f'measurement={urllib.parse.quote(measurement)}&' +
           f'interval={interval}&' +
           f'dates={start_date}+-+{end_date}')

    return f'<a href=\'{url}\'>{measurement}</a>'


def convert_format(date: str, old_format: str, new_format: str) -> str:
    return datetime.strptime(date, old_format).strftime(new_format)
