from typing import Dict, Any, Optional
from app.scraping.scraper_manager import ScraperFactory
from app.utils.logging_utils import setup_logging

logger = setup_logging(__name__)


class ScraperService:
    """Service for handling product scraping."""

    def scrape_product(self, webcode: str) -> Optional[Dict[str, Any]]:
        """
        Scrape product details using the appropriate scraper.

        Args:
            webcode (str): Product web code.

        Returns:
            Optional[Dict[str, Any]]: Scraped product data if successful, or None if scraping fails.

        Raises:
            Exception: If the scraping process encounters an unexpected issue.
        """
        try:
            logger.debug(f"Creating scraper for webcode: {webcode}")
            scraper = ScraperFactory.create_scraper(webcode)

            if not scraper:
                logger.error(f"No suitable scraper found for webcode: {webcode}")
                return None

            product_details = scraper.scrape()
            if not product_details:
                logger.warning(f"Scraper returned no data for webcode: {webcode}")
                return None

            logger.info(f"Successfully scraped product data: {product_details}")
            return product_details
        except Exception as e:
            logger.error(
                f"Error during scraping for webcode: {webcode}. Error: {str(e)}",
                exc_info=True,
            )
            return None
