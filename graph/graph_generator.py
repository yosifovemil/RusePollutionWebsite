import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

from database.client import DBClient
from graph.interval import summarise_to_interval
from utils import formats


def make_graph(measurement: str, start_date: str, end_date: str, interval: str) -> str:
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

    data = db_client.run_query(query)

    modebar = go.layout.Modebar(remove=("lasso", "lasso2d", "select", "select2d"))

    layout = go.Layout(
        margin=dict(r=10, l=10, t=30, b=10),
        xaxis={'fixedrange': True, 'title': 'Дата'},
        yaxis={'fixedrange': True, 'title': measurement},  # TODO add measurement unit
        showlegend=True,
        modebar=modebar,
        dragmode=False,
        clickmode="select"
    )

    fig = go.Figure(layout=layout)

    for (station, group_interval), group in data.groupby(['stationName', 'interval'], as_index=False):
        summarised_data = summarise_to_interval(data=group, old_interval=group_interval, new_interval=interval)
        if summarised_data is None:
            continue

        trace_name = f"{station} - {interval}"
        if len(summarised_data) < 10:
            fig.add_trace(
                go.Bar(
                    x=summarised_data.date,
                    y=summarised_data.value,
                    name=trace_name
                )
            )
        else:
            fig.add_trace(
                go.Scatter(
                    x=summarised_data.date,
                    y=summarised_data.value,
                    name=trace_name
                )
            )

    fig.update_xaxes(showspikes=True, spikemode="across")
    fig.update_layout(hovermode="x unified")
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1))
    graph = fig.to_html(full_html=False, include_plotlyjs='cdn')
    return graph
