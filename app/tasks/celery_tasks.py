from typing import Optional
from celery import Celery
import json
from app.utils.config import Config
from app.db.db_mongo import MongoDBClient
from app.db.jobs_crud import JobsCRUD
from app.db.products_crud import ProductsCRUD
from app.services.database_handler import DatabaseHandler
from app.services.helpers.scraper_helpers import ScraperHelper
from app.services.job_service import JobService
from app.services.product_service import ProductService
from app.services.scraper_service import ScraperService
from app.services.product_processor import ProductProcessor
from app.utils.data_cleaner import DataCleaner
from app.utils.logging_utils import setup_logging
from app.utils.retry_with_backoff import retry_with_backoff

logger = setup_logging(__name__)

REDIS_HOST = Config.REDIS_HOST
REDIS_PORT = Config.REDIS_PORT
CELERY_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}"
RABBITMQ_BROKER = Config.RABBITMQ_BROKER

celery_app = Celery(__name__, broker=RABBITMQ_BROKER, backend=CELERY_BACKEND)
celery_app.conf.task_routes = {"tasks.*": {"queue": "scrape_queue"}}

# Status constants
STATUS_IN_PROGRESS = "In Progress"
STATUS_FAILED = "Failed"
STATUS_COMPLETED = "Completed"


def initialize_services() -> tuple[ProductService, JobService]:
    """
    Initialize the required services for scraping tasks.

    Returns:
        tuple[ProductService, JobService]: ProductService and JobService instances.
    """
    jobs_crud = JobsCRUD()
    product_client = ProductsCRUD()
    mongo_client = MongoDBClient()
    scraper_service = ScraperService()
    data_cleaner = DataCleaner()
    product_processor = ProductProcessor(data_cleaner)

    database_handler = DatabaseHandler(jobs_crud, product_client, mongo_client)
    product_service = ProductService(
        scraper_service, product_processor, database_handler
    )
    job_service = JobService(database_handler)

    return product_service, job_service


def scrape_product(web_code: str, product_service: ProductService) -> Optional[dict]:
    """
    Scrape product details using the given web_code.

    Args:
        web_code (str): The web code for scraping.
        product_service (ProductService): Product service instance.

    Returns:
        Optional[dict]: Scraped product details if successful, else None.
    """
    scrape_helper = ScraperHelper(product_service)
    return scrape_helper.scrape_product(web_code)


@celery_app.task(
    name="tasks.scrape",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
)
def scrape_task(job_details: dict) -> dict:
    """
    Celery task for scraping a product.

    Args:
        job_details (dict): Details of the job to be processed.

    Returns:
        dict: Result of the scraping task.
    """
    job_details["job_id"] = scrape_task.request.id
    job_id = job_details["job_id"]
    web_code = job_details["web_code"]

    product_service, job_service = initialize_services()

    try:
        job_service.update_job(job_id, {"status": STATUS_IN_PROGRESS})
        result = retry_with_backoff(lambda: scrape_product(web_code, product_service))
        if not result:
            job_service.update_job(job_id, {"status": STATUS_FAILED})
            logger.error(f"Scraping failed for Job ID: {job_id}", exc_info=True)
            return {"error": "Failed to scrape the product."}

        job_service.update_job(
            job_id, {"status": STATUS_COMPLETED, "result": json.dumps(result)}
        )
        logger.info(f"Scraping completed for Job ID: {job_id}")
        return result
    except Exception as e:
        job_service.update_job(job_id, {"status": STATUS_FAILED})
        logger.error(
            f"Scraping failed for Job ID: {job_id}. Error: {str(e)}", exc_info=True
        )
        return {"error": str(e)}
