from app.db.products_crud import ProductsCRUD


def test_insert_data(client, product):
    result = client.insert_product(
        product["web_code"],
        product["title"],
        product["model"],
        product["url"],
        product["price"],
        product["save"],
    )

    print(f"Success: product_id={result}" if result else "Failed")


def test_get_all_products(client):
    products = client.get_all_products()

    print("From get all:")
    for product in products:
        print(product)
    print("End of get all\n----------------")


def test_get_product_by_id(client, product_id):
    product = client.get_product(product_id, "")

    print(f"From get by id: {product}" if product else "Not found")
    print("-----------------")


def test_get_product_by_web_code(client, web_code):
    product = client.get_product("", web_code)

    print(f"From get by web code: {product}" if product else "Not found")
    print("-----------------")


def test_update_product(client, update_data):
    result = client.update_product(product_id, update_data)

    print("Product updated successfully." if result else "Failed")
    print("-----------------")


def test_delete_product(client, product_id):
    result = client.delete_product(product_id)

    print("Product deleted successfully." if result else "Failed")


if __name__ == "__main__":
    products_crud = ProductsCRUD()

    # sample data
    product = {
        "web_code": "123456",
        "title": "Product Title",
        "model": "Product Model",
        "url": "http://example.com",
        "price": 100,
        "save": 20,
    }

    # insert data
    # test_insert_data(products_crud, product)

    # read data
    # test_get_all_products(products_crud)

    product_id = 1
    # test_get_product_by_id(products_crud, product_id)
    test_get_product_by_web_code(products_crud, "123456")
    #
    # update data
    # update_data = {
    #     "title": "Updated Product Title",
    #     "model": "Updated Product Model",
    #     "price": 5999,
    # }
    # test_update_product(products_crud, update_data)
    #
    # test_get_all_products(products_crud)
    #
    # # delete data
    # test_delete_product(products_crud, product_id)
    #
    # test_get_all_products(products_crud)
