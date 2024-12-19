from kombu import Queue

# Celery Configuration for RabbitMQ
broker_url = "pyamqp://guest@localhost//"  # RabbitMQ connection URL
result_backend = "rpc://"  # Backend for storing task results (optional)

# Define custom queues and ensure they are durable
task_queues = (
    Queue("default", durable=True),  # Default queue
    Queue("delivery_mode", durable=True),  # Queue with delivery mode
    Queue("high_priority", durable=True),  # High-priority queue
)

# Default queue to use if none is specified
task_default_queue = "default"

# Enable durable queues (default behavior with RabbitMQ)
task_queue_durable = True

# Task acknowledgment
task_acks_late = True  # Ensure tasks are acknowledged only after completion
worker_prefetch_multiplier = 1  # Fair distribution of tasks among workers

# Serialization
task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]

timezone = "Canada/Atlantic"  # Set the timezone for the Celery worker
