from flask import request, Response, Flask
from app.utils.datetime_handler import get_current_datetime

from app.services.product_service import ProductService
from app.utils.api_response import APIResponse
from app.utils.my_logger import setup_logging
from app.utils.validate_input import (
    validate_input_web_code_url,
    validate_input_product_id_web_code,
)

logger = setup_logging(__name__)


def register_routes(app: Flask, product_service: ProductService) -> None:
    """
    Register all routes for the Flask app.
    """

    @app.route("/health", methods=["GET"])
    def health_check() -> Response:
        """
        Health check endpoint.

        Returns:
            A JSON response with a status code and current time
        """
        time_now = get_current_datetime()
        logger.info(f"Health check endpoint called. Current time: {time_now}")
        return APIResponse.build(200, {"status": "healthy", "time": time_now})

    @app.route("/scrape", methods=["POST"])
    def scrape_and_store_product_details() -> Response:
        """
        Endpoint to scrape and store product data using webcode or product URL.

        Payload:
            {
                "web_code": "string",
                "url": "string"
            }

        Returns:
            A JSON response with a message and product details or an error message
        """
        try:
            # Extract request data
            web_code = request.json.get("web_code")
            url = request.json.get("url")

            # Validate input
            if not validate_input_web_code_url(web_code=web_code, url=url):
                logger.error(
                    "Either 'webcode' or 'url' must be provided, but not both."
                )
                return APIResponse.build(
                    400,
                    {
                        "error": "Either 'webcode' or 'url' must be provided, but not both."
                    },
                )

            # Process product scraping
            logger.info(f"Starting product scrape: web_code={web_code}, url={url}")
            product_details = product_service.scrape_and_process_product(web_code, url)

            if product_details:
                # Handle product details
                message, status_code = product_service.handle_product(product_details)

                response_body = {"message": message, "product_details": product_details}

                logger.info(f"Product scrape successful: {product_details}")
                return APIResponse.build(status_code, {"message": response_body})
            else:
                logger.info(f"Product scrape failed: {product_details}")
                return APIResponse.build(
                    404, {"message": "Product scrape failed. No product details found."}
                )

        except KeyError as e:
            logger.error(f"KeyError: {str(e)}")
            return APIResponse.build(400, {"error": "Invalid JSON payload"})
        except ValueError as e:
            logger.error(f"ValueError: {str(e)}")
            return APIResponse.build(400, {"error": str(e)})
        except Exception as e:
            logger.exception(
                f"Unexpected error occurred: {str(e)}"
            )  # Logs full stack trace
            return APIResponse.build(500, {"error": "An unexpected error occurred"})

    @app.route("/products", methods=["GET"])
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
            return APIResponse.build(
                500, {"error": "An unexpected error occurred while fetching products."}
            )

    @app.route("/product", methods=["GET"])
    def get_product_details() -> Response:
        web_code = request.args.get("web_code")
        product_id = request.args.get("product_id")

        if not validate_input_product_id_web_code(
            product_id=product_id, web_code=web_code
        ):
            logger.error(
                "Either 'product_id' or 'web_code' must be provided, but not both."
            )
            return APIResponse.build(
                400,
                {
                    "error": "Either 'product_id' or 'web_code' must be provided, but not both."
                },
            )

        try:
            product = product_service.get_product(
                product_id=int(product_id) if product_id else None,
                web_code=web_code if web_code else None,
            )

            if not product:
                return APIResponse.build(404, {"message": "No product found."})

            return APIResponse.build(200, {"product": product})
        except ValueError as e:
            return APIResponse.build(400, {"error": str(e)})
        except Exception as e:
            logger.exception(f"Error fetching product details: {str(e)}")
            return APIResponse.build(
                500,
                {
                    "error": "An unexpected error occurred while fetching product details."
                },
            )

    @app.route("/product-prices", methods=["GET"])
    def get_product_prices() -> Response:
        """
        Endpoint to retrieve all price details for a product by its web_code.

        Query Params:
            web_code (str): The webcode of the product.

        Returns:
            A JSON response containing the price details or an error message.
        """
        web_code = request.args.get("web_code")

        if not web_code:
            logger.error("web_code is required for /product-prices.")
            return APIResponse.build(
                400, {"error": "Query parameter 'web_code' is required."}
            )

        try:
            prices = product_service.get_product_prices(web_code)

            if not prices:
                logger.info(f"No price details found for web_code: {web_code}")
                return APIResponse.build(
                    404, {"message": f"No price details found for web_code: {web_code}"}
                )

            logger.info(
                f"Retrieved {len(prices)} price records for web_code: {web_code}"
            )
            return APIResponse.build(200, {"prices": prices})
        except Exception as e:
            logger.exception(
                f"Error fetching product prices for web_code {web_code}: {str(e)}"
            )
            return APIResponse.build(
                500,
                {
                    "error": "An unexpected error occurred while fetching product prices."
                },
            )
