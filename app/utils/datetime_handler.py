from datetime import datetime
from zoneinfo import ZoneInfo


def get_current_datetime():
    """
    Get the current datetime in the Canada/Atlantic timezone.

    Returns:
        str: The current datetime in ISO 8601 format.
    """
    return datetime.now(ZoneInfo("Canada/Atlantic")).isoformat()


def parse_datetime(datetime_str: str) -> datetime:
    """
    Parse a datetime string into a datetime object.

    Args:
        datetime_str (str): The datetime string to parse.

    Returns:
        datetime: The parsed datetime object.
    """
    return datetime.fromisoformat(datetime_str)
