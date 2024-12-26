from typing import Dict, Any, Tuple, Optional
from app.services.database_handler import DatabaseHandler
from app.utils.logging_utils import setup_logging

logger = setup_logging(__name__)

# Constants for status codes
STATUS_ERROR = 500


class JobService:
    """Service for managing job operations."""

    def __init__(self, database_handler: DatabaseHandler) -> None:
        """
        Initialize the JobService with necessary dependencies.

        Args:
            database_handler (DatabaseHandler): Service to handle database operations.
        """
        if not isinstance(database_handler, DatabaseHandler):
            raise TypeError("Expected an instance of DatabaseHandler.")
        self.database_handler = database_handler

    def store_job(self, job_details: dict) -> Tuple[int, str]:
        """
        Store job details in the database.

        Args:
            job_details (dict): The job data to store.

        Returns:
            Tuple[int, str]: A tuple containing the status code and message.
        """
        try:
            logger.debug("Storing job in the database...")
            status_code, message = self.database_handler.store_job(job_details)

            if status_code != 200:
                logger.error(
                    f"Failed to store job. Job ID: {job_details.get('job_id', 'N/A')} -> Error: {message}",
                    exc_info=True,
                )
                return status_code, message

            logger.info(
                f"Job successfully stored. Job ID: {job_details.get('job_id', 'N/A')}"
            )
            return status_code, message
        except Exception as e:
            logger.exception(
                f"Error storing new job. Job ID: {job_details.get('job_id', 'N/A')}. Error: {str(e)}",
                exc_info=True,
            )
            return STATUS_ERROR, "Failed to store job."

    def update_job(self, job_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update the status of a job in the database.

        Args:
            job_id (str): The ID of the job to update.
            updates (Dict[str, Any]): The data to update.

        Returns:
            bool: True if job updated successfully, else False.
        """
        try:
            logger.debug(f"Updating job ID: {job_id} with updates: {updates}")
            result = self.database_handler.update_job(job_id, updates)
            if not result:
                logger.warning(f"Failed to update job ID: {job_id}", exc_info=True)
            return result
        except Exception as e:
            logger.exception(
                f"Error updating job ID: {job_id}. Error: {str(e)}", exc_info=True
            )
            return False

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch job details from the database.

        Args:
            job_id (str): The ID of the job to fetch.

        Returns:
            Optional[Dict[str, Any]]: The job details if found, else None.
        """
        try:
            logger.debug(f"Fetching job details for ID: {job_id}")
            job = self.database_handler.get_job_by_id(job_id)

            if not job:
                logger.info(f"No job found with ID: {job_id}")
                return None

            logger.info(f"Fetched job details for ID: {job_id}")
            return job.to_dict()
        except Exception as e:
            logger.exception(
                f"Error fetching job ID: {job_id}. Error: {str(e)}", exc_info=True
            )
            return None
