import json
import time
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup, Tag

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductScraper:
    """A class to scrape product details from a Best Buy product page using Selenium and BeautifulSoup."""

    def __init__(self, url: str, headless: bool = True) -> None:
        """
        Initialize the ProductScraper with the given URL and headless option.

        Args:
            url (str): The URL of the product page.
            headless (bool): Run in headless mode if True. Default is True.
        """
        self.url = url
        self.driver = self._setup_driver(headless)

    def _setup_driver(self, headless: bool) -> webdriver.Chrome:
        """
        Set up the Selenium WebDriver with specified options.

        Args:
            headless (bool): Run driver in headless mode if True.

        Returns:
            webdriver.Chrome: Configured WebDriver instance.
        """
        options = Options()
        options.headless = headless
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver

    def fetch_page(self) -> None:
        """Fetch the webpage using Selenium."""
        try:
            self.driver.get(self.url)
            logger.info("Page fetched successfully")
            time.sleep(5)  # Wait for page to fully load; adjust if necessary

            # Click close button for privacy pop-up if it exists
            try:
                close_button = self.driver.find_element(By.CLASS_NAME, "onetrust-close-btn-handler")
                close_button.click()
                logger.info("Closed privacy pop-up")
            except Exception:
                pass

        except Exception as e:
            logger.error("Failed to fetch the page: %s", e)
            self.close_driver()
            raise

    def parse_page(self) -> Optional[Dict[str, Any]]:
        """
        Parse the product details from the fetched page source.

        Returns:
            Optional[Dict[str, Any]]: Dictionary of product details or None if parsing fails.
        """
        try:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            product_details = {
                "title": self._get_text(soup.find("h1", class_="font-best-buy")),
                "model": self._get_text(soup.find("div", {"data-automation": "MODEL_NUMBER_ID"})).replace("Model:", ""),
                "web_code": self._get_text(soup.find("div", {"data-automation": "SKU_ID"})).replace("Web Code:", ""),
                "price": self._get_text(soup.find("span", {"class": "style-module_screenReaderOnly__4QmbS style-module_large__g5jIz"})).replace("$", ""),
                "url": self.url,
                "save": self._get_text(soup.find("span", {"class": "style-module_productSaving__g7g1G"})).replace("SAVE $", ""),
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            logger.info("Product details extracted successfully")
            return product_details
        except Exception as e:
            logger.error("Failed to parse product details: %s", e)
            return None

    @staticmethod
    def _get_text(element: Optional[Tag]) -> str:
        """
        Safely extract and strip text from a BeautifulSoup element.

        Args:
            element (Optional[Tag]): BeautifulSoup element or None.

        Returns:
            str: Extracted text or an empty string if element is None.
        """
        return element.get_text(strip=True) if element else ""

    def close_driver(self) -> None:
        """Close the Selenium WebDriver."""
        if self.driver:
            self.driver.quit()
            logger.info("Web driver closed")

    def scrape(self) -> Optional[Dict[str, Any]]:
        """
        Perform the scraping process: fetch the page, parse details, and return them.

        Returns:
            Optional[Dict[str, Any]]: Dictionary of product details or None if scraping fails.
        """
        try:
            self.fetch_page()
            product_details = self.parse_page()
            return product_details
        finally:
            self.close_driver()


if __name__ == "__main__":
    # URL of the product page
    url = 'https://www.bestbuy.ca/en-ca/product/apple-ipad-air-10-9-64gb-with-wi-fi-5th-generation-starlight/16004374'
    scraper = ProductScraper(url)
    pd = scraper.scrape()
    if pd:
        print("Scraped Product Details:", json.dumps(pd, indent=4))
    else:
        print("Failed to scrape product details.")
