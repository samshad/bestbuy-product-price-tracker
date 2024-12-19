from typing import Dict, Any, Optional, List, Tuple

from app.db.db_mongo import MongoDBClient
from app.db.products_crud import ProductsCRUD, Products
from app.utils.datetime_handler import get_current_datetime
from app.utils.my_logger import setup_logging
from app.utils.serialization_utils import serialize_mongo_data
from app.utils.validate_input import validate_input_product_id_web_code

logger = setup_logging(__name__)


class DatabaseHandler:
    """Service for handling database operations across PostgreSQL and MongoDB."""

    def __init__(self, product_client: ProductsCRUD, mongo_client: MongoDBClient):
        """
        Initialize the DatabaseHandler.

        Args:
            product_client (ProductsCRUD): Instance for PostgreSQL operations.
            mongo_client (MongoDBClient): Instance for MongoDB operations.
        """
        self.product_client = product_client
        self.mongo_client = mongo_client
        logger.info("DatabaseHandler initialized. Product and MongoDB clients are set.")

    def store_new_product(
        self, product_details: Dict[str, Any]
    ) -> Tuple[Optional[int], Tuple[Optional[str], int]]:
        """
        Store new product data in PostgreSQL and MongoDB.

        Args:
            product_details (Dict[str, Any]): Details of the product to store.

        Returns:
            Tuple[Optional[int], Tuple[Optional[str], int]]: Product ID and status message.
        """
        try:
            # Insert product data into PostgreSQL
            response = self.product_client.insert_product(
                product_details["web_code"],
                product_details["title"],
                product_details["model"],
                product_details["url"],
                product_details["price"],
                product_details["save"],
            )

            product_id = response["product_id"]
            logger.info(f"Product stored in PostgreSQL with ID: {product_id}.")

            # Store additional data in MongoDB
            self._store_in_mongo(product_details)
            logger.info("Product data successfully stored in MongoDB.")

            return product_id, (None, 200)
        except KeyError as e:
            logger.error(f"Missing required key in product details: {e}")
            return None, ("Failed to store product data in databases.", 500)

    def update_existing_product(self, product_details: Dict[str, Any]) -> None:
        """
        Update existing product data in PostgreSQL and MongoDB.

        Args:
            product_details (Dict[str, Any]): Updated product details.
        """
        try:
            # Update PostgreSQL product data
            updates = {
                "price": product_details["price"],
                "save": product_details["save"],
            }
            self.product_client.update_product(product_details["product_id"], updates)
            logger.info(
                f"Product ID {product_details['product_id']} updated in PostgreSQL."
            )

            # Update MongoDB with new product data
            self._store_in_mongo(product_details)
            logger.info("Product data updated in MongoDB.")
        except KeyError as e:
            logger.error(f"Missing required key in product details: {e}")
            raise

    def _store_in_mongo(self, product_details: Dict[str, Any]) -> None:
        """
        Store product data in MongoDB.

        Args:
            product_details (Dict[str, Any]): Product data for MongoDB.
        """
        try:
            mongo_data = {
                "web_code": product_details["web_code"],
                "price": product_details["price"],
                "save": product_details["save"],
                "date": get_current_datetime(),
            }
            self.mongo_client.insert_data(mongo_data)
            logger.debug(
                f"MongoDB insert successful for webcode: {mongo_data['web_code']}"
            )
        except KeyError as e:
            logger.error(f"Missing required key for MongoDB insert: {e}")
            raise

    def get_all_products(self) -> List[Products]:
        """
        Retrieve all products from Products.

        Returns:
            List[Products]: List of all product records.
        """
        products = self.product_client.get_all_products()
        logger.info(f"{len(products)} products retrieved from Products.")
        return products

    def get_product_prices(self, web_code: str) -> List[Dict[str, Any]]:
        """
        Retrieve historical prices for a product from MongoDB.

        Args:
            web_code (str): The web code of the product.

        Returns:
            List[Dict[str, Any]]: Historical price data.
        """
        query = {"web_code": web_code}
        documents = self.mongo_client.get_data(query)
        logger.info(
            f"{len(documents)} price records retrieved for web code {web_code}."
        )
        return serialize_mongo_data(documents)

    def get_product(
        self, product_id: Optional[int] = None, web_code: Optional[str] = None
    ) -> Optional[Products]:
        """
        Retrieve a product by its ID or web code.

        Args:
            product_id (Optional[int]): ID of the product.
            web_code (Optional[str]): Web code of the product.

        Returns:
            Optional[Products]: Product record if found.
        """
        if not validate_input_product_id_web_code(
            product_id=product_id, web_code=web_code
        ):
            logger.error(
                "Invalid input: Provide either 'product_id' or 'web_code', but not both."
            )
            raise ValueError("Provide either 'product_id' or 'web_code', but not both.")

        product = self.product_client.get_product(product_id, web_code)
        if product:
            logger.info(f"Product retrieved. Product ID: {product.product_id}")
        else:
            logger.warning("Product not found.")
        return product
