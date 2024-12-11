from typing import Optional


def validate_input_web_code_url(
    web_code: Optional[str] = None, url: Optional[str] = None
) -> bool:
    """
    Validate input to ensure either 'web_code' or 'url' is provided, but not both.

    Args:
        web_code (Optional[str]): The product web code to validate.
        url (Optional[str]): The product URL to validate.

    Returns:
        bool: True if input is valid (only one of 'web_code' or 'url' is provided), False otherwise.
    """
    return bool(web_code) != bool(url)


def validate_input_product_id_web_code(
    product_id: Optional[int] = None, web_code: Optional[str] = None
) -> bool:
    """
    Validate input to ensure either 'product_id' or 'web_code' is provided, but not both.

    Args:
        product_id (Optional[int]): The product ID to validate.
        web_code (Optional[str]): The product web code to validate.

    Returns:
        bool: True if input is valid (only one of 'product_id' or 'web_code' is provided), False otherwise.
    """
    return bool(product_id) != bool(web_code)
