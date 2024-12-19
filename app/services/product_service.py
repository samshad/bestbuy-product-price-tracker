from typing import Dict, Any, Tuple, List, Optional

from app.db.products_crud import Products
from app.services.scraper_service import ScraperService
from app.services.product_processor import ProductProcessor
from app.services.database_handler import DatabaseHandler
from app.utils.datetime_handler import parse_datetime, get_current_datetime
from app.utils.my_logger import setup_logging
from app.utils.validate_input import validate_input_product_id_web_code

logger = setup_logging(__name__)


class ProductService:
    """High-level service for product operations."""

    def __init__(
        self,
        scraper_service: ScraperService,
        product_processor: ProductProcessor,
        database_handler: DatabaseHandler,
    ):
        self.scraper_service = scraper_service
        self.product_processor = product_processor
        self.database_handler = database_handler

    def scrape_and_process_product(self, webcode: str, url: str) -> Dict[str, Any]:
        """
        Scrape and process product details.

        Args:
            webcode (str): The webcode of the product.
            url (str): The URL of the product.

        Returns:
            Dict[str, Any]: The processed product details.
        """
        raw_data = self.scraper_service.scrape_product(webcode, url)
        if not raw_data:
            raise ValueError("Failed to scrape product data. Check webcode or URL.")
        return self.product_processor.process_product_data(raw_data)

    def handle_product(self, product_details: Dict[str, Any]) -> tuple[Any, tuple[str, int]] | tuple[
        int | None, tuple[str, int]]:
        """
        Handle product storage logic.

        Args:
            product_details (Dict[str, Any]): The product details to store.

        Returns:
            Tuple[str, int]: A message and status code.
        """
        existing_product = self.database_handler.get_product(product_id=None, web_code=product_details["web_code"])

        if existing_product:
            return self._handle_existing_product(product_details, existing_product)

        product_id = self.database_handler.store_new_product(product_details)
        return product_id, ("Product data added to PostgreSQL and MongoDB.", 201)

    def _handle_existing_product(
        self, product_details: Dict[str, Any], existing_product: Products
    ) -> tuple[Any, tuple[str, int]]:
        """
        Handle logic for existing products.

        Args:
            product_details (Dict[str, Any]): The product details to store.
            existing_product (Dict[str, Any]): The existing product details.

        Returns:
            Tuple[Any, Tuple[str, int]]: The product ID and a message with status code.
        """
        current_date = parse_datetime(get_current_datetime()).date()
        stored_date = existing_product.updated_at.date()

        if current_date == stored_date:
            return existing_product.product_id, ("Product already exists for today. No action taken.", 200)

        self.database_handler.update_existing_product(product_details)
        return existing_product.product_id, ("Product price updated and new data added to MongoDB.", 200)

    def get_all_products(self) -> List[Dict[str, Any]]:
        """
        Fetch all product details from the database.

        Returns:
            List[Dict[str, Any]]: A list of all product details.
        """
        try:
            products = self.database_handler.get_all_products()
            return products
        except Exception as e:
            logger.error(f"Error fetching all products: {str(e)}")
            return []

    def get_product_prices(self, web_code: str) -> List[Dict[str, Any]]:
        """
        Fetch all price details for a product from the database.

        Args:
            web_code (str): The webcode of the product.

        Returns:
            List[Dict[str, Any]]: A list of all price details for the product.
        """
        try:
            prices = self.database_handler.get_product_prices(web_code)
            return prices
        except Exception as e:
            logger.error(f"Error fetching product prices: {str(e)}")
            return []

    def get_product(
        self, product_id: Optional[int] = None, web_code: Optional[str] = None
    ) -> Products | None:
        """
        Retrieve product by id or web code from the database.

        Args:
            product_id (Optional[int]): The id of the product
            web_code (Optional[str]): The web code of the product

        Returns:
            Dict[str, Any]: A dict of product record.
        """
        # Validate input to ensure either 'web_code' or 'product_id' is provided, but not both.
        if not validate_input_product_id_web_code(
            product_id=product_id, web_code=web_code
        ):
            logger.error(
                "Either 'product_id' or 'web_code' must be provided, but not both."
            )
            return None

        try:
            product = self.database_handler.get_product(product_id=product_id, web_code=web_code)
            return product if product else None
        except Exception as e:
            logger.error(f"Error fetching existing product: {str(e)}")
            return None
