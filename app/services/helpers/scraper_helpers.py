from typing import Optional

from app.db.products_crud import Products
from app.services.product_service import ProductService
from app.services.helpers.product_update_helpers import handle_existing_product
from app.services.helpers.store_product_helpers import store_new_product
from app.utils.logging_utils import setup_logging

logger = setup_logging(__name__)


class ScraperHelper:
    """A helper class for scraping and processing product details."""

    def __init__(self, product_service: ProductService):
        """
        Initialize the ScraperHelper with a product service.

        Args:
            product_service (ProductService): Service layer for product operations.
        """
        self.product_service = product_service

    def scrape_product(self, web_code: str) -> Optional[dict]:
        """
        Perform scraping and handle product logic based on the provided web_code.

        Args:
            web_code (str): The web code of the product to scrape.

        Returns:
            Optional[dict]: Product details if successful, else None.
        """
        logger.info(f"Starting scrape_product for web_code: {web_code}")

        # Fetch existing product if available
        existing_product = self.product_service.get_product(None, web_code)
        logger.debug(f"Existing product fetched: {existing_product}")

        # Scrape product details
        try:
            product_details = self.product_service.scrape_and_process_product(web_code)
            return self._process_product(existing_product, product_details, web_code)
        except Exception as e:
            logger.error(
                f"Scraping failed for web_code {web_code}: {str(e)}", exc_info=True
            )
            return None

    def _process_product(
        self,
        existing_product: Optional[Products],
        scraped_product_details: dict,
        web_code: str,
    ) -> Optional[dict]:
        """
        Process scraped product details and update or store them.

        Args:
            existing_product (Optional[Products]): The existing product details.
            scraped_product_details (dict): The product details to process and store.
            web_code (str): The web code of the product.

        Returns:
            Optional[dict]: Product details if successfully processed, else None.
        """
        if not scraped_product_details:
            logger.error(
                f"Scraped product details are missing for web_code: {web_code}",
                exc_info=True,
            )
            return None

        if existing_product:
            status_code, message = handle_existing_product(
                existing_product, scraped_product_details, self.product_service
            )
            logger.info(
                f"Updated existing product. Status: {status_code}. Message: {message}"
            )
        else:
            status_code, message = store_new_product(
                scraped_product_details, self.product_service
            )
            logger.info(
                f"Stored new product. Status: {status_code}. Message: {message}"
            )

        return scraped_product_details
