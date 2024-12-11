from typing import Dict, Any, Tuple, List
from datetime import datetime
from app.services.scraper_service import ScraperService
from app.services.product_processor import ProductProcessor
from app.services.database_handler import DatabaseHandler
from app.utils.my_logger import setup_logging

logger = setup_logging(__name__)


class ProductService:
    """High-level service for product operations."""

    def __init__(
        self,
        scraper_service: ScraperService,
        product_processor: ProductProcessor,
        database_handler: DatabaseHandler
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

    def handle_product(self, product_details: Dict[str, Any]) -> Tuple[str, int]:
        """
        Handle product storage logic.

        Args:
            product_details (Dict[str, Any]): The product details to store.

        Returns:
            Tuple[str, int]: A message and status code.
        """
        existing_product = self.database_handler.get_existing_product(product_details["web_code"])

        if existing_product:
            return self._handle_existing_product(product_details, existing_product[0])

        self.database_handler.store_new_product(product_details)
        return "Product data added to PostgreSQL and MongoDB.", 201

    def _handle_existing_product(self, product_details: Dict[str, Any],
                                 existing_product: Dict[str, Any]) -> Tuple[str, int]:
        """
        Handle logic for existing products.

        Args:
            product_details (Dict[str, Any]): The product details to store.
            existing_product (Dict[str, Any]): The existing product details.

        Returns:
            Tuple[str, int]: A message and status code.
        """
        current_date = datetime.now().date()
        stored_date = existing_product["date"].date()

        if current_date == stored_date:
            return "Product already exists for today. No action taken.", 200

        self.database_handler.update_existing_product(product_details)
        return "Product price updated and new data added to MongoDB.", 200

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
