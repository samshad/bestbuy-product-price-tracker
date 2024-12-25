import pika

# Configuration
RABBITMQ_HOST = "localhost"  # Change if RabbitMQ is hosted remotely
TEST_QUEUE = "test_queue"


def test_rabbitmq_connection():
    """Test if RabbitMQ server is reachable."""
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST)
        )
        print("✅ Successfully connected to RabbitMQ server!")
        connection.close()
        return True
    except Exception as e:
        print(f"❌ Failed to connect to RabbitMQ server: {e}")
        return False


def test_queue_functionality():
    """Test if a queue can be created, publish a message, and consume it."""
    try:
        # Step 1: Connect to RabbitMQ
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST)
        )
        channel = connection.channel()

        # Step 2: Declare the queue
        channel.queue_declare(queue=TEST_QUEUE, durable=False)
        print(f"✅ Queue '{TEST_QUEUE}' declared successfully.")

        # Step 3: Publish a test message
        test_message = "Hello, RabbitMQ!"
        channel.basic_publish(exchange="", routing_key=TEST_QUEUE, body=test_message)
        print(f"✅ Test message sent: '{test_message}'")

        # Step 4: Consume the message
        def callback(ch, method, properties, body):
            print(f"✅ Message received: {body.decode()}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            # Close the connection after receiving the message
            connection.close()

        channel.basic_consume(queue=TEST_QUEUE, on_message_callback=callback)

        print("🔄 Waiting for message to confirm queue functionality...")
        channel.start_consuming()

    except Exception as e:
        print(f"❌ Error testing queue functionality: {e}")


if __name__ == "__main__":
    print("=== RabbitMQ Server and Queue Test ===")
    if test_rabbitmq_connection():
        test_queue_functionality()
    else:
        print("❌ RabbitMQ server is not reachable. Fix the connection first.")
