from typing import Dict, Any, Optional, List

from celery.bin.result import result

from app.db.db_mongo import MongoDBClient
from app.db.products_crud import ProductsCRUD, Products
from app.utils.datetime_handler import get_current_datetime
from app.utils.my_logger import setup_logging
from app.utils.serialization_utils import serialize_mongo_data
from app.utils.validate_input import validate_input_product_id_web_code

logger = setup_logging(__name__)


class DatabaseHandler:
    """Service for handling database operations."""

    def __init__(self, product_client: ProductsCRUD, mongo_client: MongoDBClient):
        """
        Initialize the DatabaseHandler.

        Args:
            product_client (ProductsCRUD): Instance of ProductsCRUD for PostgreSQL operations.
            mongo_client (MongoDBClient): Instance of MongoDBClient for MongoDB operations.
        """
        self.product_client = product_client
        self.mongo_client = mongo_client
        logger.info("DatabaseHandler initialized. Product and MongoDB clients are set.")

    def store_new_product(self, product_details: Dict[str, Any]) -> tuple[int, tuple[None, None]] | tuple[
        None, tuple[str, int]]:
        """
        Store new product data in PostgreSQL and MongoDB.

        Args:
            product_details (Dict[str, Any]): Product details to store.

        Returns:
            Optional[int]: The product ID if stored successfully, otherwise None.
        """
        try:
            response = self.product_client.insert_product(
                product_details["web_code"],
                product_details["title"],
                product_details["model"],
                product_details["url"],
                product_details["price"],
                product_details["save"],
            )

            product_id = response["product_id"]

            logger.info(f"Product data stored in PostgreSQL. Product ID: {product_id}")

            self._store_in_mongo(product_details)
            logger.info("Product data stored in MongoDB.")
            return product_id, (None, None)
        except KeyError as e:
            logger.error(f"Missing required key in product details: {e}")
            return None, ("Failed to store product data in PostgreSQL and MongoDB.", 500)

    def update_existing_product(self, product_details: Dict[str, Any]) -> None:
        """
        Update existing product data in PostgreSQL and MongoDB.

        Args:
            product_details (Dict[str, Any]): Product details to update.

        Raises:
            KeyError: If required keys are missing in product_details.
        """
        try:
            to_update = {
                "price": product_details["price"],
                "save": product_details["save"],
            }
            self.product_client.update_product(product_details["product_id"], to_update)
            logger.info("Product data updated in PostgreSQL.")

            self._store_in_mongo(product_details)
            logger.info("Product data updated in MongoDB.")
        except KeyError as e:
            logger.error(f"Missing required key in product details: {e}")
            raise

    def _store_in_mongo(self, product_details: Dict[str, Any]) -> None:
        """
        Store product data in MongoDB.

        Args:
            product_details (Dict[str, Any]): Product details to store.

        Raises:
            KeyError: If required keys are missing in product_details.
        """
        try:
            mongo_data = {
                "web_code": product_details["web_code"],
                "price": product_details["price"],
                "save": product_details["save"],
                "date": get_current_datetime(),
            }
            self.mongo_client.insert_data(mongo_data)
        except KeyError as e:
            logger.error(f"Missing required key for MongoDB data: {e}")
            raise

    def get_all_products(self) -> List[Products]:
        """
        Retrieve all products from the PostgreSQL database.

        Returns:
            List[Products]: A list of all product records.
        """
        products = self.product_client.get_all_products()
        logger.info(
            f"Retrieved {len(products)} products from Products table in PostgreSQL."
        )
        return products

    def get_product_prices(self, web_code: str) -> List[Dict[str, Any]]:
        """
        Retrieve all historical prices for a product from MongoDB.

        Args:
            web_code (str): The web code of the product.

        Returns:
            List[Dict[str, Any]]: A list of all product price records.
        """
        query = {"web_code": web_code}
        documents = self.mongo_client.get_data(query)
        logger.info(
            f"Retrieved {len(documents)} price records for product web code: {web_code}."
        )
        return serialize_mongo_data(documents)

    def get_product(
        self, product_id: Optional[int] = None, web_code: Optional[str] = None
    ) -> Optional[Products]:
        """
        Retrieve a product by either ID or web code.

        Args:
            product_id (Optional[int]): The ID of the product.
            web_code (Optional[str]): The web code of the product.

        Returns:
            Optional[Dict[str, Any]]: The product record, or None if not found.

        Raises:
            ValueError: If neither product_id nor web_code is provided, or both are provided.
        """
        if not validate_input_product_id_web_code(
            product_id=product_id, web_code=web_code
        ):
            logger.error(
                "Either 'product_id' or 'web_code' must be provided, but not both."
            )
            raise ValueError(
                "Invalid input: Provide either 'product_id' or 'web_code', but not both."
            )

        product = self.product_client.get_product(product_id, web_code)
        if product:
            logger.info("Product retrieved successfully.")
        else:
            logger.warning("Product not found.")
        return product
