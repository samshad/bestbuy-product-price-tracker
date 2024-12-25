from app.services.product_service import ProductService
from app.utils.my_logger import setup_logging

logger = setup_logging(__name__)


def store_new_product(
    product_details: dict, product_service: ProductService
) -> tuple[int, dict]:
    """
    Store a new product in the database.

    Args:
        product_details (dict): The product details to store.
        product_service (ProductService): Service layer for product operations.

    Returns:
        tuple[int, dict]: Status code and response message.
    """
    try:
        product_id, (message, status_code) = product_service.store_product(
            product_details
        )
        product_details["product_id"] = product_id
        logger.info(f"Product successfully stored. Product ID: {product_id}")
        return status_code, product_details
    except Exception as e:
        logger.exception(f"Error storing new product. Details: {str(e)}")
        return 500, {"Error": "Failed to store product."}
