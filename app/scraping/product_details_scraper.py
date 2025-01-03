import time
from typing import Optional
from app.utils.datetime_handler import get_current_datetime

from playwright.sync_api import (
    sync_playwright,
    Page,
    TimeoutError as PlaywrightTimeoutError,
)
from bs4 import BeautifulSoup, Tag

from app.utils.logging_utils import setup_logging

logger = setup_logging(__name__)


class ProductDetailsScraper:
    """A class to scrape product details from Best Buy Canada using Playwright."""

    DEFAULT_TIMEOUT = 40000  # 40 seconds

    def __init__(self, webcode: str) -> None:
        """
        Initialize the ProductDetailsScraper.

        Args:
            webcode (str): Product web code to search on Best Buy.
        """
        self.url = None
        if not webcode:
            raise ValueError("Product 'webcode' must be provided.")

        self.webcode = webcode
        self.search_url = (
            f"https://www.bestbuy.ca/en-ca/search?search={webcode}" if webcode else None
        )  # search url not allowed by robots.txt
        self.base_url_product = "https://www.bestbuy.ca/en-ca/product/"
        self.product_details = {}

    @staticmethod
    def _get_text(element: Optional[Tag], fallback: str = "") -> str:
        """Safely extract and strip text from a BeautifulSoup element."""
        return element.get_text(strip=True) if element else fallback

    def _extract_product_details(self, page: Page) -> None:
        """
        Extract product details from the loaded page and update self.product_details.

        Args:
            page (Page): The Playwright page object after navigation.
        """
        html = page.content()
        soup = BeautifulSoup(html, "html.parser")

        self.product_details = {
            "title": self._get_text(soup.find("h1", class_="font-best-buy")).strip(),
            "model": self._get_text(
                soup.find("div", {"data-automation": "MODEL_NUMBER_ID"})
            )
            .replace("Model:", "")
            .strip(),
            "web_code": self._get_text(soup.find("div", {"data-automation": "SKU_ID"}))
            .replace("Web Code:", "")
            .strip(),
            "price": self._get_text(
                soup.find(
                    "span",
                    {
                        "class": "style-module_screenReaderOnly__4QmbS style-module_large__g5jIz"
                    },
                )
            )
            .replace("$", "")
            .strip(),
            "url": page.url,
            "save": self._get_text(
                soup.find("span", {"class": "style-module_productSaving__g7g1G"})
            )
            .replace("SAVE $", "")
            .strip(),
            "date": get_current_datetime(),
        }

    def scrape(self, timeout: int = DEFAULT_TIMEOUT) -> Optional[dict]:
        """
        Scrape product details from Best Buy Canada.

        Args:
            timeout (int): Maximum time in milliseconds to wait for page elements.

        Returns:
            Optional[dict]: The product details if successfully scraped, else None.
        """
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)

                context = browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/91.0.4472.124 Safari/537.36"
                    ),
                    timezone_id="Canada/Atlantic",
                    locale="en-CA",
                )

                page = context.new_page()

                # Search for the product using the webcode. Not allowed by robots.txt
                # if self.webcode:
                #     logger.info(f"Searching for product with webcode: {self.webcode}")
                #     try:
                #         # Navigate to the search page
                #         start_time = time.time()
                #         page.goto(self.search_url)
                #         elapsed_time = time.time() - start_time
                #         logger.info(f"Search page loaded in {elapsed_time:.2f} seconds")
                #         page.wait_for_selector("button.onetrust-close-btn-handler")
                #         page.click("button.onetrust-close-btn-handler")
                #
                #         # Click on the first product in the search results
                #         page.wait_for_selector("div.productItemName_3IZ3c")
                #         page.click(
                #             "xpath=//*[@id='root']/div/div[2]/div[1]/div/main/div/div[1]/div[2]/div[1]/div[2]/ul/div/div/div/a/div/div")
                #     except PlaywrightTimeoutError:
                #         logger.warning(f"No products found for webcode: {self.webcode}. Returning None.")
                #         return None

                # Load the product page directly
                if self.webcode:
                    self.url = f"{self.base_url_product}{self.webcode}"

                logger.info(f"Scraping product details from webcode/url: {self.url}")
                try:
                    # Navigate to the product page directly
                    start_time = time.time()
                    page.goto(self.url)
                    elapsed_time = time.time() - start_time
                    logger.info(f"Product page loaded in {elapsed_time:.2f} seconds")
                except PlaywrightTimeoutError:
                    logger.warning(
                        f"Invalid URL or page could not be loaded: {self.url}. Returning None."
                    )
                    return None

                # Wait for the product page to load
                try:
                    page.wait_for_selector(
                        "div.style-module_price__ql4Q1", timeout=timeout
                    )
                except PlaywrightTimeoutError:
                    logger.warning(
                        f"Product page took too long to load for webcode {self.webcode or self.url}. Returning None."
                    )
                    return None

                # Extract product details
                self._extract_product_details(page)

                browser.close()

                # Ensure product details were successfully extracted
                if not self.product_details.get("title"):
                    logger.warning(
                        f"Product details could not be extracted for webcode {self.webcode or self.url}. Returning None."
                    )
                    return None

                logger.info(
                    f"Product details successfully scraped: {self.product_details}"
                )
                return self.product_details

        except PlaywrightTimeoutError as e:
            logger.error(f"Timeout while loading page: {str(e)}. Returning None.")
            return None

        except Exception as e:
            logger.error(f"Unexpected error occurred: {str(e)}. Returning None.")
            return None


if __name__ == "__main__":
    scraper = ProductDetailsScraper(webcode="16004258")

    product_details = scraper.scrape()
    if product_details is None:
        print("Failed to fetch product details. Please check the webcode or URL.")
    else:
        print("Product details fetched successfully:")
        print(product_details)
