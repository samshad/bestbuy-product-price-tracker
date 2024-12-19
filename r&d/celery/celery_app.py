from celery import Celery
from time import sleep

# Initialize Celery
celery_app = Celery("tasks")

# Load configuration from cloudamqp_config.py.py
celery_app.config_from_object("cloudamqp_config")


@celery_app.task
def add_numbers(a, b):
    sleep(20)  # Simulate a long-running task
    """A basic task that adds two numbers."""
    result = a + b
    print(f"Task executed: {a} + {b} = {result}")
    return result


# Run the Celery worker with the command:
# cd '.\r&d\celery\'
# celery -A celery_app worker --pool=solo --loglevel=info
# celery -A celery_app worker --pool=solo --without-heartbeat --without-gossip --without-mingle
