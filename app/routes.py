from flask import request, Response, Flask
from datetime import datetime

from app.services.product_service import ProductService
from app.utils.api_response import APIResponse
from app.utils.my_logger import setup_logging

logger = setup_logging(__name__)


def register_routes(app: Flask, product_service: ProductService) -> None:
    @app.route('/health', methods=['GET'])
    def health_check() -> Response:
        """
        Health check endpoint.
        Returns the current server time and health status.
        """
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"Health check endpoint called. Current time: {time_now}")
        return APIResponse.build(200, {"status": "healthy", "time": time_now})

    @app.route('/scrape', methods=['POST'])
    def scrape_and_store_product_details() -> Response:
        """
        Endpoint to scrape and store product data using webcode or product URL.
        Expects JSON payload with either 'web_code' or 'url'.
        Returns a JSON response with a message and status code.
        """
        try:
            # Extract request data
            web_code = request.json.get("web_code")
            url = request.json.get("url")

            # Validate input
            if not web_code and not url:
                logger.warning("Missing 'web_code' or 'url' in request payload")
                return APIResponse.build(400, {"error": "Either 'web_code' or 'url' is required"})

            # Process product scraping
            logger.info(f"Starting product scrape: web_code={web_code}, url={url}")
            product_details = product_service.scrape_product(web_code, url)
            message, status_code = product_service.handle_product(product_details)

            logger.info(f"Product scrape successful: {product_details}")
            return APIResponse.build(status_code, {"message": message})

        except KeyError as e:
            logger.error(f"KeyError: {str(e)}")
            return APIResponse.build(400, {"error": "Invalid JSON payload"})
        except ValueError as e:
            logger.error(f"ValueError: {str(e)}")
            return APIResponse.build(400, {"error": str(e)})
        except Exception as e:
            logger.exception(f"Unexpected error occurred: {str(e)}")  # Logs full stack trace
            return APIResponse.build(500, {"error": "An unexpected error occurred"})
