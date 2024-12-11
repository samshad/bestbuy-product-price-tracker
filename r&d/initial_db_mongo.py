import os
from typing import Optional, Dict, Any, List
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class MongoDBClient:
    """A MongoDB client to handle CRUD operations for product data."""

    def __init__(self) -> None:
        """
        Initialize the MongoDBClient with credentials from the .env file.
        """
        try:
            MONGO_URI = os.getenv("MONGO_URI")
            self.client = MongoClient(
                MONGO_URI, tls=True, tlsAllowInvalidCertificates=True
            )

            self.db = self.client[os.getenv("MONGO_DB_NAME")]
            self.collection = self.db[os.getenv("MONGO_COLLECTION_NAME")]

            print("Connected to MongoDB successfully.")

        except ConnectionFailure as e:
            print("Could not connect to MongoDB:", e)
            raise

    def insert_data(self, data: Dict[str, Any]) -> Optional[str]:
        """
        Insert a document into the MongoDB collection.

        Args:
            data (Dict[str, Any]): Product data to insert.

        Returns:
            Optional[str]: The ID of the inserted document or None if insertion failed.
        """
        try:
            # Remove `_id` if it is None to allow MongoDB to generate it
            if data.get("_id") is None:
                data.pop("_id", None)

            print("Attempting to insert data:", data)  # Log data to be inserted
            result = self.collection.insert_one(data)

            if result.inserted_id:
                print("Data inserted with ID:", result.inserted_id)
                return str(result.inserted_id)
            else:
                print("Insert operation returned no ID. Check data and permissions.")
                return None
        except PyMongoError as e:
            print("An error occurred while inserting data:", e)
            return None

    def get_data(self, query: Dict[str, Any] = {}) -> List[Dict[str, Any]]:
        """
        Retrieve documents from the MongoDB collection.

        Args:
            query (Dict[str, Any]): The MongoDB query filter. Default is an empty dictionary for all documents.

        Returns:
            List[Dict[str, Any]]: List of matching documents.
        """
        try:
            data = list(self.collection.find(query))
            print(f"Retrieved {len(data)} documents.")
            return data
        except PyMongoError as e:
            print("An error occurred while retrieving data:", e)
            return []

    def update_data(self, query: Dict[str, Any], update: Dict[str, Any]) -> int:
        """
        Update documents in the MongoDB collection.

        Args:
            query (Dict[str, Any]): The query filter to select documents to update.
            update (Dict[str, Any]): The update to apply.

        Returns:
            int: The number of documents modified.
        """
        try:
            result = self.collection.update_many(query, {"$set": update})
            print(f"Modified {result.modified_count} documents.")
            return result.modified_count
        except PyMongoError as e:
            print("An error occurred while updating data:", e)
            return 0

    def delete_data(self, query: Dict[str, Any]) -> int:
        """
        Delete documents from the MongoDB collection.

        Args:
            query (Dict[str, Any]): The query filter to select documents to delete.

        Returns:
            int: The number of documents deleted.
        """
        try:
            result = self.collection.delete_many(query)
            print(f"Deleted {result.deleted_count} documents.")
            return result.deleted_count
        except PyMongoError as e:
            print("An error occurred while deleting data:", e)
            return 0
