from app.services.product_service import ProductService
from app.utils.logging_utils import setup_logging

logger = setup_logging(__name__)


def scrape_product_details(
    web_code: str, product_service: ProductService
) -> dict | None:
    """
    Scrape product details for the given web_code.

    Args:
        web_code (str): The web code of the product to scrape.
        product_service (ProductService): Service layer for product operations.

    Returns:
        Optional[dict]: Scraped product details if successful, else None.
    """
    try:
        logger.info(f"Starting scraping product with web_code: {web_code}")
        return product_service.scrape_and_process_product(web_code)
    except Exception as e:
        logger.error(f"Scraping failed for web_code {web_code}: {str(e)}")
        return None
