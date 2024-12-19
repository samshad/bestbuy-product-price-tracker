from flask import request, Response, Flask

from app.services.helpers.existing_product_helpers import handle_existing_product
from app.services.helpers.scraping_helpers import scrape_product_details
from app.services.helpers.store_new_product_details_helpers import store_new_product
from app.utils.datetime_handler import get_current_datetime
from app.services.product_service import ProductService
from app.utils.api_response import APIResponse
from app.utils.my_logger import setup_logging
from app.utils.validate_input import validate_input_product_id_web_code

logger = setup_logging(__name__)


def register_routes(app: Flask, product_service: ProductService) -> None:
    """
    Register all routes for the Flask app.

    Args:
        app (Flask): Flask application instance.
        product_service (ProductService): Service layer for handling product-related logic.
    """

    @app.route("/health", methods=["GET"])
    def health_check() -> Response:
        """
        Health check endpoint.

        Returns:
            Response: JSON response with a status message and current server time.
        """
        time_now = get_current_datetime()
        logger.info(f"Health check endpoint called. Current time: {time_now}")
        return APIResponse.build(200, {"status": "healthy", "time": time_now})

    @app.route("/scrape", methods=["POST"])
    def scrape_and_store_product_details() -> Response:
        """
        Scrape and store product data based on web_code.

        Payload:
            {
                "web_code": "string"
            }

        Returns:
            Response: JSON response containing product details or error message.
        """
        try:
            payload = request.json
            web_code = payload.get("web_code") if payload else None

            if not web_code:
                logger.error("Missing 'web_code' in request payload.")
                return APIResponse.build(400, {"error": "'web_code' is required."})

            existing_product = product_service.get_product(None, web_code)

            # Scrape product details
            product_details = scrape_product_details(web_code, product_service)
            if not product_details:
                return APIResponse.build(
                    404, {"message": "Scraping failed. No product details found."}
                )

            # Handle existing product
            if existing_product:
                return handle_existing_product(
                    existing_product, product_details, product_service
                )

            # Store new product
            return store_new_product(product_details, product_service)

        except (KeyError, ValueError) as e:
            logger.error(f"Input error: {str(e)}")
            return APIResponse.build(400, {"error": str(e)})
        except Exception as e:
            logger.exception("Unexpected error occurred.")
            return APIResponse.build(500, {"error": "An unexpected error occurred."})

    @app.route("/products", methods=["GET"])
    def get_all_products() -> Response:
        """
        Fetch all products from the database.

        Returns:
            Response: JSON response containing a list of products or an error message.
        """
        try:
            logger.info("Fetching all product details.")
            products = product_service.get_all_products()
            if not products:
                logger.info("No products found.")
                return APIResponse.build(404, {"message": "No products available."})

            logger.info(f"Retrieved {len(products)} products.")
            return APIResponse.build(200, {"products": [p.to_dict() for p in products]})
        except Exception as e:
            logger.exception("Error fetching product details.")
            return APIResponse.build(
                500, {"error": "An unexpected error occurred while fetching products."}
            )

    @app.route("/product", methods=["GET"])
    def get_product_details() -> Response:
        """
        Fetch product details by product_id or web_code.

        Query Params:
            product_id (int, optional): Product ID.
            web_code (str, optional): Web code of the product.

        Returns:
            Response: JSON response containing product details or error message.
        """
        product_id = request.args.get("product_id", type=int)
        web_code = request.args.get("web_code")

        if not validate_input_product_id_web_code(
            product_id=product_id, web_code=web_code
        ):
            logger.error(
                "Invalid input: Either 'product_id' or 'web_code' must be provided."
            )
            return APIResponse.build(
                400,
                {
                    "error": "Invalid input: Either 'product_id' or 'web_code' must be provided."
                },
            )

        try:
            product = product_service.get_product(product_id, web_code)
            if not product:
                logger.info("No product found.")
                return APIResponse.build(404, {"message": "No product found."})

            logger.info(
                f"Retrieved product details for product_id: {product_id} or web_code: {web_code}"
            )
            return APIResponse.build(200, {"product": product.to_dict()})
        except Exception as e:
            logger.exception("Error fetching product details.")
            return APIResponse.build(500, {"error": "An unexpected error occurred."})

    @app.route("/product-prices", methods=["GET"])
    def get_product_prices() -> Response:
        """
        Fetch price details for a product by its web_code.

        Query Params:
            web_code (str): Web code of the product.

        Returns:
            Response: JSON response containing price details or error message.
        """
        web_code = request.args.get("web_code")
        if not web_code:
            logger.error("Missing query parameter: 'web_code'.")
            return APIResponse.build(400, {"error": "'web_code' is required."})

        try:
            prices = product_service.get_product_prices(web_code)
            if not prices:
                logger.info(f"No prices found for web_code: {web_code}")
                return APIResponse.build(404, {"message": "No prices found."})

            logger.info(f"Retrieved price details for web_code: {web_code}")
            return APIResponse.build(200, {"prices": prices})
        except Exception as e:
            logger.exception("Error fetching product prices.")
            return APIResponse.build(500, {"error": "An unexpected error occurred."})
