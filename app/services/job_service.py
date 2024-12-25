from typing import Dict, Any

from app.services.database_handler import DatabaseHandler
from app.utils.logging_utils import setup_logging

logger = setup_logging(__name__)


class JobService:
    """Service for managing job operations."""

    def __init__(self, database_handler: DatabaseHandler) -> None:
        """
        Initialize the JobService with necessary dependencies.

        Args:
            database_handler (DatabaseHandler): Service to handle database operations.
        """
        self.database_handler = database_handler

    def store_job(self, job_details: dict) -> tuple[int, str]:
        """
        Store job details in the database.

        Args:
            job_details (dict): The job data to store.

        Returns:
            bool: True if job stored successfully, else False
        """
        try:
            print("going to database handler...")
            status_code, message = self.database_handler.store_job(job_details)
            print("database handler done...")
            if status_code != 200:
                logger.error(
                    f"Failed to store job. Job ID: {job_details['job_id']} -> Error: {message}"
                )
                return status_code, message
            logger.info(f"Job successfully stored. Job ID: {job_details['job_id']}")
            return status_code, message
        except Exception as e:
            logger.exception(f"Error storing new job. {str(e)}", exc_info=True)
            return 500, f"Failed to store job. Job ID: {job_details['job_id']}"

    def update_job(self, job_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update the status of a job in the database.

        Args:
            job_id (int): The ID of the job to update.
            updates (Dict[str, Any]): The data to update.

        Returns:
            bool: True if job updated successfully, else False
        """
        try:
            return self.database_handler.update_job(job_id, updates)
        except Exception as e:
            logger.exception(f"Error updating job status. {str(e)}", exc_info=True)
            return False

    def get_job(self, job_id: str) -> dict:
        """
        Fetch job details from the database.

        Args:
            job_id (str): The ID of the job to fetch.

        Returns:
            dict: The job details.
        """
        try:
            job = self.database_handler.get_job_by_id(job_id)
            if not job:
                logger.info(f"No job found with ID: {job_id}")
                return {}
            return job.to_dict()
        except Exception as e:
            logger.exception(f"Error fetching job details. {str(e)}", exc_info=True)
            return {}
