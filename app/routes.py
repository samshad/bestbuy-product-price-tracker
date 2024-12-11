from flask import request, Response, Flask
from datetime import datetime
from zoneinfo import ZoneInfo

from app.services.product_service import ProductService
from app.utils.api_response import APIResponse
from app.utils.my_logger import setup_logging
from app.utils.validate_input import validate_input

logger = setup_logging(__name__)


def register_routes(app: Flask, product_service: ProductService) -> None:
    @app.route('/health', methods=['GET'])
    def health_check() -> Response:
        """
        Health check endpoint.
        Returns the current server time and health status.
        """
        time_now = datetime.now(ZoneInfo("Canada/Atlantic")).isoformat()
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
            if not validate_input(web_code, url):
                logger.error("Either 'webcode' or 'url' must be provided, but not both.")
                return APIResponse.build(400, {"error": "Either 'webcode' or 'url' must be provided, but not both."})

            # Process product scraping
            logger.info(f"Starting product scrape: web_code={web_code}, url={url}")
            product_details = product_service.scrape_and_process_product(web_code, url)

            # Handle product details
            message, status_code = product_service.handle_product(product_details)

            response_body = {
                "message": message,
                "product_details": product_details
            }

            logger.info(f"Product scrape successful: {product_details}")
            return APIResponse.build(status_code, {"message": response_body})

        except KeyError as e:
            logger.error(f"KeyError: {str(e)}")
            return APIResponse.build(400, {"error": "Invalid JSON payload"})
        except ValueError as e:
            logger.error(f"ValueError: {str(e)}")
            return APIResponse.build(400, {"error": str(e)})
        except Exception as e:
            logger.exception(f"Unexpected error occurred: {str(e)}")  # Logs full stack trace
            return APIResponse.build(500, {"error": "An unexpected error occurred"})

    @app.route('/products', methods=['GET'])
    def get_all_products() -> Response:
        """
        Endpoint to fetch all product details available in the database.

        Returns:
            A JSON response containing all product details or an error message.
        """
        try:
            logger.info("Fetching all product details from the database.")
            all_products = product_service.get_all_products()

            if not all_products:
                logger.info("No product details found.")
                return APIResponse.build(404, {"message": "No products available."})

            logger.info(f"Retrieved {len(all_products)} products.")
            return APIResponse.build(200, {"products": all_products})

        except Exception as e:
            logger.exception(f"Error fetching product details: {str(e)}")
            return APIResponse.build(500, {"error": "An unexpected error occurred while fetching products."})
