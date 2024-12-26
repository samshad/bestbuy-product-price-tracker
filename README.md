# Bestbuy Product Price Tracker

This project is a web application built with **Flask** that helps manage and retrieve product data from **PostgreSQL** and **MongoDB** databases. It includes some cool features like scraping product details, storing them, and providing easy access to product and price information through **REST APIs**.

#### Key Features:

1.  **Scraping with Playwright**:

    -   Collect product details using **Playwright** for web scraping.
    -   Scraping tasks are handled asynchronously using **Celery** to keep things smooth and efficient.
2.  **Database Integration**:

    -   Store product and price data in both **PostgreSQL** and **MongoDB** for flexible data management.
    -   Retrieve detailed product info and price history whenever needed.
3.  **Asynchronous Task Management**:

    -   Uses **Celery** with **RabbitMQ** as the message broker and **Redis** for the result backend to manage scraping tasks in the background.
4.  **Easy Deployment**:

    -   The app is containerized with **Docker**, so it's super easy to set up and run.
    -   Comes with a `docker-compose.yml` file for quick and hassle-free deployment.
5.  **Clean and Modular Design**:

    -   The code is organized to keep database operations, business logic, and API routes separate, making it easy to understand and extend.

This project is built to be **user-friendly** and **scalable**, so you can easily adapt it for tracking and managing product data as your needs grow.

---

## Table of Contents
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Endpoints](#endpoints)
  - [/health](#health)
  - [/scrape](#scrape)
  - [/job](#job)
  - [/products](#products)
  - [/product-prices](#product-prices)
  - [/product](#product)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

---

## Features
- Scrape product details from Best Buy Canada using web code.
- Asynchronous scraping tasks with Playwright and Celery.
- Store product data in PostgreSQL and MongoDB.
- Retrieve product details and price history through REST APIs.
- Modular design with clean separation of concerns.
- Easy deployment with Docker Compose.
- Scalable and user-friendly for managing product data.
- Detailed logging for monitoring and debugging.
- Secure and configurable with environment variables.
- CORS support for cross-origin requests.

---

## Technology Stack
- **Backend:** Flask, Celery, Playwright, BeautifulSoup, RabbitMQ, Redis
- **Database:** PostgreSQL (neon.tech), MongoDB (Atlas)
- **Other Tools:** Docker, logging

---

## Installation

### Prerequisites
Ensure you have the following installed:
- Python 3.12+
- PostgreSQL
- MongoDB
- Docker

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/samshad/bestbuy-product-price-tracker.git
   cd bestbuy-product-price-tracker
   ```

2. Configure environment variables:
   Create a `.env` file in the project root and add the following:
   ```env
   POSTGRES_URI=postgres://username:password@hostname:port/dbname  # Replace with actual credentials and host details
   MONGO_URI=mongodb+srv://username:password@cluster-url/dbname     # Replace with your MongoDB Atlas URI
   MONGO_DB_NAME=your_mongo_db_name
   MONGO_COLLECTION_NAME=your_collection_name
   ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000 # Specify allowed origins for local testing or trusted frontend sources or use wildcard * for all origins
   ```

3. Build and run the project using Docker Compose:
    ```sh
    docker-compose up -d
    ```

4. Access the application: [http://localhost:5000](http://localhost:5000)

---

## Configuration
- Environment variables are managed through a `.env` file.
- Logging configurations can be updated in the `app/utils/my_logger.py` file.
- The `Config.py` file can be updated for environment-specific settings in `app/utils/config.py`. Typical settings include:
  - **Database Credentials:** Specify database URIs, user credentials, and other connection details.
  - **API Keys:** Store API keys for third-party integrations.
  - **Application Behavior:** Define constants for features like pagination or debug mode.
  - **Security Settings:** Set allowed origins, token expiration times, and other security-related configurations.

---

## Endpoints

### `/health`
**Method:** `GET`
- Returns the current server time and health status.

**Response Example:**
```json
{
  "status": "healthy",
  "time": "2024-12-10T00:00:00-04:00"
}
```

### `/scrape`
**Method:** `POST`
- Scrapes product details using web code or URL. Required either `web_code` or `url`, but not both.

  - If both `web_code` and `url` are provided, the request will be rejected with an error message.
  - If neither `web_code` nor `url` is provided, the request will be rejected with an error message.

**Request Body Example:**
```json
{
  "web_code": "12345",
  "url": null
}
```

**Success Response Example:**
```json
{
  "message": "Product data added to PostgreSQL and MongoDB.",
  "product_details": {
    "title": "Product Title",
    "model": "Model123",
    "web_code": "12345",
    "price": 19999,
    "url": "https://www.bestbuy.ca/en-ca/product/12345",
    "save": 500,
    "date": "2024-12-10T00:00:00-04:00"
  }
}
```
*Note:* The `price` and `save` fields are stored as integers, where the last two digits represent cents for precision.

**Error Response Example:**
```json
{
  "error": "Either 'web_code' or 'url' must be provided, but not both."
}
```
### `/job`
**Method:** `GET`
- Fetches the status of a scraping task by its `job_id`.
- The `job_id` is generated when a scraping task is initiated.
- The status can be `Pending`, `In Progress`, `Complete` and `Failed`.

**Query Parameter:**
- `job_id` (required)

**Response Example:**
```json
{
    "job": {
        "created_at": "2024-12-25 16:16:09.226295",
        "job_id": "9f4f144d-741f-4211-a548-7a0b2c20039d",
        "product_id": "None",
        "result": "None",
        "status": "In Progress",
        "updated_at": "2024-12-25 16:16:10.382065",
        "webcode": "123456"
    }
}
```

### `/products`
**Method:** `GET`
- Fetches all product details from the database.

**Response Example:**
```json
{
  "products": [
    {
      "title": "Product Title",
      "model": "Model123",
      "web_code": "12345",
      "price": 19999,
      "url": "https://www.bestbuy.ca/en-ca/product/12345",
      "save": 500,
      "date": "2024-12-10T00:00:00-04:00"
    },
    { "...": "..." }
  ]
}
```
*Note:* The `price` and `save` fields are stored as integers, where the last two digits represent cents for precision.

### `/product-prices`
**Method:** `GET`
- Retrieves price history for a product by its `web_code`.

**Query Parameter:**
- `web_code` (required)

**Request Example:**
```json
{
  "web_code": "12345"
}
```

**Response Example:**
```json
{
  "prices": [
    {
      "price": 19999,
      "date": "2024-12-09T00:00:00-04:00"
    },
    {
      "price": 18999,
      "date": "2024-12-10T00:00:00-04:00"
    }
  ]
}
```
*Note:* The `price` field is stored as an integer, where the last two digits represent cents for precision.

### `/product`
**Method:** `GET`
- Fetches product details by either `web_code` or `product_id`. Required either `web_code` or `product_id`, but not both.
  - If both `web_code` and `product_id` are provided, the request will be rejected with an error message.
  - If neither `web_code` nor `product_id` is provided, the request will be rejected with an error message.

**Query Parameters:**
- `web_code` (optional)
- `product_id` (optional)

**Success Response Example:**
```json
{
  "product": {
    "title": "Product Title",
    "model": "Model123",
    "web_code": "12345",
    "price": 19999,
    "url": "https://www.bestbuy.ca/en-ca/product/12345",
    "save": 500,
    "date": "2024-12-10T00:00:00-04:00"
  }
}
```
*Note:* The `price` and `save` fields are stored as integers, where the last two digits represent cents for precision.

**Error Response Example:**
```json
{
  "error": "Either 'web_code' or 'product_id' must be provided, but not both."
}
```


## Project Structure
```
bestbuy-product-price-tracker/
├── app/
│   ├── db/               # Handles CRUD operations for PostgreSQL and MongoDB
│   ├── scrapers/         # Contains logic for scraping product data
│   ├── services/         # Implements core business logic and integrates scrapers with databases
│   │   ├── helpers/      # Helper functions for scraping and data processing
│   ├── tasks/            # Defines Celery tasks for asynchronous scraping
│   ├── utils/            # Utility modules for logging, configuration, and input validation
│   ├── routes.py         # Defines API routes for interacting with the system
├── tests/                # Unit and integration test cases
├── app.py                # Main entry point for starting the Flask application
├── requirements.txt      # Python dependencies
├── Dockerfile            # Configuration for building the Docker image
├── docker-compose.yml    # Docker Compose configuration for the application stack
└── README.md             # Project documentation
```

This structure separates concerns by organizing database operations, business logic, utility functions, and API routes into their respective directories.

---

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request.

1. Fork the repository.
2. Create a new branch for your feature or fix:
   ```bash
   git checkout -b feature/my-feature
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add my feature"
   ```
4. Push to the branch:
   ```bash
   git push origin feature/my-feature
   ```
5. Create a pull request.

---

## License
This project is licensed under the MIT License. See the LICENSE file for details.

---

## Acknowledgements
- [Flask](https://flask.palletsprojects.com/)
- [Playwright](https://playwright.dev/)
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Celery](https://docs.celeryproject.org/)
- [RabbitMQ](https://www.rabbitmq.com/)
- [Redis](https://redis.io/)
- [PostgreSQL (Neon)](https://console.neon.tech/)
- [MongoDB](https://www.mongodb.com/)
- [Docker](https://www.docker.com/)
- [Best Buy Canada](https://www.bestbuy.ca/en-ca)
