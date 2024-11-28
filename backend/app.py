from flask import Flask
from flask_cors import CORS
from product_service import ProductService
from api_response import APIResponse
from config import Config
from db_postgres import PostgresDBClient
from db_mongo import MongoDBClient
from data_cleaner import DataCleaner
from routes import register_routes


def create_app() -> Flask:
    """Create and configure Flask application."""
    app = Flask(__name__)

    # Configure CORS
    CORS(app, resources={
        r"/*": {
            "origins": Config.ALLOWED_ORIGINS,
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })

    # Initialize services
    product_service = ProductService(
        postgres_client=PostgresDBClient(),
        mongo_client=MongoDBClient(),
        data_cleaner=DataCleaner()
    )

    # Register routes
    register_routes(app, product_service)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=Config.DEBUG)