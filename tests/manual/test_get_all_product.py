from app.db.jobs_crud import JobsCRUD
from app.db.products_crud import ProductsCRUD
from app.db.db_mongo import MongoDBClient
from app.services.database_handler import DatabaseHandler


def initialize_database() -> DatabaseHandler:
    job_client = JobsCRUD()
    product_client = ProductsCRUD()
    mongo_client = MongoDBClient()
    return DatabaseHandler(
        job_client=job_client, product_client=product_client, mongo_client=mongo_client
    )


if __name__ == "__main__":
    database_handler = initialize_database()

    products = database_handler.get_all_products()

    print(type(products))
    print(products)
    print(products[0].to_dict())
    print([p.to_dict() for p in products])

    product_id = 15
    web_code = "17909546"

    specific_product = database_handler.get_product(None, web_code)
    print(specific_product.to_dict())
    web_code = None
    specific_product = database_handler.get_product(product_id, web_code)
    print(specific_product.to_dict())
