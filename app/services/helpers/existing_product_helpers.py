from app.services.product_service import ProductService


def handle_existing_product(
    existing_product, new_product_details: dict, product_service: ProductService
) -> tuple[int, str]:
    """
    Handle an existing product by updating it with new details if necessary.

    Args:
        existing_product: The existing product object.
        new_product_details (dict): Newly scraped product details.
        product_service (ProductService): Service layer for product operations.

    Returns:
        tuple[int, str]: Status code and response message.
    """
    message, status_code = product_service.handle_existing_product(
        existing_product, new_product_details
    )
    return status_code, message
