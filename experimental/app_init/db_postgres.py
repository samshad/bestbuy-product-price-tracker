import os
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.errors import DatabaseError, OperationalError
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any
from app.utils.logging_utils import setup_logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
logger = setup_logging(__name__)


class PostgresDBClient:
    """A PostgreSQL database client to handle connection and CRUD operations."""

    def __init__(self) -> None:
        """
        Initialize the PostgreSQL database connection using the connection URL from environment variables.
        """
        try:
            postgres_uri = os.getenv("POSTGRES_URI")
            if not postgres_uri:
                raise ValueError("Missing POSTGRES_URI in environment variables.")

            self.conn = psycopg2.connect(postgres_uri, cursor_factory=RealDictCursor)
            self.conn.autocommit = True
            logger.info("Connected to PostgreSQL successfully.")
        except (DatabaseError, OperationalError) as e:
            logger.critical(f"Database connection error: {str(e)}", exc_info=True)
            self.conn = None
        except ValueError as e:
            logger.error(f"Configuration error: {str(e)}")
            raise

    def create_table(self, table_name: str, schema: str) -> None:
        """
        Create a table with the specified name and schema if it doesn't already exist.

        Args:
            table_name (str): The name of the table to create.
            schema (str): SQL schema defining table columns and data types.
        """
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({schema})"
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query)
            logger.info(f"Table '{table_name}' created or already exists.")
        except psycopg2.Error as e:
            logger.error(
                f"Error creating table '{table_name}': {str(e)}", exc_info=True
            )

    def insert_data(self, table_name: str, data: Dict[str, Any]) -> Optional[int]:
        """
        Insert a row into the specified table.

        Args:
            table_name (str): The name of the table to insert data into.
            data (Dict[str, Any]): A dictionary representing the data to insert.

        Returns:
            Optional[int]: The ID of the inserted row or None if insertion failed.
        """
        columns = ", ".join(data.keys())
        values = ", ".join(["%s"] * len(data))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({values}) RETURNING id"

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, list(data.values()))
                row_id = cursor.fetchone()["id"]
            logger.info(f"Data inserted into '{table_name}' with ID: {row_id}")
            return row_id
        except psycopg2.Error as e:
            logger.error(
                f"Error inserting data into '{table_name}': {str(e)}", exc_info=True
            )
            return None

    def get_data(
        self, table_name: str, conditions: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve rows from the specified table with optional conditions.

        Args:
            table_name (str): The name of the table to retrieve data from.
            conditions (Optional[Dict[str, Any]]): A dictionary of conditions for filtering data.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries representing the retrieved rows.
        """
        query = f"SELECT * FROM {table_name}"
        values = []

        if conditions:
            where_clause = " AND ".join([f"{col} = %s" for col in conditions.keys()])
            query += f" WHERE {where_clause}"
            values = list(conditions.values())

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, values)
                rows = cursor.fetchall()
            logger.info(
                f"Retrieved {len(rows)} rows from '{table_name}' with conditions: {conditions}"
            )
            return rows
        except psycopg2.Error as e:
            logger.error(
                f"Error retrieving data from '{table_name}': {str(e)}", exc_info=True
            )
            return []

    def update_data(
        self, table_name: str, data: Dict[str, Any], conditions: Dict[str, Any]
    ) -> int:
        """
        Update rows in the specified table based on conditions.

        Args:
            table_name (str): The name of the table to update data in.
            data (Dict[str, Any]): A dictionary of columns and values to update.
            conditions (Dict[str, Any]): A dictionary of conditions for filtering which rows to update.

        Returns:
            int: The number of rows updated.
        """
        set_clause = ", ".join([f"{col} = %s" for col in data.keys()])
        where_clause = " AND ".join([f"{col} = %s" for col in conditions.keys()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
        values = list(data.values()) + list(conditions.values())

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, values)
                row_count = cursor.rowcount
            logger.info(
                f"Updated {row_count} rows in '{table_name}' with data: {data} and conditions: {conditions}"
            )
            return row_count
        except psycopg2.Error as e:
            logger.error(
                f"Error updating data in '{table_name}': {str(e)}", exc_info=True
            )
            return 0

    def delete_data(self, table_name: str, conditions: Dict[str, Any]) -> int:
        """
        Delete rows from the specified table based on conditions.

        Args:
            table_name (str): The name of the table to delete data from.
            conditions (Dict[str, Any]): A dictionary of conditions for filtering which rows to delete.

        Returns:
            int: The number of rows deleted.
        """
        where_clause = " AND ".join([f"{col} = %s" for col in conditions.keys()])
        query = f"DELETE FROM {table_name} WHERE {where_clause}"
        values = list(conditions.values())

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, values)
                row_count = cursor.rowcount
            logger.info(
                f"Deleted {row_count} rows from '{table_name}' with conditions: {conditions}"
            )
            return row_count
        except psycopg2.Error as e:
            logger.error(
                f"Error deleting data from '{table_name}': {str(e)}", exc_info=True
            )
            return 0

    def close(self) -> None:
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed.")
