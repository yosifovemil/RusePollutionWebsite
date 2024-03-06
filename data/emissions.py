from database.data_db import DataDB


def get_emissions(start_date: str, end_date: str):
    db_client = DataDB()
    query = f"SELECT * FROM EmissionEvent WHERE date >= '{start_date}' AND date <= '{end_date}'"
    data = db_client.select_query(query, date_format="%Y-%m-%d")
    return data
