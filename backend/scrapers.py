from typing import Dict, Any, Union
from abc import ABC, abstractmethod
from selenium_scraper_url import URLScraper
from product_details_scraper import ProductDetailsScraper


class ScraperFactory:
    """Factory class for creating scrapers."""

    @staticmethod
    def create_scraper(webcode: str, url: str) -> Union[URLScraper, ProductDetailsScraper]:
        """Create appropriate scraper based on type."""
        return ProductDetailsScraper(webcode, url)
        #raise ValueError(f"Invalid scraper type: {scraper_type}")