from typing import Tuple, Any
from app.services.product_service import ProductService
from app.utils.logging_utils import setup_logging

logger = setup_logging(__name__)


def handle_existing_product(
    existing_product: Any, new_product_details: dict, product_service: ProductService
) -> Tuple[int, str]:
    """
    Handle an existing product by updating it with new details if necessary.

    Args:
        existing_product (Any): The existing product object, expected to be of a type compatible with `ProductService`.
        new_product_details (dict): Newly scraped product details.
        product_service (ProductService): Service layer for product operations.

    Returns:
        Tuple[int, str]: Status code and response message.

    Raises:
        Exception: If the update operation in `ProductService` fails.
    """
    try:
        message, status_code = product_service.handle_existing_product(
            existing_product, new_product_details
        )
        return status_code, message
    except Exception as e:
        # Log the exception and re-raise for handling upstream
        # Assuming logger is available in this module
        logger.error(
            f"Failed to update existing product. Details: {new_product_details}. Error: {str(e)}",
            exc_info=True,
        )
        raise
