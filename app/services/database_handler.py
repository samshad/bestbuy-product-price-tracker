from typing import Dict, Any, Optional
from app.db.db_mongo import MongoDBClient
from app.db.db_postgres import PostgresDBClient
from app.utils.config import Config
from datetime import datetime


class DatabaseHandler:
    """Service for handling database operations."""

    def __init__(self, postgres_client: PostgresDBClient, mongo_client: MongoDBClient):
        self.postgres_client = postgres_client
        self.mongo_client = mongo_client

    def get_existing_product(self, web_code: str) -> Optional[Dict[str, Any]]:
        """Retrieve an existing product by web code."""
        return self.postgres_client.get_data(Config.TABLE_NAME, {"web_code": web_code})

    def store_new_product(self, product_details: Dict[str, Any]) -> None:
        """Store new product data in PostgreSQL and MongoDB."""
        self.postgres_client.insert_data(Config.TABLE_NAME, product_details)
        self._store_in_mongo(product_details)

    def update_existing_product(self, product_details: Dict[str, Any]) -> None:
        """Update existing product data in PostgreSQL and MongoDB."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.postgres_client.update_data(
            Config.TABLE_NAME,
            {
                "price": product_details["price"],
                "date": current_time
            },
            {"web_code": product_details["web_code"]}
        )
        self._store_in_mongo(product_details)

    def _store_in_mongo(self, product_details: Dict[str, Any]) -> None:
        """Store product data in MongoDB."""
        self.mongo_client.insert_data({
            "web_code": product_details["web_code"],
            "price": product_details["price"],
            "save": product_details["save"],
            "date": product_details["date"]
        })