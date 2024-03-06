import pandas as pd
from data.interval import summarise_to_interval
from database.data_db import DataDB


def get_readings(measurement: str,
                 start_date: str | None = None,
                 end_date: str | None = None,
                 intervals=None) -> pd.DataFrame:
    db_client = DataDB()
    if measurement == 'p-о- Крезол':
        query = __build_query(measurements=['p-Крезол', 'о-Крезол'], start_date=start_date, end_date=end_date,
                              intervals=intervals)
    elif measurement == 'Ксилен':
        query = __build_query(measurements=['Ксилен', 'm- p-Ксилен', 'о-Ксилен'], start_date=start_date,
                              end_date=end_date, intervals=intervals)
    else:
        query = __build_query(measurements=[measurement], start_date=start_date, end_date=end_date, intervals=intervals)

    query_data = db_client.select_query(query)
    if len(query_data) > 0:
        query_data = query_data.groupby(['date', 'stationName', 'interval', 'unit'], as_index=False).sum()

    return query_data


def group_and_summarise(data: pd.DataFrame, interval: str) -> pd.DataFrame:
    data = data.copy()[['date', 'stationName', 'interval', 'value']]

    dfs = []
    for (station, group_interval), group in data.groupby(['stationName', 'interval'], as_index=False):
        summarised_data = summarise_to_interval(
            data=group[['date', 'stationName', 'value']].copy(),
            old_interval=group_interval,
            new_interval=interval
        )

        if summarised_data is None:
            continue

        dfs.append(summarised_data)

    return pd.concat(dfs)


def __build_query(measurements: list[str], start_date: str | None, end_date: str | None, intervals: str | None) -> str:
    query = f"""
    SELECT date, Station.name AS stationName, MeasurementInterval.name as interval, value, Measurement.unit as unit
    FROM Reading
    LEFT JOIN Station ON Reading.stationId = Station.id
    LEFT JOIN Measurement ON Reading.measurementId = Measurement.id
    LEFT JOIN MeasurementInterval ON Reading.intervalId = MeasurementInterval.id
    WHERE Measurement.name IN {to_sql_array(measurements)}
    """

    if start_date and end_date:
        query += f" AND date >= '{start_date}' AND date <= '{end_date}'"

    if intervals:
        query += f" AND MeasurementInterval.name IN {to_sql_array(intervals)}"

    return query


def to_sql_array(lst: list[str]) -> str:
    return "('" + str.join("', '", lst) + "')"
