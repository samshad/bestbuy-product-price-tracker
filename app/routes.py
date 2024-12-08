from flask import request
from typing import Dict, Any

from app.services.product_service import ProductService
from app.utils.api_response import APIResponse

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


def register_routes(app, product_service: ProductService):
    @app.route('/health', methods=['GET'])
    def health_check() -> Dict[str, Any]:
        """Health check endpoint."""
        logger.info("Health check endpoint called")
        return APIResponse.build(200, {"status": "healthy"})

    @app.route('/scrape', methods=['POST'])
    def scrape_and_store_product_details() -> Dict[str, Any]:
        """Endpoint to scrape and store product data using webcode or product url."""
        try:
            web_code = request.json.get("web_code")
            url = request.json.get("url")
            if not web_code and not url:
                logger.warning("Webcode or URL is missing in the request")
                return APIResponse.build(400, {"error": "Webcode or URL is required"})

            product_details = product_service.scrape_product(web_code, url)
            message, status_code = product_service.handle_product(product_details)

            logger.info(f"Product details scraped successfully: {product_details}")

            return APIResponse.build(status_code, {"message": message})

        except Exception as e:
            logger.error(f"Scraping failed: {str(e)}")
            return APIResponse.build(500, {"error": str(e)})
