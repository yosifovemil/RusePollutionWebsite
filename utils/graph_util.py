from datetime import datetime, timedelta

from utils import formats


def parse_date_range(dates: str) -> tuple[str, str]:
    dates_str = dates.split("-")
    start_date = datetime.strptime(dates_str[0].strip(), "%d/%m/%Y")
    end_date = datetime.strptime(dates_str[1].strip(), "%d/%m/%Y") + timedelta(days=1)

    return start_date.strftime(formats.date_format), end_date.strftime(formats.date_format)
