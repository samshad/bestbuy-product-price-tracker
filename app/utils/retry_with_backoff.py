from time import sleep
from typing import Callable, Any
from app.utils.my_logger import setup_logging

logger = setup_logging(__name__)


def retry_with_backoff(
    func: Callable[[], Any],
    retries: int = 3,
    initial_delay: int = 5,
    backoff_factor: int = 2,
) -> Any:
    """
    Retry a function with exponential backoff.

    Args:
        func (Callable[[], Any]): The function to retry. Should accept no arguments and return a value.
        retries (int, optional): Number of retry attempts. Default is 3.
        initial_delay (int, optional): Initial delay in seconds before the first retry. Default is 5 seconds.
        backoff_factor (int, optional): Multiplier for exponential backoff. Default is 2. Delay is doubled after each retry.

    Returns:
        Any: The result of the function if it succeeds.

    Raises:
        Exception: The last exception encountered if all retries fail.
    """
    delay = initial_delay
    for attempt in range(retries):
        try:
            return func()
        except Exception as e:
            if attempt < retries - 1:
                sleep(delay)
                delay *= backoff_factor
                print(
                    f"Retry {attempt + 1}/{retries} failed. Retrying in {delay} seconds..."
                )
            else:
                print(f"All {retries} retries failed.")
                logger.exception(f"All {retries} retries failed. Error: {e}")
                raise e
