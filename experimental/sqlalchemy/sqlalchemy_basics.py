import os
from typing import List, Optional

from sqlalchemy import create_engine, Column, String, DateTime, Integer
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

from app.utils.logging_utils import setup_logging
from app.utils.datetime_handler import get_current_datetime

load_dotenv()

logger = setup_logging(__name__)
POSTGRES_URI = os.getenv("POSTGRES_URI")
Base = declarative_base()


class Jobs(Base):
    __tablename__ = "jobs"

    job_id = Column("job_id", String, primary_key=True)
    url = Column("url", String)
    status = Column("status", String)
    result = Column("result", String)
    created_at = Column("created_at", DateTime, default=get_current_datetime())
    updated_at = Column("updated_at", DateTime, default=get_current_datetime())
    product_id = Column("product_id", Integer, nullable=True, default=None)

    def __init__(self, job_id, url, status, result, created_at, updated_at):
        self.job_id = job_id
        self.url = url
        self.status = status
        self.result = result
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return f"Jobs(job_id={self.job_id}, url={self.url}, status={self.status}, result={self.result}, created_at={self.created_at}, updated_at={self.updated_at})"


class Jobs_CRUD:
    """A PostgreSQL database client to handle connection and CRUD operations."""

    def __init__(self) -> None:
        """
        Initialize the PostgreSQL database connection using the connection URL from environment variables.
        """
        try:
            self.engine = create_engine(POSTGRES_URI)
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)
            logger.info("Connected to PostgreSQL successfully.")
        except (SQLAlchemyError, ValueError) as e:
            logger.critical(f"Database connection error: {str(e)}", exc_info=True)
            raise

    def insert_data(
        self,
        job_id: str,
        url: str,
        status: str,
        result: str,
        created_at: DateTime,
        updated_at: DateTime,
    ) -> None:
        """
        Insert a row into the specified table.

        Args:
            job_id (str): Unique identifier for the task.
            url (str): The product URL to scrape.
            status (str): Pending, In Progress, Success, Failed.
            result (str): Parsed product details or error message.
            created_at (datetime): Timestamp when the task was created.
            updated_at (datetime): Timestamp when the task was last updated.
        """
        try:
            with self.Session() as session:
                with session.begin():
                    job = Jobs(
                        job_id=job_id,
                        url=url,
                        status=status,
                        result=result,
                        created_at=created_at,
                        updated_at=updated_at,
                    )
                    session.add(job)
                logger.info("Data inserted successfully.")
        except SQLAlchemyError as e:
            logger.error(f"Error inserting data: {str(e)}", exc_info=True)

    def get_all_jobs(self) -> List[Jobs]:
        """
        Retrieve all jobs from the database.

        Returns:
            List[Jobs]: A list of Jobs objects.
        """
        try:
            with self.Session() as session:
                jobs = session.query(Jobs).all()
            return jobs
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving jobs: {str(e)}", exc_info=True)
            return []

    def get_job_by_id(self, job_id: str) -> Optional[Jobs]:
        """
        Retrieve a job by its unique identifier.

        Args:
            job_id (str): The unique identifier of the job.

        Returns:
            Jobs: The job object if found, otherwise None.
        """
        try:
            with self.Session() as session:
                job = session.query(Jobs).filter_by(job_id=job_id).first()
            return job
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving job: {str(e)}", exc_info=True)
            return None

    def update_job(self, job_id: str, status: str, result: str) -> bool:
        """
        Update the status and result of a job.

        Args:
            job_id (str): The unique identifier of the job.
            status (str): The new status of the job.
            result (str): The new result of the job.

        Returns:
            bool: True if the job was updated successfully, otherwise False.
        """
        try:
            with self.Session() as session:
                job = session.query(Jobs).filter_by(job_id=job_id).first()
                job.status = status
                job.result = result
                job.updated_at = get_current_datetime()
                session.commit()
            logger.info("Job updated successfully.")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error updating job: {str(e)}", exc_info=True)
            return False

    def delete_job(self, job_id: str) -> bool:
        """
        Delete a job by its unique identifier.

        Args:
            job_id (str): The unique identifier of the job.

        Returns:
            bool: True if the job was deleted successfully, otherwise False.
        """
        try:
            with self.Session() as session:
                job = session.query(Jobs).filter_by(job_id=job_id).first()
                session.delete(job)
                session.commit()
            logger.info("Job deleted successfully.")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error deleting job: {str(e)}", exc_info=True)
            return False


if __name__ == "__main__":
    from uuid import uuid4

    jobs_client = Jobs_CRUD()

    # Insert data
    job_id = str(uuid4())
    url = "https://www.amiparina.com"
    status = "Pending"
    result = "In Progress"
    created_at = get_current_datetime()
    updated_at = get_current_datetime()

    jobs_client.insert_data(job_id, url, status, result, created_at, updated_at)

    # Get all data
    jobs = jobs_client.get_all_jobs()

    for job in jobs:
        print(job)

    # Get data by ID
    res = jobs_client.get_job_by_id("1ea317bc-8994-469c-8a1d-dba3b7a86d05")
    print("job of the ID: ", res if res else "Not found")

    # Update data
    job_id = "1ea317bc-8994-469c-8a1d-dba3b7a86d05"
    status = "Success"
    result = "Data scraped successfully."
    print(jobs_client.update_job(job_id, status, result))

    jobs = jobs_client.get_all_jobs()

    for job in jobs:
        print(job)

    # Delete data
    job_id = "1ea317bc-8994-469c-8a1d-dba3b7a86d05"
    print(jobs_client.delete_job(job_id))

    jobs = jobs_client.get_all_jobs()

    for job in jobs:
        print(job)
