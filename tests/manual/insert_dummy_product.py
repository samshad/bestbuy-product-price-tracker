from typing import Dict, Any

import pandas as pd
from time import sleep
from random import choice

from app.db.jobs_crud import JobsCRUD
from app.db.products_crud import ProductsCRUD
from app.db.db_mongo import MongoDBClient
from app.services.database_handler import DatabaseHandler


def insert_dummy_product(
    database_handler: DatabaseHandler, product: Dict[str, Any]
) -> bool:
    """Insert a dummy product into the database."""

    product_id, (message, status_code) = database_handler.store_new_product(product)
    print(product_id, message, status_code)

    if product_id is None:
        return False
    return True


def initialize_database() -> DatabaseHandler:
    job_client = JobsCRUD()
    product_client = ProductsCRUD()
    mongo_client = MongoDBClient()
    return DatabaseHandler(
        job_client=job_client, product_client=product_client, mongo_client=mongo_client
    )


if __name__ == "__main__":
    database_handler = initialize_database()

    df = pd.read_csv("products_old.csv")

    products = []

    for index, row in df.iterrows():
        product = {
            "web_code": row["web_code"],
            "title": row["title"],
            "model": row["model"],
            "price": row["price"],
            "save": row["save"],
            "url": row["url"],
        }
        products.append(product)

    count = 1
    for product in products[1:]:
        sleep_time = choice([2, 3, 4, 5, 6])
        print(f"Inserting product {count} with sleep time {sleep_time}...")
        count += 1
        sleep(sleep_time)
        insert_dummy_product(database_handler, product)
