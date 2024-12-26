from app.db.db_mongo import MongoDBClient
from app.db.products_crud import ProductsCRUD
from app.services.database_handler import DatabaseHandler
from app.services.product_processor import ProductProcessor
from app.services.product_service import ProductService
from app.services.helpers.scraper_helpers import scrape_product_details
from app.services.scraper_service import ScraperService
from app.utils.data_cleaner import DataCleaner
from app.utils.retry_with_backoff import retry_with_backoff


def start_scraping(webcode: str) -> dict | None:
    """
    Start scraping the product details for the given webcode.

    Args:
        webcode (str): The webcode of the product to scrape.

    Returns:
        dict: Scraped product details.
    """

    # Initialize services and utilities
    product_client = ProductsCRUD()
    mongo_client = MongoDBClient()
    data_cleaner = DataCleaner()
    scraper_service = ScraperService()
    product_processor = ProductProcessor(data_cleaner)
    database_handler = DatabaseHandler(product_client, mongo_client)

    product_service = ProductService(
        scraper_service=scraper_service,
        product_processor=product_processor,
        database_handler=database_handler,
    )
    return retry_with_backoff(lambda: scrape_product_details(webcode, product_service))


if __name__ == "__main__":
    webcode = "147772583"
    result = start_scraping(webcode)

    print(type(result))
    print(result)
