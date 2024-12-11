from datetime import datetime
from typing import List, Dict, Any
import re


class DataCleaner:
    """A class to clean and standardize scraped product data before database insertion."""

    @staticmethod
    def clean_text(text: str, prefix: str = "") -> str:
        """
        Remove a specific prefix from text if it exists.

        Args:
            text (str): The text to clean.
            prefix (str): The prefix to remove from the text.

        Returns:
            str: The cleaned text without the prefix.
        """
        return text.replace(prefix, "").strip() if prefix in text else text.strip()

    @staticmethod
    def clean_and_convert_amount(amount_str: str) -> float:
        """
        Clean a string containing a monetary amount by removing commas and any
        other non-numeric characters, then convert it to a float.

        Args:
            amount_str (str): The string representing the amount (e.g., "1,000.33" or "$1,000.33").

        Returns:
            float: The cleaned amount as a floating-point number.
        """
        # Remove commas and any non-numeric characters except the decimal point
        cleaned_str = re.sub(r"[^\d.]", "", amount_str)

        # check if the string is empty
        if not cleaned_str:
            cleaned_str = "0"

        # Convert to float and return
        try:
            return float(cleaned_str)
        except ValueError:
            print(f"Error: Cannot convert {amount_str} to a float.")
            return 0.0

    @staticmethod
    def clean_product_data(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Clean and standardize a list of product data dictionaries.

        Args:
            data (List[Dict[str, Any]]): List of dictionaries containing raw product data.

        Returns:
            List[Dict[str, Any]]: List of cleaned and standardized product data dictionaries.
        """
        cleaned_data = []
        for item in data:
            cleaned_item = {
                "title": item.get("title", "").strip(),
                "model": DataCleaner.clean_text(item.get("model", ""), "Model:"),
                "web_code": DataCleaner.clean_text(
                    item.get("web_code", ""), "Web Code:"
                ),
                "price": DataCleaner.clean_and_convert_amount(
                    item.get("price", "").strip()
                ),
                "url": item.get("url", "").strip(),
                "save": DataCleaner.clean_and_convert_amount(
                    item.get("save", "").strip()
                ),
                "date": item.get("date"),
            }
            cleaned_data.append(cleaned_item)
        return cleaned_data

    @staticmethod
    def remove_objectid(data):
        if "_id" in data:
            del data["_id"]
        return data

    @staticmethod
    def format_date(date_str: str) -> str:
        """
        Convert the date string to a standardized ISO format (YYYY-MM-DD HH:MM:SS).

        Args:
            date_str (str): The original date string.

        Returns:
            str: Formatted date string or the original if parsing fails.
        """
        try:
            return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").isoformat(sep=" ")
        except (ValueError, TypeError):
            return date_str  # Return original date if parsing fails


# Example usage
if __name__ == "__main__":
    raw_data = [
        {
            "_id": "6734050a42467f925ca4beb9",
            "title": 'Apple iPad Air 10.9" 64GB with Wi-Fi (5th Generation) - Starlight',
            "brand": "Apple",
            "model": "Model:MM9F3VC/A",
            "web_code": "Web Code:16004374",
            "rating": "4.2",
            "review_count": "(5 Reviews)",
            "price": "$599.99",
            "date": "2024-11-12 21:46:50",
        },
        {
            "_id": "6734051e42467f925ca4bebb",
            "title": "Instant Pot Duo V5 7-in-1 Pressure Cooker - 6QT",
            "brand": "",
            "model": "Model:112-0170-02",
            "web_code": "Web Code:16374908",
            "rating": "4.8",
            "review_count": "(682 Reviews)",
            "price": "$109.99",
            "date": "2024-11-12 21:47:10",
        },
    ]

    temp_data = {
        "_id": "6734051e42467f925ca4bebb",
        "title": "Instant Pot Duo V5 7-in-1 Pressure Cooker - 6QT",
        "brand": "",
        "model": "Model:112-0170-02",
        "web_code": "Web Code:16374908",
        "rating": "4.8",
        "review_count": "(682 Reviews)",
        "price": "$109.99",
        "date": "2024-11-12 21:47:10",
    }

    # cleaner = DataCleaner()
    # cleaned_data = cleaner.clean_product_data([temp_data])
    # print("Cleaned Data:", cleaned_data)
