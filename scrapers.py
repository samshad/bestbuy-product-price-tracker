from typing import Dict, Any, Union
from abc import ABC, abstractmethod
from selenium_scraper_url import URLScraper
from playwright_scraper_webcode import WebcodeScraper


class ScraperFactory:
    """Factory class for creating scrapers."""

    @staticmethod
    def create_scraper(scraper_type: str, identifier: str) -> Union[URLScraper, WebcodeScraper]:
        """Create appropriate scraper based on type."""
        if scraper_type == "url":
            return URLScraper(identifier)
        elif scraper_type == "webcode":
            return WebcodeScraper(identifier)
        raise ValueError(f"Invalid scraper type: {scraper_type}")