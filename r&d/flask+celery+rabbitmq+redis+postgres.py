from flask import Flask, request, jsonify
from time import sleep
import celery
import psycopg2
import uuid
import json
import os
from dotenv import load_dotenv

from app.db.jobs_crud import JobsCRUD

load_dotenv()

# REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
# REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
RABBITMQ_BROKER = os.environ.get(
    "RABBITMQ_BROKER", "amqp://guest:guest@localhost:5672//"
)  # Update with your RabbitMQ URL

app = Flask(__name__)

# Celery app setup
celery_app = celery.Celery(__name__, broker=RABBITMQ_BROKER)
# celery_app = celery.Celery(__name__, broker=RABBITMQ_BROKER, backend='redis://{}:{}'.format(REDIS_HOST, REDIS_PORT))
celery_app.conf.task_routes = {
    "tasks.*": {"queue": "scrape_queue"}
}  # Route tasks to specific queues

# Redis client
# redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)


# Database connection function
def get_db_connection():
    try:
        job_client = JobsCRUD()
        return job_client
    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
        return None


# Sample scraping function (replace with your actual scraping logic)
def scrape_url(url):
    sleep(50)  # Simulate scraping time
    return {"title": "Example Product", "price": "$10.00", "url": url}


@celery_app.task(name="tasks.scrape")
def scrape_task(job_id, url):
    try:
        sleep(20)
        conn = get_db_connection()
        conn.update_job(job_id, "In Progress", None)
        result = scrape_url(url)
        conn.update_job(job_id, "Success", json.dumps(result))
        return result
    except Exception as e:
        conn = get_db_connection()
        conn.update_job(job_id, "Failed", f"Error: {str(e)}")
        return {"error": str(e)}


@app.route("/scrape", methods=["POST"])
def scrape():
    print("Scraping request received", request.json)
    url = request.json.get("url")
    if not url:
        return jsonify({"error": "URL is required"}), 400

    job_id = str(uuid.uuid4())
    status = "Pending"
    result = None

    conn = get_db_connection()
    conn.insert_job(job_id, url, status, result)

    scrape_task.delay(job_id, url)

    return jsonify({"task_id": job_id}), 202


@app.route("/status/<task_id>", methods=["GET"])
def status(task_id):
    conn = get_db_connection()
    job = conn.get_job_by_id(task_id)
    if job:
        return jsonify({"status": job.status}), 200
    return jsonify({"error": "Task not found"}), 404


@app.route("/result/<task_id>", methods=["GET"])
def result(task_id):
    conn = get_db_connection()
    job = conn.get_job_by_id(task_id)

    if job:
        if job.status == "Success":
            return jsonify(json.loads(job.result)), 200
        elif job.status == "Failed":
            return jsonify({"error": job.result}), 500
        else:
            return jsonify({"status": job.status, "message": "Task still running"}), 200
    return jsonify({"error": "Task not found or not completed yet"}), 404


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
