import datetime

import pytz

from app.settings import DT_PATTERN, TIMEZONE


def timezone_convert(datetime_stmt: datetime) -> datetime.datetime:
    timezone_local = pytz.timezone(TIMEZONE)
    return datetime_stmt.astimezone(timezone_local)


def convert_dt_to_str(datetime_stmt: datetime) -> str:
    dt = timezone_convert(datetime_stmt=datetime_stmt)
    return dt.strftime(DT_PATTERN)
