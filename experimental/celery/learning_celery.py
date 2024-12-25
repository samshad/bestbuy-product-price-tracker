from celery import Celery
from time import sleep

app = Celery("tasks", broker="pyamqp://guest@localhost//")


@app.task
def add(x, y):
    sleep(5)
    return x + y


# Run the Celery worker with the following command:
# cd '.\experimental\celery\' && celery -A learning_celery worker --loglevel=info
# celery -A ./experimental/celery/learning_celery worker --loglevel=info
