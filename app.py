from flask import Flask
from flask_cors import CORS

from app.services.product_service import ProductService
from app.utils.config import Config
from app.db.db_postgres import PostgresDBClient
from app.db.db_mongo import MongoDBClient
from app.utils.data_cleaner import DataCleaner
from app.routes import register_routes


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