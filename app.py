import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

from app.services.product_service import ProductService
from app.services.scraper_service import ScraperService
from app.services.product_processor import ProductProcessor
from app.services.database_handler import DatabaseHandler
from app.utils.config import Config
from app.db.db_postgres import PostgresDBClient
from app.db.db_mongo import MongoDBClient
from app.utils.data_cleaner import DataCleaner
from app.routes import register_routes
from app.utils.my_logger import setup_logging

logger = setup_logging(__name__)

# Load environment variables from .env file
if not load_dotenv():
    logger.warning(".env file not found. Default values will be used.")


def create_app() -> Flask:
    """Create and configure Flask application."""
    app = Flask(__name__)

    # Initialize services and utilities
    postgres_client = PostgresDBClient()
    mongo_client = MongoDBClient()
    data_cleaner = DataCleaner()
    scraper_service = ScraperService()
    product_processor = ProductProcessor(data_cleaner)
    database_handler = DatabaseHandler(postgres_client, mongo_client)

    # Configure CORS
    if not Config.ALLOWED_ORIGINS:
        raise ValueError("Config.ALLOWED_ORIGINS is not set. Please define allowed origins in your configuration.")
    CORS(app, resources={
        r"/*": {
            "origins": Config.ALLOWED_ORIGINS,
            "methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE"],
            "allow_headers": ["Content-Type"]
        }
    })

    # Initialize services
    try:
        logger.info("Initializing services...")
        product_service = ProductService(
            scraper_service=scraper_service,
            product_processor=product_processor,
            database_handler=database_handler
        )
        logger.info("Services initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing services: {str(e)}")
        raise

    # Register routes
    register_routes(app, product_service)

    return app


if __name__ == "__main__":
    try:
        app = create_app()
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", 5000))
        debug = os.getenv("DEBUG", "True").lower() == "true"

        logger.info(f"Starting Flask app on {host}:{port} (debug={debug})")
        app.run(host=host, port=port, debug=debug)
    except Exception as e:
        logger.critical(f"Failed to start Flask app: {str(e)}", exc_info=True)
