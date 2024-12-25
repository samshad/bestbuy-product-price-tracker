import os
from typing import List, Optional, Any, Dict

from sqlalchemy import create_engine, Column, String, DateTime, Integer
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

from app.utils.my_logger import setup_logging
from app.utils.datetime_handler import get_current_datetime
from app.utils.validate_input import validate_input_product_id_web_code

# Load environment variables
load_dotenv()

# Initialize logger
logger = setup_logging(__name__)

# Database configuration
POSTGRES_URI = os.getenv("POSTGRES_URI")
if not POSTGRES_URI:
    logger.critical("POSTGRES_URI is not set in the environment variables.")
    raise ValueError("POSTGRES_URI must be set as an environment variable.")

Base = declarative_base()


class Products(Base):
    """Database model representing a product."""

    __tablename__ = "products"

    product_id = Column(
        Integer, primary_key=True, autoincrement=True, nullable=False, unique=True
    )
    web_code = Column(String, nullable=False, unique=True)
    title = Column(String, nullable=False)
    model = Column(String, nullable=True)
    url = Column(String, nullable=False)
    price = Column(Integer, nullable=False, default=0)
    save = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=get_current_datetime, nullable=False)
    updated_at = Column(
        DateTime,
        default=get_current_datetime,
        onupdate=get_current_datetime,
        nullable=False,
    )

    def __repr__(self) -> str:
        """Return the string representation of the product object."""
        return (
            f"Products(id={self.product_id}, web_code={self.web_code}, title={self.title}, "
            f"model={self.model}, url={self.url}, price={self.price}, save={self.save}, "
            f"created_at={self.created_at}, updated_at={self.updated_at})"
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the product object to a dictionary.

        Returns:
            Dict[str, Any]: A dictionary containing the product details.
        """
        return {
            column.name: str(getattr(self, column.name))
            for column_name, column in self.__table__.columns.items()
        }


class ProductsCRUD:
    """Handles database connection and CRUD operations for Products."""

    def __init__(self) -> None:
        """Initialize database connection and session."""
        try:
            self.engine = create_engine(POSTGRES_URI)
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)
            logger.info("Connected to the database successfully.")
        except SQLAlchemyError as e:
            logger.critical(f"Database connection error: {str(e)}", exc_info=True)
            raise e

    def insert_product(
        self,
        web_code: str,
        title: str,
        model: Optional[str],
        url: str,
        price: int,
        save: int,
    ) -> Optional[Dict[str, int]]:
        """
        Insert a new product into the database.

        Args:
            web_code (str): The product's web code.
            title (str): The product's title.
            model (Optional[str]): The product's model.
            url (str): The product's URL.
            price (int): The product's price.
            save (int): The product's discount amount.

        Returns:
            Optional[Dict[str, int]]: A dictionary containing the product ID if the product was inserted successfully, None otherwise.
        """
        try:
            with self.Session() as session:
                with session.begin():
                    product = Products(
                        web_code=web_code,
                        title=title,
                        model=model,
                        url=url,
                        price=price,
                        save=save,
                    )
                    session.add(product)
                logger.info(
                    f"Product inserted successfully. Product_ID: {product.product_id}"
                )
                return {"product_id": product.product_id}
        except SQLAlchemyError as e:
            logger.error(f"Error inserting product: {str(e)}", exc_info=True)
            return None

    def get_all_products(self) -> List[Products]:
        """
        Retrieve all products from the database.

        Returns:
            List[Products]: A list of all product records. If no products are found, an empty list is returned.
        """
        try:
            with self.Session() as session:
                products = session.query(Products).all()
                logger.info("All the products retrieved successfully.")
                return products
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving products: {str(e)}", exc_info=True)
            return []

    def get_all_products_pagination(
        self, offset: int = 0, limit: int = 10
    ) -> List[Products]:
        """
        Retrieve all products with pagination.

        Args:
            offset (int): Starting point of records to fetch.
            limit (int): Number of records to fetch.

        Returns:
            List[Products]: A paginated list of product records.
        """
        try:
            with self.Session() as session:
                products = session.query(Products).offset(offset).limit(limit).all()
                logger.info("Products retrieved successfully with pagination.")
                return products
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving products: {str(e)}", exc_info=True)
            return []

    def get_product(
        self, product_id: Optional[int] = None, web_code: Optional[str] = None
    ) -> Optional[Products]:
        """
        Retrieve a product by either product_id or web code.

        Args:
            product_id (Optional[int]): The product_id of the product to retrieve.
            web_code (Optional[str]): The web code of the product to retrieve.

        Returns:
            Optional[Products]: The product object if found, None otherwise.
        """
        if not validate_input_product_id_web_code(
            product_id=product_id, web_code=web_code
        ):
            logger.error(
                "Either 'product_id' or 'web_code' must be provided, but not both."
            )
            return None

        try:
            with self.Session() as session:
                if product_id:
                    product = (
                        session.query(Products)
                        .filter(Products.product_id == product_id)
                        .first()
                    )
                else:
                    product = (
                        session.query(Products)
                        .filter(Products.web_code == web_code)
                        .first()
                    )

                if product:
                    logger.info(
                        f"Product retrieved successfully. product_id: {product_id}"
                    )
                else:
                    logger.warning(
                        f"Product not found. product_id: {product_id}, web_code: {web_code}"
                    )
                return product
        except SQLAlchemyError as e:
            logger.error(
                f"Error retrieving product. product_id: {product_id}, web_code: {web_code}, error: {str(e)}",
                exc_info=True,
            )
            return None

    def update_product(self, product_id: int, updates: Dict[str, Any]) -> bool:
        """
        Update a product in the database.

        Args:
            product_id (int): The ID of the product to update.
            updates (Dict[str, Any]): A dictionary containing fields to update.

        Returns:
            bool: True if the product was updated successfully, False otherwise.
        """
        try:
            with self.Session() as session:
                product = (
                    session.query(Products)
                    .filter(Products.product_id == product_id)
                    .first()
                )
                if product:
                    for field, value in updates.items():
                        if hasattr(product, field):
                            setattr(product, field, value)
                    product.updated_at = get_current_datetime()
                    session.commit()
                    logger.info(
                        f"Product product_id: {product_id} updated successfully."
                    )
                    return True
                logger.warning(f"Product product_id: {product_id} not found.")
                return False
        except SQLAlchemyError as e:
            logger.error(
                f"Error updating product_id {product_id}: {str(e)}", exc_info=True
            )
            return False

    def delete_product(self, product_id: int) -> bool:
        """
        Delete a product from the database.

        Args:
            product_id (int): The ID of the product to delete.

        Returns:
            bool: True if the product was deleted successfully, False otherwise.
        """
        try:
            with self.Session() as session:
                product = (
                    session.query(Products)
                    .filter(Products.product_id == product_id)
                    .first()
                )
                if product:
                    session.delete(product)
                    session.commit()
                    logger.info(
                        f"Product product_id: {product_id} deleted successfully."
                    )
                    return True
                logger.warning(f"Product product_id: {product_id} not found.")
                return False
        except SQLAlchemyError as e:
            logger.error(
                f"Error deleting product_id {product_id}: {str(e)}", exc_info=True
            )
            return False


if __name__ == "__main__":
    products_crud = ProductsCRUD()

    # Sample data
    web_code = "1234562342342"
    title = "Example Product"
    model = "Model XYZ"
    url = "https://example.com/product"
    price = 10022
    save = 201
