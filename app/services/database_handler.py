from typing import Dict, Any, Optional, List
from app.db.db_mongo import MongoDBClient
from app.db.db_postgres import PostgresDBClient
from app.utils.config import Config
from datetime import datetime
from zoneinfo import ZoneInfo


class DatabaseHandler:
    """Service for handling database operations."""

    def __init__(self, postgres_client: PostgresDBClient, mongo_client: MongoDBClient):
        self.postgres_client = postgres_client
        self.mongo_client = mongo_client

    def get_existing_product(self, web_code: str) -> List[Dict[str, Any]]:
        """
        Retrieve an existing product by web code.

        Args:
            web_code (str): The web code of the product.

        Returns:
            List[Dict[str, Any]]: A list of product records.
        """
        return self.postgres_client.get_data(Config.TABLE_NAME, {"web_code": web_code})

    def store_new_product(self, product_details: Dict[str, Any]) -> None:
        """
        Store new product data in PostgreSQL and MongoDB.

        Args:
            product_details (Dict[str, Any]): Product details to store.

        Returns:
            None
        """
        self.postgres_client.insert_data(Config.TABLE_NAME, product_details)
        self._store_in_mongo(product_details)

    def update_existing_product(self, product_details: Dict[str, Any]) -> None:
        """
        Update existing product data in PostgreSQL and MongoDB.

        Args:
            product_details (Dict[str, Any]): Product details to update.

        Returns:
            None
        """
        current_time = datetime.now(ZoneInfo("Canada/Atlantic")).isoformat()
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
        """
        Store product data in MongoDB.

        Args:
            product_details (Dict[str, Any]): Product details to store.

        Returns:
            None
        """
        self.mongo_client.insert_data({
            "web_code": product_details["web_code"],
            "price": product_details["price"],
            "save": product_details["save"],
            "date": product_details["date"]
        })

    def get_all_products(self) -> List[Dict[str, Any]]:
        """
        Retrieve all products from the database.

        Returns:
            List[Dict[str, Any]]: A list of all product records.
        """
        return self.postgres_client.get_data(Config.TABLE_NAME)

