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

    products = database_handler.fetch_all_products_with_pagination()

    print(len(products))

    for product in products:
        print(product)
