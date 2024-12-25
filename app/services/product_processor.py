from typing import Dict, Any
from app.utils.data_cleaner import DataCleaner


class ProductProcessor:
    """Service for processing and cleaning product data."""

    def __init__(self, data_cleaner: DataCleaner):
        """
        Initialize the ProductProcessor with the given data cleaner.
        """
        self.data_cleaner = data_cleaner

    def process_product_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and clean the raw product data.

        Args:
            raw_data (Dict[str, Any]): Raw scraped product data.

        Returns:
            Dict[str, Any]: Processed and cleaned product data.
        """
        cleaned_data = self.data_cleaner.clean_product_data([raw_data])[0]
        cleaned_data["price"] = self._convert_to_cents(cleaned_data["price"])
        cleaned_data["save"] = self._convert_to_cents(cleaned_data["save"])
        return cleaned_data

    @staticmethod
    def _convert_to_cents(amount: float) -> int:
        """
        Convert the given amount to cents.

        Args:
            amount (float): The amount to convert.

        Returns:
            int: The amount in cents.
        """
        return int(float(amount) * 100)
