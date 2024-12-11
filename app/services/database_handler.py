from typing import Dict, Any, Optional, List
from app.db.db_mongo import MongoDBClient
from app.db.db_postgres import PostgresDBClient
from app.utils.config import Config
from datetime import datetime
from zoneinfo import ZoneInfo
from app.utils.my_logger import setup_logging
from app.utils.serialization_utils import serialize_mongo_data
from app.utils.validate_input import validate_input_product_id_web_code

logger = setup_logging(__name__)


class DatabaseHandler:
    """Service for handling database operations."""

    def __init__(self, postgres_client: PostgresDBClient, mongo_client: MongoDBClient):
        self.postgres_client = postgres_client
        self.mongo_client = mongo_client

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

    def get_product_prices(self, web_code: str) -> List[Dict[str, Any]]:
        """
        Retrieve product all existed prices so far from the database.

        Args:
            web_code (str): The web code of the product

        Returns:
            List[Dict[str, Any]]: A list of all product prices.
        """
        query = {"web_code": web_code}
        documents = self.mongo_client.get_data(query)
        return serialize_mongo_data(documents)

    def get_product(self, product_id: Optional[int] = None, web_code: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve a product by either ID or web code.

        Args:
            product_id (Optional[int]): The ID of the product.
            web_code (Optional[str]): The web code of the product.

        Returns:
            List[Dict[str, Any]]: A list of product records.

        Raises:
            ValueError: If neither 'product_id' nor 'web_code' is provided.
        """
        if not validate_input_product_id_web_code(product_id=product_id, web_code=web_code):
            logger.error("Either 'product_id' or 'web_code' must be provided, but not both.")
            return []

        query_filter = {"id": product_id} if product_id else {"web_code": web_code}
        return self.postgres_client.get_data(Config.TABLE_NAME, query_filter)
