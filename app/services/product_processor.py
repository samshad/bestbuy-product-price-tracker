from typing import Dict, Any
from app.utils.data_cleaner import DataCleaner
from app.utils.logging_utils import setup_logging

logger = setup_logging(__name__)


class ProductProcessor:
    """Service for processing and cleaning product data."""

    def __init__(self, data_cleaner: DataCleaner):
        """
        Initialize the ProductProcessor with the given data cleaner.

        Args:
            data_cleaner (DataCleaner): Utility for cleaning product data.
        """
        if not isinstance(data_cleaner, DataCleaner):
            logger.error("Invalid data cleaner provided.", exc_info=True)
            raise TypeError("Expected an instance of DataCleaner.")
        self.data_cleaner = data_cleaner

    def process_product_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and clean the raw product data.

        Args:
            raw_data (Dict[str, Any]): Raw scraped product data.

        Returns:
            Dict[str, Any]: Processed and cleaned product data.

        Raises:
            ValueError: If required keys are missing from the cleaned data.
        """
        cleaned_data = self.data_cleaner.clean_product_data([raw_data])[0]

        try:
            cleaned_data["price"] = self._convert_to_cents(cleaned_data.get("price", 0))
            cleaned_data["save"] = self._convert_to_cents(cleaned_data.get("save", 0))
        except (TypeError, ValueError) as e:
            logger.error(f"Error processing product data: {e}", exc_info=True)
            raise ValueError(f"Error processing product data: {e}")

        return cleaned_data

    @staticmethod
    def _convert_to_cents(amount: Any) -> int:
        """
        Convert the given amount to cents.

        Args:
            amount (Any): The amount to convert. Must be a number or a string that can be converted to a float.

        Returns:
            int: The amount in cents.

        Raises:
            ValueError: If the input is invalid or cannot be converted to a float.
        """
        if amount is None:
            return 0
        try:
            return int(float(amount) * 100)
        except (TypeError, ValueError):
            logger.error(f"Invalid amount for conversion to cents: {amount}")
            raise ValueError(f"Invalid amount for conversion to cents: {amount}")
