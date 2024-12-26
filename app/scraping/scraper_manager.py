from app.scraping.product_details_scraper import ProductDetailsScraper
from typing import Union
from app.utils.logging_utils import setup_logging

# Configure logging
logger = setup_logging(__name__)


class ScraperFactory:
    """Factory class for creating scraping."""

    @staticmethod
    def create_scraper(webcode: str) -> Union[ProductDetailsScraper, None]:
        """
        Create and return an appropriate scraper instance.

        Args:
            webcode (str): The product's webcode to search.

        Returns:
            ProductDetailsScraper: Instance of the ProductDetailsScraper.
            None: If both webcode and URL are missing or invalid.
        """
        try:
            if not webcode:
                logger.error("Product 'webcode' must be provided to create a scraper.")
                return None

            logger.info(f"Creating scraper with webcode={webcode}")
            return ProductDetailsScraper(webcode=webcode)

        except Exception as e:
            logger.error(
                f"An error occurred while creating the scraper: {str(e)}", exc_info=True
            )
            return None
