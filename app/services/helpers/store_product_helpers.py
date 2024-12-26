from typing import Tuple, Dict
from app.services.product_service import ProductService
from app.utils.logging_utils import setup_logging

logger = setup_logging(__name__)

# Define constants for status codes
STATUS_ERROR = 500


def store_new_product(
    product_details: dict, product_service: ProductService
) -> Tuple[int, Dict]:
    """
    Store a new product in the database.

    Args:
        product_details (dict): The product details to store.
        product_service (ProductService): Service layer for product operations.

    Returns:
        Tuple[int, Dict]: A tuple containing the status code and a dictionary with a message or product details.

    Raises:
        Exception: If an error occurs during the storage process.
    """
    try:
        # Attempt to store the product
        product_id, (message, status_code) = product_service.store_product(
            product_details
        )
        product_details["product_id"] = product_id

        logger.info(
            f"Product successfully stored. Product ID: {product_id}, Status Code: {status_code}"
        )
        return status_code, product_details
    except Exception as e:
        # Log the exception with full context
        logger.exception(
            f"Error storing new product. Details: {product_details}. Error: {str(e)}",
            exc_info=True,
        )
        return STATUS_ERROR, {"Error": "Failed to store product."}
