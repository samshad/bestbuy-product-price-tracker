from datetime import datetime
from typing import Dict, Any, Tuple
import logging

from app.utils.data_cleaner import DataCleaner
from app.db.db_mongo import MongoDBClient
from app.db.db_postgres import PostgresDBClient
from app.scrapers.scrapers import ScraperFactory
from app.utils.config import Config

logger = logging.getLogger(__name__)


class ProductService:
    """Service layer for product operations."""

    def __init__(
            self,
            postgres_client: PostgresDBClient,
            mongo_client: MongoDBClient,
            data_cleaner: DataCleaner
    ):
        """Initialize service with required dependencies."""
        self.postgres_client = postgres_client
        self.mongo_client = mongo_client
        self.data_cleaner = data_cleaner

    def scrape_product(self, webcode: str, url: str) -> Dict[str, Any]:
        """
        Scrape product data using the appropriate scraper.

        Args:
            webcode (str): Web code for the product to scrape
            url (str): URL for the product to scrape

        Returns:
            Dict[str, Any]: Cleaned product data

        Raises:
            ValueError: If scraping fails
        """
        try:
            scraper = ScraperFactory.create_scraper(webcode, url)
            raw_data = scraper.scrape()

            if not raw_data:
                raise ValueError("Failed to scrape product data")

            product_details = self._process_product_data(raw_data)
            return product_details

        except Exception as e:
            logger.error(f"Scraping failed: {str(e)}")
            raise

    def _process_product_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw product data into required format."""
        product_details = self.data_cleaner.clean_product_data([raw_data])[0]
        product_details["price"] = self._convert_to_cents(product_details["price"])
        product_details["save"] = self._convert_to_cents(product_details["save"])
        return product_details

    @staticmethod
    def _convert_to_cents(amount: float) -> int:
        """Convert dollar amount to cents."""
        return int(float(amount) * 100)

    def handle_product(self, product_details: Dict[str, Any]) -> Tuple[str, int]:
        """
        Handle product storage logic.

        Args:
            product_details (Dict[str, Any]): Product details to store

        Returns:
            Tuple[str, int]: Message and status code
        """
        existing_product = self.postgres_client.get_data(
            Config.TABLE_NAME,
            {"web_code": product_details["web_code"]}
        )

        if existing_product:
            return self._handle_existing_product(product_details, existing_product[0])
        return self._handle_new_product(product_details)

    def _handle_existing_product(
            self,
            product_details: Dict[str, Any],
            existing_product: Dict[str, Any]
    ) -> Tuple[str, int]:
        """Handle logic for existing products."""
        current_date = datetime.now().date()
        stored_date = existing_product["date"].date()

        if current_date == stored_date:
            return "Product already exists for today. No action taken.", 200

        self._update_product_data(product_details)
        return "Product price updated and new data added to MongoDB.", 200

    def _handle_new_product(self, product_details: Dict[str, Any]) -> Tuple[str, int]:
        """Handle logic for new products."""
        self._store_product_data(product_details)
        return "Product data added to PostgreSQL and MongoDB.", 201

    def _update_product_data(self, product_details: Dict[str, Any]) -> None:
        """Update existing product data in databases."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.postgres_client.update_data(
            Config.TABLE_NAME,
            {
                "price": product_details["price"],
                "date": current_time
            },
            {"web_code": product_details["web_code"]}
        )

        self._store_mongo_data(product_details)

    def _store_product_data(self, product_details: Dict[str, Any]) -> None:
        """Store new product data in databases."""
        self.postgres_client.insert_data(Config.TABLE_NAME, product_details)
        self._store_mongo_data(product_details)

    def _store_mongo_data(self, product_details: Dict[str, Any]) -> None:
        """Store product data in MongoDB."""
        self.mongo_client.insert_data({
            "web_code": product_details["web_code"],
            "price": product_details["price"],
            "save": product_details["save"],
            "date": product_details["date"]
        })