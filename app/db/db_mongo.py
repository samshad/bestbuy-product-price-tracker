from typing import Optional, Dict, Any, List
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
from app.utils.logging_utils import setup_logging
from app.utils.config import Config

# Configure logging
logger = setup_logging(__name__)


class MongoDBClient:
    """A MongoDB client to handle CRUD operations for product data."""

    def __init__(self) -> None:
        """
        Initialize the MongoDBClient with credentials from the .env file.
        """
        try:
            self.mongo_uri = Config.MONGO_URI
            self.db_name = Config.MONGO_DB_NAME
            self.collection_name = Config.MONGO_COLLECTION_NAME

            # Connect to MongoDB
            self.client = MongoClient(
                self.mongo_uri, tls=True, tlsAllowInvalidCertificates=True
            )
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]

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
            data.pop("_id", None)  # Ensure `_id` is not None to avoid conflicts.
            logger.info("Attempting to insert data into the collection.")
            result = self.collection.insert_one(data)
            logger.info(f"Data inserted successfully with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except PyMongoError as e:
            logger.error(f"Failed to insert data: {str(e)}", exc_info=True)
            return None

    def get_data(self, query: Dict[str, Any] = dict) -> List[Dict[str, Any]]:
        """
        Retrieve documents from the MongoDB collection.

        Args:
            query (Dict[str, Any]): The MongoDB query filter. Default is all documents.

        Returns:
            List[Dict[str, Any]]: List of matching documents.
        """
        try:
            logger.info(f"Retrieving data with query: {query}")
            data = list(self.collection.find(query))
            logger.info(f"Retrieved {len(data)} documents.")
            return data
        except PyMongoError as e:
            logger.error(f"Failed to retrieve data: {str(e)}", exc_info=True)
            return []

    def update_data(self, query: Dict[str, Any], update: Dict[str, Any]) -> int:
        """
        Update documents in the MongoDB collection.

        Args:
            query (Dict[str, Any]): The query filter to select documents.
            update (Dict[str, Any]): The updates to apply.

        Returns:
            int: The number of documents modified.
        """
        try:
            logger.info(f"Updating data with query: {query} and update: {update}")
            result = self.collection.update_many(query, {"$set": update})
            logger.info(f"Modified {result.modified_count} documents.")
            return result.modified_count
        except PyMongoError as e:
            logger.error(f"Failed to update data: {str(e)}", exc_info=True)
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
            logger.info(f"Deleting data with query: {query}")
            result = self.collection.delete_many(query)
            logger.info(f"Deleted {result.deleted_count} documents.")
            return result.deleted_count
        except PyMongoError as e:
            logger.error(f"Failed to delete data: {str(e)}", exc_info=True)
            return 0
