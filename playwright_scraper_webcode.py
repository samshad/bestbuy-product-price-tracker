from playwright.sync_api import sync_playwright, Page
from bs4 import BeautifulSoup
from datetime import datetime
from data_cleaner import DataCleaner


class WebcodeScraper:
    """A class to scrape product details from Best Buy Canada using Playwright."""

    def __init__(self, webcode: str):
        """
        Initialize the ProductScraper with the webcode for the product search.

        Args:
            webcode (str): Product web code to search on Best Buy.
        """
        self.webcode = webcode
        self.base_url = f"https://www.bestbuy.ca/en-ca/search?search={webcode}"
        self.product_details = {}

    @staticmethod
    def _get_text(element) -> str:
        """Safely extract and strip text from a BeautifulSoup element."""
        return element.get_text(strip=True) if element else ""

    def _extract_product_details(self, page: Page) -> None:
        """
        Extract product details from the loaded page and update self.product_details.

        Args:
            page (Page): The Playwright page object after navigation.
        """
        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')

        self.product_details = {
            "title": self._get_text(soup.find("h1", class_="font-best-buy")),
            "model": self._get_text(soup.find("div", {"data-automation": "MODEL_NUMBER_ID"})).replace("Model:", ""),
            "web_code": self._get_text(soup.find("div", {"data-automation": "SKU_ID"})).replace("Web Code:", ""),
            "price": self._get_text(
                soup.find("span", {"class": "style-module_screenReaderOnly__4QmbS style-module_large__g5jIz"})).replace("$", ""),
            "url": page.url,
            "save": self._get_text(soup.find("span", {"class": "style-module_productSaving__g7g1G"})).replace("SAVE $",""),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def scrape(self) -> dict:
        """
        Scrape product details from Best Buy Canada.

        Returns:
            dict: A dictionary of the scraped product details.
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            # Navigate to the product search page
            page.goto(self.base_url)
            page.wait_for_selector("button.onetrust-close-btn-handler")
            page.click("button.onetrust-close-btn-handler")

            # Click on the first product in the search results
            page.wait_for_selector("div.productItemName_3IZ3c")
            page.click("xpath=//*[@id='root']/div/div[2]/div[1]/div/main/div/div[1]/div[2]/div[1]/div[2]/ul/div/div/div/a/div/div")

            # Wait for the product page to load
            page.wait_for_selector("div.style-module_price__ql4Q1")

            # Extract product details
            self._extract_product_details(page)

            # Clean the data using DataCleaner
            cleaner = DataCleaner()
            self.product_details = cleaner.clean_product_data([self.product_details])[0]

            browser.close()

        return self.product_details


if __name__ == "__main__":
    scraper = WebcodeScraper("17924062")
    product_details = scraper.scrape()
    print(product_details)

    #print(scrape("17924062"))
    #print(scrape("17924066"))