from flask import Response

from app.services.product_service import ProductService
from app.utils.api_response import APIResponse

def handle_existing_product(
    existing_product, new_product_details: dict, product_service: ProductService
) -> Response:
    """
    Handle an existing product by updating it with new details if necessary.

    Args:
        existing_product: The existing product object.
        new_product_details (dict): Newly scraped product details.
        product_service (ProductService): Service layer for product operations.

    Returns:
        Response: JSON response with a status message.
    """
    message, status_code = product_service.handle_existing_product(existing_product, new_product_details)
    return APIResponse.build(status_code, {"message": message})
