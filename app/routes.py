from flask import request, Response, Flask

from app.utils.datetime_handler import get_current_datetime
from app.services.product_service import ProductService
from app.services.database_handler import DatabaseHandler
from app.services.job_service import JobService
from app.utils.api_response import APIResponse
from app.utils.my_logger import setup_logging
from app.utils.validate_input import validate_input_product_id_web_code
from app.tasks.celery_tasks import scrape_task

logger = setup_logging(__name__)


def register_routes(
    app: Flask,
    job_service: JobService,
    product_service: ProductService,
    database_handler: DatabaseHandler,
) -> None:
    """
    Register all routes for the Flask app.

    Args:
        app (Flask): Flask application instance.
        job_service (JobService): Service layer for handling job-related logic.
        product_service (ProductService): Service layer for handling product-related logic.
        database_handler (DatabaseHandler): Service for handling database operations.
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
    def scrape():
        """Endpoint to initiate a scraping job."""
        payload = request.json
        web_code = payload.get("web_code") if payload else None

        if not web_code:
            return APIResponse.build(400, {"error": "web_code is required"})

        status = "Pending"

        job_data = {
            "job_id": None,
            "web_code": str(web_code),
            "status": status,
            "result": None,
            "product_id": None,
        }

        logger.info(f"before celery task: {job_data}")

        task = scrape_task.delay(job_data)

        job_data["job_id"] = task.id

        status_code, message = job_service.store_job(
            job_data
        )  # database_handler.store_job(job_data)
        logger.info(
            f"Job stored in database -> Job_ID: {job_data['job_id']}, Status: {status_code}, Message: {message}"
        )

        return APIResponse.build(200, {"task_id": task.id})

    @app.route("/job", methods=["GET"])
    def get_job_details() -> Response:
        """
        Fetch job details by job_id.

        Query Params:
            job_id (str): Job ID.

        Returns:
            Response: JSON response containing job details or error message.
        """
        job_id = request.args.get("job_id")
        if not job_id:
            logger.error("Missing query parameter: 'job_id'.")
            return APIResponse.build(400, {"error": "'job_id' is required."})

        try:
            job = job_service.get_job(job_id)
            if not job:
                logger.info(f"No job found for job_id: {job_id}")
                return APIResponse.build(404, {"message": "No job found."})

            logger.info(f"Retrieved job details for job_id: {job_id}")
            return APIResponse.build(200, {"job": job})
        except Exception as e:
            logger.exception(f"Error fetching job details. Error: {str(e)}")
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
        except Exception:
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
        except Exception:
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
        except Exception:
            logger.exception("Error fetching product prices.")
            return APIResponse.build(500, {"error": "An unexpected error occurred."})
