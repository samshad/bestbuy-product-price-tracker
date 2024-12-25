from app.db.db_mongo import MongoDBClient

mongo_client = MongoDBClient()


def test_mongo():
    # Insert data
    # data = {"web_code": "123456", "price": 1999.99, "save": 20.00, "date": "2024-12-10"}
    # inserted_id = mongo_client.insert_data(data)
    # print(f"Inserted document ID: {inserted_id}")

    # Get data
    query = {"web_code": "16162187"}
    documents = mongo_client.get_data(query)
    print(f"Retrieved documents: {documents}")
    print(len(documents))

    print(documents)

    # for document in documents:
    #     print(f"Document ID: {document.get('_id')}")
    #     print(f"Price: {document.get('price')}")
    #     print(f"Save: {document.get('save')}")
    #     print(f"Date: {document.get('date')}")
    #
    # d = documents[0].get('date')
    # # parse isoformat string to datetime object
    # d = datetime.fromisoformat(d)
    # print("Date: ", d.date())

    # Update data
    # update = {"price": 189.99}
    # modified_count = mongo_client.update_data(query, update)
    # print(f"Modified documents count: {modified_count}")

    # Delete data
    # deleted_count = mongo_client.delete_data(query)
    # print(f"Deleted documents count: {deleted_count}")


if __name__ == "__main__":
    test_mongo()
