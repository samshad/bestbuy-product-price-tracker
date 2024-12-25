# Import the retry_with_backoff function
from app.utils.retry_with_backoff import retry_with_backoff


# Define your get_data() method
def get_data():
    """
    Example method to simulate data retrieval.
    Replace this with your actual implementation.
    """
    print("Attempting to fetch data...")
    # Simulate a potential exception (e.g., network or database failure)
    flag = True  # Set to True to simulate a failure
    if flag:  # Replace with your actual condition
        raise Exception("Data retrieval failed!")
    return {"data": "Sample data"}


# Use retry_with_backoff to call get_data with retries
if __name__ == "__main__":
    try:
        # Wrap get_data with retry_with_backoff
        result = retry_with_backoff(
            get_data, retries=5, initial_delay=2, backoff_factor=2
        )
        print("Data fetched successfully:", result)
    except Exception as e:
        print("Failed to fetch data after retries:", str(e))
