from flask import request
from typing import Dict, Any
import logging
from product_service import ProductService
from api_response import APIResponse

logger = logging.getLogger(__name__)


def register_routes(app, product_service: ProductService):
    @app.route('/health', methods=['GET'])
    def health_check() -> Dict[str, Any]:
        """Health check endpoint."""
        return APIResponse.build(200, {"status": "healthy"})

    @app.route('/scrape-url', methods=['POST'])
    def scrape_and_store_url() -> Dict[str, Any]:
        """Endpoint to scrape and store product data using URL."""
        try:
            url = request.json.get("url")
            if not url:
                return APIResponse.build(400, {"error": "URL is required"})

            product_details = product_service.scrape_product("url", url)
            message, status_code = product_service.handle_product(product_details)

            return APIResponse.build(status_code, {"message": message})

        except Exception as e:
            logger.error(f"URL scraping failed: {str(e)}")
            return APIResponse.build(500, {"error": str(e)})

    @app.route('/scrape-webcode', methods=['POST'])
    def scrape_and_store_webcode() -> Dict[str, Any]:
        """Endpoint to scrape and store product data using web code."""
        try:
            web_code = request.json.get("web_code")
            if not web_code:
                return APIResponse.build(400, {"error": "Web code is required"})

            product_details = product_service.scrape_product("webcode", web_code)
            message, status_code = product_service.handle_product(product_details)

            return APIResponse.build(status_code, {"message": message})

        except Exception as e:
            logger.error(f"Web code scraping failed: {str(e)}")
            return APIResponse.build(500, {"error": str(e)})
