import os
from typing import List, Optional, Any, Dict

from sqlalchemy import create_engine, Column, String, DateTime, Integer
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

from app.utils.logging_utils import setup_logging
from app.utils.datetime_handler import get_current_datetime

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


class Jobs(Base):
    """Database model representing a job."""

    __tablename__ = "jobs"

    job_id = Column(String, primary_key=True, nullable=False, unique=True)
    webcode = Column(String, nullable=False)
    status = Column(String, nullable=False)
    result = Column(String, nullable=True)
    product_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=get_current_datetime, nullable=False)
    updated_at = Column(
        DateTime,
        default=get_current_datetime,
        onupdate=get_current_datetime,
        nullable=False,
    )

    def __repr__(self) -> str:
        """
        Return a string representation of the job record.

        Returns:
            str: A string representation of the job record.
        """
        return (
            f"Jobs(job_id={self.job_id}, webcode={self.webcode}, status={self.status}, "
            f"result={self.result}, product_id={self.product_id}, created_at={self.created_at}, "
            f"updated_at={self.updated_at})"
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


class JobsCRUD:
    """Handles database connection and CRUD operations for Jobs."""

    def __init__(self) -> None:
        """Initialize database connection and session."""
        try:
            self.engine = create_engine(POSTGRES_URI)
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)
            logger.info("Connected to PostgreSQL successfully.")
        except SQLAlchemyError as e:
            logger.critical(f"Database connection error: {str(e)}", exc_info=True)
            raise e

    def to_dict(self):
        return {"engine": self.engine, "Session": self.Session}

    def _validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """
        Validate parameters to ensure they meet basic constraints.

        Args:
            parameters (Dict[str, Any]): Dictionary of parameters to validate.

        Returns:
            bool: True if validation passes, False otherwise.
        """
        for key, value in parameters.items():
            if not value:
                logger.error(f"Validation failed: {key} is missing or empty.")
                return False
        return True

    def insert_job(
        self,
        job_id: str,
        webcode: str,
        status: str,
        result: Optional[str] = None,
        product_id: Optional[int] = None,
    ) -> bool:
        """
        Insert a new job into the database.

        Args:
            job_id (str): Unique identifier for the job.
            webcode (str): Product webcode associated with the job.
            status (str): Status of the job (e.g., Pending, In Progress, Success, Failed).
            result (Optional[str]): Job result or error message.
            product_id (Optional[int]): ID of the product associated with the job.

        Returns:
            bool: True if the job was inserted successfully, False otherwise.
        """

        parameters = {"job_id": job_id, "webcode": webcode, "status": status}
        if not self._validate_parameters(parameters):
            return False

        try:
            with self.Session() as session:
                with session.begin():
                    job = Jobs(
                        job_id=job_id,
                        webcode=webcode,
                        status=status,
                        result=result,
                        product_id=product_id,
                    )
                    session.add(job)
                logger.info(f"Job {job_id} inserted successfully.")
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error inserting job {job_id}: {str(e)}", exc_info=True)
            return False

    def get_all_jobs(self) -> List[Jobs]:
        """
        Retrieve all jobs from the database.

        Returns:
            List[Jobs]: A list of all job records. If no jobs are found, an empty list is returned.
        """
        try:
            with self.Session() as session:
                jobs = session.query(Jobs).all()
                logger.info("Retrieved all jobs successfully.")
                return jobs
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving all jobs: {str(e)}", exc_info=True)
            return []

    def get_job_by_id(self, job_id: str) -> Optional[Jobs]:
        """
        Retrieve a job by its ID.

        Args:
            job_id (str): Unique identifier for the job.

        Returns:
            Optional[Jobs]: The job record if found, None otherwise.
        """
        try:
            with self.Session() as session:
                job = session.query(Jobs).filter_by(job_id=job_id).first()
                if job:
                    logger.info(f"Retrieved job {job_id} successfully.")
                else:
                    logger.warning(f"Job {job_id} not found.")
                return job
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving job {job_id}: {str(e)}", exc_info=True)
            return None

    def update_job(self, job_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a job in the database.

        Args:
            job_id (str): Unique identifier for the job.
            updates (Dict[str, Any]): A dictionary containing fields to update.

        Returns:
            bool: True if the job was updated successfully, False otherwise.
        """
        try:
            with self.Session() as session:
                job = session.query(Jobs).filter_by(job_id=job_id).first()
                if not job:
                    logger.warning(f"Job {job_id} not found for update.")
                    return False
                for field, value in updates.items():
                    if hasattr(job, field):
                        setattr(job, field, value)
                job.updated_at = get_current_datetime()
                session.commit()
                logger.info(f"Job {job_id} updated successfully.")
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error updating job {job_id}: {str(e)}", exc_info=True)
            return False

    def delete_job(self, job_id: str) -> bool:
        """
        Delete a job by its ID.

        Args:
            job_id (str): Unique identifier for the job.

        Returns:
            bool: True if the job was deleted successfully, False otherwise.
        """
        try:
            with self.Session() as session:
                job = session.query(Jobs).filter_by(job_id=job_id).first()
                if not job:
                    logger.warning(f"Job {job_id} not found for deletion.")
                    return False
                session.delete(job)
                session.commit()
                logger.info(f"Job {job_id} deleted successfully.")
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error deleting job {job_id}: {str(e)}", exc_info=True)
            return False


# Ensure the script doesn't run unintended code when imported
if __name__ == "__main__":
    logger.info("JobsCRUD module loaded successfully.")
