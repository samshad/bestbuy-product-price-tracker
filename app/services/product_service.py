from typing import Dict, Any, Tuple, List, Optional

from app.db.products_crud import Products
from app.services.scraper_service import ScraperService
from app.services.product_processor import ProductProcessor
from app.services.database_handler import DatabaseHandler
from app.utils.datetime_handler import parse_datetime, get_current_datetime
from app.utils.logging_utils import setup_logging
from app.utils.validate_input import validate_input_product_id_web_code

logger = setup_logging(__name__)

# Constants for HTTP status codes
STATUS_OK = 200
STATUS_CREATED = 201
STATUS_ERROR = 500


class ProductService:
    """High-level service for managing product operations."""

    def __init__(
        self,
        scraper_service: ScraperService,
        product_processor: ProductProcessor,
        database_handler: DatabaseHandler,
    ) -> None:
        """
        Initialize the ProductService with necessary dependencies.

        Args:
            scraper_service (ScraperService): Service to scrape product data.
            product_processor (ProductProcessor): Service to process scraped product data.
            database_handler (DatabaseHandler): Service to handle database operations.
        """
        self.scraper_service = scraper_service
        self.product_processor = product_processor
        self.database_handler = database_handler

    def scrape_and_process_product(self, webcode: str) -> Dict[str, Any]:
        """
        Scrape product data from the given webcode and process it.

        Args:
            webcode (str): Unique webcode identifying the product.

        Returns:
            Dict[str, Any]: Processed product data.

        Raises:
            ValueError: If scraping fails or no data is returned.
        """
        raw_data = self.scraper_service.scrape_product(webcode)
        if not raw_data:
            logger.error(f"Failed to scrape data for webcode {webcode}.", exc_info=True)
            raise ValueError("Failed to scrape product data. Verify webcode.")
        logger.info(f"Scraped data for webcode {webcode}: {raw_data}")
        return self.product_processor.process_product_data(raw_data)

    def store_product(
        self, product_details: Dict[str, Any]
    ) -> Tuple[Optional[int], Tuple[str, int]]:
        """
        Store product details in the database.

        Args:
            product_details (Dict[str, Any]): The product data to store.

        Returns:
            Tuple[Optional[int], Tuple[str, int]]: Product ID and status message with HTTP code.
        """
        try:
            product_id, (message, status_code) = (
                self.database_handler.store_new_product(product_details)
            )
            if product_id:
                logger.info(f"Product {product_id} stored successfully.")
                return product_id, (
                    "Product data added to PostgreSQL and MongoDB.",
                    STATUS_CREATED,
                )
            logger.error(f"Failed to store product: {message}", exc_info=True)
            return None, (message, status_code)
        except Exception as e:
            logger.error(f"Unexpected error storing product: {e}", exc_info=True)
            return None, ("Internal server error", STATUS_ERROR)

    def handle_existing_product(
        self, existing_product: Products, new_product_details: Dict[str, Any]
    ) -> Tuple[str, int]:
        """
        Update or skip processing for an existing product based on the last update date.

        Args:
            existing_product (Products): Existing product record from the database.
            new_product_details (Dict[str, Any]): Newly scraped product details.

        Returns:
            Tuple[str, int]: Status message and HTTP code.
        """
        current_date = parse_datetime(get_current_datetime()).date()
        stored_date = existing_product.updated_at.date()

        new_product_details["product_id"] = existing_product.product_id

        if existing_product.price != new_product_details["price"]:
            self.database_handler.update_existing_product(new_product_details)
            logger.info(
                f"Product ID: {existing_product.product_id} updated successfully."
            )
            return "Product details updated.", STATUS_OK

        if current_date == stored_date:
            logger.info(f"Product {existing_product.product_id} already updated today.")
            return "Product already updated today.", STATUS_OK

        self.database_handler.update_existing_product(new_product_details)
        logger.info(
            f"Product {new_product_details['product_id']} updated successfully."
        )
        return "Product details updated.", STATUS_OK

    def get_all_products(self) -> List[Products]:
        """
        Retrieve all products from the database.

        Returns:
            List[Products]: A list of all product records.
        """
        try:
            return self.database_handler.get_all_products()
        except Exception as e:
            logger.error(f"Error fetching all products: {e}", exc_info=True)
            return []

    def get_product_prices(self, web_code: str) -> List[Dict[str, Any]]:
        """
        Retrieve all price details for a product by its web code.

        Args:
            web_code (str): Webcode identifying the product.

        Returns:
            List[Dict[str, Any]]: Price history for the product.
        """
        try:
            return self.database_handler.get_product_prices(web_code)
        except Exception as e:
            logger.error(
                f"Error fetching prices for webcode {web_code}: {e}", exc_info=True
            )
            return []

    def get_product(
        self, product_id: Optional[int] = None, web_code: Optional[str] = None
    ) -> Optional[Products]:
        """
        Retrieve a product by its ID or web code.

        Args:
            product_id (Optional[int]): ID of the product to fetch.
            web_code (Optional[str]): Web code of the product to fetch.

        Returns:
            Optional[Products]: Product record or None if not found.

        Raises:
            ValueError: If both `product_id` and `web_code` are missing or invalid.
        """
        if not validate_input_product_id_web_code(
            product_id=product_id, web_code=web_code
        ):
            logger.error(
                "Invalid input: Provide either 'product_id' or 'web_code'. But not both!",
                exc_info=True,
            )
            return None

        try:
            return self.database_handler.get_product(
                product_id=product_id, web_code=web_code
            )
        except Exception as e:
            logger.error(
                f"Error fetching product by ID {product_id} or web code {web_code}: {e}",
                exc_info=True,
            )
            return None
