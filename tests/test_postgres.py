from app.db.db_postgres import PostgresDBClient
from datetime import datetime
from zoneinfo import ZoneInfo

postgres_client = PostgresDBClient()


def test_postgres():
    current_time = datetime.now(ZoneInfo("Canada/Atlantic")).isoformat()
    print(current_time)

    table_name = "products"
    # schema = "id SERIAL PRIMARY KEY, web_code VARCHAR(255), price INT, date TIMESTAMP"
    # postgres_client.create_table(table_name, schema)

    # Insert data
    # data = {'title': 'Bella Pro Touchscreen Air Fryer - 4.0L (4.2QT) - Stainless Steel - Only at Best Buy', 'model': '90189', 'web_code': '17109642', 'price': 6998, 'url': 'https://www.bestbuy.ca/en-ca/product/bella-pro-touchscreen-air-fryer-4-0l-4-2qt-stainless-steel-only-at-best-buy/17109642', 'save': 13000, 'date': '2024-12-10T21:03:06.074794-04:00'}
    # inserted_id = postgres_client.insert_data(table_name, data)
    # print(f"Inserted row ID: {inserted_id}")

    # Get data
    rows = postgres_client.get_data(table_name, {"web_code": "17109642"})
    print(len(rows))
    for row in rows:
        print(row)
    print(f"Retrieved rows: {rows}")

    d = rows[0].get("date")
    print(d.date())

    # Update data
    # update_count = postgres_client.update_data(table_name, {"price": 555}, {"web_code": "123456"})
    # print(f"Rows updated: {update_count}")

    # # Delete data
    # delete_count = postgres_client.delete_data(table_name, {"web_code": "12345"})
    # print(f"Rows deleted: {delete_count}")

    # Close connection
    # postgres_client.close()


if __name__ == "__main__":
    test_postgres()
