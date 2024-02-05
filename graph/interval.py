import pandas as pd

INTERVAL_HOURLY = "Средночасова стойност"
INTERVAL_DAILY = "Средноденонощна стойност"
INTERVAL_MAX_HOURLY = "Максимална средночасова стойност"
INTERVAL_MIN_HOURLY = "Минимална средночасова стойност"
INTERVAL_MAX_8HR = "Максимална 8-часова средна стойност"
INTERVAL_30MIN = "Средна 30-минутна стойност"
INTERVAL_5MIN = "Средна 5-минутна стойност"

VALID_INTERVALS = [
    INTERVAL_5MIN,
    INTERVAL_30MIN,
    INTERVAL_HOURLY,
    INTERVAL_DAILY,
    INTERVAL_MAX_HOURLY,
    INTERVAL_MIN_HOURLY,
    INTERVAL_MAX_8HR
]


def summarise_to_interval(data: pd.DataFrame, old_interval: str, new_interval: str) -> pd.DataFrame:
    if old_interval == new_interval:
        return data

    old_interval_index = VALID_INTERVALS.index(old_interval)
    new_interval_index = VALID_INTERVALS.index(new_interval)

    if old_interval_index > new_interval_index:
        return None

    if new_interval == INTERVAL_DAILY:
        format = "%Y-%m-%d"
    elif new_interval == INTERVAL_HOURLY:
        format = "%Y-%m-%d %H"
    else:
        return data

    data.date = pd.to_datetime(data.date.dt.strftime(format), format=format)
    data = data.groupby(['date'], as_index=False).value.mean()

    return data
