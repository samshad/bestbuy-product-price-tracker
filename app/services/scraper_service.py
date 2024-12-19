from typing import Dict, Any, Optional
from app.scrapers.scrapers import ScraperFactory
from app.utils.my_logger import setup_logging

logger = setup_logging(__name__)


class ScraperService:
    """Service for handling product scraping."""

    def __init__(self):
        """Initialize service with required dependencies."""
        pass

    def scrape_product(self, webcode: str) -> Optional[Dict[str, Any]]:
        """
        Scrape product details using the appropriate scraper.

        Args:
            webcode (str): Product web code.

        Returns:
            Optional[Dict[str, Any]]: Scraped product data or None if scraping fails.
        """
        try:
            scraper = ScraperFactory.create_scraper(webcode)
            product_details = scraper.scrape()

            if not product_details:
                logger.warning(f"Failed to scrape product data. Webcode: {webcode}")
                return None

            logger.info(f"Scraped product data: {product_details}")
            return product_details
        except Exception as e:
            logger.error(f"Error during scraping: {str(e)}")
            return None
