import time

def retry_with_backoff(func, retries=3, initial_delay=5, backoff_factor=2):
    """
    Retry a function with exponential backoff.

    Args:
        func (callable): The function to retry.
        retries (int): Number of retry attempts.
        initial_delay (int): Initial delay in seconds.
        backoff_factor (int): Multiplier for exponential backoff.

    Returns:
        Any: Result of the function, or raises the last exception.
    """
    delay = initial_delay
    for attempt in range(retries):
        try:
            return func()
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(delay)
                delay *= backoff_factor
            else:
                raise e

