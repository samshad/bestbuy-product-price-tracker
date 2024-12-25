from celery import Celery
import json
import os

from dotenv import load_dotenv

from app.db.db_mongo import MongoDBClient
from app.db.jobs_crud import JobsCRUD
from app.db.products_crud import ProductsCRUD
from app.services.database_handler import DatabaseHandler
from app.services.helpers.existing_product_helpers import handle_existing_product
from app.services.helpers.scraping_helpers import scrape_product_details
from app.services.helpers.store_new_product_details_helpers import store_new_product
from app.services.job_service import JobService
from app.services.product_service import ProductService
from app.services.scraper_service import ScraperService
from app.services.product_processor import ProductProcessor
from app.utils.data_cleaner import DataCleaner
from app.utils.my_logger import setup_logging
from app.utils.retry_with_backoff import retry_with_backoff

load_dotenv()
logger = setup_logging(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
CELERY_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}"
RABBITMQ_BROKER = os.getenv(
    "RABBITMQ_BROKER", "amqp://guest:guest@localhost:5672//"
)  # Update with your RabbitMQ URL

celery_app = Celery(__name__, broker=RABBITMQ_BROKER, backend=CELERY_BACKEND)
celery_app.conf.task_routes = {
    "tasks.*": {"queue": "scrape_queue"}
}  # Route tasks to specific queues


# Example scraping logic
def scrape_url(web_code: str, product_service: ProductService) -> dict | None:
    """Simulated scraping logic."""
    # sleep(10)
    # return {"title": "This is a Product", "price": "$100.00", "webcode": webcode}
    existing_product = product_service.get_product(None, web_code)

    product_details = scrape_product_details(web_code, product_service)
    if not product_details:
        return product_details

    if existing_product:
        status_code, message = handle_existing_product(
            existing_product, product_details, product_service
        )
        logger.info(
            f"Product already exists. Status: {status_code}. Message: {message}"
        )
        return product_details

    else:
        status_code, message = store_new_product(product_details, product_service)
        logger.info(f"New product stored. Status: {status_code}. Message: {message}")
        return product_details


@celery_app.task(
    name="tasks.scrape",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
)
def scrape_task(job_details: dict) -> dict:
    """Celery task for scraping a URL."""

    job_details["job_id"] = scrape_task.request.id
    job_id = job_details["job_id"]
    webcode = job_details["web_code"]
    # status = job_details["status"]
    # result = job_details["result"]
    # product_id = job_details["product_id"]

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

    try:
        flag = job_service.update_job(job_id, {"status": "In Progress"})
        logger.info(f"Job {job_id} status updated to In Progress. Flag: {flag}")
        result = retry_with_backoff(lambda: scrape_url(webcode, product_service))
        if not result:
            flag = job_service.update_job(job_id, {"status": "Failed"})
            logger.error(f"Failed in scrape_task. Flag: {flag}. Job ID: {job_id}")
            return {"error": "Failed to scrape the product."}
        flag = job_service.update_job(
            job_id, {"status": "Completed", "result": json.dumps(result)}
        )
        logger.info(f"Job {job_id} status updated to Completed. Flag: {flag}")
        return result
    except Exception as e:
        flag = job_service.update_job(job_id, {"status": "Failed"})
        logger.error(f"Failed in scrape_task. Flag: {flag}. Error: {str(e)}")
        return {"error": str(e)}
