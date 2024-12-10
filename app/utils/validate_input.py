from typing import Optional


def validate_input(web_code: Optional[str] = None, url: Optional[str] = None) -> bool:
    """
    Validate input to ensure either 'web_code' or 'url' is provided, but not both.

    Args:
        web_code (Optional[str]): The product web code to validate.
        url (Optional[str]): The product URL to validate.

    Returns:
        bool: True if input is valid (only one of 'web_code' or 'url' is provided), False otherwise.
    """
    return bool(web_code) != bool(url)
