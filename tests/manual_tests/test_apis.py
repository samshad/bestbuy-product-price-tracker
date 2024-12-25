import requests
import json
from time import sleep


def test_health():
    response = requests.get("http://localhost:5000/health")
    print(response.status_code)
    print(response.json())


def test_scrape(web_code, url):
    data = {"web_code": web_code, "url": url}
    headers = {"Content-Type": "application/json"}
    response = requests.post(
        "http://localhost:5000/scrape", headers=headers, data=json.dumps(data)
    )
    print(response.status_code)
    print(response.json())


def test_get_all_products():
    response = requests.get("http://localhost:5000/products")
    print(response.status_code)
    print(response.json())


def test_get_product_by_web_code(web_code):
    response = requests.get(f"http://localhost:5000/products?web_code={web_code}")
    print(response.status_code)
    print(response.json())


def test_get_product_by_id(product_id):
    response = requests.get(f"http://localhost:5000/product?product_id={product_id}")
    print(response.status_code)
    print(response.json())


def scrape_product():
    with open("products.json") as f:
        product_data = json.load(f)

    print(len(product_data))
    web_codes = [
        item["web_code"] for item in sorted(product_data, key=lambda x: x["web_code"])
    ]
    print(web_codes)

    cnt = 0
    for web_code in web_codes:
        cnt += 1
        print(f"Now scraping {cnt}/{len(web_codes)}: {web_code}")
        test_scrape(web_code, "")
        sleep(2)


def main():
    # test_health()
    test_scrape("17905836", "")
    # test_get_all_products()
    # test_get_product_by_web_code('16162187')
    # test_get_product_by_id(35)

    # scrape_product()

    pass


if __name__ == "__main__":
    main()
