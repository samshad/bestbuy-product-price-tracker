from time import sleep
from typing import Callable, Any
from app.utils.logging_utils import setup_logging

logger = setup_logging(__name__)


def retry_with_backoff(
    func: Callable[[], Any],
    retries: int = 3,
    initial_delay: int = 5,
    backoff_factor: int = 2,
    retry_on_none: bool = True,
) -> Any:
    """
    Retry a function with exponential backoff, including when the result is None (optional).

    Args:
        func (Callable[[], Any]): The function to retry. Should accept no arguments and return a value.
        retries (int, optional): Number of retry attempts. Default is 3.
        initial_delay (int, optional): Initial delay in seconds before the first retry. Default is 5 seconds.
        backoff_factor (int, optional): Multiplier for exponential backoff. Default is 2. Delay is doubled after each retry.
        retry_on_none (bool, optional): Whether to retry if the function returns None. Default is True.

    Returns:
        Any: The result of the function if it succeeds.

    Raises:
        Exception: The last exception encountered if all retries fail.
    """
    delay = initial_delay
    last_exception = None

    for attempt in range(1, retries + 1):
        try:
            result = func()
            if not retry_on_none and result is None:
                logger.info(
                    f"Attempt {attempt} returned None. Skipping retries as per configuration."
                )
                return None

            if result is not None:
                logger.info(f"Attempt {attempt} succeeded.")
                return result
        except Exception as e:
            last_exception = e
            logger.error(f"Attempt {attempt} failed. Error: {e}", exc_info=True)

        if attempt < retries:
            logger.warning(
                f"Retry {attempt}/{retries} failed. Retrying in {delay} seconds..."
            )
            sleep(delay)
            delay *= backoff_factor
        else:
            logger.critical(f"All {retries} retries failed.")

    if last_exception:
        raise Exception(
            f"All {retries} retries failed. Last error: {last_exception}"
        ) from last_exception

    return None
