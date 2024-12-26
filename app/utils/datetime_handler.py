from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo
from app.utils.config import Config

timezone = Config.TIMEZONE


def get_current_datetime() -> Optional[str]:
    """
    Get the current datetime in the Canada/Atlantic timezone.

    Returns:
        str: The current datetime for the given timezone in ISO 8601 format.
    """
    return datetime.now(ZoneInfo(timezone)).isoformat()


def parse_datetime(datetime_str: str) -> Optional[datetime]:
    """
    Parse a datetime string into a datetime object.

    Args:
        datetime_str (str): The datetime string to parse.

    Returns:
        datetime: The parsed datetime object.
    """
    return datetime.fromisoformat(datetime_str)
