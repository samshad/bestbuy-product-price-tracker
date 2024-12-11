from app.scrapers.product_details_scraper import ProductDetailsScraper
from typing import Optional, Union
from app.utils.my_logger import setup_logging
from app.utils.validate_input import validate_input_web_code_url

# Configure logging
logger = setup_logging(__name__)


class ScraperFactory:
    """Factory class for creating scrapers."""

    @staticmethod
    def create_scraper(
        webcode: Optional[str] = None, url: Optional[str] = None
    ) -> Union[ProductDetailsScraper, None]:
        """
        Create and return an appropriate scraper instance.

        Args:
            webcode (str): The product's webcode to search.
            url (str): The direct URL to the product page.

        Returns:
            ProductDetailsScraper: Instance of the ProductDetailsScraper.
            None: If both webcode and URL are missing or invalid.
        """
        try:
            if not validate_input_web_code_url(webcode, url):
                logger.error(
                    "Either 'webcode' or 'url' must be provided, but not both."
                )
                return None

            logger.info(f"Creating scraper with webcode={webcode}, url={url}")
            return ProductDetailsScraper(webcode=webcode, url=url)

        except Exception as e:
            logger.error(
                f"An error occurred while creating the scraper: {str(e)}", exc_info=True
            )
            return None
