from celery_app import add_numbers


def test_add_task():
    """Send a task to add two numbers."""
    print("Sending task to add 5 and 7...")
    # Send the task to the Celery worker with persistent queue
    result = add_numbers.delay(5, 7)  # Sends task to RabbitMQ queue

    # Wait for the result
    print("Task sent. Waiting for result...")
    print(f"Task ID: {result.product_id}")

    # Wait for the task to complete and print the result
    # result.wait()  # Wait for the task to complete
    # print(f"Task result: {result.result}")
    # print("Task completed.")


if __name__ == "__main__":
    test_add_task()
