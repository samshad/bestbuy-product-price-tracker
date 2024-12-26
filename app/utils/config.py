import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    # Application Configuration
    TABLE_NAME = "products"
    ALLOWED_ORIGINS = ["*"]

    # MongoDB Configuration
    MONGO_USERNAME = os.getenv("MONGO_USERNAME")
    MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
    MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME")
    MONGO_URI = os.getenv("MONGO_URI")

    # PostgreSQL Configuration
    POSTGRES_URI = os.getenv("POSTGRES_URI")

    # Flask Configuration
    FLASK_ENV = os.getenv("FLASK_ENV", "production")
    DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1")
    BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 5000) or 5000)

    # Logging Configuration
    LOG_DIRECTORY = os.getenv("LOG_DIRECTORY", "logs/")

    # Timezone
    TIMEZONE = os.getenv("TIMEZONE", "Canada/Atlantic")

    # RabbitMQ Configuration
    CLOUDAMQP_URL = os.getenv("CLOUDAMQP_URL")
    RABBITMQ_BROKER = os.getenv("RABBITMQ_BROKER")
    RABBITMQ_MESSAGE_PORT = int(os.getenv("RABBITMQ_MESSAGE_PORT", 5672))
    RABBITMQ_MANAGEMENT_PORT = int(os.getenv("RABBITMQ_MENAGEMENT_PORT", 15672))

    # Redis Configuration
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_COMMANDER_PORT = int(os.getenv("REDIS_COMMANDER_PORT", 8081))


if __name__ == "__main__":
    """Print all the configuration variables."""

    print(Config.POSTGRES_URI)
    print(Config.MONGO_URI)
    print(Config.REDIS_HOST)
    print(Config.REDIS_PORT)
    print(Config.REDIS_COMMANDER_PORT)
    print(Config.CLOUDAMQP_URL)
    print(Config.RABBITMQ_BROKER)
    print(Config.RABBITMQ_MESSAGE_PORT)
    print(Config.RABBITMQ_MANAGEMENT_PORT)
    print(Config.TIMEZONE)
    print(Config.LOG_DIRECTORY)
    print(Config.BASE_URL)
    print(Config.HOST)
    print(Config.PORT)
    print(Config.FLASK_ENV)
    print(Config.DEBUG)
    print(Config.ALLOWED_ORIGINS)
    print(Config.TABLE_NAME)
    print(Config.MONGO_USERNAME)
    print(Config.MONGO_PASSWORD)
    print(Config.MONGO_DB_NAME)
    print(Config.MONGO_COLLECTION_NAME)
