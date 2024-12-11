import os
from typing import Optional, Dict, Any, List
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
from dotenv import load_dotenv
from app.utils.my_logger import setup_logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
logger = setup_logging(__name__)


class MongoDBClient:
    """A MongoDB client to handle CRUD operations for product data."""

    def __init__(self) -> None:
        """
        Initialize the MongoDBClient with credentials from the .env file.
        """
        try:
            mongo_uri = os.getenv("MONGO_URI")
            if not mongo_uri:
                raise ValueError("Missing MONGO_URI in environment variables.")

            db_name = os.getenv("MONGO_DB_NAME")
            if not db_name:
                raise ValueError("Missing MONGO_DB_NAME in environment variables.")

            collection_name = os.getenv("MONGO_COLLECTION_NAME")
            if not collection_name:
                raise ValueError(
                    "Missing MONGO_COLLECTION_NAME in environment variables."
                )

            # Connect to MongoDB
            self.client = MongoClient(
                mongo_uri, tls=True, tlsAllowInvalidCertificates=True
            )
            self.db = self.client[db_name]
            self.collection = self.db[collection_name]

            logger.info("Connected to MongoDB successfully.")

        except ConnectionFailure as e:
            logger.error(f"Could not connect to MongoDB: {str(e)}", exc_info=True)
            raise
        except ValueError as e:
            logger.error(f"Configuration error: {str(e)}")
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
            data.pop("_id", None)

            logger.info(f"Attempting to insert data: {data}")
            result = self.collection.insert_one(data)

            if result.inserted_id:
                logger.info(f"Data inserted with ID: {result.inserted_id}")
                return str(result.inserted_id)
            else:
                logger.warning(
                    "Insert operation returned no ID. Check data and permissions."
                )
                return None
        except PyMongoError as e:
            logger.error(
                f"An error occurred while inserting data: {str(e)}", exc_info=True
            )
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
            logger.info(f"Retrieved {len(data)} documents with query: {query}")
            return data
        except PyMongoError as e:
            logger.error(
                f"An error occurred while retrieving data: {str(e)}", exc_info=True
            )
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
            logger.info(
                f"Modified {result.modified_count} documents with query: {query} and update: {update}"
            )
            return result.modified_count
        except PyMongoError as e:
            logger.error(
                f"An error occurred while updating data: {str(e)}", exc_info=True
            )
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
            logger.info(f"Deleted {result.deleted_count} documents with query: {query}")
            return result.deleted_count
        except PyMongoError as e:
            logger.error(
                f"An error occurred while deleting data: {str(e)}", exc_info=True
            )
            return 0
