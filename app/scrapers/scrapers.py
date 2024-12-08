from app.scrapers.product_details_scraper import ProductDetailsScraper


class ScraperFactory:
    """Factory class for creating scrapers."""

    @staticmethod
    def create_scraper(webcode: str, url: str) -> ProductDetailsScraper:
        """Create appropriate scraper based on type."""
        return ProductDetailsScraper(webcode, url)
