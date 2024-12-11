import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any

# Load environment variables from .env file
load_dotenv()

class PostgresDBClient:
    """A PostgreSQL database client to handle connection and CRUD operations."""

    def __init__(self) -> None:
        """Initialize the PostgreSQL database connection using the connection URL from environment variables."""
        try:
            self.conn = psycopg2.connect(os.getenv("POSTGRES_URI"), cursor_factory=RealDictCursor)
            self.conn.autocommit = True
            self.cursor = self.conn.cursor()
            print("Connected to PostgreSQL successfully.")
        except psycopg2.DatabaseError as e:
            print(f"Database connection error: {e}")
            self.conn = None

    def create_table(self, table_name: str, schema: str) -> None:
        """
        Create a table with the specified name and schema if it doesn't already exist.

        Args:
            table_name (str): The name of the table to create.
            schema (str): SQL schema defining table columns and data types.
        """
        try:
            create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({schema})"
            self.cursor.execute(create_table_query)
            print(f"Table '{table_name}' created or already exists.")
        except psycopg2.Error as e:
            print(f"Error creating table: {e}")

    def insert_data(self, table_name: str, data: Dict[str, Any]) -> Optional[int]:
        """
        Insert a row into the specified table.

        Args:
            table_name (str): The name of the table to insert data into.
            data (Dict[str, Any]): A dictionary representing the data to insert.

        Returns:
            Optional[int]: The ID of the inserted row or None if insertion failed.
        """
        columns = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({values}) RETURNING id"

        try:
            self.cursor.execute(query, list(data.values()))
            row_id = self.cursor.fetchone()["id"]
            print(f"Data inserted with ID: {row_id}")
            return row_id
        except psycopg2.Error as e:
            print(f"Error inserting data: {e}")
            return None

    def get_data(self, table_name: str, conditions: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Retrieve rows from the specified table with optional conditions.

        Args:
            table_name (str): The name of the table to retrieve data from.
            conditions (Optional[Dict[str, Any]]): A dictionary of conditions for filtering data.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries representing the retrieved rows.
        """
        query = f"SELECT * FROM {table_name}"
        if conditions:
            where_clause = ' AND '.join([f"{col} = %s" for col in conditions.keys()])
            query += f" WHERE {where_clause}"
            values = list(conditions.values())
        else:
            values = []

        try:
            self.cursor.execute(query, values)
            rows = self.cursor.fetchall()
            print(f"Retrieved {len(rows)} rows.")
            return rows
        except psycopg2.Error as e:
            print(f"Error retrieving data: {e}")
            return []

    def update_data(self, table_name: str, data: Dict[str, Any], conditions: Dict[str, Any]) -> int:
        """
        Update rows in the specified table based on conditions.

        Args:
            table_name (str): The name of the table to update data in.
            data (Dict[str, Any]): A dictionary of columns and values to update.
            conditions (Dict[str, Any]): A dictionary of conditions for filtering which rows to update.

        Returns:
            int: The number of rows updated.
        """
        set_clause = ', '.join([f"{col} = %s" for col in data.keys()])
        where_clause = ' AND '.join([f"{col} = %s" for col in conditions.keys()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
        values = list(data.values()) + list(conditions.values())

        try:
            self.cursor.execute(query, values)
            row_count = self.cursor.rowcount
            print(f"Updated {row_count} rows.")
            return row_count
        except psycopg2.Error as e:
            print(f"Error updating data: {e}")
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
        where_clause = ' AND '.join([f"{col} = %s" for col in conditions.keys()])
        query = f"DELETE FROM {table_name} WHERE {where_clause}"
        values = list(conditions.values())

        try:
            self.cursor.execute(query, values)
            row_count = self.cursor.rowcount
            print(f"Deleted {row_count} rows.")
            return row_count
        except psycopg2.Error as e:
            print(f"Error deleting data: {e}")
            return 0

    def close(self) -> None:
        """Close the database connection."""
        if self.conn:
            self.cursor.close()
            self.conn.close()
            print("Database connection closed.")
