from app.db.jobs_crud import JobsCRUD


def test_insert_job(client, job):
    result = client.insert_job(job["job_id"], job["url"], job["status"], job["result"])

    print("Success:" if result else "Failed")


def test_get_all_jobs(client):
    jobs = client.get_all_jobs()

    for job in jobs:
        print(job)


def test_get_job_by_id(client, job_id):
    job = client.get_job_by_id(job_id)

    print(job if job else "Not found")

    print(job.status)


def test_update_job(client, update_data):
    result = client.update_job(job_id, update_data)

    print("Success:" if result else "Failed")


def test_delete_job(client, job_id):
    result = client.delete_job(job_id)

    print("Success:" if result else "Failed")


if __name__ == "__main__":
    from uuid import uuid4

    jobs_crud = JobsCRUD()

    # Sample data
    job_id = uuid4()
    url = "https://hulu.com"
    status = "pending"
    result = None

    job = {"job_id": job_id, "url": url, "status": status, "result": result}

    # Insert data
    # test_insert_job(jobs_crud, job)

    # Read data
    test_get_all_jobs(jobs_crud)

    job_id = "df85c87a-7a72-4088-9de0-3fb59f7b2039"

    # Read data by ID
    # test_get_job_by_id(jobs_crud, job_id)

    # Update data
    update_data = {"product_id": 2}
    test_update_job(jobs_crud, update_data)

    # Delete data
    # test_delete_job(jobs_crud, job_id)

    # Read data
    # test_get_all_jobs(jobs_crud)
